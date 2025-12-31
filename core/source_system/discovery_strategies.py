#!/usr/bin/env python3
"""
Discovery strategy implementations for article discovery.
Implements Strategy pattern for clean separation of discovery methods.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from ..rate_limiter import acquire_rate_limit
from ..retry import network_retry
from .base_source import Article, ArticleDiscoveryError
from .feed_discovery import discover_feed_urls, validate_feed
from .feed_parser import FeedParserFactory


@network_retry
def _fetch_url_with_retry(
    session: requests.Session, url: str, timeout: int, headers: dict = None,
    source_code: str = "unknown"
) -> requests.Response:
    """
    Fetch URL with automatic retry logic and rate limiting.

    This function provides:
    - Rate limiting based on source-specific configuration
    - Up to 3 retry attempts (via @network_retry decorator)
    - Exponential backoff (1s, 2s, 4s)
    - Automatic handling of connection errors and timeouts

    Args:
        session: Requests session to use
        url: URL to fetch
        timeout: Request timeout in seconds
        headers: Optional request headers
        source_code: Source identifier for rate limiting

    Returns:
        Response object

    Raises:
        requests.exceptions.RequestException: After all retries exhausted
    """
    # Apply rate limiting before making request
    acquire_rate_limit(source_code, blocking=True)

    response = session.get(url, timeout=timeout, headers=headers or {})
    response.raise_for_status()
    return response


class DiscoveryStrategy(ABC):
    """Base class for article discovery strategies."""

    @abstractmethod
    def discover(
        self,
        count: int,
        config: dict,
        session: requests.Session,
        base_url: str,
        timeout: int,
        logger,
        should_skip_callback
    ) -> List[Article]:
        """
        Discover articles using this strategy.

        Args:
            count: Maximum number of articles to discover
            config: Configuration dictionary
            session: HTTP session for requests
            base_url: Base URL for the source
            timeout: Request timeout in seconds
            logger: Logger instance
            should_skip_callback: Callback to check if URL should be skipped

        Returns:
            List of Article objects

        Raises:
            ArticleDiscoveryError: If discovery fails
        """
        pass


class RSSDiscoveryStrategy(DiscoveryStrategy):
    """Discovery strategy using RSS/Atom feeds."""

    def discover(
        self,
        count: int,
        config: dict,
        session: requests.Session,
        base_url: str,
        timeout: int,
        logger,
        should_skip_callback
    ) -> List[Article]:
        """
        Discover articles via RSS/Atom feed.

        Args:
            count: Maximum number of articles to discover
            config: Configuration dictionary with 'discovery' section
            session: HTTP session for requests
            base_url: Base URL for the source
            timeout: Request timeout in seconds
            logger: Logger instance
            should_skip_callback: Callback(url, title) -> bool

        Returns:
            List of Article objects

        Raises:
            ArticleDiscoveryError: If RSS discovery fails
        """
        discovery_config = config.get("discovery", {})
        source_code = config.get("name", "unknown")

        # Support multiple RSS URL formats:
        # 1. New format: {primary: "url", fallbacks: ["url1", "url2"]}
        # 2. Legacy format: Single string URL
        rss_config = discovery_config.get("rss_urls") or discovery_config.get("rss_url")

        # Also check top-level for backward compatibility
        if not rss_config:
            rss_config = config.get("rss_url")

        if not rss_config:
            raise ArticleDiscoveryError(
                "RSS discovery requires rss_url or rss_urls in config",
                source_code
            )

        # Build list of URLs to try
        urls_to_try = []

        if isinstance(rss_config, dict):
            # New format with primary + fallbacks
            primary = rss_config.get("primary")
            if primary:
                urls_to_try.append(primary)
            fallbacks = rss_config.get("fallbacks", [])
            urls_to_try.extend(fallbacks)
        elif isinstance(rss_config, str):
            # Legacy single URL format
            urls_to_try.append(rss_config)
        else:
            raise ArticleDiscoveryError(
                f"Invalid rss_url configuration format: {type(rss_config)}",
                source_code
            )

        # Auto-discovery flag
        auto_discover = discovery_config.get("auto_discover", False)

        # Try each URL in sequence
        last_exception = None
        feed_items = None

        for url in urls_to_try:
            try:
                logger.debug(f"Attempting to fetch RSS feed from {url}")

                # Use retry-enabled fetch with rate limiting
                response = _fetch_url_with_retry(
                    session,
                    url,
                    timeout,
                    headers={"User-Agent": "Capcat/2.0 (Personal news archiver)"},
                    source_code=source_code,
                )

                # Validate feed before parsing
                if not validate_feed(response.content):
                    logger.debug(f"Invalid feed format at {url}, trying next")
                    continue

                # Parse feed using factory (auto-detects RSS vs Atom)
                feed_items = FeedParserFactory.detect_and_parse(response.content)

                if feed_items:
                    logger.info(f"Successfully fetched RSS feed from {url}")
                    break

            except Exception as e:
                logger.debug(f"Failed to fetch RSS from {url}: {e}")
                last_exception = e
                continue

        # If all configured URLs failed, try auto-discovery
        if not feed_items and auto_discover:
            logger.info(f"All configured URLs failed, attempting auto-discovery for {base_url}")

            try:
                discovered_urls = discover_feed_urls(base_url, timeout)

                for url in discovered_urls:
                    try:
                        logger.debug(f"Trying discovered feed URL: {url}")

                        response = _fetch_url_with_retry(
                            session,
                            url,
                            timeout,
                            headers={"User-Agent": "Capcat/2.0 (Personal news archiver)"},
                            source_code=source_code,
                        )

                        if validate_feed(response.content):
                            feed_items = FeedParserFactory.detect_and_parse(response.content)

                            if feed_items:
                                logger.info(f"Successfully discovered and fetched RSS from {url}")
                                logger.info(f"TIP: Add '{url}' to source config as primary or fallback URL")
                                break

                    except Exception as e:
                        logger.debug(f"Discovered URL {url} failed: {e}")
                        continue

            except Exception as e:
                logger.debug(f"Auto-discovery failed for {base_url}: {e}")

        # If still no feed items, raise error
        if not feed_items:
            error_msg = f"Could not fetch RSS feed from any configured URL"
            if last_exception:
                error_msg += f". Last error: {last_exception}"
            raise ArticleDiscoveryError(error_msg, source_code)

        logger.debug(f"Parsed {len(feed_items)} items from feed")

        # Convert feed items to Article objects
        articles = []
        skip_patterns = config.get("skip_patterns", [])

        for item in feed_items:
            if len(articles) >= count:
                break

            # Apply skip patterns
            if self._should_skip_patterns(item.url, skip_patterns):
                continue

            # Apply callback skip logic
            if should_skip_callback(item.url, item.title):
                continue

            article = Article(
                title=item.title,
                url=item.url,
                summary=item.description,
                comment_url=None,
            )
            articles.append(article)

        logger.debug(f"Discovered {len(articles)} articles via RSS")
        return articles

    @staticmethod
    def _should_skip_patterns(url: str, patterns: List[str]) -> bool:
        """Check if URL matches any skip pattern."""
        return any(pattern in url for pattern in patterns)


class HTMLDiscoveryStrategy(DiscoveryStrategy):
    """Discovery strategy using HTML scraping."""

    def discover(
        self,
        count: int,
        config: dict,
        session: requests.Session,
        base_url: str,
        timeout: int,
        logger,
        should_skip_callback
    ) -> List[Article]:
        """
        Discover articles via HTML scraping.

        Args:
            count: Maximum number of articles to discover
            config: Configuration dictionary with 'article_selectors'
            session: HTTP session for requests
            base_url: Base URL to scrape
            timeout: Request timeout in seconds
            logger: Logger instance
            should_skip_callback: Callback(url, title) -> bool

        Returns:
            List of Article objects

        Raises:
            ArticleDiscoveryError: If HTML discovery fails
        """
        article_selectors = config.get("article_selectors", [])
        skip_patterns = config.get("skip_patterns", [])

        if not article_selectors:
            raise ArticleDiscoveryError(
                "HTML discovery requires article_selectors in config",
                config.get("name", "unknown")
            )

        logger.debug(f"Scraping HTML from {base_url}")

        # Get source code for rate limiting
        source_code = config.get("name", "unknown")

        try:
            # Use retry-enabled fetch with rate limiting
            response = _fetch_url_with_retry(
                session, base_url, timeout, source_code=source_code
            )

            soup = BeautifulSoup(response.text, "html.parser")

            articles = []
            processed_urls = set()

            for selector in article_selectors:
                if len(articles) >= count:
                    break

                try:
                    links = soup.select(selector)
                    logger.debug(f"Selector '{selector}' found {len(links)} links")

                    for link in links:
                        if len(articles) >= count:
                            break

                        article = self._extract_article_from_link(
                            link,
                            base_url,
                            skip_patterns,
                            processed_urls,
                            should_skip_callback,
                            logger
                        )

                        if article:
                            articles.append(article)
                            processed_urls.add(article.url)

                except Exception as e:
                    logger.warning(f"Selector '{selector}' failed: {e}")
                    continue

            logger.debug(f"Discovered {len(articles)} articles via HTML")
            return articles

        except requests.RequestException as e:
            raise ArticleDiscoveryError(
                f"Failed to fetch HTML from {base_url}: {e}",
                config.get("name", "unknown")
            )

    def _extract_article_from_link(
        self,
        link,
        base_url: str,
        skip_patterns: List[str],
        processed_urls: set,
        should_skip_callback,
        logger
    ) -> Optional[Article]:
        """
        Extract article information from a link element.

        Returns:
            Article object if valid, None if should be skipped
        """
        href = link.get("href", "")
        if not href:
            return None

        # Convert to absolute URL
        absolute_url = self._make_absolute_url(href, base_url)

        # Skip if already processed
        if absolute_url in processed_urls:
            return None

        # Skip based on patterns
        if any(pattern in absolute_url for pattern in skip_patterns):
            return None

        # Extract title
        title = link.get_text().strip() or "Untitled Article"

        # Apply callback skip logic
        if should_skip_callback(absolute_url, title):
            return None

        return Article(
            title=title,
            url=absolute_url,
            comment_url=None,
        )

    @staticmethod
    def _make_absolute_url(href: str, base_url: str) -> str:
        """Convert relative URL to absolute URL."""
        if href.startswith(("http://", "https://")):
            return href
        return urljoin(base_url, href)


class DiscoveryStrategyFactory:
    """Factory for creating discovery strategies."""

    @staticmethod
    def create(discovery_config: dict, legacy_config: dict = None) -> DiscoveryStrategy:
        """
        Create appropriate discovery strategy based on configuration.

        Supports both new schema (discovery.method) and legacy schema
        (top-level rss_url).

        Args:
            discovery_config: Discovery configuration dictionary
            legacy_config: Full config for backward compatibility (optional)

        Returns:
            DiscoveryStrategy instance

        Raises:
            ValueError: If discovery method is unsupported
        """
        # Check for legacy schema (top-level rss_url)
        if legacy_config and legacy_config.get("rss_url") and not discovery_config.get("method"):
            return RSSDiscoveryStrategy()

        method = discovery_config.get("method", "html").lower()

        if method == "rss":
            return RSSDiscoveryStrategy()
        elif method == "html":
            return HTMLDiscoveryStrategy()
        else:
            raise ValueError(f"Unsupported discovery method: {method}")
