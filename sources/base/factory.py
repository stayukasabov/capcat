#!/usr/bin/env python3
"""
Clean factory pattern for creating news source adapters.
Uses the new modular configuration system.
"""

from typing import Dict, Optional

from core.news_source_adapter import NewsSourceAdapter
from core.source_system.source_registry import get_source_registry
from sources.base.config_schema import SourceConfig


class ModularNewsSource(NewsSourceAdapter):
    """
    A modular news source that adapts to any news site
    based on its individual configuration file.
    """

    def __init__(self, config: SourceConfig):
        """Initialize with source config."""
        # Convert SourceConfig to dictionary format for compatibility
        config_dict = config.to_dict()
        super().__init__(config_dict)
        self.source_name = config.name
        self.config_object = config


class ModularSourceFactory:
    """Factory for creating news source instances using modular configs."""

    def __init__(self):
        """Initialize factory with source registry."""
        self.registry = get_source_registry()

    def create_source(self, source_name: str) -> Optional[ModularNewsSource]:
        """
        Create a news source adapter for the given source name.

        Args:
            source_name: The source identifier

        Returns:
            ModularNewsSource instance or None if source not found
        """
        config = self.registry.get_source_config(source_name)
        if not config:
            return None

        return ModularNewsSource(config)

    def create_multiple_sources(self, source_names: list) -> Dict[str, ModularNewsSource]:
        """
        Create multiple news source adapters.

        Args:
            source_names: List of source identifiers

        Returns:
            Dictionary mapping source names to source instances
        """
        sources = {}
        for source_name in source_names:
            try:
                source = self.create_source(source_name)
                if source:
                    sources[source_name] = source
                else:
                    print(f"Warning: Source '{source_name}' not found in registry")
            except Exception as e:
                print(f"Warning: Error creating source '{source_name}': {e}")
        return sources

    def get_available_sources(self) -> list:
        """Get list of all available source names."""
        return self.registry.get_available_sources()

    def is_source_available(self, source_name: str) -> bool:
        """Check if a source is available."""
        return source_name in self.registry.get_available_sources()


# Global factory instance for backward compatibility
_factory = None


def get_modular_source_factory() -> ModularSourceFactory:
    """Get the global modular source factory instance."""
    global _factory
    if _factory is None:
        _factory = ModularSourceFactory()
    return _factory


# Compatibility functions for existing code
def create_source(source_name: str) -> Optional[ModularNewsSource]:
    """Create a source using the modular factory."""
    return get_modular_source_factory().create_source(source_name)


def create_multiple_sources(source_names: list) -> Dict[str, ModularNewsSource]:
    """Create multiple sources using the modular factory."""
    return get_modular_source_factory().create_multiple_sources(source_names)