"""Tests for add-source / remove-source userspace redirect and manifest integration."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from capcat.core.source_system.add_source_service import AddSourceService


@pytest.fixture
def project(tmp_path):
    (tmp_path / ".capcat").mkdir()
    return tmp_path


def test_add_source_service_writes_to_userspace(project):
    """AddSourceService uses Config/sources/active/config_driven/configs/ as target."""
    svc = AddSourceService(project_root=project)
    expected = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    assert svc._config_path == expected


def test_add_source_service_writes_manifest_entry(project, monkeypatch):
    """After writing a config file, manifest entry has builtin_hash: ''."""
    # Create the config dir and a fake file (simulating what AddSourceCommand does)
    config_dir = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    config_dir.mkdir(parents=True)
    fake_config = config_dir / "test-source.yaml"
    fake_config.write_text("name: test-source\n")

    svc = AddSourceService(project_root=project)
    svc._write_manifest_entry("test-source.yaml")

    manifest_path = project / ".capcat" / "source_hashes.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    key = "config_driven/configs/test-source.yaml"
    assert key in manifest
    assert manifest[key]["builtin_hash"] == ""
    assert len(manifest[key]["user_hash"]) == 64


def test_write_manifest_entry_after_add_picks_newest_file(project):
    """_write_manifest_entry_after_add writes manifest for the most recently touched file."""
    import time
    config_dir = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    config_dir.mkdir(parents=True)

    older = config_dir / "older.yaml"
    older.write_text("name: older\n")
    time.sleep(0.05)
    newer = config_dir / "newer.yaml"
    newer.write_text("name: newer\n")

    svc = AddSourceService(project_root=project)
    svc._write_manifest_entry_after_add()

    manifest_path = project / ".capcat" / "source_hashes.json"
    manifest = json.loads(manifest_path.read_text())
    assert "config_driven/configs/newer.yaml" in manifest
    assert "config_driven/configs/older.yaml" not in manifest
