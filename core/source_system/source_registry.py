#!/usr/bin/env python3
"""
Source registry for automatic discovery and management of news sources.
Handles both config-driven and custom source types.
"""

import importlib
import importlib.util
import json
import os
import sys
from abc import ABC
from pathlib import Path
from typing import Dict, List, Optional, Set, Type

import yaml

from ..logging_config import get_logger
from .base_source import (
    BaseSource,
    ConfigurationError,
    SourceConfig,
    SourceError,
)
from .validation_engine import ValidationEngine


class SourceRegistry:
    """
    Registry for managing and discovering news sources.

    Supports both config-driven sources (YAML/JSON) and custom source implementations.
    Provides auto-discovery and validation of sources.
    """

    def __init__(self, sources_dir: str = None):
        """
        Initialize the source registry.

        Args:
            sources_dir: Path to sources directory (defaults to sources/ relative to app root)
        """
        self.logger = get_logger(__name__)
        self._sources: Dict[str, Type[BaseSource]] = {}
        self._configs: Dict[str, SourceConfig] = {}
        self._source_instances: Dict[str, BaseSource] = {}
        self.validation_engine = ValidationEngine()

        # Determine sources directory - now uses active/ subdirectory
        if sources_dir is None:
            app_root = Path(__file__).parent.parent.parent
            self.sources_dir = app_root / "sources" / "active"
        else:
            self.sources_dir = Path(sources_dir)

        self.logger.debug(
            f"Source registry initialized with sources_dir: {self.sources_dir}"
        )

    def discover_sources(self) -> Dict[str, SourceConfig]:
        """
        Discover all available sources (both config-driven and custom).

        Returns:
            Dictionary mapping source names to their configurations

        Raises:
            SourceError: If source discovery fails
        """
        self.logger.debug("Starting source discovery")

        try:
            # Clear existing data
            self._sources.clear()
            self._configs.clear()
            self._source_instances.clear()

            # Discover config-driven sources
            self._discover_config_driven_sources()

            # Discover custom sources
            self._discover_custom_sources()

            self.logger.debug(
                f"Source discovery completed. Found {len(self._configs)} sources"
            )
            return self._configs.copy()

        except Exception as e:
            raise SourceError(f"Source discovery failed: {e}")

    def _discover_config_driven_sources(self):
        """Discover sources defined by configuration files."""
        config_dir = self.sources_dir / "config_driven" / "configs"

        if not config_dir.exists():
            self.logger.debug(
                f"Config-driven sources directory not found: {config_dir}"
            )
            return

        self.logger.debug(
            f"Discovering config-driven sources in: {config_dir}"
        )

        for config_file in config_dir.iterdir():
            if config_file.suffix in {".yaml", ".yml", ".json"}:
                try:
                    config = self._load_config_file(config_file)
                    source_name = config_file.stem

                    # Create SourceConfig
                    source_config = SourceConfig(
                        name=source_name,
                        display_name=config.get(
                            "display_name", source_name.title()
                        ),
                        base_url=config["base_url"],
                        timeout=config.get("timeout", 10.0),
                        rate_limit=config.get("rate_limit", 1.0),
                        supports_comments=config.get(
                            "supports_comments", False
                        ),
                        category=config.get("category", "general"),
                        custom_config=config,
                    )

                    # Validate configuration
                    errors = self._validate_config_driven_config(source_config)
                    if errors:
                        self.logger.warning(
                            f"Config validation failed for {source_name}: {errors}"
                        )
                        continue

                    self._configs[source_name] = source_config
                    self.logger.debug(
                        f"Registered config-driven source: {source_name}"
                    )

                except Exception as e:
                    self.logger.warning(
                        f"Failed to load config-driven source {config_file}: {e}"
                    )

    def _discover_custom_sources(self):
        """Discover custom source implementations."""
        custom_dir = self.sources_dir / "custom"

        if not custom_dir.exists():
            self.logger.debug(
                f"Custom sources directory not found: {custom_dir}"
            )
            return

        self.logger.debug(f"Discovering custom sources in: {custom_dir}")

        for source_dir in custom_dir.iterdir():
            if source_dir.is_dir() and not source_dir.name.startswith("_"):
                try:
                    self._load_custom_source(source_dir)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to load custom source {source_dir.name}: {e}"
                    )

    def _load_custom_source(self, source_dir: Path):
        """Load a custom source implementation."""
        source_name = source_dir.name

        # Look for source.py file
        source_file = source_dir / "source.py"
        if not source_file.exists():
            self.logger.debug(f"No source.py found in {source_dir}")
            return

        # Look for config file
        config_file = None
        for ext in [".yaml", ".yml", ".json"]:
            candidate = source_dir / f"config{ext}"
            if candidate.exists():
                config_file = candidate
                break

        if not config_file:
            self.logger.warning(
                f"No config file found for custom source: {source_name}"
            )
            return

        # Load configuration
        config_data = self._load_config_file(config_file)
        source_config = SourceConfig(
            name=source_name,
            display_name=config_data.get("display_name", source_name.title()),
            base_url=config_data["base_url"],
            timeout=config_data.get("timeout", 10.0),
            rate_limit=config_data.get("rate_limit", 1.0),
            supports_comments=config_data.get("supports_comments", False),
            category=config_data.get("category", "general"),
            custom_config=config_data,
        )

        # Load source class
        module_name = f"sources.custom.{source_name}.source"
        spec = importlib.util.spec_from_file_location(module_name, source_file)
        module = importlib.util.module_from_spec(spec)

        # Add to sys.modules for proper import handling
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Find the source class (should inherit from BaseSource)
        source_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseSource)
                and attr != BaseSource
            ):
                source_class = attr
                break

        if not source_class:
            raise SourceError(f"No BaseSource subclass found in {source_file}")

        # Validate the source class
        try:
            # Create a test instance to validate
            test_instance = source_class(source_config)
            validation_errors = test_instance.validate_config()
            if validation_errors:
                raise ConfigurationError(
                    f"Configuration validation failed: {validation_errors}"
                )
        except Exception as e:
            raise SourceError(f"Source validation failed: {e}")

        # Register the source
        self._sources[source_name] = source_class
        self._configs[source_name] = source_config
        self.logger.debug(f"Registered custom source: {source_name}")

    def _load_config_file(self, config_file: Path) -> Dict:
        """Load a configuration file (YAML or JSON)."""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                if config_file.suffix == ".json":
                    return json.load(f)
                else:  # YAML
                    return yaml.safe_load(f)
        except Exception as e:
            raise SourceError(f"Failed to load config file {config_file}: {e}")

    def _validate_config_driven_config(
        self, config: SourceConfig
    ) -> List[str]:
        """Validate configuration for config-driven sources."""
        errors = []

        # Check required fields for config-driven sources
        custom_config = config.custom_config

        if not custom_config.get("article_selectors"):
            errors.append(
                "article_selectors is required for config-driven sources"
            )

        if not custom_config.get("content_selectors"):
            errors.append(
                "content_selectors is required for config-driven sources"
            )

        # Validate selectors format
        selectors = custom_config.get("article_selectors", [])
        if not isinstance(selectors, list) or not selectors:
            errors.append("article_selectors must be a non-empty list")

        selectors = custom_config.get("content_selectors", [])
        if not isinstance(selectors, list) or not selectors:
            errors.append("content_selectors must be a non-empty list")

        return errors

    def get_source(self, source_name: str, session=None) -> BaseSource:
        """
        Get a source instance by name.

        Args:
            source_name: Name of the source
            session: Optional HTTP session

        Returns:
            BaseSource instance

        Raises:
            SourceError: If source is not found or cannot be instantiated
        """
        if source_name not in self._configs:
            available = ", ".join(self._configs.keys())
            raise SourceError(
                f"Source '{source_name}' not found. Available: {available}"
            )

        # Return cached instance if available
        cache_key = f"{source_name}_{id(session) if session else 'default'}"
        if cache_key in self._source_instances:
            return self._source_instances[cache_key]

        config = self._configs[source_name]

        # Create instance based on source type
        if source_name in self._sources:
            # Custom source
            source_class = self._sources[source_name]
            instance = source_class(config, session)
        else:
            # Config-driven source
            from .config_driven_source import ConfigDrivenSource

            instance = ConfigDrivenSource(config, session)

        # Cache the instance
        self._source_instances[cache_key] = instance
        return instance

    def get_available_sources(self) -> List[str]:
        """Get list of available source names."""
        return list(self._configs.keys())

    def get_sources_by_category(self, category: str) -> List[str]:
        """Get sources by category."""
        return [
            name
            for name, config in self._configs.items()
            if config.category == category
        ]

    def get_source_config(self, source_name: str) -> Optional[SourceConfig]:
        """Get source configuration by name."""
        return self._configs.get(source_name)

    def validate_all_sources(
        self, deep_validation: bool = False
    ) -> Dict[str, List[str]]:
        """
        Validate all registered sources using enhanced validation engine.

        Args:
            deep_validation: Whether to perform deep validation (network tests)

        Returns:
            Dictionary mapping source names to validation errors (empty list if valid)
        """
        # Use enhanced validation engine
        validation_results = self.validation_engine.validate_all_sources(
            self._configs, deep_validation
        )

        # Convert ValidationResult objects to string lists for backward compatibility
        legacy_results = {}
        for source_name, results in validation_results.items():
            error_messages = []
            for result in results:
                if not result.is_valid and result.severity == "error":
                    error_messages.append(result.message)
            legacy_results[source_name] = error_messages

        return legacy_results

    def enhanced_validate_all_sources(self, deep_validation: bool = False):
        """
        Enhanced validation with detailed results.

        Args:
            deep_validation: Whether to perform deep validation

        Returns:
            Dictionary mapping source names to ValidationResult objects
        """
        return self.validation_engine.validate_all_sources(
            self._configs, deep_validation
        )

    def generate_validation_report(self, deep_validation: bool = False) -> str:
        """
        Generate a comprehensive validation report.

        Args:
            deep_validation: Whether to perform deep validation

        Returns:
            Human-readable validation report
        """
        validation_results = self.enhanced_validate_all_sources(
            deep_validation
        )
        return self.validation_engine.generate_validation_report(
            validation_results
        )

    def get_registry_stats(self) -> Dict[str, int]:
        """Get registry statistics."""
        custom_count = len(self._sources)
        config_driven_count = len(self._configs) - custom_count

        return {
            "total_sources": len(self._configs),
            "custom_sources": custom_count,
            "config_driven_sources": config_driven_count,
            "cached_instances": len(self._source_instances),
        }

    def clear_cache(self):
        """Clear cached source instances."""
        self._source_instances.clear()
        self.logger.debug("Source instance cache cleared")

    def reload_sources(self):
        """Reload all sources (useful for development)."""
        self.clear_cache()
        return self.discover_sources()


# Global registry instance
_global_registry: Optional[SourceRegistry] = None


def get_source_registry() -> SourceRegistry:
    """Get the global source registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = SourceRegistry()
        _global_registry.discover_sources()
    return _global_registry


def reset_source_registry():
    """Reset the global source registry (useful for testing)."""
    global _global_registry
    _global_registry = None
