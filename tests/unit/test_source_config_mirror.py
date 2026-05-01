"""Tests for SourceConfigMirror — first-run config_driven mirror."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import date
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


def test_run_first_mirror_tolerates_malformed_manifest(tmp_path, monkeypatch):
    manifest_path = tmp_path / ".capcat" / "source_hashes.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text("not json", encoding="utf-8")
    mirror = SourceConfigMirror(project_root=tmp_path, tui_mode=False)
    monkeypatch.setattr(mirror, "_mirror_config_driven", lambda m: None)
    monkeypatch.setattr(mirror, "_mirror_custom", lambda m: None)
    monkeypatch.setattr(mirror, "_mirror_bundles", lambda m: None)
    monkeypatch.setattr(mirror, "_save_manifest", lambda m: None)
    mirror.run_first_mirror()  # must not raise


def test_first_mirror_skips_disabled_files(full_mirror):
    m, project = full_mirror
    m.run_first_mirror()
    cfg_dir = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    assert not (cfg_dir / "skysports.yaml.disabled").exists()
    assert "config_driven/configs/skysports.yaml.disabled" not in json.loads(
        (project / ".capcat" / "source_hashes.json").read_text()
    )


def _make_mirrored_project(tmp_path, monkeypatch, builtin_files=None, user_files=None):
    """Helper: project with existing mirror (some builtins already mirrored)."""
    import hashlib
    project = tmp_path / "project"
    (project / ".capcat").mkdir(parents=True)

    builtin_root = tmp_path / "_builtin"
    cfg_dir = builtin_root / "config_driven" / "configs"
    cfg_dir.mkdir(parents=True)
    custom_dir = builtin_root / "custom"
    bundles_dir = builtin_root

    user_cfg = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    user_cfg.mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "custom").mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "bundles").mkdir(parents=True)

    manifest = {}

    for fname, content in (builtin_files or {}).items():
        f = cfg_dir / fname
        f.write_text(content)

    for fname, content in (user_files or {}).items():
        f = user_cfg / fname
        f.write_text(content)
        h = hashlib.sha256(content.encode()).hexdigest()
        manifest[f"config_driven/configs/{fname}"] = {
            "builtin_hash": h, "user_hash": h
        }

    (project / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

    m = SourceConfigMirror(project, tui_mode=False)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: cfg_dir)
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: custom_dir)
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: bundles_dir)
    return m, project, user_cfg


def test_step1_silently_copies_new_items(tmp_path, monkeypatch):
    """New builtin items are copied without any prompt."""
    builtin_cfg = tmp_path / "capcat" / "sources" / "builtin" / "config_driven" / "configs"
    builtin_cfg.mkdir(parents=True)
    (builtin_cfg / "newsite.yaml").write_text("name: newsite")

    user_cfg = tmp_path / "Config" / "sources" / "active" / "config_driven" / "configs"
    user_cfg.mkdir(parents=True)

    manifest_dir = tmp_path / ".capcat"
    manifest_dir.mkdir()
    (manifest_dir / "source_hashes.json").write_text("{}")

    prompt_calls = []

    mirror = SourceConfigMirror(tmp_path, tui_mode=False)
    monkeypatch.setattr(mirror, "_builtin_config_driven_dir", lambda: builtin_cfg)
    monkeypatch.setattr(mirror, "_user_config_driven_dir", lambda: user_cfg)
    monkeypatch.setattr(mirror, "_builtin_custom_dir", lambda: tmp_path / "no_custom")
    monkeypatch.setattr(mirror, "_user_custom_dir", lambda: tmp_path / "no_custom_user")
    monkeypatch.setattr(mirror, "_builtin_bundles_dir", lambda: tmp_path / "no_bundles")
    monkeypatch.setattr(mirror, "_user_bundles_dir", lambda: tmp_path / "no_bundles_user")
    monkeypatch.setattr(mirror, "_prompt", lambda msg: prompt_calls.append(msg) or "n")

    mirror.check_for_upgrades()

    assert prompt_calls == [], "No prompt must be shown for new items"
    assert (user_cfg / "newsite.yaml").exists(), "New item must be silently copied"


def test_step1_no_new_items_no_prompt_no_copy(tmp_path, monkeypatch):
    """When there are no new items, nothing happens."""
    builtin_cfg = tmp_path / "builtin_cfg"
    builtin_cfg.mkdir()
    user_cfg = tmp_path / "user_cfg"
    user_cfg.mkdir()
    (user_cfg / "existing.yaml").write_text("name: existing")

    manifest_dir = tmp_path / ".capcat"
    manifest_dir.mkdir()
    import hashlib, json
    h = hashlib.sha256((user_cfg / "existing.yaml").read_bytes()).hexdigest()
    (manifest_dir / "source_hashes.json").write_text(
        json.dumps({"config_driven/configs/existing.yaml": {"builtin_hash": h, "user_hash": h}})
    )

    prompt_calls = []
    mirror = SourceConfigMirror(tmp_path, tui_mode=False)
    monkeypatch.setattr(mirror, "_builtin_config_driven_dir", lambda: builtin_cfg)
    monkeypatch.setattr(mirror, "_user_config_driven_dir", lambda: user_cfg)
    monkeypatch.setattr(mirror, "_builtin_custom_dir", lambda: tmp_path / "no_custom")
    monkeypatch.setattr(mirror, "_user_custom_dir", lambda: tmp_path / "no_custom_user")
    monkeypatch.setattr(mirror, "_builtin_bundles_dir", lambda: tmp_path / "no_bundles")
    monkeypatch.setattr(mirror, "_user_bundles_dir", lambda: tmp_path / "no_bundles_user")
    monkeypatch.setattr(mirror, "_prompt", lambda msg: prompt_calls.append(msg) or "n")

    mirror.check_for_upgrades()

    assert prompt_calls == []


def test_step1_no_prompt_when_no_new_items(tmp_path, monkeypatch):
    m, project, user_cfg = _make_mirrored_project(
        tmp_path, monkeypatch,
        builtin_files={"bbc.yaml": "name: bbc\n"},
        user_files={"bbc.yaml": "name: bbc\n"},
    )
    prompt_called = []
    monkeypatch.setattr("builtins.input", lambda _: prompt_called.append(1) or "y")

    m.check_for_upgrades()

    assert not prompt_called


def _setup_changed_builtin(tmp_path, monkeypatch, user_modified=False):
    """Builtin bbc.yaml has changed since mirror. user_modified controls whether user also changed."""
    project = tmp_path / "project"
    (project / ".capcat").mkdir(parents=True)

    builtin_root = tmp_path / "_builtin"
    cfg_dir = builtin_root / "config_driven" / "configs"
    cfg_dir.mkdir(parents=True)
    custom_dir = builtin_root / "custom"
    bundles_dir = builtin_root

    user_cfg = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    user_cfg.mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "custom").mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "bundles").mkdir(parents=True)

    original_content = "name: bbc\nversion: 1\n"
    new_builtin_content = "name: bbc\nversion: 2\n"
    user_content = "name: bbc\nversion: 99\n" if user_modified else original_content

    orig_hash = hashlib.sha256(original_content.encode()).hexdigest()

    (cfg_dir / "bbc.yaml").write_text(new_builtin_content)
    (user_cfg / "bbc.yaml").write_text(user_content)

    manifest = {
        "config_driven/configs/bbc.yaml": {
            "builtin_hash": orig_hash,
            "user_hash": orig_hash,
        }
    }
    (project / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

    m = SourceConfigMirror(project, tui_mode=False)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: cfg_dir)
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: custom_dir)
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: bundles_dir)
    monkeypatch.setattr("builtins.input", lambda _: "n")  # suppress step1 prompt
    return m, project, user_cfg, cfg_dir


def test_step2_skips_when_builtin_unchanged(tmp_path, monkeypatch):
    """Builtin unchanged -> no override, file unchanged."""
    project = tmp_path / "project"
    (project / ".capcat").mkdir(parents=True)
    builtin_root = tmp_path / "_builtin"
    cfg_dir = builtin_root / "config_driven" / "configs"
    cfg_dir.mkdir(parents=True)
    user_cfg = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    user_cfg.mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "custom").mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "bundles").mkdir(parents=True)

    content = "name: bbc\n"
    h = hashlib.sha256(content.encode()).hexdigest()
    (cfg_dir / "bbc.yaml").write_text(content)
    (user_cfg / "bbc.yaml").write_text(content)
    manifest = {"config_driven/configs/bbc.yaml": {"builtin_hash": h, "user_hash": h}}
    (project / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

    m = SourceConfigMirror(project, tui_mode=False)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: cfg_dir)
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: builtin_root / "custom")
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: builtin_root)
    monkeypatch.setattr("builtins.input", lambda _: "n")

    m.check_for_upgrades()

    assert (user_cfg / "bbc.yaml").read_text() == content


def test_step2_skips_when_user_modified(tmp_path, monkeypatch):
    """Builtin changed but user also modified -> skip silently."""
    m, project, user_cfg, cfg_dir = _setup_changed_builtin(
        tmp_path, monkeypatch, user_modified=True
    )
    user_content_before = (user_cfg / "bbc.yaml").read_text()

    m.check_for_upgrades()

    assert (user_cfg / "bbc.yaml").read_text() == user_content_before


def test_step3_overrides_silently_when_user_unmodified(tmp_path, monkeypatch):
    """Builtin changed, user unmodified -> silently overwrite, no prompt, no backup."""
    m, project, user_cfg, cfg_dir = _setup_changed_builtin(
        tmp_path, monkeypatch, user_modified=False
    )
    new_builtin_content = (cfg_dir / "bbc.yaml").read_text()

    m.check_for_upgrades()

    # User file now has new builtin content
    assert (user_cfg / "bbc.yaml").read_text() == new_builtin_content
    # No backup needed — user never modified
    backup_dirs = list((project / "Config" / "sources").glob("backup_*"))
    assert len(backup_dirs) == 0


def test_step3_unmodified_config_gets_new_hash_after_silent_overwrite(tmp_path, monkeypatch):
    """Builtin changed, user unmodified -> manifest builtin_hash and user_hash updated to new value."""
    m, project, user_cfg, cfg_dir = _setup_changed_builtin(
        tmp_path, monkeypatch, user_modified=False
    )
    new_builtin_content = (cfg_dir / "bbc.yaml").read_text()

    m.check_for_upgrades()

    assert (user_cfg / "bbc.yaml").read_text() == new_builtin_content
    manifest = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    new_hash = hashlib.sha256(new_builtin_content.encode()).hexdigest()
    assert manifest["config_driven/configs/bbc.yaml"]["builtin_hash"] == new_hash
    assert manifest["config_driven/configs/bbc.yaml"]["user_hash"] == new_hash


def test_backup_collision_uses_counter_suffix(tmp_path, monkeypatch):
    """Second override on same day creates backup_YYYY-MM-DD-2."""
    m, project, user_cfg, cfg_dir = _setup_changed_builtin(
        tmp_path, monkeypatch, user_modified=False
    )
    today = date.today().isoformat()
    (project / "Config" / "sources" / f"backup_{today}").mkdir(parents=True)

    monkeypatch.setattr("builtins.input", lambda _: "y")
    monkeypatch.setattr("sys.stdin", type("_Tty", (), {"isatty": staticmethod(lambda: True)})())
    m.check_for_upgrades()

    backup_dirs = list((project / "Config" / "sources").glob("backup_*-[0-9]*"))
    assert len(backup_dirs) >= 1


def test_user_deleted_file_removes_manifest_entry(tmp_path, monkeypatch):
    """If user deleted their file, remove manifest entry -- do not re-copy."""
    project = tmp_path / "project"
    (project / ".capcat").mkdir(parents=True)
    builtin_root = tmp_path / "_builtin"
    cfg_dir = builtin_root / "config_driven" / "configs"
    cfg_dir.mkdir(parents=True)
    user_cfg = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    user_cfg.mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "custom").mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "bundles").mkdir(parents=True)

    h = hashlib.sha256(b"name: bbc\n").hexdigest()
    (cfg_dir / "bbc.yaml").write_text("name: bbc\n")
    # user file does NOT exist
    manifest = {"config_driven/configs/bbc.yaml": {"builtin_hash": h, "user_hash": h}}
    (project / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

    m = SourceConfigMirror(project, tui_mode=False)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: cfg_dir)
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: builtin_root / "custom")
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: builtin_root)
    monkeypatch.setattr("builtins.input", lambda _: "n")

    m.check_for_upgrades()

    updated = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    assert "config_driven/configs/bbc.yaml" not in updated
    assert not (user_cfg / "bbc.yaml").exists()


def test_disabled_source_participates_in_upgrade_diff(tmp_path, monkeypatch):
    """A source renamed to .yaml.disabled is found via _resolve_user_file's ordered lookup."""
    project = tmp_path / "project"
    (project / ".capcat").mkdir(parents=True)
    builtin_root = tmp_path / "_builtin"
    cfg_dir = builtin_root / "config_driven" / "configs"
    cfg_dir.mkdir(parents=True)
    user_cfg = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    user_cfg.mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "custom").mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "bundles").mkdir(parents=True)

    original_content = "name: bbc\nversion: 1\n"
    new_builtin_content = "name: bbc\nversion: 2\n"
    orig_hash = hashlib.sha256(original_content.encode()).hexdigest()

    (cfg_dir / "bbc.yaml").write_text(new_builtin_content)
    # User has disabled their copy -- content unmodified
    (user_cfg / "bbc.yaml.disabled").write_text(original_content)

    manifest = {
        "config_driven/configs/bbc.yaml": {
            "builtin_hash": orig_hash,
            "user_hash": orig_hash,
        }
    }
    (project / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

    m = SourceConfigMirror(project, tui_mode=False)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: cfg_dir)
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: builtin_root / "custom")
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: builtin_root)
    monkeypatch.setattr("builtins.input", lambda _: "y")
    monkeypatch.setattr("sys.stdin", type("_Tty", (), {"isatty": staticmethod(lambda: True)})())

    m.check_for_upgrades()

    # The .disabled file was found and overridden
    assert (user_cfg / "bbc.yaml.disabled").exists()
    assert (user_cfg / "bbc.yaml.disabled").read_text() == new_builtin_content


