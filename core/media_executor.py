#!/usr/bin/env python3
"""
Shared executor pool for media processing to prevent nested ThreadPoolExecutor deadlock.

This module provides a global executor that can be safely used by multiple article
processing threads without creating nested executors that exhaust thread resources.
"""

from concurrent.futures import ThreadPoolExecutor
from typing import Optional


class MediaExecutorPool:
    """Singleton executor pool for media downloads across all articles."""

    _instance: Optional['MediaExecutorPool'] = None
    _executor: Optional[ThreadPoolExecutor] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the shared executor pool."""
        if self._executor is None:
            # Create shared executor with reasonable worker count
            # This pool is shared across ALL article processing
            self._executor = ThreadPoolExecutor(
                max_workers=8,
                thread_name_prefix="media_worker"
            )

    @property
    def executor(self) -> ThreadPoolExecutor:
        """Get the shared executor instance."""
        if self._executor is None:
            self.__init__()
        return self._executor

    def shutdown(self, wait=True):
        """Shutdown the executor pool."""
        if self._executor is not None:
            self._executor.shutdown(wait=wait)
            self._executor = None


# Global accessor functions
_pool = MediaExecutorPool()


def get_media_executor() -> ThreadPoolExecutor:
    """
    Get the shared media processing executor.

    Returns:
        ThreadPoolExecutor: Shared executor for media downloads
    """
    return _pool.executor


def shutdown_media_executor(wait=True):
    """
    Shutdown the shared media executor.

    Args:
        wait: If True, wait for all tasks to complete
    """
    _pool.shutdown(wait=wait)
