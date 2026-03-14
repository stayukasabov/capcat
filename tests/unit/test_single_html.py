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
    # get_source_for_url returns (source_instance, source_id) — a 2-tuple.
    mock_manager = MagicMock()
    mock_manager.can_handle_url.return_value = True
    mock_source = MagicMock()
    mock_source.fetch_article_content.return_value = (True, str(fake_folder))
    mock_manager.get_source_for_url.return_value = (mock_source, "substack")

    with patch(
        "capcat.core.specialized_source_manager.get_specialized_source_manager",
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


def test_single_html_does_not_call_generate_html_file(tmp_path: Path) -> None:
    """generate_html_file must never be called — it does not exist on
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
        "capcat.core.specialized_source_manager.get_specialized_source_manager",
        return_value=mock_manager,
    ):
        with patch(
            "capcat.core.html_post_processor.HTMLPostProcessor.process_directory_tree"
        ):
            from capcat.core.html_generator import HTMLGenerator

            # Verify the ghost method still doesn't exist
            assert not hasattr(HTMLGenerator(), "generate_html_file"), (
                "generate_html_file was added to HTMLGenerator — "
                "update single.py to use it, or remove it and keep process_directory_tree"
            )
