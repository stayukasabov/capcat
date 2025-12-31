#!/usr/bin/env python3
"""
Graceful shutdown handling for Capcat.
Handles signal interrupts and cleanup operations.
"""

import signal
import sys
import threading
import time
from typing import Callable, Optional

from .logging_config import get_logger


class GracefulShutdown:
    """
    Context manager for handling graceful shutdown on signals.
    """

    def __init__(self, cleanup_func: Optional[Callable] = None):
        """
        Initialize graceful shutdown handler.

        Args:
            cleanup_func: Optional cleanup function to call on shutdown
        """
        self.cleanup_func = cleanup_func
        self.shutdown_event = threading.Event()
        self.logger = get_logger(__name__)
        self._original_handlers = {}

    def __enter__(self):
        """Set up signal handlers."""
        # Store original handlers
        self._original_handlers[signal.SIGINT] = signal.signal(
            signal.SIGINT, self._signal_handler
        )
        self._original_handlers[signal.SIGTERM] = signal.signal(
            signal.SIGTERM, self._signal_handler
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            signal.signal(sig, handler)

    def _signal_handler(self, signum: int, frame):
        """Handle shutdown signals."""
        signal_names = {
            signal.SIGINT: "SIGINT (Ctrl+C)",
            signal.SIGTERM: "SIGTERM",
        }

        signal_name = signal_names.get(signum, f"Signal {signum}")
        self.logger.info(
            f"Received {signal_name}, initiating graceful shutdown..."
        )

        self.shutdown_event.set()

        # Run cleanup function if provided
        if self.cleanup_func:
            try:
                self.logger.debug("Running cleanup function...")
                self.cleanup_func()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")

        # Give some time for cleanup to complete
        time.sleep(0.5)

        self.logger.info("Shutdown complete.")
        sys.exit(130)  # Standard exit code for SIGINT

    def should_shutdown(self) -> bool:
        """Check if shutdown has been requested."""
        return self.shutdown_event.is_set()

    def wait_for_shutdown(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for shutdown signal.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if shutdown was requested, False if timeout occurred
        """
        return self.shutdown_event.wait(timeout)


class InterruptibleOperation:
    """
    Context manager for operations that can be interrupted gracefully.
    """

    def __init__(
        self,
        operation_name: str,
        shutdown_handler: Optional[GracefulShutdown] = None,
    ):
        """
        Initialize interruptible operation.

        Args:
            operation_name: Name of the operation for logging
            shutdown_handler: Optional existing shutdown handler to use
        """
        self.operation_name = operation_name
        self.shutdown_handler = shutdown_handler
        self.logger = get_logger(__name__)
        self._own_shutdown_handler = shutdown_handler is None

        if self._own_shutdown_handler:
            self.shutdown_handler = GracefulShutdown()

    def __enter__(self):
        """Start the interruptible operation."""
        if self._own_shutdown_handler:
            self.shutdown_handler.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up the interruptible operation."""
        if self._own_shutdown_handler:
            self.shutdown_handler.__exit__(exc_type, exc_val, exc_tb)

    def check_shutdown(self):
        """
        Check if shutdown has been requested and raise KeyboardInterrupt if so.
        Call this periodically during long-running operations.
        """
        if self.shutdown_handler and self.shutdown_handler.should_shutdown():
            self.logger.info(
                f"Interrupting {self.operation_name} due to shutdown request"
            )
            raise KeyboardInterrupt(
                "Operation interrupted by shutdown request"
            )

    def should_continue(self) -> bool:
        """
        Check if the operation should continue.

        Returns:
            False if shutdown has been requested, True otherwise
        """
        return not (
            self.shutdown_handler and self.shutdown_handler.should_shutdown()
        )


def setup_signal_handlers():
    """
    Set up basic signal handlers for the application.
    This is a simple version that just logs and exits.
    """
    logger = get_logger(__name__)

    def signal_handler(signum: int, frame):
        signal_names = {
            signal.SIGINT: "SIGINT (Ctrl+C)",
            signal.SIGTERM: "SIGTERM",
        }

        signal_name = signal_names.get(signum, f"Signal {signum}")
        logger.warning(f"Received {signal_name}, exiting...")
        sys.exit(130)

    # Set up handlers for common signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.debug("Signal handlers installed")


def with_graceful_shutdown(cleanup_func: Optional[Callable] = None):
    """
    Decorator to add graceful shutdown handling to functions.

    Args:
        cleanup_func: Optional cleanup function to call on shutdown
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            with GracefulShutdown(cleanup_func):
                return func(*args, **kwargs)

        return wrapper

    return decorator
