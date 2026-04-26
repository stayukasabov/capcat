"""Tests for _rename_to_dated helper in commands/single.py."""
from __future__ import annotations
from pathlib import Path

import pytest

from capcat.commands.single import _rename_to_dated, _scrape_with_specialized_source, scrape_single_article


def test_rename_adds_date_prefix(tmp_path):
    """Should prepend DD-MM-YYYY- to folder name when not already present."""
    folder = tmp_path / "My-Article"
    folder.mkdir()
    result = _rename_to_dated(str(folder), "26-04-2026")
    assert Path(result).name == "26-04-2026-My-Article"
    assert Path(result).exists()
    assert not folder.exists()


def test_rename_returns_new_path_string(tmp_path):
    """Should return absolute path string of renamed folder."""
    folder = tmp_path / "Some-Title"
    folder.mkdir()
    result = _rename_to_dated(str(folder), "01-01-2026")
    assert result == str(tmp_path / "01-01-2026-Some-Title")
    assert isinstance(result, str)


def test_rename_idempotent_when_already_dated(tmp_path):
    """Should return original path unchanged when folder already has date prefix."""
    folder = tmp_path / "26-04-2026-My-Article"
    folder.mkdir()
    result = _rename_to_dated(str(folder), "26-04-2026")
    assert result == str(folder)
    assert folder.exists()


def test_rename_preserves_folder_contents(tmp_path):
    """Should preserve all files and subdirectories during rename."""
    folder = tmp_path / "Article-Title"
    folder.mkdir()
    (folder / "article.md").write_text("# content")
    (folder / "images").mkdir()
    (folder / "images" / "photo.jpg").write_text("fake image")

    result = _rename_to_dated(str(folder), "26-04-2026")
    new_folder = Path(result)

    assert (new_folder / "article.md").exists()
    assert (new_folder / "article.md").read_text() == "# content"
    assert (new_folder / "images").is_dir()
    assert (new_folder / "images" / "photo.jpg").exists()


def test_rename_works_with_hyphenated_folder_names(tmp_path):
    """Should handle folder names that already contain hyphens."""
    folder = tmp_path / "Multi-Word-Article-Title"
    folder.mkdir()
    result = _rename_to_dated(str(folder), "15-12-2025")
    assert Path(result).name == "15-12-2025-Multi-Word-Article-Title"


def test_rename_handles_different_date_formats(tmp_path):
    """Should work with various DD-MM-YYYY date strings."""
    folder = tmp_path / "Test-Article"
    folder.mkdir()

    # Test single digits
    result1 = _rename_to_dated(str(folder), "01-01-2026")
    assert "01-01-2026-Test-Article" in result1

    # Reset for next test
    Path(result1).rename(folder)

    # Test double digits
    result2 = _rename_to_dated(str(folder), "31-12-2026")
    assert "31-12-2026-Test-Article" in result2


def test_rename_idempotent_with_different_date_prefix(tmp_path):
    """Should only be idempotent when exact date prefix matches."""
    folder = tmp_path / "01-01-2026-My-Article"
    folder.mkdir()

    # Different date should still rename
    result = _rename_to_dated(str(folder), "02-02-2026")
    assert Path(result).name == "02-02-2026-01-01-2026-My-Article"
    assert Path(result).exists()
    assert not folder.exists()


def test_rename_empty_folder_name_edge_case(tmp_path):
    """Should handle edge case where folder has empty name components."""
    folder = tmp_path / "."
    # Create actual folder with problematic name
    problem_folder = tmp_path / "-"
    problem_folder.mkdir()

    result = _rename_to_dated(str(problem_folder), "26-04-2026")
    assert Path(result).name == "26-04-2026--"
    assert Path(result).exists()


def test_rename_very_long_folder_name(tmp_path):
    """Should handle very long folder names without truncation."""
    long_name = "A" * 200 + "-Very-Long-Article-Title"
    folder = tmp_path / long_name
    folder.mkdir()

    result = _rename_to_dated(str(folder), "26-04-2026")
    expected_name = f"26-04-2026-{long_name}"
    assert Path(result).name == expected_name
    assert Path(result).exists()


