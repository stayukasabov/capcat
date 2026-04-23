"""TDD for capcat init command."""
from __future__ import annotations
from pathlib import Path
import pytest


def test_init_creates_capcat_dir(project_dir: Path):
    from capcat.commands.init import init_project
    init_project(project_dir)
    assert (project_dir / ".capcat").is_dir()


def test_init_creates_config_dir(project_dir: Path):
    from capcat.commands.init import init_project
    init_project(project_dir)
    assert (project_dir / "Config").is_dir()
    assert (project_dir / "Config" / "themes").is_dir()
    assert not (project_dir / "Config" / "capcat.yml").exists()


def test_init_does_not_create_source_dirs(project_dir: Path):
    """Source dirs are owned by SourceConfigMirror, not init_project.
    Pre-creating them causes is_mirrored() to return True on first fetch,
    skipping run_first_mirror() and leaving the vault with no YAMLs (B6)."""
    from capcat.commands.init import init_project
    init_project(project_dir)
    sources_active = project_dir / "Config" / "sources" / "active"
    assert not sources_active.exists()


def test_init_creates_gitignore(project_dir: Path):
    from capcat.commands.init import init_project
    init_project(project_dir)
    gitignore = project_dir / ".gitignore"
    assert gitignore.is_file()
    content = gitignore.read_text()
    assert "News/" in content
    assert "Capcats/" in content
    assert ".capcat/" in content


def test_init_appends_to_existing_gitignore(project_dir: Path):
    from capcat.commands.init import init_project
    gitignore = project_dir / ".gitignore"
    gitignore.write_text("node_modules/\n")
    init_project(project_dir)
    content = gitignore.read_text()
    assert "node_modules/" in content
    assert "News/" in content


def test_init_fails_if_already_initialized(project_dir: Path):
    from capcat.commands.init import init_project, AlreadyInitializedError
    init_project(project_dir)
    with pytest.raises(AlreadyInitializedError):
        init_project(project_dir)


def test_reinit_resets_capcat_dir_only(project_dir: Path):
    from capcat.commands.init import init_project
    init_project(project_dir)
    user_file = project_dir / "Config" / "themes" / "base.css"
    original = user_file.read_text()
    user_file.write_text("/* custom */\n")
    init_project(project_dir, reinit=True)
    assert (project_dir / ".capcat").is_dir()
    # reinit must not touch Config/
    assert user_file.read_text() == "/* custom */\n"