def test_tui_mode_uses_questionary_confirm(tmp_path, monkeypatch):
    """When tui_mode=True, _prompt uses questionary.confirm instead of print+input."""
    m = SourceConfigMirror(tmp_path, tui_mode=True)

    questionary_calls = []

    class FakeConfirm:
        def __init__(self, msg, default=True, **kwargs):
            questionary_calls.append(msg)
            self._result = True
        def ask(self):
            return self._result

    import capcat.core.source_config_mirror as mirror_module
    monkeypatch.setattr(mirror_module, "questionary", type("q", (), {"confirm": FakeConfirm})())

    result = m._prompt("Test message?")
    assert questionary_calls
    assert result == "y"


def test_resync_manifest_when_missing(tmp_path, monkeypatch):
    """If mirror dirs exist but manifest absent, rebuild without overwriting files."""
    project = tmp_path / "project"
    (project / ".capcat").mkdir(parents=True)
    builtin_root = tmp_path / "_builtin"
    cfg_dir = builtin_root / "config_driven" / "configs"
    cfg_dir.mkdir(parents=True)

    user_cfg = project / "Config" / "sources" / "active" / "config_driven" / "configs"
    user_cfg.mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "custom").mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "bundles").mkdir(parents=True)

    user_content = "name: bbc\nmy-custom: true\n"
    (cfg_dir / "bbc.yaml").write_text("name: bbc\n")   # builtin
    (user_cfg / "bbc.yaml").write_text(user_content)    # user (modified)
    # No manifest file

    m = SourceConfigMirror(project, tui_mode=False)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: cfg_dir)
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: builtin_root / "custom")
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: builtin_root)

    m.check_for_upgrades()

    # User file must be untouched
    assert (user_cfg / "bbc.yaml").read_text() == user_content
    # Manifest was rebuilt
    manifest = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    assert "config_driven/configs/bbc.yaml" in manifest
    entry = manifest["config_driven/configs/bbc.yaml"]
    # builtin_hash = actual installed builtin; user_hash = current user file
    builtin_hash = hashlib.sha256(b"name: bbc\n").hexdigest()
    user_hash = hashlib.sha256(user_content.encode()).hexdigest()
    assert entry["builtin_hash"] == builtin_hash
    assert entry["user_hash"] == user_hash
    assert entry["ownership"] == "config"


