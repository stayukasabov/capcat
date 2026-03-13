"""Test source registry discovers builtin and user sources."""
from pathlib import Path
from unittest.mock import patch

import pytest


def test_registry_imports():
    from capcat.core.source_system.source_registry import SourceRegistry

    assert SourceRegistry is not None


def test_registry_accepts_project_root(tmp_path):
    """Registry accepts project_root kwarg without error."""
    from capcat.core.source_system.source_registry import SourceRegistry

    registry = SourceRegistry(project_root=tmp_path)
    assert registry._project_root == tmp_path


def test_registry_discovers_from_builtin_path(tmp_path):
    """Registry discovers sources from the builtin package path."""
    from capcat.core.source_system.source_registry import SourceRegistry

    # Create a fake builtin config-driven source
    builtin_cfg = tmp_path / "builtin" / "config_driven" / "configs"
    builtin_cfg.mkdir(parents=True)
    (builtin_cfg / "testsite.yaml").write_text(
        "display_name: Test Site\n"
        "base_url: https://example.com\n"
        "article_selectors:\n  - 'a.headline'\n"
        "content_selectors:\n  - '.body'\n"
    )

    registry = SourceRegistry(project_root=tmp_path)
    # Patch the builtin path to our fake directory
    registry._builtin_path = tmp_path / "builtin"
    sources = registry.discover_sources()
    assert "testsite" in sources, "Builtin source not discovered"


def test_user_source_overrides_builtin(tmp_path):
    """User source with same ID as builtin takes precedence."""
    from capcat.core.source_system.source_registry import SourceRegistry

    # Create builtin source
    builtin_cfg = tmp_path / "builtin" / "config_driven" / "configs"
    builtin_cfg.mkdir(parents=True)
    (builtin_cfg / "hn.yaml").write_text(
        "display_name: HN Builtin\n"
        "base_url: https://news.ycombinator.com\n"
        "article_selectors:\n  - '.titleline a'\n"
        "content_selectors:\n  - '.article-content'\n"
    )

    # Create user source with same name
    user_cfg = (
        tmp_path / "Config" / "sources" / "active"
        / "config_driven" / "configs"
    )
    user_cfg.mkdir(parents=True)
    (user_cfg / "hn.yaml").write_text(
        "display_name: HN Override\n"
        "base_url: https://news.ycombinator.com\n"
        "article_selectors:\n  - '.titleline a'\n"
        "content_selectors:\n  - '.article-content'\n"
    )

    registry = SourceRegistry(project_root=tmp_path)
    registry._builtin_path = tmp_path / "builtin"
    sources = registry.discover_sources()
    hn = sources.get("hn")
    assert hn is not None
    assert "Override" in hn.display_name


def test_legacy_sources_dir_still_works(tmp_path):
    """Passing sources_dir directly still works (backward compat)."""
    from capcat.core.source_system.source_registry import SourceRegistry

    sources_active = tmp_path / "config_driven" / "configs"
    sources_active.mkdir(parents=True)
    (sources_active / "legacy.yaml").write_text(
        "display_name: Legacy Source\n"
        "base_url: https://legacy.example.com\n"
        "article_selectors:\n  - 'a'\n"
        "content_selectors:\n  - '.content'\n"
    )

    registry = SourceRegistry(sources_dir=str(tmp_path))
    sources = registry.discover_sources()
    assert "legacy" in sources
