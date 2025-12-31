#!/usr/bin/env python3
"""
Network Resilience Patterns for Source Processing

Clean architecture implementation applying SOLID principles:
- Single Responsibility: Each class has one clear purpose
- Open/Closed: Extensible via strategy pattern
- Liskov Substitution: RetryStrategy implementations interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions not concretions
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
import requests

from core.logging_config import get_logger


class RetryDecision(Enum):
    """Enum representing retry decisions."""
    RETRY = "retry"
    SKIP = "skip"
    SUCCESS = "success"


@dataclass
class RetryAttempt:
    """Data class representing a retry attempt."""
    attempt_number: int
    max_attempts: int
    operation_name: str
    error: Optional[Exception] = None
    success: bool = False

    @property
    def is_first_attempt(self) -> bool:
        """Check if this is the first attempt."""
        return self.attempt_number == 1

    @property
    def is_last_attempt(self) -> bool:
        """Check if this is the last attempt."""
        return self.attempt_number >= self.max_attempts

    @property
    def attempts_remaining(self) -> int:
        """Get number of attempts remaining."""
        return max(0, self.max_attempts - self.attempt_number)


class RetryStrategy(ABC):
    """
    Abstract base class for retry strategies.

    Single Responsibility: Defines retry decision logic.
    Open/Closed: New strategies can be added without modifying existing code.
    """

    @abstractmethod
    def should_retry(self, attempt: RetryAttempt) -> RetryDecision:
        """
        Determine if an operation should be retried.

        Args:
            attempt: Information about the current attempt

        Returns:
            RetryDecision indicating next action
        """
        pass

    @abstractmethod
    def get_delay(self, attempt: RetryAttempt) -> float:
        """
        Calculate delay before next retry.

        Args:
            attempt: Information about the current attempt

        Returns:
            Delay in seconds
        """
        pass


class ExponentialBackoffStrategy(RetryStrategy):
    """
    Exponential backoff retry strategy.

    Single Responsibility: Implements exponential backoff timing.
    """

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize exponential backoff strategy.

        Args:
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential calculation
            jitter: Whether to add random jitter
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def should_retry(self, attempt: RetryAttempt) -> RetryDecision:
        """
        Determine if should retry based on attempt count.

        Args:
            attempt: Current attempt information

        Returns:
            RETRY if attempts remaining, SKIP otherwise
        """
        if attempt.success:
            return RetryDecision.SUCCESS

        if attempt.is_last_attempt:
            return RetryDecision.SKIP

        return RetryDecision.RETRY

    def get_delay(self, attempt: RetryAttempt) -> float:
        """
        Calculate exponential backoff delay.

        Args:
            attempt: Current attempt information

        Returns:
            Delay in seconds with exponential backoff
        """
        # Calculate exponential delay
        delay = min(
            self.base_delay * (self.exponential_base ** (attempt.attempt_number - 1)),
            self.max_delay
        )

        # Add jitter to prevent thundering herd
        if self.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)

        return delay


class ErrorClassifier:
    """
    Classifies errors as retryable or non-retryable.

    Single Responsibility: Error classification logic.
    """

    def __init__(
        self,
        retryable_exceptions: Tuple[Type[Exception], ...] = None
    ):
        """
        Initialize error classifier.

        Args:
            retryable_exceptions: Tuple of exception types to retry
        """
        if retryable_exceptions is None:
            self.retryable_exceptions = (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.RequestException,
            )
        else:
            self.retryable_exceptions = retryable_exceptions

    def is_retryable(self, error: Exception) -> bool:
        """
        Check if error is retryable.

        Args:
            error: Exception to classify

        Returns:
            True if retryable, False otherwise
        """
        return isinstance(error, self.retryable_exceptions)

    def get_error_type(self, error: Exception) -> str:
        """
        Get human-readable error type.

        Args:
            error: Exception to classify

        Returns:
            Error type string
        """
        return type(error).__name__


class RetryLogger:
    """
    Handles logging for retry operations.

    Single Responsibility: Logging logic separation.
    """

    def __init__(self, logger_name: str = __name__):
        """
        Initialize retry logger.

        Args:
            logger_name: Name for logger instance
        """
        self.logger = get_logger(logger_name)

    def log_attempt(self, attempt: RetryAttempt):
        """
        Log retry attempt.

        Args:
            attempt: Attempt information
        """
        if attempt.error:
            self.logger.warning(
                f"Timeout accessing {attempt.operation_name} "
                f"(attempt {attempt.attempt_number}/{attempt.max_attempts})"
            )

    def log_skip(self, operation_name: str, attempts: int, error_type: str):
        """
        Log skip decision.

        Args:
            operation_name: Name of operation being skipped
            attempts: Number of attempts made
            error_type: Type of error that caused skip
        """
        self.logger.warning(
            f"Skipping source '{operation_name}' after {attempts} failed attempts "
            f"({error_type})"
        )

    def log_success(self, operation_name: str, attempt_number: int):
        """
        Log successful retry.

        Args:
            operation_name: Name of operation that succeeded
            attempt_number: Attempt number that succeeded
        """
        if attempt_number > 1:
            self.logger.info(
                f"Operation '{operation_name}' succeeded on attempt {attempt_number}"
            )


@dataclass
class SkipRecord:
    """Record of a skipped operation."""
    source_name: str
    operation_name: str
    reason: str
    attempts: int
    error_type: str
    timestamp: float


class SkipTracker:
    """
    Tracks skipped operations for reporting.

    Single Responsibility: Skip tracking and reporting.
    """

    def __init__(self):
        """Initialize skip tracker."""
        self.skipped_operations: Dict[str, SkipRecord] = {}

    def record_skip(
        self,
        source_name: str,
        operation_name: str,
        reason: str,
        attempts: int,
        error_type: str
    ):
        """
        Record a skipped operation.

        Args:
            source_name: Source identifier
            operation_name: Operation name
            reason: Reason for skip
            attempts: Number of attempts made
            error_type: Type of error
        """
        import time
        self.skipped_operations[source_name] = SkipRecord(
            source_name=source_name,
            operation_name=operation_name,
            reason=reason,
            attempts=attempts,
            error_type=error_type,
            timestamp=time.time()
        )

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of skipped operations.

        Returns:
            Dictionary with skip summary
        """
        return {
            'skipped': {
                name: {
                    'reason': record.reason,
                    'attempts': record.attempts,
                    'error_type': record.error_type
                }
                for name, record in self.skipped_operations.items()
            },
            'total_skipped': len(self.skipped_operations)
        }

    def reset(self):
        """Reset skip tracking."""
        self.skipped_operations.clear()


