#!/usr/bin/env python3
"""
Ethical scraping utilities for Capcat.

Implements best practices:
1. Robots.txt caching with 15-minute TTL
2. 429/503 error handling with exponential backoff
3. Rate limiting enforcement
4. Path validation against robots.txt
"""

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests


@dataclass
class RobotsTxtCache:
    """Cache entry for robots.txt."""

    parser: RobotFileParser
    crawl_delay: float
    timestamp: datetime


class EthicalScrapingManager:
    """
    Manages ethical scraping compliance.

    Features:
    - Robots.txt caching (15-minute TTL)
    - Crawl delay enforcement
    - 429/503 exponential backoff
    - Path validation
    """

    def __init__(self, user_agent: str = "Capcat/2.0"):
        """
        Initialize ethical scraping manager.

        Args:
            user_agent: User agent string for requests
        """
        self.user_agent = user_agent
        self.robots_cache: Dict[str, RobotsTxtCache] = {}
        self.cache_ttl = timedelta(minutes=15)
        self.last_request_time: Dict[str, float] = {}

    def get_robots_txt(
        self, base_url: str, timeout: int = 10
    ) -> Tuple[RobotFileParser, float]:
        """
        Fetch and parse robots.txt with caching.

        Args:
            base_url: Base URL of the site
            timeout: Request timeout in seconds

        Returns:
            Tuple of (RobotFileParser, crawl_delay)
        """
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        # Check cache
        if domain in self.robots_cache:
            cached = self.robots_cache[domain]
            age = datetime.now() - cached.timestamp

            if age < self.cache_ttl:
                return cached.parser, cached.crawl_delay

        # Fetch robots.txt
        robots_url = f"{domain}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            response = requests.get(
                robots_url,
                timeout=timeout,
                headers={"User-Agent": self.user_agent},
            )

            if response.status_code == 200:
                parser.parse(response.text.splitlines())
            else:
                # No robots.txt or error - allow all
                parser.parse([])

        except Exception:
            # On error, assume permissive rules
            parser.parse([])

        # Extract crawl delay
        crawl_delay = self._extract_crawl_delay(parser)

        # Cache result
        self.robots_cache[domain] = RobotsTxtCache(
            parser=parser, crawl_delay=crawl_delay, timestamp=datetime.now()
        )

        return parser, crawl_delay

    def _extract_crawl_delay(self, parser: RobotFileParser) -> float:
        """
        Extract crawl delay from robots.txt parser.

        Args:
            parser: RobotFileParser instance

        Returns:
            Crawl delay in seconds (0.0 if not specified)
        """
        try:
            # Try to get crawl delay for our user agent
            if hasattr(parser, "crawl_delay"):
                delay = parser.crawl_delay(self.user_agent)
                if delay is not None:
                    return float(delay)

            # Parse manually from entries
            for entry in parser.entries:
                if entry.applies_to(self.user_agent):
                    if hasattr(entry, "delay"):
                        return float(entry.delay or 0.0)

        except Exception:
            pass

        return 0.0

    def can_fetch(self, url: str) -> Tuple[bool, str]:
        """
        Check if URL can be fetched according to robots.txt.

        Args:
            url: URL to check

        Returns:
            Tuple of (allowed, reason)
        """
        try:
            parser, crawl_delay = self.get_robots_txt(url)
            allowed = parser.can_fetch(self.user_agent, url)

            if not allowed:
                return False, "Blocked by robots.txt"

            return True, f"Allowed (crawl_delay: {crawl_delay}s)"

        except Exception as e:
            # On error, be conservative and allow
            return True, f"Robots.txt check failed: {e}"

    def enforce_rate_limit(
        self, domain: str, crawl_delay: float, min_delay: float = 1.0
    ):
        """
        Enforce rate limiting with crawl delay.

        Args:
            domain: Domain being accessed
            crawl_delay: Required crawl delay from robots.txt
            min_delay: Minimum delay even if robots.txt doesn't specify
        """
        effective_delay = max(crawl_delay, min_delay)

        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            remaining = effective_delay - elapsed

            if remaining > 0:
                time.sleep(remaining)

        self.last_request_time[domain] = time.time()

    def request_with_backoff(
        self,
        session: requests.Session,
        url: str,
        method: str = "GET",
        max_retries: int = 3,
        initial_delay: float = 1.0,
        **kwargs,
    ) -> requests.Response:
        """
        Make HTTP request with exponential backoff for 429/503 errors.

        Args:
            session: Requests session
            url: URL to fetch
            method: HTTP method (GET, POST, etc.)
            max_retries: Maximum number of retries
            initial_delay: Initial retry delay in seconds
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            requests.RequestException: If all retries fail
        """
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        # Check robots.txt
        parser, crawl_delay = self.get_robots_txt(url)

        if not parser.can_fetch(self.user_agent, url):
            raise requests.RequestException(
                f"URL blocked by robots.txt: {url}"
            )

        # Enforce rate limit
        self.enforce_rate_limit(domain, crawl_delay)

        # Make request with backoff
        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries):
            try:
                response = session.request(method, url, **kwargs)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")

                    if retry_after:
                        try:
                            wait_time = float(retry_after)
                        except ValueError:
                            wait_time = delay
                    else:
                        wait_time = delay

                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                        delay *= 2  # Exponential backoff
                        continue

                # Handle service unavailable
                elif response.status_code == 503:
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2
                        continue

                # Success or non-retryable error
                response.raise_for_status()
                return response

            except requests.RequestException as e:
                last_exception = e

                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise

        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        else:
            raise requests.RequestException(f"Failed to fetch {url}")

    def validate_source_config(
        self, base_url: str, rate_limit: float
    ) -> Tuple[bool, str]:
        """
        Validate source configuration against robots.txt.

        Args:
            base_url: Base URL of the source
            rate_limit: Configured rate limit in seconds

        Returns:
            Tuple of (valid, message)
        """
        try:
            parser, crawl_delay = self.get_robots_txt(base_url)

            # Check if path is allowed
            if not parser.can_fetch(self.user_agent, base_url):
                return (
                    False,
                    f"Base URL blocked by robots.txt: {base_url}",
                )

            # Check rate limit compliance
            if crawl_delay > 0 and rate_limit < crawl_delay:
                return (
                    False,
                    f"Rate limit {rate_limit}s < required {crawl_delay}s",
                )

            return True, f"Compliant (crawl_delay: {crawl_delay}s)"

        except Exception as e:
            return False, f"Validation error: {e}"

    def get_cache_stats(self) -> Dict[str, any]:
        """
        Get statistics about robots.txt cache.

        Returns:
            Dictionary with cache statistics
        """
        now = datetime.now()
        fresh = 0
        stale = 0

        for cached in self.robots_cache.values():
            age = now - cached.timestamp
            if age < self.cache_ttl:
                fresh += 1
            else:
                stale += 1

        return {
            "total_cached": len(self.robots_cache),
            "fresh_entries": fresh,
            "stale_entries": stale,
            "cache_ttl_minutes": self.cache_ttl.total_seconds() / 60,
        }

    def clear_stale_cache(self):
        """Remove stale entries from robots.txt cache."""
        now = datetime.now()
        domains_to_remove = []

        for domain, cached in self.robots_cache.items():
            age = now - cached.timestamp
            if age >= self.cache_ttl:
                domains_to_remove.append(domain)

        for domain in domains_to_remove:
            del self.robots_cache[domain]


# Global instance for convenience
_global_manager: Optional[EthicalScrapingManager] = None


def get_ethical_manager(
    user_agent: str = "Capcat/2.0",
) -> EthicalScrapingManager:
    """
    Get or create global ethical scraping manager.

    Args:
        user_agent: User agent string

    Returns:
        EthicalScrapingManager instance
    """
    global _global_manager

    if _global_manager is None:
        _global_manager = EthicalScrapingManager(user_agent)

    return _global_manager
