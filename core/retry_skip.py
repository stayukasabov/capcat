#!/usr/bin/env python3
"""
Retry-and-Skip Logic for Network Resilience

Implements intelligent retry-and-skip mechanism for sources that timeout
or refuse connection. After N failed attempts, sources are skipped
(not endlessly retried) to maintain batch processing momentum.

GREEN PHASE - Minimal Implementation
This is the minimal code needed to pass all TDD tests.
Refactoring will be applied in the REFACTOR phase.
"""

import time
from typing import Optional, List, Dict, Any, Callable, Tuple
import requests

from core.logging_config import get_logger


class RetrySkipManager:
    """
    Manages retry-and-skip logic for source processing.

    GREEN PHASE: Minimal implementation to pass tests.
    """

    def __init__(self, max_retries: int = 2):
        """
        Initialize retry-skip manager.

        Args:
            max_retries: Maximum retry attempts before skipping
        """
        self.max_retries = max_retries
        self.logger = get_logger(__name__)
        self.skipped_sources = {}  # Track skipped sources

    def execute_with_retry_skip(
        self,
        operation: Callable,
        operation_name: str,
        source_name: str = "unknown",
        retryable_exceptions: Tuple = None,
    ) -> Optional[Any]:
        """
        Execute operation with retry-skip logic.

        Args:
            operation: Callable to execute
            operation_name: Name for logging
            source_name: Source identifier
            retryable_exceptions: Exceptions that trigger retry

        Returns:
            Operation result or None if skipped
        """
        if retryable_exceptions is None:
            retryable_exceptions = (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.RequestException,
            )

        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            attempt += 1
            try:
                # Execute operation
                result = operation()
                return result

            except retryable_exceptions as e:
                last_error = e
                self.logger.warning(
                    f"Timeout accessing {operation_name} "
                    f"(attempt {attempt}/{self.max_retries})"
                )

                # Don't sleep after last attempt
                if attempt < self.max_retries:
                    time.sleep(1.0 * attempt)  # Basic exponential backoff

        # All attempts exhausted - skip source
        self.logger.warning(
            f"Skipping source '{source_name}' after {self.max_retries} "
            f"failed attempts"
        )

        # Track skip
        self.skipped_sources[source_name] = {
            'reason': str(last_error),
            'attempts': self.max_retries,
            'error_type': type(last_error).__name__ if last_error else 'Unknown'
        }

        return None

    def execute_with_url_fallbacks(
        self,
        urls: List[str],
        fetch_function: Callable[[str], Any],
        source_name: str = "unknown",
        max_retries_per_url: int = 2,
    ) -> Optional[Any]:
        """
        Try multiple URLs with retry logic before skipping.

        Args:
            urls: List of URLs to try
            fetch_function: Function to fetch from URL
            source_name: Source identifier
            max_retries_per_url: Retries per URL

        Returns:
            Fetch result or None if all URLs exhausted
        """
        for url in urls:
            self.logger.debug(f"Trying URL: {url}")

            # Create operation that wraps fetch_function
            def operation():
                return fetch_function(url)

            result = self.execute_with_retry_skip(
                operation=operation,
                operation_name=url,
                source_name=source_name,
                retryable_exceptions=(
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.RequestException,
                    Exception,
                ),
            )

            if result is not None:
                return result

        # All URLs exhausted
        self.logger.warning(
            f"All URL fallbacks exhausted for source '{source_name}'"
        )
        return None

    def get_skip_summary(self) -> Dict[str, Any]:
        """
        Get summary of skipped sources.

        Returns:
            Dictionary with skip information
        """
        return {
            'skipped': self.skipped_sources.copy(),
            'total_skipped': len(self.skipped_sources),
        }

    def reset(self):
        """Reset skip tracking."""
        self.skipped_sources.clear()


# Global instance
_retry_skip_manager = None


def get_retry_skip_manager(max_retries: int = 2) -> RetrySkipManager:
    """Get global retry-skip manager instance."""
    global _retry_skip_manager
    if _retry_skip_manager is None:
        _retry_skip_manager = RetrySkipManager(max_retries=max_retries)
    return _retry_skip_manager


def reset_retry_skip_manager():
    """Reset global retry-skip manager."""
    global _retry_skip_manager
    if _retry_skip_manager is not None:
        _retry_skip_manager.reset()