class RetryExecutor:
    """
    Executes operations with retry logic.

    Single Responsibility: Orchestrates retry execution.
    Dependency Inversion: Depends on abstractions (RetryStrategy, etc.)
    """

    def __init__(
        self,
        strategy: RetryStrategy,
        error_classifier: ErrorClassifier,
        logger: RetryLogger,
        skip_tracker: SkipTracker
    ):
        """
        Initialize retry executor.

        Args:
            strategy: Retry strategy to use
            error_classifier: Error classifier
            logger: Retry logger
            skip_tracker: Skip tracker
        """
        self.strategy = strategy
        self.error_classifier = error_classifier
        self.logger = logger
        self.skip_tracker = skip_tracker

    def execute(
        self,
        operation: Callable[[], Any],
        operation_name: str,
        source_name: str,
        max_attempts: int = 2
    ) -> Optional[Any]:
        """
        Execute operation with retry logic.

        Args:
            operation: Callable to execute
            operation_name: Name for logging
            source_name: Source identifier
            max_attempts: Maximum retry attempts

        Returns:
            Operation result or None if skipped
        """
        attempt_number = 0

        while attempt_number < max_attempts:
            attempt_number += 1

            try:
                # Execute operation
                result = operation()

                # Log success if retried
                self.logger.log_success(operation_name, attempt_number)

                return result

            except Exception as error:
                # Create attempt record
                attempt = RetryAttempt(
                    attempt_number=attempt_number,
                    max_attempts=max_attempts,
                    operation_name=operation_name,
                    error=error,
                    success=False
                )

                # Check if error is retryable
                if not self.error_classifier.is_retryable(error):
                    # Non-retryable error, raise immediately
                    raise

                # Log attempt
                self.logger.log_attempt(attempt)

                # Get retry decision
                decision = self.strategy.should_retry(attempt)

                if decision == RetryDecision.SKIP:
                    # Record skip
                    error_type = self.error_classifier.get_error_type(error)
                    self.skip_tracker.record_skip(
                        source_name=source_name,
                        operation_name=operation_name,
                        reason=str(error),
                        attempts=max_attempts,
                        error_type=error_type
                    )
                    self.logger.log_skip(source_name, max_attempts, error_type)
                    return None

                elif decision == RetryDecision.RETRY:
                    # Calculate delay and wait
                    delay = self.strategy.get_delay(attempt)
                    if delay > 0 and not attempt.is_last_attempt:
                        time.sleep(delay)

        # Exhausted all attempts (shouldn't reach here)
        return None


