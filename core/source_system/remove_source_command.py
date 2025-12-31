"""
Professional implementation of the remove-source command using clean architecture.
Follows the same patterns as add-source for consistency.
"""

from typing import List, Optional, Protocol
from pathlib import Path
from dataclasses import dataclass

from core.exceptions import CapcatError, ValidationError
from core.logging_config import get_logger


@dataclass
class SourceRemovalInfo:
    """Information about a source to be removed."""
    source_id: str
    display_name: str
    config_path: Path
    bundles: List[str]


class SourceLister(Protocol):
    """Protocol for listing available sources."""

    def get_available_sources(self) -> List[tuple[str, str]]:
        """
        Get list of available sources.

        Returns:
            List of tuples (source_id, display_name)
        """
        ...


class SourceInfoProvider(Protocol):
    """Protocol for getting source information."""

    def get_source_info(self, source_id: str) -> Optional[SourceRemovalInfo]:
        """
        Get detailed information about a source.

        Args:
            source_id: Source identifier

        Returns:
            SourceRemovalInfo or None if not found
        """
        ...


class RemovalUserInterface(Protocol):
    """Protocol for user interaction during removal."""

    def select_sources_to_remove(
        self, sources: List[tuple[str, str]]
    ) -> List[str]:
        """
        Let user select sources to remove.

        Args:
            sources: List of (source_id, display_name) tuples

        Returns:
            List of selected source IDs
        """
        ...

    def confirm_removal(self, sources_info: List[SourceRemovalInfo]) -> bool:
        """
        Confirm removal with user.

        Args:
            sources_info: Information about sources to be removed

        Returns:
            True if user confirms, False otherwise
        """
        ...

    def show_removal_summary(
        self, sources_info: List[SourceRemovalInfo]
    ) -> None:
        """
        Show summary of what will be removed.

        Args:
            sources_info: Information about sources to be removed
        """
        ...

    def show_success(self, message: str) -> None:
        """Display success message."""
        ...

    def show_error(self, message: str) -> None:
        """Display error message."""
        ...

    def show_info(self, message: str) -> None:
        """Display informational message."""
        ...


class ConfigFileRemover(Protocol):
    """Protocol for removing configuration files."""

    def remove_config_file(self, config_path: Path) -> None:
        """
        Remove a configuration file.

        Args:
            config_path: Path to config file to remove
        """
        ...


class BundleUpdater(Protocol):
    """Protocol for updating bundles."""

    def remove_source_from_all_bundles(self, source_id: str) -> List[str]:
        """
        Remove source from all bundles.

        Args:
            source_id: Source identifier

        Returns:
            List of bundle names that were updated
        """
        ...


class RemoveSourceCommand:
    """
    Command to remove existing sources.

    Follows clean architecture principles with dependency injection
    and single responsibility per component.
    """

    def __init__(
        self,
        source_lister: SourceLister,
        source_info_provider: SourceInfoProvider,
        ui: RemovalUserInterface,
        config_remover: ConfigFileRemover,
        bundle_updater: BundleUpdater,
        logger: Optional[any] = None
    ):
        self._source_lister = source_lister
        self._source_info_provider = source_info_provider
        self._ui = ui
        self._config_remover = config_remover
        self._bundle_updater = bundle_updater
        self._logger = logger or get_logger(__name__)

    def execute(self) -> None:
        """
        Execute the remove-source command.

        Raises:
            CapcatError: If removal fails
        """
        try:
            self._logger.info("Starting remove-source workflow")

            # Step 1: Get available sources
            available_sources = self._get_available_sources()
            if not available_sources:
                self._ui.show_info("No sources available to remove.")
                return

            # Step 2: Let user select sources to remove
            selected_ids = self._ui.select_sources_to_remove(available_sources)
            if not selected_ids:
                self._ui.show_info("No sources selected for removal.")
                return

            # Step 3: Gather information about selected sources
            sources_info = self._gather_sources_info(selected_ids)

            # Step 4: Show summary and confirm
            self._ui.show_removal_summary(sources_info)
            if not self._ui.confirm_removal(sources_info):
                self._ui.show_info("Removal cancelled.")
                return

            # Step 5: Perform removal
            self._remove_sources(sources_info)

            # Refresh the source registry to reflect deletions
            self._refresh_registry()

            self._ui.show_success(
                f"Successfully removed {len(sources_info)} source(s)."
            )
            self._logger.info(
                f"Successfully removed sources: {[s.source_id for s in sources_info]}"
            )

        except CapcatError:
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error in remove-source: {e}")
            raise CapcatError(f"Unexpected error: {e}") from e

    def _get_available_sources(self) -> List[tuple[str, str]]:
        """Step 1: Get list of available sources."""
        try:
            return self._source_lister.get_available_sources()
        except Exception as e:
            self._ui.show_error(f"Failed to list sources: {e}")
            raise CapcatError(f"Failed to list sources: {e}") from e

    def _gather_sources_info(
        self, source_ids: List[str]
    ) -> List[SourceRemovalInfo]:
        """Step 3: Gather detailed information about sources to remove."""
        sources_info = []
        for source_id in source_ids:
            info = self._source_info_provider.get_source_info(source_id)
            if info:
                sources_info.append(info)
            else:
                self._logger.warning(
                    f"Could not find info for source: {source_id}"
                )

        return sources_info

    def _remove_sources(self, sources_info: List[SourceRemovalInfo]) -> None:
        """Step 5: Remove sources and update system."""
        for info in sources_info:
            try:
                # Remove from bundles
                updated_bundles = self._bundle_updater.remove_source_from_all_bundles(
                    info.source_id
                )
                if updated_bundles:
                    self._logger.info(
                        f"Removed '{info.source_id}' from bundles: {updated_bundles}"
                    )

                # Remove config file
                self._config_remover.remove_config_file(info.config_path)
                self._logger.info(
                    f"Deleted config file: {info.config_path}"
                )

                self._ui.show_info(f"Removed '{info.display_name}'")

            except Exception as e:
                self._logger.error(
                    f"Failed to remove source '{info.source_id}': {e}"
                )
                self._ui.show_error(
                    f"Failed to remove '{info.display_name}': {e}"
                )

    def _refresh_registry(self) -> None:
        """Refresh the source registry to reflect filesystem changes."""
        try:
            from core.source_system.source_registry import reset_source_registry
            reset_source_registry()
            self._logger.info("Source registry refreshed")
        except Exception as e:
            self._logger.warning(f"Failed to refresh registry: {e}")


