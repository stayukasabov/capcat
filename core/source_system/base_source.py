#!/usr/bin/env python3
"""
Abstract base class for all news sources.
Defines the contract that all source implementations must follow.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests


@dataclass
class SourceConfig:
    """Configuration data class for news sources."""

    name: str
    display_name: str
    base_url: str
    timeout: float = 10.0
    rate_limit: float = 1.0
    supports_comments: bool = False
    has_comments: bool = False
    category: str = "general"

    # Optional custom configuration
    custom_config: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_config is None:
            self.custom_config = {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format for compatibility.

        Returns:
            Dictionary representation of the source configuration
        """
        result = {
            "name": self.name,
            "display_name": self.display_name,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "rate_limit": self.rate_limit,
            "supports_comments": self.supports_comments,
            "has_comments": self.has_comments,
            "category": self.category,
        }

        # Add custom configuration
        if self.custom_config:
            result.update(self.custom_config)

        return result


@dataclass
class Article:
    """Data class representing a news article."""

    title: str
    url: str
    comment_url: Optional[str] = None

    # Optional metadata
    author: Optional[str] = None
    published_date: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class BaseSource(ABC):
    """
    Abstract base class for all news sources.

    This defines the contract that all source implementations must follow,
    ensuring consistent behavior across different news sources.
    """

    def __init__(
        self, config: SourceConfig, session: Optional[requests.Session] = None
    ):
        """
        Initialize the source with configuration.

        Args:
            config: Source configuration
            session: Optional HTTP session for connection pooling
        """
        self.config = config
        self.session = session or requests.Session()
        self.logger = self._get_logger()

        # Initialize performance monitoring
        self._setup_performance_monitoring()

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Return the source type ('config_driven' or 'custom')."""
        pass

    @abstractmethod
    def discover_articles(self, count: int) -> List[Article]:
        """
        Discover articles from the source.

        Args:
            count: Maximum number of articles to discover

        Returns:
            List of Article objects

        Raises:
            SourceError: If article discovery fails
        """
        pass

    @abstractmethod
    def fetch_article_content(
        self, article: Article, output_dir: str, progress_callback=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Fetch and save article content.

        Args:
            article: Article to fetch
            output_dir: Directory to save content
            progress_callback: Optional progress callback function

        Returns:
            Tuple of (success, article_path)

        Raises:
            SourceError: If content fetching fails
        """
        pass

    def fetch_comments(
        self, article: Article, output_dir: str, progress_callback=None
    ) -> bool:
        """
        Fetch and save article comments (if supported).

        Args:
            article: Article to fetch comments for
            output_dir: Directory to save comments
            progress_callback: Optional progress callback function

        Returns:
            True if comments were fetched successfully, False otherwise
        """
        if not self.config.supports_comments:
            return False
        return self._fetch_comments_impl(
            article, output_dir, progress_callback
        )

    def _fetch_comments_impl(
        self, article: Article, output_dir: str, progress_callback=None
    ) -> bool:
        """
        Implementation of comment fetching (override in subclasses that support comments).

        Args:
            article: Article to fetch comments for
            output_dir: Directory to save comments
            progress_callback: Optional progress callback function

        Returns:
            True if comments were fetched successfully, False otherwise
        """
        return False

    def validate_config(self) -> List[str]:
        """
        Validate the source configuration.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.config.name:
            errors.append("Source name is required")

        if not self.config.display_name:
            errors.append("Source display name is required")

        if not self.config.base_url:
            errors.append("Source base URL is required")
        elif not self.config.base_url.startswith(("http://", "https://")):
            errors.append(
                "Source base URL must start with http:// or https://"
            )

        if self.config.timeout <= 0:
            errors.append("Timeout must be positive")

        if self.config.rate_limit < 0:
            errors.append("Rate limit must be non-negative")

        # Allow subclasses to add their own validation
        errors.extend(self._validate_custom_config())

        return errors

    def _validate_custom_config(self) -> List[str]:
        """
        Validate custom configuration (override in subclasses).

        Returns:
            List of validation error messages
        """
        return []

    def should_skip_url(self, url: str, title: str = "") -> bool:
        """
        Check if a URL should be skipped during processing.

        Args:
            url: URL to check
            title: Optional article title

        Returns:
            True if URL should be skipped
        """
        # Skip only clearly non-content URLs (keep binary files for proper handling by article fetcher)
        skip_extensions = [".zip", ".tar", ".gz", ".exe", ".dmg", ".iso"]
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return True

        # Allow subclasses to add custom skip logic
        return self._should_skip_custom(url, title)

    def _should_skip_custom(self, url: str, title: str = "") -> bool:
        """
        Custom skip logic (override in subclasses).

        Args:
            url: URL to check
            title: Optional article title

        Returns:
            True if URL should be skipped
        """
        return False

    def get_rate_limit(self) -> float:
        """Get the rate limit for this source."""
        return self.config.rate_limit

    def get_timeout(self) -> float:
        """Get the timeout for this source."""
        return self.config.timeout

    def _get_logger(self):
        """Get a logger instance for this source."""
        from ..logging_config import get_logger

        return get_logger(f"source.{self.config.name}")

    def _setup_performance_monitoring(self):
        """Setup performance monitoring for this source."""
        try:
            from .performance_monitor import get_performance_monitor

            self.performance_monitor = get_performance_monitor()
        except ImportError:
            # Performance monitoring is optional
            self.performance_monitor = None

    def _start_performance_timing(self) -> float:
        """Start performance timing for an operation."""
        if self.performance_monitor:
            return self.performance_monitor.start_request(
                self.config.name, self.source_type
            )
        return 0.0

    def _end_performance_timing(
        self,
        start_time: float,
        success: bool,
        error_type: Optional[str] = None,
    ):
        """End performance timing for an operation."""
        if self.performance_monitor:
            self.performance_monitor.end_request(
                self.config.name, start_time, success, error_type
            )

    def _record_article_discovery(self, count: int):
        """Record successful article discovery."""
        if self.performance_monitor:
            self.performance_monitor.record_article_discovery(
                self.config.name, count
            )

    def _record_content_fetch(self, success: bool):
        """Record content fetching result."""
        if self.performance_monitor:
            self.performance_monitor.record_content_fetch(
                self.config.name, success
            )

    def discover_articles_with_retry_skip(
        self, count: int, max_retries: int = 2, batch_mode: bool = False
    ) -> Optional[List[Article]]:
        """
        Discover articles with retry-and-skip logic for network resilience.

        Attempts to discover articles up to max_retries times. If all attempts
        fail due to timeout or connection errors, returns None (skip source).

        Args:
            count: Maximum number of articles to discover
            max_retries: Maximum number of retry attempts (default: 2)
            batch_mode: Whether processing multiple sources (affects user messages)

        Returns:
            List of Article objects if successful, None if skipped

        Example:
            >>> source = MySource(config)
            >>> articles = source.discover_articles_with_retry_skip(
            ...     count=10, max_retries=2
            ... )
            >>> if articles is None:
            ...     print("Source skipped after failures")
        """
        import sys
        first_failure = True

        # Show immediate feedback so user knows something is happening
        if max_retries > 1:
            print(f"Capcat Info: Connecting to {self.config.display_name}...", flush=True)

        for attempt in range(1, max_retries + 1):
            try:
                articles = self.discover_articles(count)
                if attempt > 1:
                    # Log successful retry
                    self.logger.info(
                        f"Successfully recovered on attempt {attempt}/{max_retries}"
                    )
                return articles

            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ) as e:
                # Show user-friendly message on first failure
                if first_failure:
                    first_failure = False
                    timeout_seconds = max_retries * self.config.timeout

                    if batch_mode:
                        # Bundle/multiple sources message
                        user_msg = (
                            f"\nWarning: Source '{self.config.display_name}' not responding. "
                            f"Attempting {max_retries} retries over ~{int(timeout_seconds)} seconds, "
                            f"then skipping to next source...\n"
                        )
                    else:
                        # Single source message
                        user_msg = (
                            f"\nWarning: Can't connect to {self.config.display_name} right now. "
                            f"Retrying {max_retries} times over the next ~{int(timeout_seconds)} seconds...\n"
                            f"Tip: The source might be temporarily down or blocking requests.\n"
                        )

                    # Print once to stdout (removes duplicate)
                    print(user_msg, flush=True)

                # Log technical details
                error_type = (
                    "Timeout" if isinstance(e, requests.exceptions.Timeout)
                    else "Connection error"
                )
                self.logger.warning(
                    f"{error_type} accessing {self.config.base_url} "
                    f"(attempt {attempt}/{max_retries})"
                )

                # If this was the last attempt, skip the source
                if attempt == max_retries:
                    self.logger.warning(
                        f"Skipping source '{self.config.name}' after "
                        f"{max_retries} failed attempts"
                    )
                    return None

            except Exception as e:
                # For other exceptions, log and skip
                self.logger.error(
                    f"Unexpected error in {self.config.name}: {e} "
                    f"(attempt {attempt}/{max_retries})"
                )
                if attempt == max_retries:
                    self.logger.warning(
                        f"Skipping source '{self.config.name}' after "
                        f"{max_retries} failed attempts"
                    )
                    return None

        # Should never reach here, but return None as safety
        return None

    def __str__(self) -> str:
        """String representation of the source."""
        return f"{self.__class__.__name__}(name={self.config.name}, type={self.source_type})"

    def __repr__(self) -> str:
        """Detailed string representation of the source."""
        return (
            f"{self.__class__.__name__}("
            f"name={self.config.name!r}, "
            f"display_name={self.config.display_name!r}, "
            f"type={self.source_type!r})"
        )


class SourceError(Exception):
    """Base exception for source-related errors."""

    def __init__(self, message: str, source_name: str = None):
        self.source_name = source_name
        super().__init__(message)

    def __str__(self):
        if self.source_name:
            return f"[{self.source_name}] {super().__str__()}"
        return super().__str__()


class ArticleDiscoveryError(SourceError):
    """Exception raised when article discovery fails."""

    pass


class ContentFetchError(SourceError):
    """Exception raised when content fetching fails."""

    pass


class ConfigurationError(SourceError):
    """Exception raised when source configuration is invalid."""

    pass
