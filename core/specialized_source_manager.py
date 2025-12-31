#!/usr/bin/env python3
"""
Specialized Source Manager for automatic URL-based source activation.
Handles Medium, Substack, and other blog platforms with paywall detection.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

from core.logging_config import get_logger
from core.source_system.source_config import SourceConfig
from sources.specialized import (
    get_specialized_source_for_url,
    list_specialized_sources,
)


class SpecializedSourceManager:
    """
    Manager for specialized sources that are automatically activated based on URL patterns.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.specialized_sources = list_specialized_sources()
        self.configs_cache = {}
        self._load_specialized_configs()

    def _load_specialized_configs(self):
        """Load configuration files for all specialized sources."""
        specialized_dir = (
            Path(__file__).parent.parent / "sources" / "specialized"
        )

        for source_id in self.specialized_sources.keys():
            config_file = specialized_dir / source_id / "config.yaml"

            if config_file.exists():
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    self.configs_cache[source_id] = config_data
                    self.logger.debug(
                        f"Loaded specialized config for {source_id}"
                    )

                except Exception as e:
                    self.logger.warning(
                        f"Failed to load specialized config for {source_id}: {e}"
                    )

    def can_handle_url(self, url: str) -> bool:
        """
        Check if any specialized source can handle the given URL.

        Args:
            url: The URL to check

        Returns:
            True if a specialized source can handle this URL
        """
        source_class, source_id = get_specialized_source_for_url(url)
        return source_class is not None

    def get_source_for_url(self, url: str) -> Optional[Tuple[object, str]]:
        """
        Get the appropriate specialized source instance for a URL.

        Args:
            url: The URL to process

        Returns:
            Tuple of (source_instance, source_id) if available, None otherwise
        """
        source_class, source_id = get_specialized_source_for_url(url)

        if source_class and source_id:
            try:
                # Create source config
                config_data = self.configs_cache.get(source_id, {})
                config = self._create_source_config(
                    source_id, config_data, url
                )

                # Instantiate source
                source_instance = source_class(config)

                self.logger.info(
                    f"Activated specialized source '{source_id}' for URL: {url}"
                )
                return source_instance, source_id

            except Exception as e:
                self.logger.error(
                    f"Failed to create specialized source {source_id}: {e}"
                )

        return None

    def _create_source_config(
        self, source_id: str, config_data: Dict[str, Any], url: str
    ) -> SourceConfig:
        """
        Create a SourceConfig instance for a specialized source.

        Args:
            source_id: The source identifier
            config_data: Configuration data from YAML
            url: The URL being processed

        Returns:
            SourceConfig instance
        """
        # Extract domain for dynamic naming
        domain = self._extract_domain(url)

        config = SourceConfig(
            source_id=source_id,
            name=config_data.get("name", source_id.title()),
            display_name=config_data.get(
                "display_name", f"{source_id.title()} ({domain})"
            ),
            base_url=config_data.get("base_url", f"https://{domain}"),
            timeout=config_data.get("timeout", 30),
            headers=config_data.get("headers", {}),
            source_type="specialized",
        )

        # Add specialized configuration attributes
        for key, value in config_data.items():
            if not hasattr(config, key):
                setattr(config, key, value)

        return config

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL for dynamic configuration.

        Args:
            url: The URL to extract domain from

        Returns:
            Domain name
        """
        import re

        # Extract domain patterns
        patterns = [r"https?://([^/]+)", r"([^/]+)"]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                domain = match.group(1)
                return domain.replace("www.", "")

        return "unknown"

    def get_paywall_info(self, source_id: str) -> Dict[str, Any]:
        """
        Get paywall detection configuration for a specialized source.

        Args:
            source_id: The source identifier

        Returns:
            Paywall configuration dict
        """
        config_data = self.configs_cache.get(source_id, {})
        return config_data.get("paywall", {})

    def list_supported_platforms(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all supported specialized platforms.

        Returns:
            Dict with platform info
        """
        platforms = {}

        for source_id, source_class in self.specialized_sources.items():
            config_data = self.configs_cache.get(source_id, {})

            platforms[source_id] = {
                "name": config_data.get("display_name", source_id.title()),
                "url_patterns": config_data.get("url_patterns", []),
                "paywall_detection": config_data.get("paywall", {}).get(
                    "enabled", False
                ),
                "rss_support": config_data.get("rss", {}).get(
                    "enabled", False
                ),
                "source_class": source_class.__name__,
            }

        return platforms

    def validate_specialized_sources(self) -> Dict[str, list]:
        """
        Validate all specialized source configurations.

        Returns:
            Dict with validation results
        """
        results = {}

        for source_id in self.specialized_sources.keys():
            errors = []
            config_data = self.configs_cache.get(source_id)

            if not config_data:
                errors.append(f"No configuration file found for {source_id}")
            else:
                # Validate required fields
                required_fields = ["source_id", "name", "url_patterns"]
                for field in required_fields:
                    if field not in config_data:
                        errors.append(f"Missing required field: {field}")

                # Validate URL patterns
                url_patterns = config_data.get("url_patterns", [])
                if not isinstance(url_patterns, list) or not url_patterns:
                    errors.append("url_patterns must be a non-empty list")

            results[source_id] = errors

        return results


# Global instance
_specialized_manager = None


def get_specialized_source_manager() -> SpecializedSourceManager:
    """Get the global specialized source manager instance."""
    global _specialized_manager
    if _specialized_manager is None:
        _specialized_manager = SpecializedSourceManager()
    return _specialized_manager