# Concrete implementations

class FileSystemConfigRemover:
    """Concrete implementation for removing config files and directories."""

    def remove_config_file(self, config_path: Path) -> None:
        """Remove configuration file or directory from filesystem."""
        import os
        import shutil

        if config_path.exists():
            if config_path.is_dir():
                # Remove custom source directory (e.g., sources/active/custom/lesswrong/)
                shutil.rmtree(config_path)
            else:
                # Remove config file (e.g., sources/active/config_driven/configs/hn.yml)
                os.remove(config_path)


class RegistrySourceLister:
    """Source lister using the source registry."""

    def get_available_sources(self) -> List[tuple[str, str]]:
        """Get sources from registry."""
        from core.source_system.source_registry import get_source_registry

        try:
            registry = get_source_registry()
            sources = []

            for source_id in sorted(registry.get_available_sources()):
                config = registry.get_source_config(source_id)
                if config:
                    display_name = getattr(config, 'display_name', source_id)
                    sources.append((source_id, display_name))

            return sources
        except Exception as e:
            raise CapcatError(f"Failed to load sources from registry: {e}")


class RegistrySourceInfoProvider:
    """Source info provider using registry and filesystem."""

    def __init__(self, config_base_path: Path, bundles_path: Path):
        self._config_base_path = config_base_path
        self._bundles_path = bundles_path

    def get_source_info(self, source_id: str) -> Optional[SourceRemovalInfo]:
        """Get source information from registry and bundles."""
        from core.source_system.source_registry import get_source_registry

        try:
            registry = get_source_registry()
            config = registry.get_source_config(source_id)

            if not config:
                return None

            # Find config file path - check all possible extensions
            config_path = None

            # First check config-driven sources (YAML/JSON files)
            for ext in [".yaml", ".yml", ".json"]:
                candidate = self._config_base_path / f"{source_id}{ext}"
                if candidate.exists():
                    config_path = candidate
                    break

            # If not found, check for custom source (directory-based)
            if not config_path:
                custom_source_dir = (
                    self._config_base_path.parent.parent / "custom" / source_id
                )
                if custom_source_dir.exists() and custom_source_dir.is_dir():
                    config_path = custom_source_dir
                else:
                    # Fallback to .yml if file doesn't exist (shouldn't happen)
                    config_path = self._config_base_path / f"{source_id}.yml"

            # Find bundles containing this source
            bundles = self._find_bundles_with_source(source_id)

            return SourceRemovalInfo(
                source_id=source_id,
                display_name=getattr(config, 'display_name', source_id),
                config_path=config_path,
                bundles=bundles
            )
        except Exception:
            return None

    def _find_bundles_with_source(self, source_id: str) -> List[str]:
        """Find all bundles containing the source."""
        import yaml

        try:
            with open(self._bundles_path, 'r') as f:
                data = yaml.safe_load(f)

            bundles = []
            for bundle_name, bundle_data in data.get('bundles', {}).items():
                if source_id in bundle_data.get('sources', []):
                    bundles.append(bundle_name)

            return bundles
        except Exception:
            return []


class BundleManagerUpdater:
    """Bundle updater using BundleManager."""

    def __init__(self, bundles_path: Path):
        self._bundles_path = bundles_path

    def remove_source_from_all_bundles(self, source_id: str) -> List[str]:
        """Remove source from all bundles it appears in."""
        from core.source_system.bundle_manager import BundleManager

        try:
            manager = BundleManager(str(self._bundles_path))
            return manager.remove_source_from_all_bundles(source_id)
        except Exception as e:
            raise CapcatError(
                f"Failed to update bundles for '{source_id}': {e}"
            ) from e