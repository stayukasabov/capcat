"""
Service layer for remove-source command.
Provides clean integration with CLI while maintaining separation of concerns.
"""

from pathlib import Path
from typing import Optional

from core.source_system.remove_source_command import (
    RemoveSourceCommand,
    RegistrySourceLister,
    RegistrySourceInfoProvider,
    FileSystemConfigRemover,
    BundleManagerUpdater
)
from core.source_system.removal_ui import QuestionaryRemovalUI
from core.logging_config import get_logger


class RemoveSourceService:
    """
    Service for removing existing sources.
    Provides high-level interface for CLI integration.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the remove-source service.

        Args:
            base_path: Optional base path for the application
        """
        if base_path is None:
            # Default to application directory
            import cli
            base_path = Path(cli.__file__).parent

        self._base_path = base_path
        self._config_path = (
            base_path / "sources" / "active" / "config_driven" / "configs"
        )
        self._bundles_path = base_path / "sources" / "active" / "bundles.yml"
        self._logger = get_logger(__name__)

    def remove_sources(self) -> None:
        """
        Interactive removal of sources.

        Raises:
            CapcatError: If removal fails
        """
        self._logger.info("Starting remove-source workflow")

        # Create command with dependencies
        command = self._create_remove_source_command()

        # Execute
        command.execute()

    def _create_remove_source_command(self) -> RemoveSourceCommand:
        """Create and configure RemoveSourceCommand with dependencies."""
        return RemoveSourceCommand(
            source_lister=RegistrySourceLister(),
            source_info_provider=RegistrySourceInfoProvider(
                self._config_path, self._bundles_path
            ),
            ui=QuestionaryRemovalUI(),
            config_remover=FileSystemConfigRemover(),
            bundle_updater=BundleManagerUpdater(self._bundles_path),
            logger=self._logger
        )


def create_remove_source_service() -> RemoveSourceService:
    """
    Factory function to create RemoveSourceService.

    Returns:
        Configured RemoveSourceService instance
    """
    return RemoveSourceService()