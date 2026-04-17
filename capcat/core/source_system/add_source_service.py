"""
Service layer for the add-source command.
Provides a clean interface for CLI integration while maintaining separation of concerns.
"""

import hashlib
import json
from pathlib import Path
from typing import Optional

from capcat.core.source_system.add_source_command import (
    AddSourceCommand,
    RssFeedIntrospectorFactory,
    SourceConfigGeneratorAdapter,
    SubprocessSourceTester,
    RegistryCategoryProvider
)
from capcat.core.source_system.questionary_ui import QuestionaryUserInterface
from capcat.core.source_system.bundle_manager import BundleManager
from capcat.core.source_system.source_config_generator import SourceConfigGenerator
from capcat.core.logging_config import get_logger


class AddSourceService:
    """
    Service for adding new RSS sources.
    Provides a clean, high-level interface for CLI integration.
    """

    def __init__(self, base_path: Optional[Path] = None, project_root: Optional[Path] = None):
        """
        Args:
            project_root: Project root (preferred). When provided, writes to
                Config/sources/active/config_driven/configs/.
            base_path: Legacy fallback (package root). Ignored when project_root is set.
        """
        if project_root is not None:
            self._project_root = project_root
            self._config_path = (
                project_root / "Config" / "sources" / "active" / "config_driven" / "configs"
            )
            self._bundles_path = (
                project_root / "Config" / "sources" / "active" / "bundles" / "bundles.yml"
            )
            self._config_path.mkdir(parents=True, exist_ok=True)
            self._bundles_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            if base_path is None:
                base_path = Path(__file__).parent.parent.parent
            self._project_root = None
            builtin = base_path / "sources" / "builtin"
            self._config_path = builtin / "config_driven" / "configs"
            self._bundles_path = builtin / "bundles.yml"

        self._base_path = base_path
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
        config_file = command.execute(url)
        self._write_manifest_entry(config_file.name)

    def _write_manifest_entry(self, filename: str) -> None:
        """Write a manifest entry with builtin_hash='' for a user-added source."""
        if self._project_root is None:
            return
        config_file = self._config_path / filename
        if not config_file.exists():
            return
        user_hash = hashlib.sha256(config_file.read_bytes()).hexdigest()
        key = f"config_driven/configs/{filename}"
        manifest_path = self._project_root / ".capcat" / "source_hashes.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {}
        if manifest_path.exists():
            content = manifest_path.read_text(encoding="utf-8").strip()
            if content:
                try:
                    manifest = json.loads(content)
                except json.JSONDecodeError as exc:
                    self._logger.warning(f"Failed to read manifest, starting fresh: {exc}")
        manifest[key] = {"ownership": "user", "builtin_hash": "", "user_hash": user_hash}
        try:
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        except OSError as exc:
            self._logger.warning(f"Failed to write manifest entry for {filename}: {exc}")

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
    """Factory: creates AddSourceService with project_root when inside a capcat project."""
    try:
        from capcat.core.config import find_project_root
        project_root = find_project_root()
        return AddSourceService(project_root=project_root)
    except Exception as exc:
        get_logger(__name__).debug(f"No project root, using builtin path: {exc}")
        return AddSourceService()