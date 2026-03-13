#!/usr/bin/env python3
"""
Adaptive timeout configuration for Capcat.
Provides source-specific timeouts and adaptive learning from response times.
"""

import statistics
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class TimeoutConfig:
    """Configuration for connection and read timeouts."""

    connect_timeout: int  # Time to establish connection (seconds)
    read_timeout: int  # Time to read response (seconds)
    total_timeout: int  # Overall operation timeout (seconds)

    def as_tuple(self) -> Tuple[int, int]:
        """
        Get timeout as tuple for requests library.

        Returns:
            Tuple of (connect_timeout, read_timeout)
        """
        return (self.connect_timeout, self.read_timeout)

    def __post_init__(self):
        """Validate timeout values."""
        if self.connect_timeout < 1:
            raise ValueError("connect_timeout must be at least 1")
        if self.read_timeout < 1:
            raise ValueError("read_timeout must be at least 1")
        if self.total_timeout < self.connect_timeout + self.read_timeout:
            raise ValueError(
                "total_timeout must be >= connect_timeout + read_timeout"
            )


# Source-specific timeout configurations
# Based on observed performance characteristics
SOURCE_TIMEOUTS: Dict[str, TimeoutConfig] = {
    # Very slow sources (large pages, slow servers)
    "scientificamerican": TimeoutConfig(
        connect_timeout=15,
        read_timeout=60,
        total_timeout=90,
    ),
    "nature": TimeoutConfig(
        connect_timeout=15,
        read_timeout=45,
        total_timeout=75,
    ),
    "smithsonianmag": TimeoutConfig(
        connect_timeout=15,
        read_timeout=45,
        total_timeout=75,
    ),
    # Moderately slow sources
    "guardian": TimeoutConfig(
        connect_timeout=10,
        read_timeout=30,
        total_timeout=45,
    ),
    "bbc": TimeoutConfig(
        connect_timeout=10,
        read_timeout=30,
        total_timeout=45,
    ),
    "gizmodo": TimeoutConfig(
        connect_timeout=10,
        read_timeout=30,
        total_timeout=45,
    ),
    "techcrunch": TimeoutConfig(
        connect_timeout=10,
        read_timeout=30,
        total_timeout=45,
    ),
    # Fast sources (RSS, simple pages)
    "lesswrong": TimeoutConfig(
        connect_timeout=5,
        read_timeout=15,
        total_timeout=25,
    ),
    "hn": TimeoutConfig(
        connect_timeout=8,
        read_timeout=20,
        total_timeout=30,
    ),
    "lb": TimeoutConfig(
        connect_timeout=8,
        read_timeout=20,
        total_timeout=30,
    ),
    "iq": TimeoutConfig(
        connect_timeout=8,
        read_timeout=20,
        total_timeout=30,
    ),
    # Default for unknown sources
    "default": TimeoutConfig(
        connect_timeout=10,
        read_timeout=30,
        total_timeout=45,
    ),
}