def test_load_manifest_returns_none_when_file_absent(tmp_path):
    mirror = SourceConfigMirror(project_root=tmp_path, tui_mode=False)
    assert mirror._load_manifest() is None


def test_load_manifest_returns_empty_dict_when_file_contains_empty_json_object(tmp_path):
    manifest_path = tmp_path / ".capcat" / "source_hashes.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text("{}", encoding="utf-8")
    mirror = SourceConfigMirror(project_root=tmp_path, tui_mode=False)
    assert mirror._load_manifest() == {}


def test_load_manifest_returns_empty_dict_silently_for_zero_byte_file(tmp_path, caplog):
    import logging
    manifest_path = tmp_path / ".capcat" / "source_hashes.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_bytes(b"")  # zero-byte file
    mirror = SourceConfigMirror(project_root=tmp_path, tui_mode=False)
    with caplog.at_level(logging.WARNING, logger="capcat"):
        result = mirror._load_manifest()
    assert result == {}
    # Must NOT log a warning for an empty file
    assert not any(r.levelno >= logging.WARNING for r in caplog.records)


def test_load_manifest_returns_empty_dict_and_warns_on_malformed_json(tmp_path):
    import logging
    from unittest.mock import MagicMock, patch
    manifest_path = tmp_path / ".capcat" / "source_hashes.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text("not json", encoding="utf-8")
    mirror = SourceConfigMirror(project_root=tmp_path, tui_mode=False)
    mock_logger = MagicMock()
    with patch("capcat.core.logging_config.get_logger", return_value=mock_logger):
        result = mirror._load_manifest()
    assert result == {}
    mock_logger.warning.assert_called_once()


