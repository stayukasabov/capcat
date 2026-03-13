"""Test project-model path resolution."""
from pathlib import Path
import pytest


def test_find_project_root_from_cwd(project_dir: Path) -> None:
    from capcat.core.config import find_project_root
    (project_dir / ".capcat").mkdir()
    result = find_project_root(start=project_dir)
    assert result == project_dir


def test_find_project_root_from_subdir(project_dir: Path) -> None:
    from capcat.core.config import find_project_root
    (project_dir / ".capcat").mkdir()
    subdir = project_dir / "deep" / "nested"
    subdir.mkdir(parents=True)
    result = find_project_root(start=subdir)
    assert result == project_dir


def test_find_project_root_raises_outside_project(project_dir: Path) -> None:
    from capcat.core.config import find_project_root, NoProjectError
    with pytest.raises(NoProjectError):
        find_project_root(start=project_dir)


def test_news_dir_auto_created(project_dir: Path) -> None:
    from capcat.core.config import get_news_dir
    (project_dir / ".capcat").mkdir()
    news = get_news_dir(project_root=project_dir)
    assert news.is_dir()


def test_capcats_dir_auto_created(project_dir: Path) -> None:
    from capcat.core.config import get_capcats_dir
    (project_dir / ".capcat").mkdir()
    capcats = get_capcats_dir(project_root=project_dir)
    assert capcats.is_dir()
