#!/usr/bin/env python3
"""
Timeout wrapper utilities for preventing hanging operations.
Provides robust timeout handling for network operations that may hang.
"""

import queue
import threading
import time
from typing import Any, Callable, Optional

from .logging_config import get_logger


def with_timeout(func: Callable, timeout_seconds: int = 30) -> Callable:
    """
    Wrapper that adds timeout functionality to any function call.

    Args:
        func: Function to execute with timeout
        timeout_seconds: Maximum time to wait for function completion

    Returns:
        Function result or None if timeout occurred
    """

    def wrapper(*args, **kwargs) -> Optional[Any]:
        logger = get_logger(__name__)
        result_queue = queue.Queue()
        exception_queue = queue.Queue()

        def target():
            try:
                result = func(*args, **kwargs)
                result_queue.put(result)
            except Exception as e:
                exception_queue.put(e)

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

        thread.join(timeout=timeout_seconds)

        if thread.is_alive():
            # Timeout occurred
            logger.debug(
                f"Function {func.__name__} timed out after {timeout_seconds} seconds"
            )
            return None

        # Check for exceptions
        if not exception_queue.empty():
            raise exception_queue.get()

        # Return result
        if not result_queue.empty():
            return result_queue.get()

        return None

    return wrapper


def safe_network_operation(
    operation: Callable, *args, timeout: int = 15, **kwargs
) -> Optional[Any]:
    """
    Execute a network operation with timeout protection.

    Args:
        operation: Network function to execute
        *args: Arguments for the operation
        timeout: Timeout in seconds
        **kwargs: Keyword arguments for the operation

    Returns:
        Operation result or None if timeout/error occurred
    """
    logger = get_logger(__name__)

    try:
        wrapped_operation = with_timeout(operation, timeout)
        return wrapped_operation(*args, **kwargs)
    except Exception as e:
        logger.debug(f"Network operation {operation.__name__} failed: {e}")
        return None
