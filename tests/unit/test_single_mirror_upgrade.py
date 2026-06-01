"""Regression: scrape_single_article must run mirror upgrade before URL routing.

Without the upgrade check, a user's outdated Config/sources/active/custom/twitter/source.py
(with old substring-match logic) overrides the fixed installed version and causes
stayux.com to be misrouted to TwitterSource, producing "X.com post" instead of scraping.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch


def test_scrape_single_article_runs_mirror_upgrade_before_registry(tmp_path):
    """Mirror check_for_upgrades must be called before get_source_registry in single path."""
    call_order = []

    mock_mirror_instance = MagicMock()
    mock_mirror_instance.is_mirrored.return_value = True
    mock_mirror_instance.check_for_upgrades.side_effect = lambda: call_order.append("upgrade")

    mock_registry = MagicMock()
    mock_registry.can_handle_url.side_effect = lambda url: (
        call_order.append("registry") or False
    )

    mock_fetcher_instance = MagicMock()
    mock_fetcher_instance.fetch_article_content.return_value = (False, "", None)

    # Patch at source module paths - works for lazy `from X import Y` inside functions
    with (
        patch("capcat.commands.single.SourceConfigMirror", return_value=mock_mirror_instance),
        patch("capcat.commands.single.MIRROR_AVAILABLE", True),
        patch("capcat.core.source_system.source_registry.get_source_registry", return_value=mock_registry),
        patch("capcat.core.source_system.source_registry.reset_source_registry"),
        patch("capcat.core.config.find_project_root", return_value=tmp_path),
        patch("capcat.core.tui_context.is_tui_active", return_value=False),
        patch("capcat.core.source_config.detect_source", return_value=None),
        patch("capcat.core.article_fetcher.ArticleFetcher.fetch_article_content",
              return_value=(False, "", None)),
        patch("capcat.core.session_pool.get_global_session", return_value=MagicMock()),
    ):
        from capcat.commands.single import scrape_single_article
        scrape_single_article("https://stayux.com/works/capcat-cli/", str(tmp_path))

    assert "upgrade" in call_order, "check_for_upgrades was not called"
    assert "registry" in call_order, "get_source_registry().can_handle_url was not called"
    upgrade_idx = call_order.index("upgrade")
    registry_idx = call_order.index("registry")
    assert upgrade_idx < registry_idx, (
        f"mirror upgrade (pos {upgrade_idx}) must happen before registry lookup (pos {registry_idx})"
    )


def test_reset_registry_called_after_mirror_upgrade(tmp_path):
    """reset_source_registry must be called after mirror check so updated files are reloaded."""
    reset_called = []

    mock_mirror_instance = MagicMock()
    mock_mirror_instance.is_mirrored.return_value = True

    mock_registry = MagicMock()
    mock_registry.can_handle_url.return_value = False

    mock_fetcher_instance = MagicMock()
    mock_fetcher_instance.fetch_article_content.return_value = (False, "", None)

    with (
        patch("capcat.commands.single.SourceConfigMirror", return_value=mock_mirror_instance),
        patch("capcat.commands.single.MIRROR_AVAILABLE", True),
        patch("capcat.core.source_system.source_registry.get_source_registry", return_value=mock_registry),
        patch(
            "capcat.core.source_system.source_registry.reset_source_registry",
            side_effect=lambda: reset_called.append(True),
        ),
        patch("capcat.core.config.find_project_root", return_value=tmp_path),
        patch("capcat.core.tui_context.is_tui_active", return_value=False),
        patch("capcat.core.source_config.detect_source", return_value=None),
        patch("capcat.core.article_fetcher.ArticleFetcher.fetch_article_content",
              return_value=(False, "", None)),
        patch("capcat.core.session_pool.get_global_session", return_value=MagicMock()),
    ):
        from capcat.commands.single import scrape_single_article
        scrape_single_article("https://stayux.com/works/capcat-cli/", str(tmp_path))

    assert reset_called, "reset_source_registry was not called after mirror upgrade"
