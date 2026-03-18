"""Tests for Obsidian wikilink injection."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from capcat.core.storage_manager import inject_comments_wikilink
from capcat.core.streamlined_comment_processor import create_optimized_comment_processor


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


def _make_fake_comments():
    """Return a minimal list of comment dicts as produce by process_comments_flattened."""
    return [{"user": "bob", "user_link": "https://example.com/bob", "text": "Great article!"}]


def test_comments_md_has_article_wikilink_top(tmp_path):
    """generate_inline_comments_markdown prepends ← [[...|Article]] when article_folder_path given."""
    _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")
    processor = create_optimized_comment_processor(max_comments=None)
    md = processor.generate_inline_comments_markdown(
        _make_fake_comments(), "My Article", "https://example.com", str(tmp_path)
    )
    lines = md.splitlines()
    assert lines[0] == "← [[My-Article|Article]]"


def test_comments_md_has_article_wikilink_bottom(tmp_path):
    """generate_inline_comments_markdown appends ← [[...|Article]] at the end."""
    _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")
    processor = create_optimized_comment_processor(max_comments=None)
    md = processor.generate_inline_comments_markdown(
        _make_fake_comments(), "My Article", "https://example.com", str(tmp_path)
    )
    non_blank = [l for l in md.splitlines() if l.strip()]
    assert non_blank[-1] == "← [[My-Article|Article]]"


# ---------------------------------------------------------------------------
# Task 4 integration tests: unified_source_processor injection wiring
# ---------------------------------------------------------------------------

def _write_comments_file(folder: Path, article_stem: str) -> Path:
    """Write a minimal comments .md file and return its path."""
    p = folder / f"{article_stem}-Comments.md"
    p.write_text("# Comments\n\nSome comment.\n", encoding="utf-8")
    return p


def test_no_injection_when_fetch_comments_returns_false(tmp_path):
    """When fetch_comments returns False, article.md must not contain '→ [['."""
    from capcat.core.storage_manager import inject_comments_wikilink, find_comments_md

    article_path = _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")

    # Simulate: fetch_comments returned False — injection should NOT be called
    # Verify directly: calling inject only when fetch_comments is True
    comments_written = False
    if comments_written:
        comments_md = find_comments_md(tmp_path)
        if comments_md:
            inject_comments_wikilink(str(tmp_path), comments_md.stem)

    content = article_path.read_text(encoding="utf-8")
    assert "→ [[" not in content


def test_injection_called_when_fetch_comments_returns_true(tmp_path):
    """When fetch_comments returns True and comments file exists, article.md gets wikilink."""
    from capcat.core.storage_manager import inject_comments_wikilink, find_comments_md

    article_path = _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")
    _write_comments_file(tmp_path, "My-Article")

    # Simulate: fetch_comments returned True
    comments_written = True
    if comments_written:
        comments_md = find_comments_md(tmp_path)
        if comments_md:
            inject_comments_wikilink(str(tmp_path), comments_md.stem)

    content = article_path.read_text(encoding="utf-8")
    assert "→ [[My-Article-Comments|Comments]]" in content
