#!/usr/bin/env python3
"""
Modernized factory for creating news source adapters.
Uses the new modular configuration system while maintaining backward compatibility.
"""

from typing import Any, Dict

from core.news_source_adapter import NewsSourceAdapter
from sources.base.factory import get_modular_source_factory


class ConfigurableNewsSource(NewsSourceAdapter):
    """
    A configurable news source that can adapt to any news site
    based on its configuration. Updated to use modular system.
    """

    def __init__(self, source_name: str):
        """Initialize with source name, loading from modular system."""
        # Get config from modular system
        modular_factory = get_modular_source_factory()
        modular_source = modular_factory.create_source(source_name)

        if not modular_source:
            raise ValueError(f"No configuration found for source: {source_name}")

        # Use the modular source's source config (not system config)
        source_config = modular_source.config_object.to_dict()
        super().__init__(source_config)
        self.source_name = source_name


class SourceFactory:
    """Factory for creating news source instances (backward compatible)."""

    @staticmethod
    def create_source(source_name: str) -> ConfigurableNewsSource:
        """Create a news source adapter for the given source name."""
        return ConfigurableNewsSource(source_name)

    @staticmethod
    def create_multiple_sources(
        source_names: list,
    ) -> Dict[str, ConfigurableNewsSource]:
        """Create multiple news source adapters."""
        sources = {}
        for source_name in source_names:
            try:
                sources[source_name] = SourceFactory.create_source(source_name)
            except ValueError as e:
                print(f"Warning: {e}")
        return sources