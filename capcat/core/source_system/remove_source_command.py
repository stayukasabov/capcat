"""
Base classes and implementations for the remove-source command.

Provides the command pattern foundation used by EnhancedRemoveCommand
and RemoveSourceService:
  - SourceRemovalInfo: value object describing a source to be removed
  - RemovalUserInterface: ABC for UI interactions (enables testability)
  - RemoveSourceCommand: orchestrates selection → confirmation → removal
  - RegistrySourceLister: queries SourceRegistry for available sources
  - RegistrySourceInfoProvider: builds SourceRemovalInfo from config files
  - FileSystemConfigRemover: deletes YAML config files from disk
  - BundleManagerUpdater: removes the source from bundles.yml
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

from capcat.core.logging_config import get_logger


# ---------------------------------------------------------------------------
# Value object
# ---------------------------------------------------------------------------

@dataclass
class SourceRemovalInfo:
    """Describes a source that is about to be removed.

    Attributes:
        source_id: Machine-readable source identifier (e.g. ``"hn"``).
        display_name: Human-readable name shown in the UI.
        config_path: Filesystem path to the source YAML config file.
        bundles: List of bundle names that include this source.
    """

    source_id: str
    display_name: str
    config_path: Optional[Path]
    bundles: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# UI interface (enables swapping real UI for mocks in tests)
# ---------------------------------------------------------------------------

class RemovalUserInterface(abc.ABC):
    """Abstract interface for all UI interactions during source removal.

    Concrete implementations live in removal_ui.py (questionary-based)
    and tests/fixtures (mock-based).
    """

    @abc.abstractmethod
    def select_sources_to_remove(
        self, sources: List[tuple]
    ) -> List[str]:
        """Prompt the user to select one or more sources.

        Args:
            sources: List of ``(source_id, display_name)`` tuples.

        Returns:
            List of selected source IDs.
        """

    @abc.abstractmethod
    def show_removal_summary(
        self, sources_info: List[SourceRemovalInfo]
    ) -> None:
        """Show a summary of what will be removed before confirming.

        Args:
            sources_info: Sources scheduled for removal.
        """

    @abc.abstractmethod
    def confirm_removal(
        self, sources_info: List[SourceRemovalInfo]
    ) -> bool:
        """Ask the user to confirm the removal.

        Args:
            sources_info: Sources scheduled for removal.

        Returns:
            ``True`` if the user confirmed, ``False`` to abort.
        """

    @abc.abstractmethod
    def show_success(self, message: str) -> None:
        """Display a success notification."""

    @abc.abstractmethod
    def show_error(self, message: str) -> None:
        """Display an error notification."""

    @abc.abstractmethod
    def show_info(self, message: str) -> None:
        """Display an informational message."""


# ---------------------------------------------------------------------------
# Dependency interfaces
# ---------------------------------------------------------------------------

class SourceLister(abc.ABC):
    """Returns the list of removable sources as (source_id, display_name) pairs."""

    @abc.abstractmethod
    def list_sources(self) -> List[tuple]:
        """Return ``[(source_id, display_name), ...]`` for every available source."""


class SourceInfoProvider(abc.ABC):
    """Builds SourceRemovalInfo objects for a list of source IDs."""

    @abc.abstractmethod
    def get_sources_info(
        self, source_ids: List[str]
    ) -> List[SourceRemovalInfo]:
        """Return removal metadata for each requested source_id.

        Args:
            source_ids: IDs returned by the UI selection step.

        Returns:
            One SourceRemovalInfo per valid source ID.
        """


class ConfigRemover(abc.ABC):
    """Deletes a source's config file from disk."""

    @abc.abstractmethod
    def remove_config(self, source_info: SourceRemovalInfo) -> None:
        """Remove the config file described by *source_info*.

        Args:
            source_info: Removal metadata including the config path.
        """


