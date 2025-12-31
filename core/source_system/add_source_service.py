"""
Service layer for the add-source command.
Provides a clean interface for CLI integration while maintaining separation of concerns.
"""

from pathlib import Path
from typing import Optional

from core.source_system.add_source_command import (
    AddSourceCommand,
    RssFeedIntrospectorFactory,
    SourceConfigGeneratorAdapter,
    SubprocessSourceTester,
    RegistryCategoryProvider
)
from core.source_system.questionary_ui import QuestionaryUserInterface
from core.source_system.bundle_manager import BundleManager
from core.source_system.source_config_generator import SourceConfigGenerator
from core.logging_config import get_logger


class AddSourceService:
    """
    Service for adding new RSS sources.
    Provides a clean, high-level interface for CLI integration.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the add-source service.

        Args:
            base_path: Optional base path for the application (defaults to CLI's parent)
        """
        if base_path is None:
            # Default to the application directory
            import cli
            base_path = Path(cli.__file__).parent

        self._base_path = base_path
        self._config_path = base_path / "sources" / "active" / "config_driven" / "configs"
        self._bundles_path = base_path / "sources" / "active" / "bundles.yml"
        self._logger = get_logger(__name__)

    def add_source(self, url: str) -> None:
        """
        Add a new RSS source using the provided URL.

        Args:
            url: URL of the RSS feed to add

        Raises:
            CapcatError: If the source cannot be added
        """
        self._logger.info(f"Attempting to add new source from: {url}")

        # Create dependencies
        command = self._create_add_source_command()

        # Execute the command
        command.execute(url)

    def _create_add_source_command(self) -> AddSourceCommand:
        """Create and configure the AddSourceCommand with all dependencies."""
        return AddSourceCommand(
            introspector_factory=RssFeedIntrospectorFactory(),
            ui=QuestionaryUserInterface(),
            config_generator=SourceConfigGeneratorAdapter(SourceConfigGenerator),
            bundle_manager=BundleManager(str(self._bundles_path)),
            source_tester=SubprocessSourceTester(),
            category_provider=RegistryCategoryProvider(),
            config_path=self._config_path,
            bundles_path=self._bundles_path,
            logger=self._logger
        )


def create_add_source_service() -> AddSourceService:
    """
    Factory function to create an AddSourceService instance.

    Returns:
        Configured AddSourceService instance
    """
    return AddSourceService()