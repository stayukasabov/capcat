"""
Professional implementation of the add-source command using clean architecture principles.
Separates concerns through dependency injection and follows SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
from pathlib import Path
import sys

from core.exceptions import CapcatError, ValidationError
from core.logging_config import get_logger


@dataclass
class SourceMetadata:
    """Value object containing all source metadata."""
    source_id: str
    display_name: str
    base_url: str
    rss_url: str
    category: str

    def validate(self) -> None:
        """Validate source metadata."""
        if not self.source_id.isalnum():
            raise ValidationError("source_id", self.source_id, "Must be alphanumeric")
        if not self.display_name.strip():
            raise ValidationError("display_name", self.display_name, "Cannot be empty")
        if not self.category.strip():
            raise ValidationError("category", self.category, "Cannot be empty")


class FeedIntrospector(Protocol):
    """Protocol for RSS feed introspection."""

    @property
    def feed_title(self) -> str: ...

    @property
    def base_url(self) -> str: ...


class UserInterface(Protocol):
    """Protocol for user interaction."""

    def get_source_id(self, suggested: str) -> str: ...
    def select_category(self, categories: List[str]) -> str: ...
    def confirm_bundle_addition(self) -> bool: ...
    def select_bundle(self, bundles: List[str]) -> Optional[str]: ...
    def confirm_test_fetch(self) -> bool: ...
    def show_success(self, message: str) -> None: ...
    def show_error(self, message: str) -> None: ...


class ConfigGenerator(Protocol):
    """Protocol for configuration file generation."""

    def generate_and_save(self, metadata: SourceMetadata, config_path: Path) -> Path: ...


class BundleManager(Protocol):
    """Protocol for bundle management."""

    def get_bundle_names(self) -> List[str]: ...
    def add_source_to_bundle(self, source_id: str, bundle_name: str) -> None: ...


class SourceTester(Protocol):
    """Protocol for testing new sources."""

    def test_source(self, source_id: str, count: int = 1) -> bool: ...


class CategoryProvider(Protocol):
    """Protocol for category management."""

    def get_available_categories(self) -> List[str]: ...


class AddSourceCommand:
    """
    Command to add a new RSS source using clean architecture principles.

    Follows SOLID principles:
    - Single Responsibility: Only orchestrates the add-source workflow
    - Open/Closed: Extensible through dependency injection
    - Liskov Substitution: Uses protocols for type safety
    - Interface Segregation: Small, focused protocols
    - Dependency Inversion: Depends on abstractions, not concretions
    """

    def __init__(
        self,
        introspector_factory: 'IntrospectorFactory',
        ui: UserInterface,
        config_generator: ConfigGenerator,
        bundle_manager: BundleManager,
        source_tester: SourceTester,
        category_provider: CategoryProvider,
        config_path: Path,
        bundles_path: Path,
        logger: Optional[Any] = None
    ):
        self._introspector_factory = introspector_factory
        self._ui = ui
        self._config_generator = config_generator
        self._bundle_manager = bundle_manager
        self._source_tester = source_tester
        self._category_provider = category_provider
        self._config_path = config_path
        self._bundles_path = bundles_path
        self._logger = logger or get_logger(__name__)

    def execute(self, url: str) -> None:
        """
        Execute the add-source command.

        Args:
            url: RSS feed URL to add

        Raises:
            CapcatError: If any step in the process fails
        """
        try:
            self._logger.info(f"Starting add-source workflow for URL: {url}")

            # Step 1: Introspect RSS feed
            introspector = self._introspect_feed(url)

            # Step 2: Collect user input
            metadata = self._collect_source_metadata(introspector, url)

            # Step 3: Generate and save configuration
            config_file = self._generate_configuration(metadata)

            # Step 4: Optional bundle integration
            self._handle_bundle_integration(metadata.source_id)

            # Step 5: Optional testing
            self._handle_source_testing(metadata.source_id)

            self._ui.show_success(f"Source '{metadata.source_id}' added successfully!")
            self._logger.info(f"Successfully added source: {metadata.source_id}")

        except CapcatError:
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error in add-source: {e}")
            raise CapcatError(f"Unexpected error: {e}") from e

    def _introspect_feed(self, url: str) -> FeedIntrospector:
        """Step 1: Introspect the RSS feed."""
        try:
            return self._introspector_factory.create(url)
        except Exception as e:
            self._ui.show_error(f"Failed to introspect feed: {e}")
            raise

    def _collect_source_metadata(self, introspector: FeedIntrospector, url: str) -> SourceMetadata:
        """Step 2: Collect all required metadata from user and introspector."""
        # Generate suggested source ID
        suggested_id = self._generate_source_id_suggestion(introspector.feed_title)

        # Collect user input
        source_id = self._ui.get_source_id(suggested_id)
        category = self._ui.select_category(self._category_provider.get_available_categories())

        # Create and validate metadata
        metadata = SourceMetadata(
            source_id=source_id,
            display_name=introspector.feed_title,
            base_url=introspector.base_url,
            rss_url=url,
            category=category
        )

        metadata.validate()
        return metadata

    def _generate_configuration(self, metadata: SourceMetadata) -> Path:
        """Step 3: Generate and save configuration file."""
        try:
            return self._config_generator.generate_and_save(metadata, self._config_path)
        except Exception as e:
            self._ui.show_error(f"Failed to generate configuration: {e}")
            raise

    def _handle_bundle_integration(self, source_id: str) -> None:
        """Step 4: Handle optional bundle integration."""
        if not self._ui.confirm_bundle_addition():
            return

        try:
            bundles = self._bundle_manager.get_bundle_names()
            selected_bundle = self._ui.select_bundle(bundles)

            if selected_bundle:
                self._bundle_manager.add_source_to_bundle(source_id, selected_bundle)
                self._ui.show_success(f"Added '{source_id}' to bundle '{selected_bundle}'")

        except Exception as e:
            self._ui.show_error(f"Failed to add to bundle: {e}")
            # Don't raise - bundle integration is optional

    def _handle_source_testing(self, source_id: str) -> None:
        """Step 5: Handle optional source testing."""
        if not self._ui.confirm_test_fetch():
            return

        try:
            if self._source_tester.test_source(source_id):
                self._ui.show_success("Test fetch successful!")
            else:
                self._ui.show_error("Test fetch failed. Check configuration.")

        except Exception as e:
            self._ui.show_error(f"Test fetch error: {e}")
            # Don't raise - testing is optional

    def _generate_source_id_suggestion(self, feed_title: str) -> str:
        """Generate a suggested source ID from feed title."""
        import re
        return re.sub(r'[^a-z0-9]', '', feed_title.lower())[:20]  # Limit length


class IntrospectorFactory(Protocol):
    """Factory for creating feed introspectors."""

    def create(self, url: str) -> FeedIntrospector: ...


# Concrete implementations for existing classes
class RssFeedIntrospectorAdapter:
    """Adapter to make existing RssFeedIntrospector compatible with protocol."""

    def __init__(self, introspector):
        self._introspector = introspector

    @property
    def feed_title(self) -> str:
        return self._introspector.feed_title

    @property
    def base_url(self) -> str:
        return self._introspector.base_url


class RssFeedIntrospectorFactory:
    """Factory for creating RSS feed introspectors."""

    def create(self, url: str) -> FeedIntrospector:
        from core.source_system.rss_feed_introspector import RssFeedIntrospector
        introspector = RssFeedIntrospector(url)
        return RssFeedIntrospectorAdapter(introspector)


class SourceConfigGeneratorAdapter:
    """Adapter for existing SourceConfigGenerator."""

    def __init__(self, generator_class):
        self._generator_class = generator_class

    def generate_and_save(self, metadata: SourceMetadata, config_path: Path) -> Path:
        source_metadata = {
            "source_id": metadata.source_id,
            "display_name": metadata.display_name,
            "base_url": metadata.base_url,
            "rss_url": metadata.rss_url,
            "category": metadata.category
        }
        generator = self._generator_class(source_metadata)
        return Path(generator.generate_and_save(str(config_path)))


class SubprocessSourceTester:
    """Source tester using subprocess calls."""

    def test_source(self, source_id: str, count: int = 1) -> bool:
        import subprocess
        try:
            command = ["./capcat", "fetch", source_id, "--count", str(count)]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False


class RegistryCategoryProvider:
    """Category provider using source registry."""

    def get_available_categories(self) -> List[str]:
        try:
            from core.source_system.source_registry import get_source_registry
            registry = get_source_registry()
            all_configs = [
                registry.get_source_config(sid)
                for sid in registry.get_available_sources()
            ]
            categories = sorted(list(set(
                config.category for config in all_configs
                if config and hasattr(config, 'category')
            )))
            return categories or ['tech', 'news', 'science', 'ai', 'sports', 'general']
        except Exception:
            return ['tech', 'news', 'science', 'ai', 'sports', 'general']