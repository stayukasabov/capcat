"""Tests for user themes copy on capcat init and upgrade detection."""
from __future__ import annotations
import shutil
from pathlib import Path

import pytest

from capcat.commands.init import init_project


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
