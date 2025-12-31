"""
Backup and restore functionality for source configurations.
Enables undo capability and safe removal operations.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json
import shutil

from core.logging_config import get_logger
from core.exceptions import CapcatError


@dataclass
class BackupMetadata:
    """Metadata about a backup operation."""
    backup_id: str
    timestamp: str
    sources: List[str]
    backup_dir: Path
    bundle_backup: Optional[Path] = None


class SourceBackupManager:
    """
    Manages backup and restore of source configurations.
    Supports undo functionality and safe deletions.
    """

    def __init__(self, backup_base_dir: Optional[Path] = None):
        """
        Initialize backup manager.

        Args:
            backup_base_dir: Base directory for backups (default: .capcat_backups)
        """
        if backup_base_dir is None:
            import cli
            app_root = Path(cli.__file__).parent
            backup_base_dir = app_root.parent / ".capcat_backups"

        self._backup_base_dir = Path(backup_base_dir)
        self._backup_base_dir.mkdir(parents=True, exist_ok=True)
        self._logger = get_logger(__name__)

    def create_backup(
        self,
        source_ids: List[str],
        config_paths: List[Path],
        bundles_path: Path
    ) -> BackupMetadata:
        """
        Create backup of sources before removal.

        Args:
            source_ids: List of source IDs being backed up
            config_paths: Paths to source config files
            bundles_path: Path to bundles.yml file

        Returns:
            BackupMetadata with backup information
        """
        # Generate backup ID with timestamp (including microseconds for uniqueness)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_id = f"removal_{timestamp}"
        backup_dir = self._backup_base_dir / backup_id

        try:
            backup_dir.mkdir(parents=True)

            # Backup each config file
            configs_backup_dir = backup_dir / "configs"
            configs_backup_dir.mkdir()

            for source_id, config_path in zip(source_ids, config_paths):
                if config_path.exists():
                    dest = configs_backup_dir / f"{source_id}.yml"
                    shutil.copy2(config_path, dest)
                    self._logger.info(f"Backed up {source_id} config to {dest}")

            # Backup bundles.yml
            bundle_backup = None
            if bundles_path.exists():
                bundle_backup = backup_dir / "bundles.yml"
                shutil.copy2(bundles_path, bundle_backup)
                self._logger.info(f"Backed up bundles.yml to {bundle_backup}")

            # Save metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now().isoformat(),
                sources=source_ids,
                backup_dir=backup_dir,
                bundle_backup=bundle_backup
            )

            self._save_metadata(metadata)
            self._logger.info(f"Backup created: {backup_id}")

            return metadata

        except Exception as e:
            self._logger.error(f"Failed to create backup: {e}")
            # Clean up partial backup
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            raise CapcatError(f"Failed to create backup: {e}") from e

    def restore_backup(
        self,
        backup_id: str,
        config_base_path: Path,
        bundles_path: Path
    ) -> List[str]:
        """
        Restore sources from a backup.

        Args:
            backup_id: ID of backup to restore
            config_base_path: Base path for config files
            bundles_path: Path to bundles.yml file

        Returns:
            List of restored source IDs
        """
        backup_dir = self._backup_base_dir / backup_id

        if not backup_dir.exists():
            raise CapcatError(f"Backup not found: {backup_id}")

        try:
            metadata = self._load_metadata(backup_dir)
            restored_sources = []

            # Restore config files
            configs_backup_dir = backup_dir / "configs"
            if configs_backup_dir.exists():
                for config_file in configs_backup_dir.glob("*.yml"):
                    source_id = config_file.stem
                    dest = config_base_path / config_file.name

                    shutil.copy2(config_file, dest)
                    restored_sources.append(source_id)
                    self._logger.info(f"Restored {source_id} config")

            # Restore bundles.yml if backed up
            bundle_backup = backup_dir / "bundles.yml"
            if bundle_backup.exists():
                shutil.copy2(bundle_backup, bundles_path)
                self._logger.info("Restored bundles.yml")

            self._logger.info(f"Restore completed: {len(restored_sources)} sources")
            return restored_sources

        except Exception as e:
            self._logger.error(f"Failed to restore backup: {e}")
            raise CapcatError(f"Failed to restore backup: {e}") from e

    def list_backups(self) -> List[BackupMetadata]:
        """
        List all available backups.

        Returns:
            List of BackupMetadata objects
        """
        backups = []

        for backup_dir in sorted(self._backup_base_dir.glob("removal_*")):
            try:
                metadata = self._load_metadata(backup_dir)
                backups.append(metadata)
            except Exception as e:
                self._logger.warning(f"Failed to load backup {backup_dir}: {e}")

        return backups

    def delete_backup(self, backup_id: str) -> None:
        """
        Delete a backup.

        Args:
            backup_id: ID of backup to delete
        """
        backup_dir = self._backup_base_dir / backup_id

        if not backup_dir.exists():
            raise CapcatError(f"Backup not found: {backup_id}")

        try:
            shutil.rmtree(backup_dir)
            self._logger.info(f"Deleted backup: {backup_id}")
        except Exception as e:
            raise CapcatError(f"Failed to delete backup: {e}") from e

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Delete old backups, keeping only the most recent ones.

        Args:
            keep_count: Number of recent backups to keep

        Returns:
            Number of backups deleted
        """
        backups = sorted(
            self._backup_base_dir.glob("removal_*"),
            key=lambda p: p.name,
            reverse=True
        )

        deleted_count = 0
        for backup_dir in backups[keep_count:]:
            try:
                shutil.rmtree(backup_dir)
                deleted_count += 1
                self._logger.info(f"Cleaned up old backup: {backup_dir.name}")
            except Exception as e:
                self._logger.warning(f"Failed to delete backup {backup_dir}: {e}")

        return deleted_count

    def _save_metadata(self, metadata: BackupMetadata) -> None:
        """Save backup metadata to JSON file."""
        metadata_file = metadata.backup_dir / "metadata.json"

        metadata_dict = {
            "backup_id": metadata.backup_id,
            "timestamp": metadata.timestamp,
            "sources": metadata.sources,
            "bundle_backup": str(metadata.bundle_backup) if metadata.bundle_backup else None
        }

        with open(metadata_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)

    def _load_metadata(self, backup_dir: Path) -> BackupMetadata:
        """Load backup metadata from JSON file."""
        metadata_file = backup_dir / "metadata.json"

        if not metadata_file.exists():
            # Fallback: infer from directory structure
            return BackupMetadata(
                backup_id=backup_dir.name,
                timestamp="unknown",
                sources=[],
                backup_dir=backup_dir
            )

        with open(metadata_file, 'r') as f:
            data = json.load(f)

        return BackupMetadata(
            backup_id=data["backup_id"],
            timestamp=data["timestamp"],
            sources=data["sources"],
            backup_dir=backup_dir,
            bundle_backup=Path(data["bundle_backup"]) if data.get("bundle_backup") else None
        )


class BackupStrategy:
    """Protocol for different backup strategies."""

    def should_backup(self, source_ids: List[str]) -> bool:
        """Determine if backup should be created."""
        raise NotImplementedError


class AlwaysBackupStrategy(BackupStrategy):
    """Always create backups."""

    def should_backup(self, source_ids: List[str]) -> bool:
        return True


class ConditionalBackupStrategy(BackupStrategy):
    """Backup only if conditions are met."""

    def __init__(self, min_sources: int = 1):
        self.min_sources = min_sources

    def should_backup(self, source_ids: List[str]) -> bool:
        return len(source_ids) >= self.min_sources


class NoBackupStrategy(BackupStrategy):
    """Never create backups (for testing or forced removal)."""

    def should_backup(self, source_ids: List[str]) -> bool:
        return False