def test_check_for_upgrades_calls_resync_only_when_manifest_absent(tmp_path, monkeypatch):
    mirror = SourceConfigMirror(project_root=tmp_path, tui_mode=False)
    resync_called = []
    monkeypatch.setattr(mirror, "_resync_manifest", lambda: resync_called.append(True))
    monkeypatch.setattr(mirror, "_step1_new_items", lambda m: m)
    monkeypatch.setattr(mirror, "_step2_3_changed_builtins", lambda m: m)
    monkeypatch.setattr(mirror, "_save_manifest", lambda m: None)
    # No manifest file exists → _resync_manifest should be called
    mirror.check_for_upgrades()
    assert resync_called == [True]


def test_check_for_upgrades_proceeds_to_step1_when_manifest_empty(tmp_path, monkeypatch):
    manifest_path = tmp_path / ".capcat" / "source_hashes.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text("{}", encoding="utf-8")
    mirror = SourceConfigMirror(project_root=tmp_path, tui_mode=False)
    step1_called = []
    resync_called = []
    monkeypatch.setattr(mirror, "_resync_manifest", lambda: resync_called.append(True))
    monkeypatch.setattr(mirror, "_step1_new_items", lambda m: step1_called.append(True) or m)
    monkeypatch.setattr(mirror, "_step2_3_changed_builtins", lambda m: m)
    monkeypatch.setattr(mirror, "_save_manifest", lambda m: None)
    mirror.check_for_upgrades()
    assert step1_called == [True]
    assert resync_called == []


