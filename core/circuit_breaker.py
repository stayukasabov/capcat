#!/usr/bin/env python3
"""
Circuit Breaker pattern implementation for Capcat.
Prevents repeated attempts to failing sources, providing fail-fast behavior
and automatic recovery testing.
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional

from .logging_config import get_logger

logger = get_logger(__name__)


class CircuitState(Enum):
    """States of the circuit breaker."""

    CLOSED = "closed"  # Normal operation, requests pass through
    OPEN = "open"  # Blocking requests, source is considered unavailable
    HALF_OPEN = "half_open"  # Testing if source has recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5  # Failures before opening circuit
    success_threshold: int = 2  # Successes in half-open to close circuit
    timeout_seconds: int = 60  # Time before attempting recovery (half-open)
    half_open_max_calls: int = 3  # Max calls allowed in half-open state

    def __post_init__(self):
        """Validate configuration values."""
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1")
        if self.success_threshold < 1:
            raise ValueError("success_threshold must be at least 1")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be at least 1")
        if self.half_open_max_calls < 1:
            raise ValueError("half_open_max_calls must be at least 1")


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""

    def __init__(self, source_name: str, last_exception: Optional[Exception] = None):
        self.source_name = source_name
        self.last_exception = last_exception
        message = f"Circuit breaker is OPEN for {source_name}"
        if last_exception:
            message += f" (last error: {last_exception})"
        super().__init__(message)


class CircuitBreaker:
    """
    Circuit breaker implementation with state machine.

    States:
    - CLOSED: Normal operation, all calls go through
    - OPEN: Blocking calls, failing fast
    - HALF_OPEN: Testing recovery, limited calls allowed

    Transitions:
    - CLOSED -> OPEN: After failure_threshold failures
    - OPEN -> HALF_OPEN: After timeout_seconds elapsed
    - HALF_OPEN -> CLOSED: After success_threshold successes
    - HALF_OPEN -> OPEN: On any failure

    Example:
        breaker = CircuitBreaker("my_service", config)
        result = breaker.call(risky_function, arg1, arg2)
    """

    def __init__(self, name: str, config: CircuitBreakerConfig):
        """
        Initialize circuit breaker.

        Args:
            name: Name of the protected resource (e.g., source code)
            config: Circuit breaker configuration
        """
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self.last_exception: Optional[Exception] = None
        self.half_open_calls = 0
        self.lock = threading.Lock()

        # Statistics
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.state_transitions = []

        logger.debug(
            f"Circuit breaker initialized for {name}: "
            f"failure_threshold={config.failure_threshold}, "
            f"timeout={config.timeout_seconds}s"
        )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            CircuitBreakerOpenError: If circuit is OPEN and timeout not expired
            Exception: Any exception raised by func
        """
        with self.lock:
            self.total_calls += 1
            current_state = self.state

            # Check if we should transition from OPEN to HALF_OPEN
            if current_state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to(CircuitState.HALF_OPEN)
                    current_state = CircuitState.HALF_OPEN
                else:
                    # Circuit is still open, fail fast
                    raise CircuitBreakerOpenError(self.name, self.last_exception)

            # Check half-open call limit
            if current_state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.config.half_open_max_calls:
                    # Too many calls in half-open, reject
                    raise CircuitBreakerOpenError(
                        self.name, Exception("Half-open call limit reached")
                    )
                self.half_open_calls += 1

        # Execute the function (outside lock to avoid blocking other threads)
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            raise

    def _on_success(self):
        """Handle successful call."""
        with self.lock:
            self.total_successes += 1
            self.last_success_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.debug(
                    f"Circuit breaker {self.name} success in half-open "
                    f"({self.success_count}/{self.config.success_threshold})"
                )

                if self.success_count >= self.config.success_threshold:
                    # Enough successes, close the circuit
                    self._transition_to(CircuitState.CLOSED)
                    self.failure_count = 0
                    self.success_count = 0
                    self.half_open_calls = 0

            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success in closed state
                self.failure_count = 0

    def _on_failure(self, exception: Exception):
        """Handle failed call."""
        with self.lock:
            self.total_failures += 1
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            self.last_exception = exception

            if self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open reopens the circuit
                logger.warning(
                    f"Circuit breaker {self.name} failed in half-open, "
                    f"reopening circuit"
                )
                self._transition_to(CircuitState.OPEN)
                self.success_count = 0
                self.half_open_calls = 0

            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    # Too many failures, open the circuit
                    logger.warning(
                        f"Circuit breaker {self.name} opening after "
                        f"{self.failure_count} failures: {exception}"
                    )
                    self._transition_to(CircuitState.OPEN)

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if not self.last_failure_time:
            return True

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.timeout_seconds

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        old_state = self.state
        self.state = new_state
        self.state_transitions.append(
            {
                "from": old_state.value,
                "to": new_state.value,
                "timestamp": datetime.now(),
            }
        )

        logger.info(
            f"Circuit breaker {self.name} transitioned: {old_state.value} -> {new_state.value}"
        )

    def get_state(self) -> CircuitState:
        """Get current circuit state (thread-safe)."""
        with self.lock:
            return self.state

    def get_stats(self) -> Dict[str, Any]:
        """
        Get circuit breaker statistics.

        Returns:
            Dictionary with statistics
        """
        with self.lock:
            uptime = None
            if self.state_transitions:
                first_transition = self.state_transitions[0]["timestamp"]
                uptime = (datetime.now() - first_transition).total_seconds()

            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "total_calls": self.total_calls,
                "total_failures": self.total_failures,
                "total_successes": self.total_successes,
                "last_failure_time": (
                    self.last_failure_time.isoformat() if self.last_failure_time else None
                ),
                "last_success_time": (
                    self.last_success_time.isoformat() if self.last_success_time else None
                ),
                "last_exception": str(self.last_exception) if self.last_exception else None,
                "uptime_seconds": uptime,
                "state_transitions_count": len(self.state_transitions),
            }

    def reset(self):
        """Reset circuit breaker to initial state."""
        with self.lock:
            logger.info(f"Resetting circuit breaker {self.name}")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.half_open_calls = 0
            self.last_failure_time = None
            self.last_exception = None


