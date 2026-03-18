"""Tests for Obsidian wikilink injection."""
import pytest
from pathlib import Path
from capcat.core.storage_manager import inject_comments_wikilink


def _make_article(folder: Path, stem: str, content: str) -> Path:
    """Write a .md file to folder and return its path."""
    p = folder / f"{stem}.md"
    p.write_text(content, encoding="utf-8")
    return p


def test_inject_adds_wikilink_at_top(tmp_path):
    """Line 1 of article.md becomes the comments wikilink after injection."""
    _make_article(tmp_path, "My-Article", "# My Article\n\nSome content.\n")
    inject_comments_wikilink(str(tmp_path), "My-Article-Comments")
    lines = (tmp_path / "My-Article.md").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "→ [[My-Article-Comments|Comments]]"


def test_inject_adds_wikilink_at_bottom(tmp_path):
    """Last non-blank line of article.md becomes the comments wikilink."""
    _make_article(tmp_path, "My-Article", "# My Article\n\nSome content.\n")
    inject_comments_wikilink(str(tmp_path), "My-Article-Comments")
    lines = [l for l in (tmp_path / "My-Article.md").read_text(encoding="utf-8").splitlines() if l.strip()]
    assert lines[-1] == "→ [[My-Article-Comments|Comments]]"


def test_inject_uses_exact_filename_stem(tmp_path):
    """Wikilink stem matches the actual .md file stem on disk."""
    _make_article(tmp_path, "Exact-Stem-Here", "# Title\n\nBody.\n")
    inject_comments_wikilink(str(tmp_path), "Exact-Stem-Here-Comments")
    content = (tmp_path / "Exact-Stem-Here.md").read_text(encoding="utf-8")
    assert "[[Exact-Stem-Here-Comments|Comments]]" in content


def test_inject_returns_false_if_no_article_md(tmp_path):
    """Returns False gracefully when folder contains no .md file."""
    result = inject_comments_wikilink(str(tmp_path), "Some-Comments")
    assert result is False


def test_inject_idempotent_on_second_call(tmp_path):
    """Calling inject twice does not duplicate the top wikilink."""
    _make_article(tmp_path, "My-Article", "# My Article\n\nSome content.\n")
    inject_comments_wikilink(str(tmp_path), "My-Article-Comments")
    inject_comments_wikilink(str(tmp_path), "My-Article-Comments")
    content = (tmp_path / "My-Article.md").read_text(encoding="utf-8")
    assert content.count("→ [[My-Article-Comments|Comments]]") == 2  # one top, one bottom