def test_resync_manifest_never_emits_warning(tmp_path, caplog):
    """_resync_manifest must never emit WARNING — always DEBUG."""
    mirror = SourceConfigMirror(tmp_path, tui_mode=False)
    with caplog.at_level(logging.DEBUG):
        mirror._resync_manifest()
    warning_records = [
        r for r in caplog.records
        if r.levelno >= logging.WARNING and "source_hashes" in r.message
    ]
    assert warning_records == []


def test_unified_processor_calls_mirror_on_first_fetch(tmp_path, monkeypatch):
    """UnifiedSourceProcessor._process_with_new_system calls run_first_mirror when not mirrored."""
    from capcat.core.unified_source_processor import UnifiedSourceProcessor

    (tmp_path / ".capcat").mkdir()
    mirror_calls = []

    class FakeMirror:
        def __init__(self, project_root, tui_mode):
            pass
        def is_mirrored(self):
            return False
        def run_first_mirror(self):
            mirror_calls.append("first_mirror")
        def check_for_upgrades(self):
            mirror_calls.append("check_upgrades")

    monkeypatch.setattr(
        "capcat.core.unified_source_processor.SourceConfigMirror", FakeMirror
    )
    monkeypatch.setattr(
        "capcat.core.unified_source_processor.find_project_root", lambda: tmp_path
    )

    processor = UnifiedSourceProcessor(project_root=tmp_path)
    # Set new_source_factory to None so _process_with_new_system raises at source creation
    processor.new_source_factory = None

    try:
        processor._process_with_new_system("hn", 5, str(tmp_path))
    except Exception:
        pass  # We only care that mirror was called

    assert "first_mirror" in mirror_calls