# Source-specific circuit breaker configurations
CIRCUIT_BREAKER_CONFIGS: Dict[str, CircuitBreakerConfig] = {
    # Very sensitive for problematic sources
    "scientificamerican": CircuitBreakerConfig(
        failure_threshold=3,  # Open faster
        success_threshold=2,
        timeout_seconds=120,  # Longer recovery time
        half_open_max_calls=2,
    ),
    "smithsonianmag": CircuitBreakerConfig(
        failure_threshold=2,  # Very sensitive
        success_threshold=2,
        timeout_seconds=180,  # Long recovery time
        half_open_max_calls=2,
    ),
    # Moderate sensitivity
    "openai": CircuitBreakerConfig(
        failure_threshold=4,
        success_threshold=2,
        timeout_seconds=90,
        half_open_max_calls=3,
    ),
    "nature": CircuitBreakerConfig(
        failure_threshold=4,
        success_threshold=2,
        timeout_seconds=90,
        half_open_max_calls=3,
    ),
    # Default for all other sources
    "default": CircuitBreakerConfig(
        failure_threshold=5,
        success_threshold=2,
        timeout_seconds=60,
        half_open_max_calls=3,
    ),
}


class CircuitBreakerPool:
    """
    Pool of circuit breakers, one per source.

    Manages circuit breakers for multiple sources, creating them on-demand
    and applying source-specific configurations.
    """

    def __init__(
        self, configs: Optional[Dict[str, CircuitBreakerConfig]] = None
    ):
        """
        Initialize circuit breaker pool.

        Args:
            configs: Optional custom circuit breaker configurations
        """
        self.configs = configs or CIRCUIT_BREAKER_CONFIGS
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.lock = threading.Lock()

    def get_breaker(self, source_code: str) -> CircuitBreaker:
        """
        Get or create circuit breaker for a source.

        Args:
            source_code: Source identifier (e.g., 'hn', 'scientificamerican')

        Returns:
            CircuitBreaker instance for the source
        """
        with self.lock:
            if source_code not in self.breakers:
                # Get source-specific config or default
                config = self.configs.get(
                    source_code, self.configs.get("default")
                )
                self.breakers[source_code] = CircuitBreaker(source_code, config)
                logger.debug(
                    f"Created circuit breaker for {source_code}: "
                    f"threshold={config.failure_threshold}, "
                    f"timeout={config.timeout_seconds}s"
                )

            return self.breakers[source_code]

    def call(self, source_code: str, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker for a source.

        Args:
            source_code: Source identifier
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Any exception raised by func
        """
        breaker = self.get_breaker(source_code)
        return breaker.call(func, *args, **kwargs)

    def get_all_states(self) -> Dict[str, str]:
        """
        Get states of all circuit breakers.

        Returns:
            Dictionary mapping source codes to their states
        """
        with self.lock:
            return {
                source: breaker.get_state().value
                for source, breaker in self.breakers.items()
            }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all circuit breakers.

        Returns:
            Dictionary mapping source codes to their statistics
        """
        with self.lock:
            return {
                source: breaker.get_stats()
                for source, breaker in self.breakers.items()
            }

    def reset_all(self):
        """Reset all circuit breakers."""
        with self.lock:
            for breaker in self.breakers.values():
                breaker.reset()
            logger.info("Reset all circuit breakers")


# Global circuit breaker pool instance
_global_breaker_pool: Optional[CircuitBreakerPool] = None
_pool_lock = threading.Lock()


def get_circuit_breaker_pool() -> CircuitBreakerPool:
    """
    Get the global circuit breaker pool instance (singleton).

    Returns:
        Global CircuitBreakerPool instance
    """
    global _global_breaker_pool

    if _global_breaker_pool is None:
        with _pool_lock:
            if _global_breaker_pool is None:
                _global_breaker_pool = CircuitBreakerPool()
                logger.debug("Initialized global circuit breaker pool")

    return _global_breaker_pool


def call_with_circuit_breaker(
    source_code: str, func: Callable, *args, **kwargs
) -> Any:
    """
    Convenience function to call function through global circuit breaker pool.

    Args:
        source_code: Source identifier
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Result of function execution

    Raises:
        CircuitBreakerOpenError: If circuit is open
        Exception: Any exception raised by func
    """
    pool = get_circuit_breaker_pool()
    return pool.call(source_code, func, *args, **kwargs)


def get_circuit_state(source_code: str) -> CircuitState:
    """
    Get circuit breaker state for a source.

    Args:
        source_code: Source identifier

    Returns:
        Current circuit state
    """
    pool = get_circuit_breaker_pool()
    breaker = pool.get_breaker(source_code)
    return breaker.get_state()
