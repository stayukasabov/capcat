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


from capcat.core.source_system.remove_source_service import RemoveSourceService


def test_remove_source_service_uses_userspace_path(project):
    """RemoveSourceService uses Config/sources/active/config_driven/configs/ as target."""
    svc = RemoveSourceService(project_root=project)
    expected = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    assert svc._config_path == expected


def test_remove_source_service_removes_manifest_entry(project):
    """Removing a source clears its manifest entry."""
    import hashlib, json
    config_dir = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    config_dir.mkdir(parents=True)
    (config_dir / "bbc.yaml").write_text("name: bbc\n")

    h = hashlib.sha256(b"name: bbc\n").hexdigest()
    manifest = {"config_driven/configs/bbc.yaml": {"builtin_hash": h, "user_hash": h}}
    (project / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

    svc = RemoveSourceService(project_root=project)
    svc._remove_manifest_entry("bbc.yaml")

    updated = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    assert "config_driven/configs/bbc.yaml" not in updated


def test_remove_manifest_entry_after_remove_cleans_stale_entries(project):
    """_remove_manifest_entry_after_remove removes entries for deleted config files."""
    config_dir = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    config_dir.mkdir(parents=True)
    (config_dir / "bbc.yaml").write_text("name: bbc\n")
    # hn.yaml does NOT exist on disk — stale entry

    manifest = {
        "config_driven/configs/bbc.yaml": {"builtin_hash": "aa", "user_hash": "bb"},
        "config_driven/configs/hn.yaml": {"builtin_hash": "cc", "user_hash": "dd"},
    }
    (project / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

    svc = RemoveSourceService(project_root=project)
    svc._remove_manifest_entry_after_remove()

    updated = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    assert "config_driven/configs/bbc.yaml" in updated    # present on disk → kept
    assert "config_driven/configs/hn.yaml" not in updated  # absent on disk → pruned


def test_add_source_service_uses_execute_return_value_not_mtime(tmp_path):
    """add_source() must pass the filename returned by execute() to _write_manifest_entry."""
    from unittest.mock import MagicMock, patch
    from capcat.core.source_system.add_source_service import AddSourceService

    written_file = tmp_path / "Config" / "sources" / "active" / "config_driven" / "configs" / "mynewsource.yaml"
    written_file.parent.mkdir(parents=True)
    written_file.write_text("source_id: mynewsource\n", encoding="utf-8")

    service = AddSourceService(project_root=tmp_path)
    recorded_filenames = []

    with patch.object(service, "_create_add_source_command") as mock_cmd_factory, \
         patch.object(service, "_write_manifest_entry", side_effect=lambda fn: recorded_filenames.append(fn)):
        mock_cmd = MagicMock()
        mock_cmd.execute.return_value = written_file
        mock_cmd_factory.return_value = mock_cmd
        service.add_source("https://example.com/feed.rss")

    assert recorded_filenames == ["mynewsource.yaml"]


def test_write_manifest_entry_after_add_is_gone():
    """_write_manifest_entry_after_add must not exist on AddSourceService."""
    from capcat.core.source_system.add_source_service import AddSourceService
    assert not hasattr(AddSourceService, "_write_manifest_entry_after_add")


def test_write_manifest_entry_tolerates_zero_byte_manifest(project):
    """_write_manifest_entry must not raise or lose data when manifest is zero-byte."""
    config_dir = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    config_dir.mkdir(parents=True)
    cfg = config_dir / "mysource.yaml"
    cfg.write_text("source_id: mysource\n", encoding="utf-8")

    manifest_path = project / ".capcat" / "source_hashes.json"
    manifest_path.write_bytes(b"")  # zero-byte file

    svc = AddSourceService(project_root=project)
    svc._write_manifest_entry("mysource.yaml")  # must not raise

    result = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "config_driven/configs/mysource.yaml" in result


def test_write_manifest_entry_tolerates_malformed_manifest(project):
    """_write_manifest_entry must not raise when manifest is malformed JSON."""
    config_dir = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    config_dir.mkdir(parents=True)
    cfg = config_dir / "mysource.yaml"
    cfg.write_text("source_id: mysource\n", encoding="utf-8")

    manifest_path = project / ".capcat" / "source_hashes.json"
    manifest_path.write_text("not json", encoding="utf-8")

    svc = AddSourceService(project_root=project)
    svc._write_manifest_entry("mysource.yaml")  # must not raise

    result = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "config_driven/configs/mysource.yaml" in result