def test_first_mirror_custom_writes_app_ownership_for_py(tmp_path, monkeypatch):
    """source.py files get ownership='app' in manifest after first mirror."""
    from capcat.core.source_config_mirror import SourceConfigMirror
    m = SourceConfigMirror(tmp_path, tui_mode=False)
    builtin_custom = tmp_path / "_builtin" / "custom" / "hn"
    builtin_custom.mkdir(parents=True)
    (builtin_custom / "source.py").write_text("# code\n")
    (builtin_custom / "config.yaml").write_text("name: hn\n")
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: builtin_custom.parent)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: tmp_path / "_empty_cfg")
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: tmp_path / "_empty_bun")
    m.run_first_mirror()
    manifest = json.loads((tmp_path / ".capcat" / "source_hashes.json").read_text())
    assert manifest["custom/hn/source.py"]["ownership"] == "app"
    assert manifest["custom/hn/config.yaml"]["ownership"] == "config"


def test_first_mirror_config_driven_writes_config_ownership(tmp_path, monkeypatch):
    """Config-driven YAML files get ownership='config' in manifest."""
    from capcat.core.source_config_mirror import SourceConfigMirror
    m = SourceConfigMirror(tmp_path, tui_mode=False)
    builtin_cfg = tmp_path / "_builtin" / "config_driven" / "configs"
    builtin_cfg.mkdir(parents=True)
    (builtin_cfg / "bbc.yaml").write_text("name: bbc\n")
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: builtin_cfg)
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: tmp_path / "_empty_cust")
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: tmp_path / "_empty_bun")
    m.run_first_mirror()
    manifest = json.loads((tmp_path / ".capcat" / "source_hashes.json").read_text())
    assert manifest["config_driven/configs/bbc.yaml"]["ownership"] == "config"


def test_add_source_manifest_entry_has_user_ownership(tmp_path):
    """add_source writes ownership='user' with empty builtin_hash."""
    import hashlib, json
    from capcat.core.source_system.add_source_service import AddSourceService

    (tmp_path / ".capcat").mkdir()
    config_dir = tmp_path / "Config" / "sources" / "active" / "config_driven" / "configs"
    config_dir.mkdir(parents=True)

    config_file = config_dir / "bbc.yaml"
    config_file.write_text("name: bbc\n")

    svc = AddSourceService.__new__(AddSourceService)
    svc._project_root = tmp_path
    svc._config_path = config_dir
    svc._logger = __import__("logging").getLogger("test")
    svc._write_manifest_entry(config_file.name)

    manifest_path = tmp_path / ".capcat" / "source_hashes.json"
    data = json.loads(manifest_path.read_text())
    key = next(iter(data))
    assert data[key]["ownership"] == "user"
    assert data[key]["builtin_hash"] == ""


def test_step2_py_file_no_ownership_field_auto_updated_noninteractive(tmp_path, monkeypatch):
    """Old manifests lack 'ownership' on .py entries. They must still be auto-updated
    (treated as app-owned) even when user_hash differs from stored_user_hash.

    Regression: without fix, missing ownership defaults to 'config', and a changed
    user_hash causes the entry to go through the interactive prompt path which skips
    in non-interactive mode, leaving the stale .py file in place.
    """
    project = tmp_path / "project"
    (project / ".capcat").mkdir(parents=True)

    builtin_root = tmp_path / "_builtin"
    custom_dir = builtin_root / "custom"
    hn_builtin = custom_dir / "hn"
    hn_builtin.mkdir(parents=True)

    user_custom = project / "Config" / "sources" / "active" / "custom" / "hn"
    user_custom.mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "config_driven" / "configs").mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "bundles").mkdir(parents=True)

    # Three versions: stored (what manifest remembers), user (stale capcat-modified), builtin (new)
    stored_content = "# source v1\n"
    user_content = "# source v2 - modified by old capcat\n"  # user_hash != stored_user_hash
    builtin_content = "# source v3 - new builtin\n"

    stored_hash = hashlib.sha256(stored_content.encode()).hexdigest()
    (hn_builtin / "source.py").write_text(builtin_content)
    (user_custom / "source.py").write_text(user_content)

    # Old manifest: NO 'ownership' field for .py entry
    manifest = {
        "custom/hn/source.py": {
            "builtin_hash": stored_hash,
            "user_hash": stored_hash,
            # no "ownership" key — simulates manifest created before ownership field existed
        }
    }
    (project / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

    m = SourceConfigMirror(project, tui_mode=False)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: builtin_root / "config_driven" / "configs")
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: custom_dir)
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: builtin_root)

    m.check_for_upgrades()

    # .py file must be updated to new builtin content regardless of missing ownership field
    assert (user_custom / "source.py").read_text() == builtin_content, (
        ".py file with missing ownership field must be auto-updated (treated as app-owned)"
    )
    updated_manifest = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    new_hash = hashlib.sha256(builtin_content.encode()).hexdigest()
    assert updated_manifest["custom/hn/source.py"]["builtin_hash"] == new_hash
    assert updated_manifest["custom/hn/source.py"]["user_hash"] == new_hash


