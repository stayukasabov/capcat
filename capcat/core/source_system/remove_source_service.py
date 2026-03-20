"""
Service layer for remove-source command.
Provides clean integration with CLI while maintaining separation of concerns.
"""

import json
from pathlib import Path
from typing import Optional

from capcat.core.source_system.remove_source_command import (
    RemoveSourceCommand,
    RegistrySourceLister,
    RegistrySourceInfoProvider,
    FileSystemConfigRemover,
    BundleManagerUpdater
)
from capcat.core.source_system.removal_ui import QuestionaryRemovalUI
from capcat.core.logging_config import get_logger


class RemoveSourceService:
    """
    Service for removing existing sources.
    Provides high-level interface for CLI integration.
    """

    def __init__(self, base_path: Optional[Path] = None, project_root: Optional[Path] = None):
        """
        Initialize the remove-source service.

        Args:
            base_path: Optional base path for the application
            project_root: Optional project root for userspace redirect
        """
        if project_root is not None:
            self._project_root = project_root
            self._config_path = (
                project_root / "Config" / "sources" / "active" / "config_driven" / "configs"
            )
            self._bundles_path = (
                project_root / "Config" / "sources" / "active" / "bundles" / "bundles.yml"
            )
        else:
            if base_path is None:
                # capcat package root: capcat/core/source_system/ → up 3 levels → capcat/
                base_path = Path(__file__).parent.parent.parent
            self._project_root = None
            builtin = base_path / "sources" / "builtin"
            self._config_path = builtin / "config_driven" / "configs"
            self._bundles_path = builtin / "bundles.yml"

        self._base_path = base_path
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
        self._remove_manifest_entry_after_remove()

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

    def _remove_manifest_entry(self, filename: str) -> None:
        """Remove a manifest entry after successful source removal."""
        if self._project_root is None:
            return
        key = f"config_driven/configs/{filename}"
        manifest_path = self._project_root / ".capcat" / "source_hashes.json"
        if not manifest_path.exists():
            return
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.pop(key, None)
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        except Exception as exc:
            self._logger.warning(f"Failed to update manifest after remove: {exc}")

    def _remove_manifest_entry_after_remove(self) -> None:
        """Remove manifest entries for config files that no longer exist on disk."""
        if self._project_root is None:
            return
        manifest_path = self._project_root / ".capcat" / "source_hashes.json"
        if not manifest_path.exists():
            return
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self._logger.warning(f"Failed to read manifest: {exc}")
            return
        changed = False
        for key in list(manifest.keys()):
            if key.startswith("config_driven/configs/"):
                filename = key.split("/")[-1]
                if not (self._config_path / filename).exists():
                    manifest.pop(key)
                    changed = True
        if changed:
            try:
                manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            except Exception as exc:
                self._logger.warning(f"Failed to write manifest after remove: {exc}")


def create_remove_source_service() -> RemoveSourceService:
    """Factory: creates RemoveSourceService with project_root when inside a capcat project."""
    try:
        from capcat.core.config import find_project_root
        project_root = find_project_root()
        return RemoveSourceService(project_root=project_root)
    except Exception as exc:
        get_logger(__name__).debug(f"No project root, using builtin path: {exc}")
        return RemoveSourceService()
