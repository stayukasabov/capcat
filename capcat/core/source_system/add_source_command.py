"""
Professional implementation of the add-source command using clean architecture principles.
Separates concerns through dependency injection and follows SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
from pathlib import Path
import sys

from capcat.core.exceptions import CapcatError, ValidationError
from capcat.core.logging_config import get_logger


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
    """Protocol for RSS feed introspection.

    Implementations read a feed URL and expose its title and base URL.
    See ``RssFeedIntrospector`` for the production implementation.
    """

    @property
    def feed_title(self) -> str:
        """Human-readable title extracted from the RSS/Atom feed."""
        ...

    @property
    def base_url(self) -> str:
        """Root URL of the publisher (stripped of path)."""
        ...


class UserInterface(Protocol):
    """Protocol for user interaction during the add-source workflow.

    Implementations may use questionary (interactive TUI), a mock (tests),
    or any other mechanism that satisfies this contract.
    """

    def get_source_id(self, suggested: str) -> str:
        """Prompt the user to confirm or override the suggested source ID.

        Args:
            suggested: Auto-derived source ID (e.g. ``"mysite"``).

        Returns:
            The confirmed or overridden source ID string.
        """
        ...

    def select_category(self, categories: List[str]) -> str:
        """Prompt the user to choose a topic category.

        Args:
            categories: Available category names.

        Returns:
            The selected category string.
        """
        ...

    def confirm_bundle_addition(self) -> bool:
        """Ask whether to add the new source to an existing bundle.

        Returns:
            ``True`` if the user wants to add to a bundle.
        """
        ...

    def select_bundle(self, bundles: List[str]) -> Optional[str]:
        """Prompt the user to pick a bundle to add the source to.

        Args:
            bundles: Available bundle names.

        Returns:
            Selected bundle name, or ``None`` if cancelled.
        """
        ...

    def confirm_test_fetch(self) -> bool:
        """Ask whether to run a test fetch after saving the config.

        Returns:
            ``True`` if the user wants a test fetch.
        """
        ...

    def show_success(self, message: str) -> None:
        """Display a success notification.

        Args:
            message: Success text to show the user.
        """
        ...

    def show_error(self, message: str) -> None:
        """Display an error notification.

        Args:
            message: Error text to show the user.
        """
        ...


class ConfigGenerator(Protocol):
    """Protocol for configuration file generation."""

    def generate_and_save(
        self, metadata: SourceMetadata, config_path: Path
    ) -> Path:
        """Generate a YAML config file and write it to disk.

        Args:
            metadata: Source metadata to serialize.
            config_path: Directory where the config file should be saved.

        Returns:
            Path to the written config file.
        """
        ...


class BundleManager(Protocol):
    """Protocol for bundle management."""

    def get_bundle_names(self) -> List[str]:
        """Return the names of all available bundles.

        Returns:
            List of bundle name strings.
        """
        ...

    def add_source_to_bundle(self, source_id: str, bundle_name: str) -> None:
        """Add a source to a named bundle in bundles.yml.

        Args:
            source_id: Source identifier to add.
            bundle_name: Bundle to add the source to.
        """
        ...


class SourceTester(Protocol):
    """Protocol for testing new sources."""

    def test_source(self, source_id: str, count: int = 1) -> bool:
        """Run a test fetch to verify the source is functional.

        Args:
            source_id: The source identifier to test.
            count: Number of articles to attempt fetching.

        Returns:
            ``True`` if at least one article was fetched successfully.
        """
        ...


class CategoryProvider(Protocol):
    """Protocol for category management."""

    def get_available_categories(self) -> List[str]:
        """Return all available topic category names.

        Returns:
            List of category strings (e.g. ``["tech", "science", "news"]``).
        """
        ...


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
        logger: Optional[Any] = None,
    ) -> None:
        """Wire up all dependencies for the add-source workflow.

        Args:
            introspector_factory: Creates FeedIntrospector instances for URLs.
            ui: User interaction layer (questionary, mock, etc.).
            config_generator: Writes YAML config files to disk.
            bundle_manager: Reads and updates bundles.yml.
            source_tester: Runs test fetches against new sources.
            category_provider: Returns available topic categories.
            config_path: Directory where new source configs are saved.
            bundles_path: Path to bundles.yml.
            logger: Optional logger; defaults to module logger.
        """
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

    def create(self, url: str) -> FeedIntrospector:
        """Create a FeedIntrospector for the given feed URL.

        Args:
            url: RSS/Atom feed URL to introspect.

        Returns:
            A FeedIntrospector instance ready to expose feed metadata.
        """
        ...


# Concrete implementations for existing classes
class RssFeedIntrospectorAdapter:
    """Adapter to make existing RssFeedIntrospector compatible with protocol."""

    def __init__(self, introspector):
        """Wrap an existing RssFeedIntrospector instance.

        Args:
            introspector: An ``RssFeedIntrospector`` instance whose
                ``feed_title`` and ``base_url`` attributes will be proxied.
        """
        self._introspector = introspector

    @property
    def feed_title(self) -> str:
        """Human-readable title extracted from the wrapped introspector."""
        return self._introspector.feed_title

    @property
    def base_url(self) -> str:
        """Root URL of the publisher from the wrapped introspector."""
        return self._introspector.base_url


class RssFeedIntrospectorFactory:
    """Factory for creating RSS feed introspectors."""

    def create(self, url: str) -> FeedIntrospector:
        """Create an adapted RSS feed introspector for the given URL.

        Instantiates ``RssFeedIntrospector`` and wraps it in
        ``RssFeedIntrospectorAdapter`` so it satisfies the
        ``FeedIntrospector`` protocol.

        Args:
            url: RSS/Atom feed URL to introspect.

        Returns:
            An ``RssFeedIntrospectorAdapter`` exposing ``feed_title``
            and ``base_url`` for the given feed.
        """
        from capcat.core.source_system.rss_feed_introspector import RssFeedIntrospector
        introspector = RssFeedIntrospector(url)
        return RssFeedIntrospectorAdapter(introspector)


class SourceConfigGeneratorAdapter:
    """Adapter for existing SourceConfigGenerator."""

    def __init__(self, generator_class):
        """Store the SourceConfigGenerator class for deferred instantiation.

        Args:
            generator_class: The ``SourceConfigGenerator`` class (not an
                instance). It will be instantiated per call to
                ``generate_and_save`` with the serialized metadata dict.
        """
        self._generator_class = generator_class

    def generate_and_save(self, metadata: SourceMetadata, config_path: Path) -> Path:
        """Serialize metadata and delegate to the wrapped generator class.

        Converts ``SourceMetadata`` to the dict format expected by
        ``SourceConfigGenerator``, instantiates it, and calls its own
        ``generate_and_save`` method.

        Args:
            metadata: Source metadata to serialize into a YAML config file.
            config_path: Directory where the config file should be written.

        Returns:
            Path to the written YAML config file.
        """
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
        """Run a test fetch via the ``./capcat fetch`` subprocess.

        Invokes ``./capcat fetch <source_id> --count <count>`` and treats
        a zero exit code as success.

        Args:
            source_id: The source identifier to test.
            count: Number of articles to attempt fetching. Defaults to 1.

        Returns:
            ``True`` if the subprocess exits with code 0 within 30 seconds,
            ``False`` on non-zero exit, timeout, or if the ``capcat``
            wrapper is not found.
        """
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
        """Return categories derived from all currently registered sources.

        Queries the global ``SourceRegistry`` for all active source configs
        and collects unique ``category`` values. Falls back to a hard-coded
        default list if the registry is unavailable or yields no categories.

        Returns:
            Sorted list of category strings (e.g. ``["ai", "news", "tech"]``).
            Defaults to ``['tech', 'news', 'science', 'ai', 'sports', 'general']``
            if the registry cannot be reached.
        """
        try:
            from capcat.core.source_system.source_registry import get_source_registry
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