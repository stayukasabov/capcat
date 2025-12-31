#!/usr/bin/env python3
"""
Rate limiting system for Capcat to prevent overwhelming source servers.
Implements token bucket algorithm for smooth request throttling.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting a specific source."""

    requests_per_second: float = 2.0
    burst_size: int = 5
    min_delay_seconds: float = 0.5

    def __post_init__(self):
        """Validate configuration values."""
        if self.requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        if self.burst_size < 1:
            raise ValueError("burst_size must be at least 1")
        if self.min_delay_seconds < 0:
            raise ValueError("min_delay_seconds cannot be negative")


class RateLimiter:
    """
    Token bucket rate limiter for per-source request throttling.

    Implements a smooth rate limiting algorithm that allows bursts
    while maintaining an average rate limit over time.

    Example:
        limiter = RateLimiter(RateLimitConfig(requests_per_second=2.0))
        limiter.acquire()  # Blocks until token is available
        make_request()  # Perform the rate-limited operation
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter with configuration.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.tokens = float(config.burst_size)
        self.last_update = time.time()
        self.lock = threading.Lock()
        self.total_waits = 0
        self.total_wait_time = 0.0

    def acquire(self, blocking: bool = True) -> bool:
        """
        Acquire permission to make a request.

        Args:
            blocking: If True, block until a token is available.
                     If False, return immediately if no token available.

        Returns:
            True if token acquired, False if non-blocking and no token available
        """
        with self.lock:
            self._refill_tokens()

            if self.tokens >= 1:
                self.tokens -= 1
                return True

            if not blocking:
                return False

            # Calculate wait time for next token
            wait_time = (1 - self.tokens) / self.config.requests_per_second

            # Apply minimum delay if configured
            wait_time = max(wait_time, self.config.min_delay_seconds)

            # Track statistics
            self.total_waits += 1
            self.total_wait_time += wait_time

            logger.debug(
                f"Rate limit reached, waiting {wait_time:.2f}s "
                f"(total waits: {self.total_waits})"
            )

        # Release lock during sleep to allow other threads
        time.sleep(wait_time)

        with self.lock:
            self._refill_tokens()
            self.tokens = max(0, self.tokens - 1)
            return True

    def _refill_tokens(self):
        """Refill tokens based on elapsed time since last update."""
        now = time.time()
        elapsed = now - self.last_update
        new_tokens = elapsed * self.config.requests_per_second
        self.tokens = min(
            self.config.burst_size, self.tokens + new_tokens
        )
        self.last_update = now

    def get_stats(self) -> Dict[str, float]:
        """
        Get rate limiter statistics.

        Returns:
            Dictionary with wait statistics
        """
        with self.lock:
            return {
                "total_waits": self.total_waits,
                "total_wait_time": self.total_wait_time,
                "average_wait_time": (
                    self.total_wait_time / self.total_waits
                    if self.total_waits > 0
                    else 0.0
                ),
                "current_tokens": self.tokens,
            }

    def reset_stats(self):
        """Reset statistics counters."""
        with self.lock:
            self.total_waits = 0
            self.total_wait_time = 0.0


# Source-specific rate limit configurations
# Aggressive rate limiting for sources that commonly fail
SOURCE_RATE_LIMITS: Dict[str, RateLimitConfig] = {
    # Very conservative for problematic sources
    "scientificamerican": RateLimitConfig(
        requests_per_second=0.5, burst_size=2, min_delay_seconds=2.0
    ),
    "smithsonianmag": RateLimitConfig(
        requests_per_second=1.0, burst_size=3, min_delay_seconds=1.0
    ),
    # Moderate limits for sources with occasional issues
    "openai": RateLimitConfig(
        requests_per_second=1.5, burst_size=4, min_delay_seconds=0.7
    ),
    "nature": RateLimitConfig(
        requests_per_second=1.5, burst_size=4, min_delay_seconds=0.7
    ),
    # Default for all other sources
    "default": RateLimitConfig(
        requests_per_second=2.0, burst_size=5, min_delay_seconds=0.5
    ),
}


class RateLimiterPool:
    """
    Pool of rate limiters, one per source.

    Manages rate limiters for multiple sources, creating them on-demand
    and applying source-specific configurations.
    """

    def __init__(
        self, rate_limits: Optional[Dict[str, RateLimitConfig]] = None
    ):
        """
        Initialize rate limiter pool.

        Args:
            rate_limits: Optional custom rate limit configurations
        """
        self.rate_limits = rate_limits or SOURCE_RATE_LIMITS
        self.limiters: Dict[str, RateLimiter] = {}
        self.lock = threading.Lock()

    def get_limiter(self, source_code: str) -> RateLimiter:
        """
        Get or create rate limiter for a source.

        Args:
            source_code: Source identifier (e.g., 'hn', 'scientificamerican')

        Returns:
            RateLimiter instance for the source
        """
        with self.lock:
            if source_code not in self.limiters:
                # Get source-specific config or default
                config = self.rate_limits.get(
                    source_code, self.rate_limits.get("default")
                )
                self.limiters[source_code] = RateLimiter(config)
                logger.debug(
                    f"Created rate limiter for {source_code}: "
                    f"{config.requests_per_second} req/s, "
                    f"burst: {config.burst_size}"
                )

            return self.limiters[source_code]

    def acquire(self, source_code: str, blocking: bool = True) -> bool:
        """
        Acquire rate limit permission for a source.

        Args:
            source_code: Source identifier
            blocking: Whether to block until token available

        Returns:
            True if acquired, False if non-blocking and unavailable
        """
        limiter = self.get_limiter(source_code)
        return limiter.acquire(blocking)

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistics for all rate limiters.

        Returns:
            Dictionary mapping source codes to their statistics
        """
        with self.lock:
            return {
                source: limiter.get_stats()
                for source, limiter in self.limiters.items()
            }

    def reset_all_stats(self):
        """Reset statistics for all rate limiters."""
        with self.lock:
            for limiter in self.limiters.values():
                limiter.reset_stats()


# Global rate limiter pool instance
_global_limiter_pool: Optional[RateLimiterPool] = None
_pool_lock = threading.Lock()


def get_rate_limiter_pool() -> RateLimiterPool:
    """
    Get the global rate limiter pool instance (singleton).

    Returns:
        Global RateLimiterPool instance
    """
    global _global_limiter_pool

    if _global_limiter_pool is None:
        with _pool_lock:
            if _global_limiter_pool is None:
                _global_limiter_pool = RateLimiterPool()
                logger.debug("Initialized global rate limiter pool")

    return _global_limiter_pool


def acquire_rate_limit(source_code: str, blocking: bool = True) -> bool:
    """
    Convenience function to acquire rate limit from global pool.

    Args:
        source_code: Source identifier
        blocking: Whether to block until available

    Returns:
        True if acquired, False if non-blocking and unavailable
    """
    pool = get_rate_limiter_pool()
    return pool.acquire(source_code, blocking)
