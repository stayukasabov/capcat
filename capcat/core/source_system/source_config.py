#!/usr/bin/env python3
"""
Source configuration system for specialized sources.
Provides configuration management for automated source activation.
"""

from typing import Any, Dict, Optional


class SourceConfig:
    """
    Configuration container for specialized sources.
    Stores source metadata, selectors, and processing rules.
    """

    def __init__(
        self,
        source_id: str,
        name: str,
        display_name: str,
        base_url: str,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        source_type: str = "specialized",
    ):
        """
        Initialize source configuration.

        Args:
            source_id: Unique identifier for the source
            name: Source name
            display_name: Human-readable display name
            base_url: Base URL for the source
            timeout: Request timeout in seconds
            headers: Custom headers for requests
            source_type: Type of source (specialized, standard, etc.)
        """
        self.source_id = source_id
        self.name = name
        self.display_name = display_name
        self.base_url = base_url
        self.timeout = timeout
        self.headers = headers or {}
        self.source_type = source_type

    def get_headers(self) -> Dict[str, str]:
        """
        Get request headers for this source.

        Returns:
            Dictionary of headers to use in requests
        """
        default_headers = {
            "User-Agent": "Capcat/2.0 (Personal news archiver)"
        }
        default_headers.update(self.headers)
        return default_headers

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
            "source_type": self.source_type,
        }

        # Add headers if present
        if self.headers:
            result["headers"] = self.headers.copy()

        return result

    def __repr__(self) -> str:
        """String representation of the config."""
        return f"SourceConfig(id='{self.source_id}', name='{self.name}', type='{self.source_type}')"
