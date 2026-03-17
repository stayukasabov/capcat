"""Tests for user themes copy on capcat init and upgrade detection."""
from __future__ import annotations
from pathlib import Path

import pytest

from capcat.commands.init import init_project
from capcat.core.config import check_theme_upgrade


# ---------------------------------------------------------------------------
# init_project: theme copy
# ---------------------------------------------------------------------------

def test_init_copies_base_css(tmp_path):
    init_project(tmp_path)
    assert (tmp_path / "Config" / "themes" / "base.css").exists()


def test_init_copies_design_system_css(tmp_path):
    init_project(tmp_path)
    assert (tmp_path / "Config" / "themes" / "design-system.css").exists()


def test_init_copies_space_grotesk_fonts(tmp_path):
    init_project(tmp_path)
    font_dir = tmp_path / "Config" / "themes" / "Space-Grotesk"
    assert font_dir.is_dir()
    assert any(f.suffix in (".woff", ".woff2") for f in font_dir.iterdir())


def test_init_writes_version_marker(tmp_path):
    from capcat import __version__
    init_project(tmp_path)
    marker = tmp_path / "Config" / "themes" / ".capcat-version"
    assert marker.exists()
    assert marker.read_text().strip() == __version__


def test_reinit_does_not_touch_themes(tmp_path):
    init_project(tmp_path)
    css = tmp_path / "Config" / "themes" / "base.css"
    css.write_text("/* custom */")
    init_project(tmp_path, reinit=True)
    assert css.read_text() == "/* custom */"


# ---------------------------------------------------------------------------
# check_theme_upgrade
# ---------------------------------------------------------------------------

def test_upgrade_no_op_when_version_matches(tmp_path, monkeypatch):
    """No prompt when version marker matches current package version."""
    from capcat import __version__
    themes = tmp_path / "Config" / "themes"
    themes.mkdir(parents=True)
    (themes / ".capcat-version").write_text(__version__ + "\n")
    called = []
    monkeypatch.setattr("builtins.input", lambda _: called.append(True) or "y")
    check_theme_upgrade(tmp_path)
    assert not called


def test_upgrade_prompts_on_version_mismatch(tmp_path, monkeypatch):
    """Prompt shown when marker version differs from package version."""
    themes = tmp_path / "Config" / "themes"
    themes.mkdir(parents=True)
    (themes / ".capcat-version").write_text("0.0.1\n")
    called = []
    monkeypatch.setattr("builtins.input", lambda _: (called.append(True), "n")[1])
    check_theme_upgrade(tmp_path)
    assert called


def test_upgrade_prompts_when_marker_absent(tmp_path, monkeypatch):
    """Prompt shown when .capcat-version is missing (interrupted init)."""
    themes = tmp_path / "Config" / "themes"
    themes.mkdir(parents=True)
    called = []
    monkeypatch.setattr("builtins.input", lambda _: (called.append(True), "n")[1])
    check_theme_upgrade(tmp_path)
    assert called


def test_upgrade_no_op_when_themes_dir_absent(tmp_path):
    """Silent no-op when Config/themes/ does not exist (uninitialised project)."""
    check_theme_upgrade(tmp_path)  # must not raise


def test_upgrade_y_recopies_files(tmp_path, monkeypatch):
    """Y answer overwrites user themes with package copy."""
    init_project(tmp_path)
    (tmp_path / "Config" / "themes" / ".capcat-version").write_text("0.0.1\n")
    css = tmp_path / "Config" / "themes" / "base.css"
    css.write_text("/* old */")
    monkeypatch.setattr("builtins.input", lambda _: "y")
    check_theme_upgrade(tmp_path)
    assert "/* old */" not in css.read_text()


def test_upgrade_n_preserves_user_files(tmp_path, monkeypatch):
    """N answer leaves user theme files untouched."""
    init_project(tmp_path)
    (tmp_path / "Config" / "themes" / ".capcat-version").write_text("0.0.1\n")
    css = tmp_path / "Config" / "themes" / "base.css"
    css.write_text("/* custom */")
    monkeypatch.setattr("builtins.input", lambda _: "n")
    check_theme_upgrade(tmp_path)
    assert css.read_text() == "/* custom */"


def test_upgrade_n_updates_version_marker(tmp_path, monkeypatch):
    """N answer still writes new version marker to suppress re-prompt."""
    from capcat import __version__
    init_project(tmp_path)
    (tmp_path / "Config" / "themes" / ".capcat-version").write_text("0.0.1\n")
    monkeypatch.setattr("builtins.input", lambda _: "n")
    check_theme_upgrade(tmp_path)
    marker = tmp_path / "Config" / "themes" / ".capcat-version"
    assert marker.read_text().strip() == __version__
