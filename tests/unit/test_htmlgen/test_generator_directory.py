"""Tests for ArticleHTMLGenerator directory index generation and title cleaning."""
from __future__ import annotations
from pathlib import Path
import pytest


def test_generate_directory_index_returns_html_string(tmp_path: Path):
    from capcat.htmlgen import ArticleHTMLGenerator
    gen = ArticleHTMLGenerator()
    result = gen.generate_directory_index(
        str(tmp_path), "Test Directory", ["News_19-03-2026"]
    )
    assert isinstance(result, str)
    assert "<html" in result


def test_generate_directory_index_root_level_title_in_result(tmp_path: Path):
    from capcat.htmlgen import ArticleHTMLGenerator
    # Root-level directory: name starts with News_
    root_dir = tmp_path / "News_19-03-2026"
    root_dir.mkdir()
    gen = ArticleHTMLGenerator()
    result = gen.generate_directory_index(
        str(root_dir), "News Archive", ["News_19-03-2026"]
    )
    assert "News Archive" in result


def test_generate_directory_index_source_level_title_in_result(tmp_path: Path):
    from capcat.htmlgen import ArticleHTMLGenerator
    source_dir = tmp_path / "Hacker-News_19-03-2026"
    source_dir.mkdir()
    gen = ArticleHTMLGenerator()
    result = gen.generate_directory_index(
        str(source_dir), "Hacker News", ["News_19-03-2026", "Hacker-News_19-03-2026"]
    )
    assert "Hacker News" in result


def test_clean_title_for_display_strips_date_suffix():
    from capcat.htmlgen import ArticleHTMLGenerator
    gen = ArticleHTMLGenerator()
    result = gen._clean_title_for_display("Hacker-News_19-03-2026")
    assert "19-03-2026" not in result


def test_clean_title_for_display_normalises_hyphens():
    from capcat.htmlgen import ArticleHTMLGenerator
    gen = ArticleHTMLGenerator()
    result = gen._clean_title_for_display("Hacker-News_19-03-2026")
    assert "Hacker News" in result
