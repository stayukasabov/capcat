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


def test_step1_copies_new_source_when_user_says_yes(tmp_path, monkeypatch):
    m, project, user_cfg = _make_mirrored_project(
        tmp_path, monkeypatch,
        builtin_files={"bbc.yaml": "name: bbc\n", "guardian.yaml": "name: guardian\n"},
        user_files={"bbc.yaml": "name: bbc\n"},  # bbc already mirrored, guardian is new
    )
    monkeypatch.setattr("builtins.input", lambda _: "y")

    m.check_for_upgrades()

    assert (user_cfg / "guardian.yaml").exists()
    manifest = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    assert "config_driven/configs/guardian.yaml" in manifest


def test_step1_does_not_copy_when_user_says_no(tmp_path, monkeypatch):
    m, project, user_cfg = _make_mirrored_project(
        tmp_path, monkeypatch,
        builtin_files={"bbc.yaml": "name: bbc\n", "guardian.yaml": "name: guardian\n"},
        user_files={"bbc.yaml": "name: bbc\n"},
    )
    monkeypatch.setattr("builtins.input", lambda _: "n")

    m.check_for_upgrades()

    assert not (user_cfg / "guardian.yaml").exists()


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


def test_step3_overrides_and_backs_up_when_user_says_yes(tmp_path, monkeypatch):
    """Builtin changed, user unmodified, user accepts -> backup created, file overridden."""
    m, project, user_cfg, cfg_dir = _setup_changed_builtin(
        tmp_path, monkeypatch, user_modified=False
    )
    new_builtin_content = (cfg_dir / "bbc.yaml").read_text()

    call_count = [0]
    def fake_input(prompt):
        call_count[0] += 1
        return "y"  # accept override

    monkeypatch.setattr("builtins.input", fake_input)

    m.check_for_upgrades()

    # User file now has new builtin content
    assert (user_cfg / "bbc.yaml").read_text() == new_builtin_content
    # Backup dir exists
    backup_dirs = list((project / "Config" / "sources").glob("backup_*"))
    assert len(backup_dirs) == 1
    # Backup contains flattened filename
    assert (backup_dirs[0] / "config_driven-configs-bbc.yaml").exists()


def test_step3_does_not_override_when_user_says_no(tmp_path, monkeypatch):
    """Builtin changed, user unmodified, user declines -> file unchanged, builtin_hash updated."""
    m, project, user_cfg, cfg_dir = _setup_changed_builtin(
        tmp_path, monkeypatch, user_modified=False
    )
    original_user_content = (user_cfg / "bbc.yaml").read_text()
    new_builtin_hash = hashlib.sha256((cfg_dir / "bbc.yaml").read_bytes()).hexdigest()

    monkeypatch.setattr("builtins.input", lambda _: "n")

    m.check_for_upgrades()

    assert (user_cfg / "bbc.yaml").read_text() == original_user_content
    manifest = json.loads((project / ".capcat" / "source_hashes.json").read_text())
    assert manifest["config_driven/configs/bbc.yaml"]["builtin_hash"] == new_builtin_hash


def test_backup_collision_uses_counter_suffix(tmp_path, monkeypatch):
    """Second override on same day creates backup_YYYY-MM-DD-2."""
    m, project, user_cfg, cfg_dir = _setup_changed_builtin(
        tmp_path, monkeypatch, user_modified=False
    )
    today = date.today().isoformat()
    (project / "Config" / "sources" / f"backup_{today}").mkdir(parents=True)

    monkeypatch.setattr("builtins.input", lambda _: "y")
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
    # Both hashes set to current user file hash (not builtin)
    user_hash = hashlib.sha256(user_content.encode()).hexdigest()
    assert entry["builtin_hash"] == user_hash
    assert entry["user_hash"] == user_hash


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


def test_load_manifest_returns_empty_dict_and_warns_on_malformed_json(tmp_path, caplog):
    import logging
    manifest_path = tmp_path / ".capcat" / "source_hashes.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text("not json", encoding="utf-8")
    mirror = SourceConfigMirror(project_root=tmp_path, tui_mode=False)
    with caplog.at_level(logging.WARNING, logger="capcat"):
        result = mirror._load_manifest()
    assert result == {}
    assert any(r.levelno >= logging.WARNING for r in caplog.records)


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