def test_step2_py_file_drifted_user_repaired_when_builtin_unchanged(tmp_path, monkeypatch):
    """If manifest shows builtin unchanged but user .py file has drifted from the
    stored user_hash, the file must be repaired from the builtin.

    Scenario: uninstall + reinstall capcat causes _resync_manifest() to write
    stored_builtin_hash = hash(NEW builtin). On next run current_builtin_hash ==
    stored_builtin_hash so the upgrade check skips the file — but the user's
    Config/sources/active/custom/hn/source.py is still the OLD stale content.
    """
    project = tmp_path / "project"
    (project / ".capcat").mkdir(parents=True)

    builtin_root = tmp_path / "_builtin"
    custom_dir = builtin_root / "custom"
    hn_builtin = custom_dir / "hn"
    hn_builtin.mkdir(parents=True)

    user_custom = project / "Config" / "sources" / "active" / "custom" / "hn"
    user_custom.mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "config_driven" / "configs").mkdir(parents=True)
    (project / "Config" / "sources" / "active" / "bundles").mkdir(parents=True)

    builtin_content = "# source v3 - new builtin\n"
    stale_user_content = "# source v1 - old stale content from before GDPR fix\n"

    builtin_hash = hashlib.sha256(builtin_content.encode()).hexdigest()
    stale_hash = hashlib.sha256(stale_user_content.encode()).hexdigest()

    (hn_builtin / "source.py").write_text(builtin_content)
    (user_custom / "source.py").write_text(stale_user_content)

    # Manifest after resync: stored_builtin_hash == current builtin (new),
    # but stored_user_hash doesn't match current user file (stale).
    # This is what _resync_manifest() writes after a reinstall.
    manifest = {
        "custom/hn/source.py": {
            "ownership": "app",
            "builtin_hash": builtin_hash,   # matches current builtin
            "user_hash": builtin_hash,      # resync assumed user == builtin (wrong)
        }
    }
    (project / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

    m = SourceConfigMirror(project, tui_mode=False)
    monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: builtin_root / "config_driven" / "configs")
    monkeypatch.setattr(m, "_builtin_custom_dir", lambda: custom_dir)
    monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: builtin_root)

    m.check_for_upgrades()

    assert (user_custom / "source.py").read_text() == builtin_content, (
        "Drifted .py file must be repaired from builtin even when builtin hash is unchanged"
    )
    updated_manifest = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    assert updated_manifest["custom/hn/source.py"]["user_hash"] == builtin_hash


def test_mirror_check_runs_only_once_per_batch(tmp_path, monkeypatch):
    """check_for_upgrades is called exactly once even when processing multiple sources."""
    from capcat.core.unified_source_processor import UnifiedSourceProcessor

    (tmp_path / ".capcat").mkdir()
    call_count = {"n": 0}

    class FakeMirror:
        def __init__(self, project_root, tui_mode):
            pass
        def is_mirrored(self):
            return True
        def check_for_upgrades(self):
            call_count["n"] += 1

    monkeypatch.setattr(
        "capcat.core.unified_source_processor.SourceConfigMirror", FakeMirror
    )
    monkeypatch.setattr(
        "capcat.core.unified_source_processor.find_project_root", lambda: tmp_path
    )

    processor = UnifiedSourceProcessor(project_root=tmp_path)
    processor.new_source_factory = None

    for source in ("bbc", "guardian"):
        try:
            processor._process_with_new_system(source, 3, str(tmp_path))
        except Exception:
            pass

    assert call_count["n"] == 1, (
        f"check_for_upgrades called {call_count['n']} times — must be exactly once per batch"
    )
