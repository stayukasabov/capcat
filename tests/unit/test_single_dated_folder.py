"""Tests for _rename_to_dated helper in commands/single.py."""
from __future__ import annotations
from pathlib import Path

import pytest

from capcat.commands.single import _rename_to_dated


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