class URLFallbackExecutor:
    """
    Executes operations with URL fallback logic.

    Single Responsibility: URL fallback orchestration.
    """

    def __init__(self, retry_executor: RetryExecutor):
        """
        Initialize URL fallback executor.

        Args:
            retry_executor: Retry executor to use
        """
        self.retry_executor = retry_executor
        self.logger = get_logger(__name__)

    def execute_with_fallbacks(
        self,
        urls: List[str],
        fetch_function: Callable[[str], Any],
        source_name: str,
        max_retries_per_url: int = 2
    ) -> Optional[Any]:
        """
        Try multiple URLs with retry logic.

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

            # Execute with retry logic
            result = self.retry_executor.execute(
                operation=operation,
                operation_name=url,
                source_name=source_name,
                max_attempts=max_retries_per_url
            )

            if result is not None:
                return result

        # All URLs exhausted
        self.logger.warning(
            f"All URL fallbacks exhausted for source '{source_name}'"
        )
        return None


# Factory function
def create_retry_executor(max_retries: int = 2) -> RetryExecutor:
    """
    Create a retry executor with default configuration.

    Factory pattern for clean object creation.

    Args:
        max_retries: Maximum retry attempts

    Returns:
        Configured RetryExecutor instance
    """
    strategy = ExponentialBackoffStrategy(
        base_delay=1.0,
        max_delay=10.0,
        exponential_base=2.0,
        jitter=True
    )
    error_classifier = ErrorClassifier()
    logger = RetryLogger()
    skip_tracker = SkipTracker()

    return RetryExecutor(
        strategy=strategy,
        error_classifier=error_classifier,
        logger=logger,
        skip_tracker=skip_tracker
    )


# Global instances for backward compatibility
_global_executor: Optional[RetryExecutor] = None
_global_skip_tracker: Optional[SkipTracker] = None


def get_retry_executor() -> RetryExecutor:
    """Get global retry executor instance."""
    global _global_executor, _global_skip_tracker
    if _global_executor is None:
        _global_skip_tracker = SkipTracker()
        _global_executor = RetryExecutor(
            strategy=ExponentialBackoffStrategy(),
            error_classifier=ErrorClassifier(),
            logger=RetryLogger(),
            skip_tracker=_global_skip_tracker
        )
    return _global_executor


def get_skip_tracker() -> SkipTracker:
    """Get global skip tracker instance."""
    get_retry_executor()  # Initialize if needed
    return _global_skip_tracker


def reset_retry_state():
    """Reset global retry state."""
    global _global_executor, _global_skip_tracker
    _global_executor = None
    _global_skip_tracker = None
