#!/usr/bin/env python3
"""
Source Registry for managing all available news sources and their configurations.
Provides centralized access to source definitions and bundle configurations.
"""

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from ..logging_config import get_logger
from .source_base import BundleConfig, SourceConfig, SourceConfigLoader


@dataclass
class SourceRegistryConfig:
    """Configuration for the source registry."""

    config_dir: Path
    auto_reload: bool = True
    cache_configs: bool = True
    validate_on_load: bool = True


class SourceRegistry:
    """
    Registry for all available news sources and their configurations.

    Provides centralized management of source configurations, bundle definitions,
    and source discovery capabilities.
    """

    def __init__(self, config: Optional[SourceRegistryConfig] = None):
        """
        Initialize the source registry.

        Args:
            config: Registry configuration settings
        """
        self.logger = get_logger(__name__)
        self._lock = threading.RLock()

        # Configuration
        self.config = config or SourceRegistryConfig(
            config_dir=Path(__file__).parent.parent.parent
            / "sources"
            / "active"
        )

        # Storage
        self._sources: Dict[str, SourceConfig] = {}
        self._bundles: Dict[str, BundleConfig] = {}
        self._source_categories: Dict[str, List[str]] = {}
        self._config_loader = SourceConfigLoader()

        # Registry state
        self._initialized = False
        self._last_load_time = 0

        # Initialize registry
        self._initialize()

    def _initialize(self):
        """Initialize the registry by loading all available configurations."""
        try:
            self._load_default_sources()
            self._load_default_bundles()
            self._load_user_configurations()
            self._initialized = True
            self.logger.debug("Source registry initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize source registry: {e}")
            self._initialized = False

    def _load_default_sources(self):
        """Load default source configurations from config files."""
        config_dir = self.config.config_dir
        if not config_dir.exists():
            self.logger.warning(
                f"Source config directory not found: {config_dir}"
            )
            return

        # Load source configuration files
        source_files = [
            "tech_sources.yml",
            "news_sources.yml",
            "science_sources.yml",
            "business_sources.yml",
            "aggregator_sources.yml",
        ]

        for source_file in source_files:
            file_path = config_dir / source_file
            if file_path.exists():
                self._load_sources_from_file(file_path)

    def _load_sources_from_file(self, file_path: Path):
        """Load source configurations from a specific file."""
        try:
            data = self._config_loader.load_from_file(file_path)
            sources = data.get("sources", {})

            for source_id, source_data in sources.items():
                source_data["source_id"] = source_id
                source_config = SourceConfig.from_dict(source_data)
                self._sources[source_id] = source_config

                # Add to category if specified
                category = source_data.get("category")
                if category:
                    if category not in self._source_categories:
                        self._source_categories[category] = []
                    self._source_categories[category].append(source_id)

            self.logger.debug(
                f"Loaded {len(sources)} sources from {file_path}"
            )

        except Exception as e:
            self.logger.error(f"Error loading sources from {file_path}: {e}")

    def _load_default_bundles(self):
        """Load default bundle configurations."""
        bundle_file = self.config.config_dir / "bundles.yml"
        if not bundle_file.exists():
            # Create default bundles if file doesn't exist
            self._create_default_bundles()
            return

        try:
            data = self._config_loader.load_from_file(bundle_file)
            bundles = data.get("bundles", {})

            for bundle_id, bundle_data in bundles.items():
                bundle_data["name"] = bundle_id
                bundle_config = BundleConfig.from_dict(bundle_data)
                self._bundles[bundle_id] = bundle_config

            self.logger.debug(
                f"Loaded {len(bundles)} bundles from {bundle_file}"
            )

        except Exception as e:
            self.logger.error(f"Error loading bundles from {bundle_file}: {e}")

    def _create_default_bundles(self):
        """Create and register default bundle configurations."""
        default_bundles = {
            "tech": BundleConfig(
                name="tech",
                description="Technology news sources",
                sources=["hn", "lb", "iq", "engadget"],
                default_count=30,
            ),
            "news": BundleConfig(
                name="news",
                description="General news sources",
                sources=[
                    "bbc",
                    "cnn",
                    "aljazeera",
                    "euronews",
                    "straitstimes",
                ],
                default_count=25,
            ),
            "science": BundleConfig(
                name="science",
                description="Science and research sources",
                sources=["nature", "scientificamerican", "mittechreview"],
                default_count=20,
            ),
            "business": BundleConfig(
                name="business",
                description="Business and finance sources",
                sources=["financialtimes"],
                default_count=15,
            ),
            "aggregators": BundleConfig(
                name="aggregators",
                description="News aggregator sources",
                sources=["gn", "newsmap", "upday"],
                default_count=40,
            ),
            "all": BundleConfig(
                name="all",
                description="All available sources",
                sources=[],  # Will be populated dynamically
                default_count=10,
            ),
        }

        for bundle_id, bundle_config in default_bundles.items():
            self._bundles[bundle_id] = bundle_config

    def _load_user_configurations(self):
        """Load user-specific source and bundle configurations."""
        user_config_dir = Path.home() / ".capcat" / "sources"
        if not user_config_dir.exists():
            return

        try:
            # Load user source overrides
            user_sources_file = user_config_dir / "custom_sources.yml"
            if user_sources_file.exists():
                self._load_sources_from_file(user_sources_file)

            # Load user bundle overrides
            user_bundles_file = user_config_dir / "custom_bundles.yml"
            if user_bundles_file.exists():
                data = self._config_loader.load_from_file(user_bundles_file)
                bundles = data.get("bundles", {})

                for bundle_id, bundle_data in bundles.items():
                    bundle_data["name"] = bundle_id
                    bundle_config = BundleConfig.from_dict(bundle_data)
                    self._bundles[bundle_id] = bundle_config

        except Exception as e:
            self.logger.error(f"Error loading user configurations: {e}")

    # Public API methods

    def register_source(
        self,
        source_id: str,
        config: SourceConfig,
        category: Optional[str] = None,
    ):
        """
        Register a news source with its configuration.

        Args:
            source_id: Unique identifier for the source
            config: Source configuration
            category: Optional category for grouping
        """
        with self._lock:
            self._sources[source_id] = config

            if category:
                if category not in self._source_categories:
                    self._source_categories[category] = []
                if source_id not in self._source_categories[category]:
                    self._source_categories[category].append(source_id)

            self.logger.debug(f"Registered source: {source_id}")

    def register_bundle(self, bundle_id: str, config: BundleConfig):
        """
        Register a source bundle with its configuration.

        Args:
            bundle_id: Unique identifier for the bundle
            config: Bundle configuration
        """
        with self._lock:
            self._bundles[bundle_id] = config
            self.logger.debug(f"Registered bundle: {bundle_id}")

    def get_source_config(self, source_id: str) -> Optional[SourceConfig]:
        """
        Get configuration for a specific source.

        Args:
            source_id: ID of the source

        Returns:
            SourceConfig instance or None if not found
        """
        with self._lock:
            return self._sources.get(source_id)

    def get_bundle_config(self, bundle_id: str) -> Optional[BundleConfig]:
        """
        Get configuration for a specific bundle.

        Args:
            bundle_id: ID of the bundle

        Returns:
            BundleConfig instance or None if not found
        """
        with self._lock:
            bundle = self._bundles.get(bundle_id)

            # Special handling for 'all' bundle - populate with all available sources
            if bundle and bundle_id == "all" and not bundle.sources:
                bundle.sources = list(self._sources.keys())

            return bundle

    def list_available_sources(self) -> List[str]:
        """
        List all available source IDs.

        Returns:
            List of source IDs
        """
        with self._lock:
            return list(self._sources.keys())

    def list_available_bundles(self) -> List[str]:
        """
        List all available bundle IDs.

        Returns:
            List of bundle IDs
        """
        with self._lock:
            return list(self._bundles.keys())

    def list_sources_by_category(self, category: str) -> List[str]:
        """
        List sources in a specific category.

        Args:
            category: Category name

        Returns:
            List of source IDs in the category
        """
        with self._lock:
            return self._source_categories.get(category, [])

    def list_categories(self) -> List[str]:
        """
        List all available source categories.

        Returns:
            List of category names
        """
        with self._lock:
            return list(self._source_categories.keys())

    def validate_source_ids(self, source_ids: List[str]) -> Dict[str, bool]:
        """
        Validate a list of source IDs.

        Args:
            source_ids: List of source IDs to validate

        Returns:
            Dictionary mapping source IDs to validation status
        """
        with self._lock:
            return {
                source_id: source_id in self._sources
                for source_id in source_ids
            }

    def get_bundle_sources(self, bundle_id: str) -> List[str]:
        """
        Get the list of source IDs in a bundle.

        Args:
            bundle_id: ID of the bundle

        Returns:
            List of source IDs, empty list if bundle not found
        """
        bundle = self.get_bundle_config(bundle_id)
        return bundle.sources if bundle else []

    def search_sources(self, query: str) -> List[str]:
        """
        Search for sources by name or description.

        Args:
            query: Search query

        Returns:
            List of matching source IDs
        """
        query_lower = query.lower()
        matches = []

        with self._lock:
            for source_id, config in self._sources.items():
                if (
                    query_lower in source_id.lower()
                    or query_lower in config.name.lower()
                    or query_lower in config.base_url.lower()
                ):
                    matches.append(source_id)

        return matches

    def get_registry_stats(self) -> Dict[str, int]:
        """
        Get statistics about the registry.

        Returns:
            Dictionary with registry statistics
        """
        with self._lock:
            return {
                "total_sources": len(self._sources),
                "total_bundles": len(self._bundles),
                "total_categories": len(self._source_categories),
                "initialized": self._initialized,
            }

    def reload_configurations(self):
        """Reload all configurations from disk."""
        with self._lock:
            self.logger.info("Reloading source configurations...")
            self._sources.clear()
            self._bundles.clear()
            self._source_categories.clear()
            self._initialize()


# Global registry instance
_registry_instance: Optional[SourceRegistry] = None
_registry_lock = threading.Lock()


def get_source_registry() -> SourceRegistry:
    """
    Get the global source registry instance.

    Returns:
        SourceRegistry instance
    """
    global _registry_instance

    if _registry_instance is None:
        with _registry_lock:
            if _registry_instance is None:
                _registry_instance = SourceRegistry()

    return _registry_instance


def reset_source_registry():
    """Reset the global source registry instance. Used primarily for testing."""
    global _registry_instance
    with _registry_lock:
        _registry_instance = None
