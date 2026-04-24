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


def test_init_does_not_copy_font_folders(tmp_path):
    init_project(tmp_path)
    themes_dir = tmp_path / "Config" / "themes"
    font_dirs = [p for p in themes_dir.iterdir() if p.is_dir()]
    assert font_dirs == [], f"No font folders should be copied; found: {font_dirs}"


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
    monkeypatch.setattr("sys.stdin", type("_Tty", (), {"isatty": staticmethod(lambda: True)})())
    check_theme_upgrade(tmp_path)
    assert called


def test_upgrade_prompts_when_marker_absent(tmp_path, monkeypatch):
    """Prompt shown when .capcat-version is missing (interrupted init)."""
    themes = tmp_path / "Config" / "themes"
    themes.mkdir(parents=True)
    called = []
    monkeypatch.setattr("builtins.input", lambda _: (called.append(True), "n")[1])
    monkeypatch.setattr("sys.stdin", type("_Tty", (), {"isatty": staticmethod(lambda: True)})())
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
    monkeypatch.setattr("sys.stdin", type("_Tty", (), {"isatty": staticmethod(lambda: True)})())
    check_theme_upgrade(tmp_path)
    assert "/* old */" not in css.read_text()


def test_upgrade_n_preserves_user_files(tmp_path, monkeypatch):
    """N answer leaves user theme files untouched."""
    init_project(tmp_path)
    (tmp_path / "Config" / "themes" / ".capcat-version").write_text("0.0.1\n")
    css = tmp_path / "Config" / "themes" / "base.css"
    css.write_text("/* custom */")
    monkeypatch.setattr("builtins.input", lambda _: "n")
    monkeypatch.setattr("sys.stdin", type("_Tty", (), {"isatty": staticmethod(lambda: True)})())
    check_theme_upgrade(tmp_path)
    assert css.read_text() == "/* custom */"


def test_upgrade_n_updates_version_marker(tmp_path, monkeypatch):
    """N answer still writes new version marker to suppress re-prompt."""
    from capcat import __version__
    init_project(tmp_path)
    (tmp_path / "Config" / "themes" / ".capcat-version").write_text("0.0.1\n")
    monkeypatch.setattr("builtins.input", lambda _: "n")
    monkeypatch.setattr("sys.stdin", type("_Tty", (), {"isatty": staticmethod(lambda: True)})())
    check_theme_upgrade(tmp_path)
    marker = tmp_path / "Config" / "themes" / ".capcat-version"
    assert marker.read_text().strip() == __version__


# ---------------------------------------------------------------------------
# HTMLGenerator: user themes priority
# ---------------------------------------------------------------------------

from pathlib import Path as _Path
from capcat.htmlgen import ArticleHTMLGenerator as HTMLGenerator
from capcat.core.config import NoProjectError


def test_generator_embeds_user_base_css(tmp_path, monkeypatch):
    """Generator reads base.css from Config/themes/ when present."""
    themes = tmp_path / "Config" / "themes"
    themes.mkdir(parents=True)
    (themes / "base.css").write_text("/* user-base */")

    import capcat.htmlgen.generator as hg
    monkeypatch.setattr(hg, "find_project_root", lambda: tmp_path)

    gen = HTMLGenerator()
    result = gen._get_embedded_css(_Path(tmp_path))
    assert "/* user-base */" in result


def test_generator_falls_back_to_package_base_css(monkeypatch):
    """Generator falls back to package base.css when no project root found."""
    import capcat.htmlgen.generator as hg

    def _raise_no_project():
        raise NoProjectError("no project")

    monkeypatch.setattr(hg, "find_project_root", _raise_no_project)

    gen = HTMLGenerator()
    result = gen._get_embedded_css(_Path("."))
    assert result  # non-empty — package CSS loaded
    assert "user-base" not in result


def test_generator_per_file_fallback(tmp_path, monkeypatch):
    """If Config/themes/base.css absent but dir exists, falls back to package."""
    themes = tmp_path / "Config" / "themes"
    themes.mkdir(parents=True)
    # dir exists but base.css not present

    import capcat.htmlgen.generator as hg
    monkeypatch.setattr(hg, "find_project_root", lambda: tmp_path)

    gen = HTMLGenerator()
    result = gen._get_embedded_css(_Path(tmp_path))
    assert result  # fell back to package


def test_design_system_compiler_uses_user_dir(tmp_path, monkeypatch):
    """HTMLGenerator passes user themes_dir to DesignSystemCompiler when present."""
    themes = tmp_path / "Config" / "themes"
    themes.mkdir(parents=True)
    (themes / "design-system.css").write_text(":root { --color-accent: pink; }")

    import capcat.htmlgen.generator as hg
    monkeypatch.setattr(hg, "find_project_root", lambda: tmp_path)

    gen = HTMLGenerator()
    assert gen.design_system_compiler.themes_dir == themes


# ---------------------------------------------------------------------------
# TemplateRenderer: user themes priority (article pages)
# ---------------------------------------------------------------------------

from capcat.core.template_renderer import TemplateRenderer


def test_template_renderer_embeds_user_base_css(tmp_path, monkeypatch):
    """TemplateRenderer reads base.css from Config/themes/ when present."""
    themes = tmp_path / "Config" / "themes"
    themes.mkdir(parents=True)
    (themes / "base.css").write_text("/* user-article-base */")

    import capcat.core.template_renderer as tr
    monkeypatch.setattr(tr, "find_project_root", lambda: tmp_path)

    renderer = TemplateRenderer()
    assets = renderer._get_embedded_assets()
    assert "/* user-article-base */" in assets["embedded_styles"]


def test_template_renderer_falls_back_to_package(monkeypatch):
    """TemplateRenderer falls back to package base.css when no project root."""
    import capcat.core.template_renderer as tr

    def _raise_no_project():
        raise NoProjectError("no project")

    monkeypatch.setattr(tr, "find_project_root", _raise_no_project)

    renderer = TemplateRenderer()
    assets = renderer._get_embedded_assets()
    assert assets["embedded_styles"]  # non-empty
    assert "user-article-base" not in assets["embedded_styles"]
