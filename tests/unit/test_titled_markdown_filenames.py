"""Tests for titled markdown filename helpers in storage_manager."""
from __future__ import annotations
from pathlib import Path

import pytest

from capcat.core.storage_manager import (
    article_md_filename,
    comments_md_filename,
    find_article_md,
    find_comments_md,
)


# ---------------------------------------------------------------------------
# article_md_filename
# ---------------------------------------------------------------------------

def test_article_md_filename_basic():
    assert article_md_filename("My Title") == "My-Title.md"


def test_article_md_filename_truncates_at_200_chars():
    long = "A" * 250
    result = article_md_filename(long)
    assert result.endswith(".md")
    assert len(result.removesuffix(".md")) <= 200


# ---------------------------------------------------------------------------
# comments_md_filename
# ---------------------------------------------------------------------------

def test_comments_md_filename_basic():
    assert comments_md_filename("My Title") == "My-Title-Comments.md"


def test_comments_md_filename_truncates_at_200_chars():
    long = "A" * 250
    result = comments_md_filename(long)
    assert result.endswith("-Comments.md")
    assert len(result.removesuffix("-Comments.md")) <= 200


# ---------------------------------------------------------------------------
# find_article_md
# ---------------------------------------------------------------------------

def test_find_article_md_returns_path_when_titled_md_exists(tmp_path):
    (tmp_path / "My-Title.md").write_text("content")
    result = find_article_md(tmp_path)
    assert result is not None
    assert result.name == "My-Title.md"


def test_find_article_md_returns_none_when_folder_empty(tmp_path):
    assert find_article_md(tmp_path) is None


def test_find_article_md_ignores_comments_files(tmp_path):
    (tmp_path / "My-Title-Comments.md").write_text("content")
    assert find_article_md(tmp_path) is None


def test_find_article_md_still_finds_legacy_article_md(tmp_path):
    """article.md is also found — stem 'article' doesn't end in '-Comments'."""
    (tmp_path / "article.md").write_text("content")
    result = find_article_md(tmp_path)
    assert result is not None
    assert result.name == "article.md"


# ---------------------------------------------------------------------------
# find_comments_md
# ---------------------------------------------------------------------------

def test_find_comments_md_returns_path_when_comments_file_exists(tmp_path):
    (tmp_path / "My-Title-Comments.md").write_text("content")
    result = find_comments_md(tmp_path)
    assert result is not None
    assert result.name == "My-Title-Comments.md"


def test_find_comments_md_returns_none_when_absent(tmp_path):
    assert find_comments_md(tmp_path) is None


def test_find_comments_md_does_not_match_plain_comments_md(tmp_path):
    """Legacy comments.md does NOT match the new *-Comments.md glob."""
    (tmp_path / "comments.md").write_text("content")
    assert find_comments_md(tmp_path) is None


# ---------------------------------------------------------------------------
# save_article_content uses titled filename
# ---------------------------------------------------------------------------

def test_save_article_content_writes_titled_filename(tmp_path):
    from capcat.core.storage_manager import StorageManager
    sm = StorageManager()
    path = sm.save_article_content(str(tmp_path), "hello", "My Title")
    assert (tmp_path / "My-Title.md").exists()
    assert "My-Title.md" in path
