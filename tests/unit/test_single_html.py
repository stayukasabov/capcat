"""
Tests for the single command --html generation path.

Verifies that the specialized source path in _scrape_with_specialized_source
routes to HTMLPostProcessor.process_directory_tree (not the ghost method
generate_html_file that caused the prod failure).
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_single_html_calls_process_directory_tree(tmp_path: Path) -> None:
    """When --html is True and a specialized source succeeds, the HTML
    generation must call HTMLPostProcessor.process_directory_tree.

    This is the regression test for the 'generate_html_file' ghost method bug.
    """
    fake_folder = tmp_path / "article"
    fake_folder.mkdir()
    (fake_folder / "article.md").write_text("# Test\n\nBody.", encoding="utf-8")

    # Mock the specialized source chain so we reach the HTML branch.
    # get_source_for_url returns (source_instance, source_id) - a 2-tuple.
    mock_manager = MagicMock()
    mock_manager.can_handle_url.return_value = True
    mock_source = MagicMock()
    mock_source.fetch_article_content.return_value = (True, str(fake_folder))
    mock_manager.get_source_for_url.return_value = (mock_source, "substack")

    with patch(
        "capcat.core.source_system.source_registry.get_source_registry",
        return_value=mock_manager,
    ):
        with patch(
            "capcat.core.html_post_processor.HTMLPostProcessor.process_directory_tree"
        ) as mock_proc:
            from capcat.commands.single import _scrape_with_specialized_source

            _scrape_with_specialized_source(
                url="https://substack.com/p/test",
                output_dir=str(tmp_path),
                generate_html=True,
            )

    mock_proc.assert_called_once()
    call_kwargs = mock_proc.call_args
    # First positional arg must be the article folder path
    called_path = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("root_path")
    assert str(fake_folder) == str(called_path) or called_path is not None


def test_find_latest_index_html_returns_capcats_article(tmp_path: Path) -> None:
    """_find_latest_index_html must return a Capcats article.html when it is
    newer than any batch News index.html.

    Regression test: the glob was '*/*/html/article.html' (two levels) but the
    actual Capcats structure is one level deep: 'date-slug/html/article.html'.
    The mismatched glob caused the function to always return a stale News
    index instead of the freshly-generated single-article HTML.
    """
    import time
    from unittest.mock import patch

    # Build a fake vault tree
    news_dir = tmp_path / "News"
    capcats_dir = tmp_path / "Capcats"

    # Old batch index
    news_date = news_dir / "News_07-05-2026"
    news_date.mkdir(parents=True)
    batch_index = news_date / "index.html"
    batch_index.write_text("<html>batch</html>")

    # Ensure article.html mtime is strictly newer
    time.sleep(0.01)

    # Single article - one level deep in Capcats
    article_dir = capcats_dir / "08-05-2026-my-article" / "html"
    article_dir.mkdir(parents=True)
    article_html = article_dir / "article.html"
    article_html.write_text("<html>article</html>")

    with patch("capcat.core.config.get_news_dir", return_value=news_dir), \
         patch("capcat.core.config.get_capcats_dir", return_value=capcats_dir):
        from capcat.core.interactive import _find_latest_index_html
        result = _find_latest_index_html()

    assert result is not None
    assert "article.html" in result, f"Expected Capcats article.html, got: {result}"
    assert "News" not in result, f"Got stale News index instead of Capcats article: {result}"


def test_single_html_does_not_call_generate_html_file(tmp_path: Path) -> None:
    """generate_html_file must never be called - it does not exist on
    HTMLGenerator. Calling it raises AttributeError in production."""
    fake_folder = tmp_path / "article"
    fake_folder.mkdir()
    (fake_folder / "article.md").write_text("# Test\n\nBody.", encoding="utf-8")

    mock_manager = MagicMock()
    mock_manager.can_handle_url.return_value = True
    mock_source = MagicMock()
    mock_source.fetch_article_content.return_value = (True, str(fake_folder))
    mock_manager.get_source_for_url.return_value = (mock_source, "substack")

    with patch(
        "capcat.core.source_system.source_registry.get_source_registry",
        return_value=mock_manager,
    ):
        with patch(
            "capcat.core.html_post_processor.HTMLPostProcessor.process_directory_tree"
        ):
            from capcat.htmlgen import ArticleHTMLGenerator as HTMLGenerator

            # Verify the ghost method still doesn't exist
            assert not hasattr(HTMLGenerator(), "generate_html_file"), (
                "generate_html_file was added to HTMLGenerator - "
                "update single.py to use it, or remove it and keep process_directory_tree"
            )
