#!/usr/bin/env python3
"""
Retry mechanisms with exponential backoff for Capcat.
Provides robust error recovery for network and other transient failures.
"""

import functools
import random
import time
from typing import Any, Callable, Tuple, Type, Union

from .config import get_config
from .exceptions import NetworkError, CapcatError
from .logging_config import get_logger


def exponential_backoff_retry(
    max_retries: int = None,
    base_delay: float = None,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    skip_after: int = None,
):
    """
    Decorator that implements exponential backoff retry logic.

    Args:
        max_retries: Maximum number of retry attempts (uses config default if None)
        base_delay: Base delay in seconds (uses config default if None)
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        retryable_exceptions: Tuple of exception types that should trigger retry
        skip_after: Number of attempts after which to skip instead of raising exception (None = never skip)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            config = get_config()
            logger = get_logger(func.__module__)

            # Use config defaults if not specified
            retry_count = (
                max_retries
                if max_retries is not None
                else config.network.max_retries
            )
            delay = (
                base_delay
                if base_delay is not None
                else config.network.retry_delay
            )

            last_exception = None

            # Determine the actual number of attempts
            max_attempts = retry_count + 1

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    # Check if we should skip instead of retrying
                    if skip_after is not None and attempt + 1 >= skip_after:
                        logger.debug(
                            f"Skipping {func.__name__} after {attempt + 1} failed attempts: {e}"
                        )
                        return None

                    # Don't retry on the last attempt
                    if attempt == retry_count:
                        break

                    # Calculate delay with exponential backoff
                    retry_delay = min(
                        delay * (exponential_base**attempt), max_delay
                    )

                    # Add jitter to prevent thundering herd
                    if jitter:
                        retry_delay *= 0.5 + random.random() * 0.5

                    logger.debug(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {retry_delay:.2f} seconds..."
                    )

                    time.sleep(retry_delay)
                except Exception as e:
                    # Non-retryable exception, fail immediately
                    logger.error(
                        f"Non-retryable error in {func.__name__}: {e}"
                    )
                    raise

            # All retries exhausted
            logger.debug(
                f"Could not complete {func.__name__} after {max_attempts} attempts"
            )
            raise last_exception

        return wrapper

    return decorator


def network_retry(func: Callable) -> Callable:
    """
    Convenience decorator for network operations with appropriate retry settings.
    Handles connection errors, timeouts, and transient HTTP errors.
    """
    import requests

    return exponential_backoff_retry(
        max_retries=3,
        base_delay=1.0,
        retryable_exceptions=(
            ConnectionError,
            TimeoutError,
            NetworkError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.RequestException,
        ),
        skip_after=None,  # Don't skip, raise exception after retries
    )(func)


def fast_media_retry(func: Callable) -> Callable:
    """
    Fast retry decorator optimized for media downloads (images, audio, video).
    Uses shorter delays and fewer retries for better performance with bulk downloads.
    """
    return exponential_backoff_retry(
        max_retries=2,  # Reduced from 3 to 2
        base_delay=0.3,  # Reduced from 1.0 to 0.3 seconds
        max_delay=2.0,  # Reduced from 60.0 to 2.0 seconds
        retryable_exceptions=(
            ConnectionError,
            TimeoutError,
            NetworkError,
            # requests specific exceptions
            Exception,
        ),
    )(func)


class RetryableOperation:
    """
    Context manager for retryable operations with custom logic.
    """

    def __init__(self, operation_name: str, max_retries: int = None):
        self.operation_name = operation_name
        self.max_retries = max_retries or get_config().network.max_retries
        self.logger = get_logger(__name__)
        self.attempt = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.info(
                f"Operation '{self.operation_name}' could not be completed: {exc_val}"
            )
        return False

    def should_retry(self, exception: Exception) -> bool:
        """
        Determine if an exception should trigger a retry.

        Args:
            exception: The exception that occurred

        Returns:
            True if the operation should be retried
        """
        self.attempt += 1

        if self.attempt > self.max_retries:
            return False

        # Check if it's a retryable exception
        retryable_types = (
            ConnectionError,
            TimeoutError,
            NetworkError,
        )

        is_retryable = isinstance(exception, retryable_types)

        if is_retryable:
            delay = get_config().network.retry_delay * (
                2 ** (self.attempt - 1)
            )
            delay = min(delay, 60.0)  # Cap at 60 seconds

            self.logger.debug(
                f"Attempt {self.attempt}/{self.max_retries + 1} failed for '{self.operation_name}': {exception}. "
                f"Retrying in {delay:.2f} seconds..."
            )

            time.sleep(delay)

        return is_retryable