class BundleUpdater(abc.ABC):
    """Removes a source ID from all bundles in bundles.yml."""

    @abc.abstractmethod
    def remove_from_bundles(self, source_id: str) -> None:
        """Strip *source_id* from every bundle that contains it.

        Args:
            source_id: The source to remove from bundles.
        """


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class RemoveSourceCommand:
    """Orchestrates the interactive remove-source workflow.

    Steps:
      1. List available sources via *source_lister*.
      2. Let the user select via *ui*.
      3. Gather removal info via *source_info_provider*.
      4. Show summary and ask for confirmation via *ui*.
      5. Delete config via *config_remover*.
      6. Update bundles via *bundle_updater*.

    Args:
        source_lister: Provides ``[(source_id, display_name)]``.
        source_info_provider: Builds SourceRemovalInfo objects.
        ui: User-facing interaction layer.
        config_remover: Removes YAML config files.
        bundle_updater: Keeps bundles.yml consistent.
        logger: Optional logger; defaults to module logger.
    """

    def __init__(
        self,
        source_lister: SourceLister,
        source_info_provider: SourceInfoProvider,
        ui: RemovalUserInterface,
        config_remover: ConfigRemover,
        bundle_updater: BundleUpdater,
        logger: Optional[Any] = None,
    ) -> None:
        self._source_lister = source_lister
        self._source_info_provider = source_info_provider
        self._ui = ui
        self._config_remover = config_remover
        self._bundle_updater = bundle_updater
        self._logger = logger or get_logger(__name__)

    def execute(self) -> None:
        """Run the full interactive removal workflow."""
        sources = self._source_lister.list_sources()
        if not sources:
            self._ui.show_info("No removable sources found.")
            return

        selected_ids = self._ui.select_sources_to_remove(sources)
        if not selected_ids:
            self._ui.show_info("No sources selected — nothing removed.")
            return

        sources_info = self._source_info_provider.get_sources_info(selected_ids)
        self._ui.show_removal_summary(sources_info)

        if not self._ui.confirm_removal(sources_info):
            self._ui.show_info("Removal cancelled.")
            return

        for info in sources_info:
            try:
                self._config_remover.remove_config(info)
                self._bundle_updater.remove_from_bundles(info.source_id)
                self._ui.show_success(f"Removed {info.display_name}")
                self._logger.info("Removed source: %s", info.source_id)
            except Exception as exc:  # noqa: BLE001
                self._ui.show_error(
                    f"Failed to remove {info.display_name}: {exc}"
                )
                self._logger.error(
                    "Failed to remove source %s: %s", info.source_id, exc
                )

    def _remove_sources(self, sources_info: List["SourceRemovalInfo"]) -> None:
        """Remove a list of sources (config + bundles) without UI interaction.

        Used by EnhancedRemoveCommand after confirmation has been handled.

        Args:
            sources_info: Sources to remove.
        """
        for info in sources_info:
            try:
                self._config_remover.remove_config(info)
                self._bundle_updater.remove_from_bundles(info.source_id)
                self._logger.info("Removed source: %s", info.source_id)
            except Exception as exc:  # noqa: BLE001
                self._ui.show_error(
                    f"Failed to remove {info.display_name}: {exc}"
                )
                self._logger.error(
                    "Failed to remove source %s: %s", info.source_id, exc
                )

    def _refresh_registry(self) -> None:
        """Reset the global source registry so it reflects removed sources."""
        try:
            from capcat.core.source_system.source_registry import reset_source_registry
            reset_source_registry()
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Failed to refresh source registry: %s", exc)


# ---------------------------------------------------------------------------
# Registry-backed implementations
# ---------------------------------------------------------------------------

class RegistrySourceLister(SourceLister):
    """Lists sources via SourceRegistry — reads the live registry at call time."""

    def list_sources(self) -> List[tuple]:
        """Return ``[(source_id, display_name)]`` for every user-removable source.

        Builtin sources (shipped with the application) are excluded — they
        cannot be removed and would silently no-op if the removal were attempted.
        """
        from capcat.core.source_system.source_registry import SourceRegistry

        registry = SourceRegistry()
        registry.discover_sources()
        result = []
        for sid in sorted(registry.get_available_sources()):
            if registry.is_builtin_source(sid):
                continue
            cfg = registry.get_source_config(sid)
            name = cfg.display_name if cfg else sid
            result.append((sid, name))
        return result


class RegistrySourceInfoProvider(SourceInfoProvider):
    """Builds SourceRemovalInfo by inspecting config files and bundles.yml.

    Args:
        config_path: Directory containing per-source YAML config files.
        bundles_path: Path to bundles.yml.
    """

    def __init__(
        self, config_path: Path, bundles_path: Path
    ) -> None:
        self._config_path = config_path
        self._bundles_path = bundles_path

    def get_sources_info(
        self, source_ids: List[str]
    ) -> List[SourceRemovalInfo]:
        """Build SourceRemovalInfo for each source_id.

        Args:
            source_ids: IDs selected for removal.

        Returns:
            List of SourceRemovalInfo, one per valid ID.
        """
        bundles_map = self._load_bundles_map()
        result = []
        for sid in source_ids:
            config_file = self._config_path / f"{sid}.yaml"
            if not config_file.exists():
                config_file = None
            bundles = bundles_map.get(sid, [])
            result.append(
                SourceRemovalInfo(
                    source_id=sid,
                    display_name=sid.title(),
                    config_path=config_file,
                    bundles=bundles,
                )
            )
        return result

    def _load_bundles_map(self) -> dict:
        """Return ``{source_id: [bundle_name, ...]}`` from bundles.yml."""
        if not self._bundles_path.exists():
            return {}
        try:
            import yaml

            with open(self._bundles_path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            mapping: dict = {}
            for bundle_name, bundle_data in data.get("bundles", {}).items():
                for sid in bundle_data.get("sources", []):
                    mapping.setdefault(sid, []).append(bundle_name)
            return mapping
        except Exception:  # noqa: BLE001
            return {}


class FileSystemConfigRemover(ConfigRemover):
    """Deletes the YAML config file for a source from disk."""

    def remove_config(self, source_info: SourceRemovalInfo) -> None:
        """Delete the config file if it exists.

        Args:
            source_info: Contains the config_path to delete.
        """
        if source_info.config_path and source_info.config_path.exists():
            source_info.config_path.unlink()


class BundleManagerUpdater(BundleUpdater):
    """Removes a source from all entries in bundles.yml.

    Args:
        bundles_path: Path to bundles.yml.
    """

    def __init__(self, bundles_path: Path) -> None:
        self._bundles_path = bundles_path

    def remove_from_bundles(self, source_id: str) -> None:
        """Strip *source_id* from every bundle in bundles.yml.

        Args:
            source_id: Source to remove from all bundles.
        """
        if not self._bundles_path.exists():
            return
        try:
            import yaml

            with open(self._bundles_path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}

            changed = False
            for bundle_data in data.get("bundles", {}).values():
                sources = bundle_data.get("sources", [])
                if source_id in sources:
                    sources.remove(source_id)
                    changed = True

            if changed:
                with open(self._bundles_path, "w", encoding="utf-8") as fh:
                    yaml.dump(data, fh, default_flow_style=False)
        except Exception:  # noqa: BLE001
            pass