def test_rename_folder_with_special_characters(tmp_path):
    """Should handle folder names with special characters."""
    folder = tmp_path / "Article_with_underscores_and.dots"
    folder.mkdir()

    result = _rename_to_dated(str(folder), "26-04-2026")
    assert Path(result).name == "26-04-2026-Article_with_underscores_and.dots"
    assert Path(result).exists()


def test_specialized_source_returns_dated_folder(tmp_path):
    """_scrape_with_specialized_source must return a DD-MM-YYYY-prefixed folder."""
    from unittest.mock import MagicMock, patch

    article_folder = tmp_path / "My-Medium-Article"
    article_folder.mkdir()

    mock_source = MagicMock()
    mock_source.fetch_article_content.return_value = (True, str(article_folder))

    mock_registry = MagicMock()
    mock_registry.get_source_for_url.return_value = (mock_source, "medium")

    with patch("capcat.core.source_system.source_registry.get_source_registry", return_value=mock_registry), \
         patch("capcat.core.config.get_capcats_dir", return_value=tmp_path):
        success, result_dir = _scrape_with_specialized_source(
            "https://medium.com/some/article",
            output_dir=".",
            generate_html=False,
        )

    assert success is True
    import re
    assert re.match(r"\d{2}-\d{2}-\d{4}-", Path(result_dir).name), (
        f"Expected DD-MM-YYYY- prefix, got: {Path(result_dir).name}"
    )


def test_known_source_path_returns_dated_folder(tmp_path):
    """Known-source branch of scrape_single_article returns a DD-MM-YYYY folder."""
    from unittest.mock import MagicMock, patch

    article_folder = tmp_path / "My-HN-Article"
    article_folder.mkdir()

    mock_source_obj = MagicMock()
    mock_source_obj.fetch_article_content.return_value = (True, str(article_folder))

    mock_factory = MagicMock()
    mock_factory.get_available_sources.return_value = ["hn"]
    mock_factory.create_source.return_value = mock_source_obj

    mock_registry = MagicMock()
    mock_registry.can_handle_url.return_value = False  # skip specialized path
    mock_registry.get_source_config.return_value = MagicMock(display_name="Hacker News")

    with patch("capcat.core.source_system.source_registry.get_source_registry", return_value=mock_registry), \
         patch("capcat.core.source_config.detect_source", return_value="hn"), \
         patch("capcat.core.source_system.source_factory.get_source_factory", return_value=mock_factory), \
         patch("capcat.core.config.get_capcats_dir", return_value=tmp_path):
        success, result_dir = scrape_single_article(
            "https://news.ycombinator.com/item?id=123",
            output_dir=".",
        )

    assert success is True
    import re
    assert re.match(r"\d{2}-\d{2}-\d{4}-", Path(result_dir).name), (
        f"Expected DD-MM-YYYY- prefix, got: {Path(result_dir).name}"
    )


def test_generic_path_returns_dated_folder(tmp_path):
    """Generic fallback of scrape_single_article returns a DD-MM-YYYY folder."""
    from unittest.mock import MagicMock, patch

    article_folder = tmp_path / "Some-Generic-Article"
    article_folder.mkdir()

    mock_session = MagicMock()
    mock_registry = MagicMock()
    mock_registry.can_handle_url.return_value = False

    with patch("capcat.core.source_system.source_registry.get_source_registry", return_value=mock_registry), \
         patch("capcat.core.source_config.detect_source", return_value=None), \
         patch("capcat.core.config.get_capcats_dir", return_value=tmp_path), \
         patch("capcat.core.session_pool.get_global_session", return_value=mock_session), \
         patch("capcat.core.article_fetcher.ArticleFetcher.fetch_article_content",
               return_value=(True, str(article_folder), "Some Generic Article")):
        success, result_dir = scrape_single_article(
            "https://example.com/some-article",
            output_dir=".",
        )

    assert success is True
    import re
    assert re.match(r"\d{2}-\d{2}-\d{4}-", Path(result_dir).name), (
        f"Expected DD-MM-YYYY- prefix, got: {Path(result_dir).name}"
    )