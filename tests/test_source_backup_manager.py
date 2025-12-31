"""
Comprehensive tests for SourceBackupManager.
"""

import pytest
from pathlib import Path
import json
import shutil

from core.source_system.source_backup_manager import (
    SourceBackupManager,
    BackupMetadata,
    AlwaysBackupStrategy,
    NoBackupStrategy
)
from core.exceptions import CapcatError


class TestSourceBackupManager:
    """Test backup manager functionality."""

    @pytest.fixture
    def temp_backup_dir(self, tmp_path):
        """Create temporary backup directory."""
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        return backup_dir

    @pytest.fixture
    def test_configs(self, tmp_path):
        """Create test configuration files."""
        configs_dir = tmp_path / "configs"
        configs_dir.mkdir()

        test1 = configs_dir / "test1.yml"
        test1.write_text("display_name: Test 1\ncategory: tech")

        test2 = configs_dir / "test2.yml"
        test2.write_text("display_name: Test 2\ncategory: news")

        return [test1, test2]

    @pytest.fixture
    def test_bundles(self, tmp_path):
        """Create test bundles file."""
        bundles = tmp_path / "bundles.yml"
        bundles.write_text("bundles:\n  tech:\n    sources: [test1, test2]")
        return bundles

    def test_create_backup(self, temp_backup_dir, test_configs, test_bundles):
        """Test creating a backup."""
        manager = SourceBackupManager(temp_backup_dir)

        metadata = manager.create_backup(
            ["test1", "test2"],
            test_configs,
            test_bundles
        )

        assert metadata.backup_id.startswith("removal_")
        assert metadata.sources == ["test1", "test2"]
        assert metadata.backup_dir.exists()

        # Verify backup contents
        assert (metadata.backup_dir / "configs" / "test1.yml").exists()
        assert (metadata.backup_dir / "configs" / "test2.yml").exists()
        assert (metadata.backup_dir / "bundles.yml").exists()
        assert (metadata.backup_dir / "metadata.json").exists()

    def test_backup_metadata_saved(self, temp_backup_dir, test_configs, test_bundles):
        """Test that metadata is correctly saved."""
        manager = SourceBackupManager(temp_backup_dir)

        metadata = manager.create_backup(
            ["test1"],
            [test_configs[0]],
            test_bundles
        )

        # Load and verify metadata
        metadata_file = metadata.backup_dir / "metadata.json"
        with open(metadata_file) as f:
            data = json.load(f)

        assert data["backup_id"] == metadata.backup_id
        assert data["sources"] == ["test1"]
        assert "timestamp" in data

    def test_restore_backup(self, temp_backup_dir, test_configs, test_bundles, tmp_path):
        """Test restoring from backup."""
        manager = SourceBackupManager(temp_backup_dir)

        # Create backup
        metadata = manager.create_backup(
            ["test1", "test2"],
            test_configs,
            test_bundles
        )

        # Restore to new location
        restore_dir = tmp_path / "restored"
        restore_dir.mkdir()

        restored = manager.restore_backup(
            metadata.backup_id,
            restore_dir,
            tmp_path / "bundles_restored.yml"
        )

        assert restored == ["test1", "test2"]
        assert (restore_dir / "test1.yml").exists()
        assert (restore_dir / "test2.yml").exists()
        assert (tmp_path / "bundles_restored.yml").exists()

    def test_list_backups(self, temp_backup_dir, test_configs, test_bundles):
        """Test listing all backups."""
        manager = SourceBackupManager(temp_backup_dir)

        # Create multiple backups
        metadata1 = manager.create_backup(["test1"], [test_configs[0]], test_bundles)
        metadata2 = manager.create_backup(["test2"], [test_configs[1]], test_bundles)

        # List backups
        backups = manager.list_backups()

        assert len(backups) == 2
        backup_ids = [b.backup_id for b in backups]
        assert metadata1.backup_id in backup_ids
        assert metadata2.backup_id in backup_ids

    def test_delete_backup(self, temp_backup_dir, test_configs, test_bundles):
        """Test deleting a backup."""
        manager = SourceBackupManager(temp_backup_dir)

        metadata = manager.create_backup(["test1"], [test_configs[0]], test_bundles)

        assert metadata.backup_dir.exists()

        manager.delete_backup(metadata.backup_id)

        assert not metadata.backup_dir.exists()

    def test_cleanup_old_backups(self, temp_backup_dir, test_configs, test_bundles):
        """Test cleaning up old backups."""
        manager = SourceBackupManager(temp_backup_dir)

        # Create 5 backups
        for i in range(5):
            manager.create_backup([f"test{i}"], [test_configs[0]], test_bundles)

        # Keep only 2
        deleted_count = manager.cleanup_old_backups(keep_count=2)

        assert deleted_count == 3
        assert len(manager.list_backups()) == 2

    def test_backup_nonexistent_file(self, temp_backup_dir, tmp_path, test_bundles):
        """Test backup with nonexistent config file."""
        manager = SourceBackupManager(temp_backup_dir)

        nonexistent = tmp_path / "nonexistent.yml"

        metadata = manager.create_backup(
            ["nonexistent"],
            [nonexistent],
            test_bundles
        )

        # Backup should succeed but not include the missing file
        assert metadata.backup_dir.exists()
        assert not (metadata.backup_dir / "configs" / "nonexistent.yml").exists()

    def test_restore_nonexistent_backup(self, temp_backup_dir, tmp_path):
        """Test restoring a backup that doesn't exist."""
        manager = SourceBackupManager(temp_backup_dir)

        with pytest.raises(CapcatError, match="Backup not found"):
            manager.restore_backup("nonexistent_id", tmp_path, tmp_path / "bundles.yml")


class TestBackupStrategies:
    """Test backup strategy patterns."""

    def test_always_backup_strategy(self):
        """Test AlwaysBackupStrategy."""
        strategy = AlwaysBackupStrategy()

        assert strategy.should_backup([]) is True
        assert strategy.should_backup(["test"]) is True
        assert strategy.should_backup(["test1", "test2"]) is True

    def test_no_backup_strategy(self):
        """Test NoBackupStrategy."""
        strategy = NoBackupStrategy()

        assert strategy.should_backup([]) is False
        assert strategy.should_backup(["test"]) is False
        assert strategy.should_backup(["test1", "test2"]) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.source_system.source_backup_manager'])