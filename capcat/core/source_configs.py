#!/usr/bin/env python3
"""
Modular source configuration system with backward compatibility.
This replaces the monolithic configuration with the new modular system.
"""

from typing import Any, Dict, List
from capcat.core.source_system.source_registry import get_source_registry


class LegacyConfigAdapter:
    """
    Adapter to provide backward compatibility with the old SOURCE_CONFIGURATIONS format.
    """

    def __init__(self):
        """Initialize with source registry."""
        self.registry = get_source_registry()
        self._legacy_configs = None

    def _build_legacy_configs(self) -> Dict[str, Dict[str, Any]]:
        """Build legacy configuration dictionary from modular sources."""
        if self._legacy_configs is not None:
            return self._legacy_configs

        sources = self.registry.discover_sources()

        legacy_configs = {}
        for source_id, config in sources.items():
            legacy_configs[source_id] = config.to_dict()

        self._legacy_configs = legacy_configs
        return legacy_configs

    def get_legacy_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all configurations in legacy format."""
        return self._build_legacy_configs()

    def reload(self):
        """Reload configurations from modular system."""
        self._legacy_configs = None
        self.registry.reload_sources()


# Global adapter instance
_adapter = LegacyConfigAdapter()


class SourceConfigDict(dict):
    """
    Dictionary subclass that dynamically loads from modular system.
    Provides full backward compatibility with SOURCE_CONFIGURATIONS.
    """

    def __init__(self):
        """Initialize with an empty dict; configs are loaded on first access."""
        super().__init__()
        self._loaded = False

    def _ensure_loaded(self):
        """Ensure configurations are loaded."""
        if not self._loaded:
            self.clear()
            self.update(_adapter.get_legacy_configs())
            self._loaded = True

    def __getitem__(self, key):
        """Load configs if needed, then return item for *key*.

        Args:
            key: Source identifier string.

        Returns:
            Source configuration dict for *key*.

        Raises:
            KeyError: If *key* is not a registered source.
        """
        self._ensure_loaded()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        """Load configs if needed, then set *key* to *value*.

        Args:
            key: Source identifier string.
            value: Configuration dict to store.
        """
        self._ensure_loaded()
        super().__setitem__(key, value)

    def __contains__(self, key):
        """Load configs if needed, then test membership.

        Args:
            key: Source identifier string.

        Returns:
            ``True`` if *key* is a registered source.
        """
        self._ensure_loaded()
        return super().__contains__(key)

    def get(self, key, default=None):
        """Load configs if needed, then return item or *default*.

        Args:
            key: Source identifier string.
            default: Value to return when *key* is absent.

        Returns:
            Config dict for *key*, or *default*.
        """
        self._ensure_loaded()
        return super().get(key, default)

    def keys(self):
        """Load configs if needed, then return all source IDs.

        Returns:
            Dict keys view of all registered source identifiers.
        """
        self._ensure_loaded()
        return super().keys()

    def values(self):
        """Load configs if needed, then return all config dicts.

        Returns:
            Dict values view of all source configuration dicts.
        """
        self._ensure_loaded()
        return super().values()

    def items(self):
        """Load configs if needed, then return (source_id, config) pairs.

        Returns:
            Dict items view of ``(source_id, config_dict)`` pairs.
        """
        self._ensure_loaded()
        return super().items()

    def __len__(self):
        """Load configs if needed, then return the number of registered sources.

        Returns:
            Count of registered source configurations.
        """
        self._ensure_loaded()
        return super().__len__()

    def __iter__(self):
        """Load configs if needed, then iterate over source IDs.

        Returns:
            Iterator over all registered source identifier strings.
        """
        self._ensure_loaded()
        return super().__iter__()

    def reload(self):
        """Reload configurations from modular system."""
        _adapter.reload()
        self._loaded = False


# Create the legacy-compatible SOURCE_CONFIGURATIONS
SOURCE_CONFIGURATIONS = SourceConfigDict()


# Legacy function compatibility
def get_source_config(source_name: str) -> Dict[str, Any]:
    """Get configuration for a specific source."""
    config = SOURCE_CONFIGURATIONS.get(source_name.lower())
    if not config:
        raise ValueError(f"No configuration found for source: {source_name}")
    return config.copy()


def get_all_source_names() -> List[str]:
    """Get list of all configured source names."""
    return list(SOURCE_CONFIGURATIONS.keys())


def is_source_configured(source_name: str) -> bool:
    """Check if a source is configured."""
    return source_name.lower() in SOURCE_CONFIGURATIONS


def reload_source_configs():
    """Reload source configurations from modular system."""
    SOURCE_CONFIGURATIONS.reload()