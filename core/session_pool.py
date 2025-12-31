#!/usr/bin/env python3
"""
Global session pooling for optimal network performance across all sources.
Eliminates memory waste from individual session instances and provides
centralized connection management.
"""

import random
from threading import Lock
from typing import Dict, Optional

import requests

from core.config import get_config
from core.logging_config import get_logger

# Modern, realistic User-Agent strings for better compatibility
# Rotated to avoid detection as automated scraper
USER_AGENTS = [
    # Chrome on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    # Chrome on Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    # Safari on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    # Firefox on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    # Firefox on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
]


class SessionPool:
    """
    Global session pool manager for optimal network performance.
    Provides shared, configured sessions with connection pooling.
    """

    _instance: Optional["SessionPool"] = None
    _lock = Lock()

    def __new__(cls):
        """Singleton pattern to ensure only one session pool."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the session pool if not already done."""
        if hasattr(self, "_initialized"):
            return

        self.config = get_config()
        self.logger = get_logger(__name__)
        self._sessions: Dict[str, requests.Session] = {}
        self._session_lock = Lock()
        self._initialized = True

        self.logger.info("Initialized global session pool")

    def get_session(self, source_name: str = "default") -> requests.Session:
        """
        Get or create a configured session for a source.

        Args:
            source_name: Name of the source (for logging and potential customization)

        Returns:
            Configured requests.Session instance
        """
        with self._session_lock:
            if source_name not in self._sessions:
                self._sessions[source_name] = self._create_session(source_name)
                self.logger.debug(f"Created new session for {source_name}")

            return self._sessions[source_name]

    def _create_session(self, source_name: str) -> requests.Session:
        """
        Create a properly configured session with realistic browser headers.

        Uses rotating User-Agent strings and comprehensive browser headers
        to avoid anti-bot detection while maintaining ethical scraping practices.
        """
        session = requests.Session()

        # Use realistic, rotating User-Agent instead of generic one
        user_agent = random.choice(USER_AGENTS)

        # Configure comprehensive browser-like headers
        session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",  # Do Not Track
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            }
        )

        self.logger.debug(f"Using User-Agent for {source_name}: {user_agent[:50]}...")

        # Configure adapters with connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=self.config.network.pool_connections,
            pool_maxsize=self.config.network.pool_maxsize,
            max_retries=3,  # Built-in retry mechanism
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Configure timeouts and other settings
        session.timeout = self.config.network.connect_timeout

        self.logger.debug(
            f"Configured session for {source_name} with "
            f"pool_connections={self.config.network.pool_connections}, "
            f"pool_maxsize={self.config.network.pool_maxsize}"
        )

        return session

    def close_all_sessions(self):
        """Close all sessions in the pool."""
        with self._session_lock:
            for source_name, session in self._sessions.items():
                try:
                    session.close()
                    self.logger.debug(f"Closed session for {source_name}")
                except Exception as e:
                    self.logger.warning(
                        f"Error closing session for {source_name}: {e}"
                    )

            self._sessions.clear()
            self.logger.info("Closed all sessions in pool")

    def get_session_stats(self) -> Dict[str, int]:
        """Get statistics about session pool usage."""
        with self._session_lock:
            return {
                "active_sessions": len(self._sessions),
                "session_sources": list(self._sessions.keys()),
            }


# Global session pool instance
_session_pool = SessionPool()


def get_global_session(source_name: str = "default") -> requests.Session:
    """
    Get a global session instance for the given source.

    This function provides the main interface for getting optimized,
    pooled session instances throughout the application.

    Args:
        source_name: Name of the source requesting the session

    Returns:
        Configured requests.Session instance from the global pool
    """
    return _session_pool.get_session(source_name)


def close_all_sessions():
    """Close all sessions in the global pool."""
    _session_pool.close_all_sessions()


def get_session_stats() -> Dict[str, int]:
    """Get statistics about global session pool usage."""
    return _session_pool.get_session_stats()
