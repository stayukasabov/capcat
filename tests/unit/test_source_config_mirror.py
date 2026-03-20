"""Tests for SourceConfigMirror — first-run config_driven mirror."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from capcat.core.source_config_mirror import SourceConfigMirror


@pytest.fixture
def fake_project(tmp_path):
    """A minimal fake project: .capcat/ exists, no Config/sources/active/ yet."""
    (tmp_path / ".capcat").mkdir()
    return tmp_path


@pytest.fixture
def mirror(fake_project, monkeypatch):
    """SourceConfigMirror pointed at fake_project, with monkeypatched builtin dirs."""
    m = SourceConfigMirror(fake_project, tui_mode=False)
    # Point builtin config_driven dir at a temp dir we control
    builtin = fake_project / "_builtin" / "config_driven" / "configs"
    builtin.mkdir(parents=True)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: builtin)
    return m, fake_project, builtin


def test_is_mirrored_false_when_dirs_absent(mirror):
    m, project, _ = mirror
    assert m.is_mirrored() is False


def test_is_mirrored_true_when_config_driven_dir_exists(mirror):
    m, project, _ = mirror
    (project / "Config" / "sources" / "active" / "config_driven" / "configs").mkdir(
        parents=True
    )
    assert m.is_mirrored() is True


def test_first_mirror_copies_yaml_files(mirror):
    m, project, builtin = mirror
    (builtin / "bbc.yaml").write_text("name: bbc\n")
    (builtin / "mashable.yml").write_text("name: mashable\n")
    (builtin / "skysports.yaml.disabled").write_text("name: skysports\n")

    m.run_first_mirror()

    user_dir = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    assert (user_dir / "bbc.yaml").exists()
    assert (user_dir / "mashable.yml").exists()
    # .disabled must NOT be copied
    assert not (user_dir / "skysports.yaml.disabled").exists()


def test_first_mirror_writes_manifest(mirror):
    m, project, builtin = mirror
    (builtin / "bbc.yaml").write_text("name: bbc\n")

    m.run_first_mirror()

    manifest_path = project / ".capcat" / "source_hashes.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert "config_driven/configs/bbc.yaml" in manifest
    entry = manifest["config_driven/configs/bbc.yaml"]
    assert entry["builtin_hash"] == entry["user_hash"]
    assert len(entry["builtin_hash"]) == 64  # sha256 hex


def test_compute_hash_returns_sha256_hex(mirror):
    m, project, builtin = mirror
    f = builtin / "test.yaml"
    f.write_text("hello")
    expected = hashlib.sha256(b"hello").hexdigest()
    assert m._compute_hash(f) == expected


@pytest.fixture
def full_mirror(tmp_path, monkeypatch):
    """Mirror with all three builtin domain dirs populated."""
    project = tmp_path / "project"
    (project / ".capcat").mkdir(parents=True)

    builtin_root = tmp_path / "_builtin"
    cfg_dir = builtin_root / "config_driven" / "configs"
    cfg_dir.mkdir(parents=True)
    custom_dir = builtin_root / "custom"
    (custom_dir / "hn").mkdir(parents=True)
    bundles_dir = builtin_root  # bundles are at builtin root

    (cfg_dir / "bbc.yaml").write_text("name: bbc\n")
    (cfg_dir / "skysports.yaml.disabled").write_text("name: skysports\n")
    (custom_dir / "hn" / "config.yaml").write_text("name: hn\n")
    (custom_dir / "hn" / "source.py").write_text("# hn source\n")
    (bundles_dir / "bundles.yml").write_text("bundles: {}\n")

    m = SourceConfigMirror(project, tui_mode=False)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: cfg_dir)
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: custom_dir)
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: bundles_dir)
    return m, project


def test_first_mirror_copies_custom_dir(full_mirror):
    m, project = full_mirror
    m.run_first_mirror()
    user_hn = project / "Config" / "sources" / "active" / "custom" / "hn"
    assert (user_hn / "config.yaml").exists()
    assert (user_hn / "source.py").exists()


def test_first_mirror_custom_manifest_entries(full_mirror):
    m, project = full_mirror
    m.run_first_mirror()
    manifest = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    assert "custom/hn/config.yaml" in manifest
    assert "custom/hn/source.py" in manifest
    entry = manifest["custom/hn/config.yaml"]
    assert entry["builtin_hash"] == entry["user_hash"]


def test_first_mirror_copies_bundles(full_mirror):
    m, project = full_mirror
    m.run_first_mirror()
    user_bundles = project / "Config" / "sources" / "active" / "bundles"
    assert (user_bundles / "bundles.yml").exists()


def test_first_mirror_bundles_manifest_entry(full_mirror):
    m, project = full_mirror
    m.run_first_mirror()
    manifest = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    assert "bundles/bundles.yml" in manifest


def test_first_mirror_skips_disabled_files(full_mirror):
    m, project = full_mirror
    m.run_first_mirror()
    cfg_dir = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    assert not (cfg_dir / "skysports.yaml.disabled").exists()
    assert "config_driven/configs/skysports.yaml.disabled" not in json.loads(
        (project / ".capcat" / "source_hashes.json").read_text()
    )
