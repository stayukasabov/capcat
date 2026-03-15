"""
Tests for HTMLPostProcessor.process_directory_tree.

Creates a minimal but realistic article directory structure in tmp_path,
runs the processor, and verifies the expected HTML files are produced with
correct content. This covers the full generation pipeline end-to-end without
network calls.
"""
from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def article_dir(tmp_path: Path) -> Path:
    """Build a minimal batch-mode article directory.

    Structure:
        tmp_path/
          News_14-03-2026/
            Hacker-News_14-03-2026/
              01_Test_Article/
                article.md
    """
    article_folder = (
        tmp_path
        / "News_14-03-2026"
        / "Hacker-News_14-03-2026"
        / "01_Test_Article"
    )
    article_folder.mkdir(parents=True)
    (article_folder / "article.md").write_text(
        "# Test Article\n\n**Source URL:** https://example.com/test\n\nBody content.",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture()
def article_with_comments_dir(tmp_path: Path) -> Path:
    """Article directory that also has a comments.md file."""
    article_folder = (
        tmp_path
        / "News_14-03-2026"
        / "Hacker-News_14-03-2026"
        / "01_Test_Article"
    )
    article_folder.mkdir(parents=True)
    (article_folder / "article.md").write_text(
        "# Article With Comments\n\nContent.",
        encoding="utf-8",
    )
    (article_folder / "comments.md").write_text(
        "# Comments\n\n**Anonymous**: Great read!",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture()
def single_article_dir(tmp_path: Path) -> Path:
    """Capcats-style single-article directory (no source subfolder)."""
    article_folder = tmp_path / "cc_14-03-2026-Test-Article"
    article_folder.mkdir(parents=True)
    (article_folder / "article.md").write_text(
        "# Single Article\n\nContent.",
        encoding="utf-8",
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Basic generation
# ---------------------------------------------------------------------------

def test_process_directory_tree_creates_article_html(article_dir: Path) -> None:
    """process_directory_tree must create html/article.html inside the article dir."""
    from capcat.core.html_post_processor import HTMLPostProcessor

    processor = HTMLPostProcessor()
    processor.process_directory_tree(str(article_dir), incremental=False)

    html_file = (
        article_dir
        / "News_14-03-2026"
        / "Hacker-News_14-03-2026"
        / "01_Test_Article"
        / "html"
        / "article.html"
    )
    assert html_file.exists(), f"Expected {html_file} to be created"


def test_process_directory_tree_html_contains_doctype(article_dir: Path) -> None:
    """Generated article.html must be valid HTML starting with DOCTYPE."""
    from capcat.core.html_post_processor import HTMLPostProcessor

    processor = HTMLPostProcessor()
    processor.process_directory_tree(str(article_dir), incremental=False)

    html_file = (
        article_dir
        / "News_14-03-2026"
        / "Hacker-News_14-03-2026"
        / "01_Test_Article"
        / "html"
        / "article.html"
    )
    content = html_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE" in content or "<html" in content


def test_process_directory_tree_html_contains_template_marker(
    article_dir: Path,
) -> None:
    """Generated HTML must embed the current template marker so incremental
    re-runs skip up-to-date files and forced updates regenerate stale ones."""
    from capcat.core.html_post_processor import HTMLPostProcessor

    processor = HTMLPostProcessor()
    processor.process_directory_tree(str(article_dir), incremental=False)

    html_file = (
        article_dir
        / "News_14-03-2026"
        / "Hacker-News_14-03-2026"
        / "01_Test_Article"
        / "html"
        / "article.html"
    )
    content = html_file.read_text(encoding="utf-8")
    assert HTMLPostProcessor._TEMPLATE_MARKER in content, (
        "Template marker missing — incremental regeneration will not work"
    )


# ---------------------------------------------------------------------------
# Comments generation
# ---------------------------------------------------------------------------

def test_process_directory_tree_creates_comments_html(
    article_with_comments_dir: Path,
) -> None:
    """When comments.md is present, html/comments.html must be created."""
    from capcat.core.html_post_processor import HTMLPostProcessor

    processor = HTMLPostProcessor()
    processor.process_directory_tree(
        str(article_with_comments_dir), incremental=False
    )

    comments_html = (
        article_with_comments_dir
        / "News_14-03-2026"
        / "Hacker-News_14-03-2026"
        / "01_Test_Article"
        / "html"
        / "comments.html"
    )
    assert comments_html.exists(), "comments.html was not generated"


def test_comments_page_has_back_to_article_link(
    article_with_comments_dir: Path,
) -> None:
    """comments.html must contain a 'Back to Article' link (orange nav)."""
    from capcat.core.html_post_processor import HTMLPostProcessor

    processor = HTMLPostProcessor()
    processor.process_directory_tree(
        str(article_with_comments_dir), incremental=False
    )

    comments_html = (
        article_with_comments_dir
        / "News_14-03-2026"
        / "Hacker-News_14-03-2026"
        / "01_Test_Article"
        / "html"
        / "comments.html"
    )
    content = comments_html.read_text(encoding="utf-8")
    assert "Back to Article" in content


def test_comments_page_has_no_back_to_news_button(
    article_with_comments_dir: Path,
) -> None:
    """comments.html must NOT have a 'Back to News' button — that was the
    blue abomination bug. Navigation is Back to Article only."""
    from capcat.core.html_post_processor import HTMLPostProcessor

    processor = HTMLPostProcessor()
    processor.process_directory_tree(
        str(article_with_comments_dir), incremental=False
    )

    comments_html = (
        article_with_comments_dir
        / "News_14-03-2026"
        / "Hacker-News_14-03-2026"
        / "01_Test_Article"
        / "html"
        / "comments.html"
    )
    content = comments_html.read_text(encoding="utf-8")
    assert "Back to News" not in content


# ---------------------------------------------------------------------------
# Incremental re-generation (template marker)
# ---------------------------------------------------------------------------

def test_incremental_skips_up_to_date_file(article_dir: Path) -> None:
    """On the second run with incremental=True, an up-to-date file must not
    be rewritten (mtime must stay the same)."""
    from capcat.core.html_post_processor import HTMLPostProcessor

    processor = HTMLPostProcessor()
    processor.process_directory_tree(str(article_dir), incremental=False)

    html_file = (
        article_dir
        / "News_14-03-2026"
        / "Hacker-News_14-03-2026"
        / "01_Test_Article"
        / "html"
        / "article.html"
    )
    mtime_before = html_file.stat().st_mtime
    processor.process_directory_tree(str(article_dir), incremental=True)
    mtime_after = html_file.stat().st_mtime

    assert mtime_before == mtime_after, (
        "Incremental run rewrote an up-to-date file — template marker check is broken"
    )


# ---------------------------------------------------------------------------
# Single article mode
# ---------------------------------------------------------------------------

def test_single_article_mode_generates_html(single_article_dir: Path) -> None:
    """is_single_article=True (Capcats mode) must still produce article.html."""
    from capcat.core.html_post_processor import HTMLPostProcessor

    article_folder = single_article_dir / "cc_14-03-2026-Test-Article"
    processor = HTMLPostProcessor()
    processor.process_directory_tree(
        str(article_folder),
        incremental=False,
        is_single_article=True,
    )

    html_file = article_folder / "html" / "article.html"
    assert html_file.exists(), "html/article.html not created in single article mode"


# ---------------------------------------------------------------------------
# _is_archive_root — canonical Source-Name_DD-MM-YYYY format
# ---------------------------------------------------------------------------

class TestIsArchiveRoot:
    """_is_archive_root must recognise only the canonical Source-Name_DD-MM-YYYY format.

    Uses monkeypatch to isolate from live registry state:
    - list_available_sources() returns ['hn']
    - get_source_folder_name('hn') returns 'Hacker-News' (after Phase 1 fix)
    """

    @pytest.fixture()
    def processor(self):
        from capcat.core.html_post_processor import HTMLPostProcessor
        return HTMLPostProcessor()

    @pytest.fixture(autouse=True)
    def mock_registry(self, monkeypatch):
        """Isolate from live registry — always exposes 'hn' with display_name 'Hacker News'."""
        from unittest.mock import MagicMock
        mock_reg = MagicMock()
        mock_reg.list_available_sources.return_value = ["hn"]

        monkeypatch.setattr(
            "capcat.core.utils.get_source_folder_name",
            lambda code: "Hacker-News" if code == "hn" else code,
        )

        import capcat.core.config as cfg_mod
        monkeypatch.setattr(cfg_mod, "get_source_registry", lambda: mock_reg)

    def test_new_hyphen_format_is_recognised(self, processor, tmp_path):
        """Hacker-News_15-03-2026 is the canonical format — must return True."""
        path = tmp_path / "Hacker-News_15-03-2026"
        path.mkdir()
        assert processor._is_archive_root(path) is True

    def test_old_underscore_format_is_not_recognised(self, processor, tmp_path):
        """Hacker_News_15-03-2026 is the old format — must return False."""
        path = tmp_path / "Hacker_News_15-03-2026"
        path.mkdir()
        assert processor._is_archive_root(path) is False

    def test_sg_prefix_is_not_recognised(self, processor, tmp_path):
        """sg_15-03-2026 is dead legacy code — must return False."""
        path = tmp_path / "sg_15-03-2026"
        path.mkdir()
        assert processor._is_archive_root(path) is False

    def test_news_date_folder_is_recognised(self, processor, tmp_path):
        """News_15-03-2026 is the date folder — must still return True."""
        path = tmp_path / "News_15-03-2026"
        path.mkdir()
        assert processor._is_archive_root(path) is True