class TimeoutTracker:
    """
    Track actual response times to recommend timeout adjustments.

    Collects response time data and uses statistical analysis to
    suggest optimal timeout values.
    """

    def __init__(self, history_size: int = 100):
        """
        Initialize timeout tracker.

        Args:
            history_size: Maximum number of response times to track per source
        """
        self.history_size = history_size
        self.response_times: Dict[str, List[float]] = {}
        self.lock = threading.Lock()

    def record_response_time(self, source_code: str, duration: float):
        """
        Record successful response time.

        Args:
            source_code: Source identifier
            duration: Response time in seconds
        """
        with self.lock:
            if source_code not in self.response_times:
                self.response_times[source_code] = []

            self.response_times[source_code].append(duration)

            # Keep only recent measurements
            if len(self.response_times[source_code]) > self.history_size:
                self.response_times[source_code] = self.response_times[source_code][
                    -self.history_size :
                ]

            logger.debug(
                f"Recorded response time for {source_code}: {duration:.2f}s "
                f"(total samples: {len(self.response_times[source_code])})"
            )

    def get_recommended_timeout(
        self, source_code: str, min_samples: int = 10
    ) -> Optional[TimeoutConfig]:
        """
        Get recommended timeout based on historical data.

        Uses percentile analysis to suggest timeout values that
        will succeed for most requests while allowing margin for slower responses.

        Args:
            source_code: Source identifier
            min_samples: Minimum number of samples required

        Returns:
            Recommended TimeoutConfig or None if insufficient data
        """
        with self.lock:
            if source_code not in self.response_times:
                return None

            times = self.response_times[source_code]
            if len(times) < min_samples:
                logger.debug(
                    f"Insufficient data for {source_code}: "
                    f"{len(times)}/{min_samples} samples"
                )
                return None

            # Calculate percentiles
            p50 = statistics.median(times)  # Median
            sorted_times = sorted(times)

            # Calculate 95th percentile manually
            p95_index = int(len(sorted_times) * 0.95)
            p95 = sorted_times[min(p95_index, len(sorted_times) - 1)]

            # Calculate 99th percentile
            p99_index = int(len(sorted_times) * 0.99)
            p99 = sorted_times[min(p99_index, len(sorted_times) - 1)]

            # Recommend timeouts with safety margins
            # Connect: p50 * 1.5 + 5s (should be quick)
            # Read: p95 * 1.2 + 10s (handle slower responses)
            # Total: p99 * 1.1 + 15s (maximum allowed time)
            recommended = TimeoutConfig(
                connect_timeout=max(5, int(p50 * 1.5) + 5),
                read_timeout=max(15, int(p95 * 1.2) + 10),
                total_timeout=max(30, int(p99 * 1.1) + 15),
            )

            logger.debug(
                f"Recommended timeout for {source_code}: "
                f"connect={recommended.connect_timeout}s, "
                f"read={recommended.read_timeout}s (based on {len(times)} samples)"
            )

            return recommended

    def get_stats(self, source_code: str) -> Dict[str, float]:
        """
        Get statistics for a source.

        Args:
            source_code: Source identifier

        Returns:
            Dictionary with statistics (empty if no data)
        """
        with self.lock:
            if source_code not in self.response_times or not self.response_times[
                source_code
            ]:
                return {}

            times = self.response_times[source_code]
            sorted_times = sorted(times)

            # Calculate percentiles
            p95_index = int(len(sorted_times) * 0.95)
            p95 = sorted_times[min(p95_index, len(sorted_times) - 1)]

            return {
                "count": len(times),
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "p95": p95,
            }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistics for all sources.

        Returns:
            Dictionary mapping source codes to their statistics
        """
        with self.lock:
            return {source: self.get_stats(source) for source in self.response_times}


# Global timeout tracker instance
_global_timeout_tracker: Optional[TimeoutTracker] = None
_tracker_lock = threading.Lock()


def get_timeout_tracker() -> TimeoutTracker:
    """
    Get the global timeout tracker instance (singleton).

    Returns:
        Global TimeoutTracker instance
    """
    global _global_timeout_tracker

    if _global_timeout_tracker is None:
        with _tracker_lock:
            if _global_timeout_tracker is None:
                _global_timeout_tracker = TimeoutTracker()
                logger.debug("Initialized global timeout tracker")

    return _global_timeout_tracker


def get_timeout_for_source(source_code: str, use_adaptive: bool = True) -> TimeoutConfig:
    """
    Get timeout configuration for source.

    Tries in order:
    1. Configured source-specific timeout
    2. Adaptive learned timeout (if enabled and sufficient data)
    3. Default timeout

    Args:
        source_code: Source identifier
        use_adaptive: Whether to use adaptive learned timeouts

    Returns:
        TimeoutConfig for the source
    """
    # Try configured timeout first
    if source_code in SOURCE_TIMEOUTS:
        config = SOURCE_TIMEOUTS[source_code]
        logger.debug(
            f"Using configured timeout for {source_code}: "
            f"{config.connect_timeout}s connect, {config.read_timeout}s read"
        )
        return config

    # Try adaptive learning if enabled
    if use_adaptive:
        tracker = get_timeout_tracker()
        recommended = tracker.get_recommended_timeout(source_code)
        if recommended:
            logger.debug(f"Using adaptive timeout for {source_code}")
            return recommended

    # Fall back to default
    logger.debug(f"Using default timeout for {source_code}")
    return SOURCE_TIMEOUTS["default"]


def record_response_time(source_code: str, duration: float):
    """
    Convenience function to record response time.

    Args:
        source_code: Source identifier
        duration: Response time in seconds
    """
    tracker = get_timeout_tracker()
    tracker.record_response_time(source_code, duration)
