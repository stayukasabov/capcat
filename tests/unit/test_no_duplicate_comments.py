"""Tests that fetch_article_content does not write comments internally.

After the fix, only the outer caller (unified_source_processor) is
responsible for writing comments. These tests confirm that
fetch_article_content returns without side-effect comment files.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from capcat.core.source_system.base_source import Article, SourceConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_article(**kwargs) -> Article:
    defaults = dict(
        title="Test Article Title",
        url="https://example.com/article",
        comment_url="https://news.ycombinator.com/item?id=99999",
    )
    defaults.update(kwargs)
    return Article(**defaults)


def _hn_config() -> SourceConfig:
    return SourceConfig(
        name="hn",
        display_name="Hacker News",
        base_url="https://news.ycombinator.com",
        has_comments=True,
    )


def _lb_config() -> SourceConfig:
    return SourceConfig(
        name="lb",
        display_name="Lobsters",
        base_url="https://lobste.rs",
        has_comments=True,
    )


# ---------------------------------------------------------------------------
# HnSource: fetch_article_content must not write a comments file
# ---------------------------------------------------------------------------

class TestHnSourceNoInternalComments:
    """fetch_article_content must return without calling fetch_comments."""

    def test_fetch_article_content_does_not_call_fetch_comments(self, tmp_path):
        """fetch_comments must NOT be called inside fetch_article_content."""
        from capcat.sources.builtin.custom.hn.source import HnSource

        source = HnSource(_hn_config())
        article = _make_article()

        # Patch the external fetcher so the test is fast and offline
        mock_fetcher_cls = MagicMock()
        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch_article_content.return_value = (
            True,
            article.title,
            str(tmp_path),
        )

        with patch(
            "capcat.sources.builtin.custom.hn.source.NewsSourceArticleFetcher",
            mock_fetcher_cls,
        ):
            with patch.object(source, "fetch_comments") as mock_fetch_comments:
                source.fetch_article_content(article, str(tmp_path))

        mock_fetch_comments.assert_not_called()

    def test_fetch_article_content_returns_folder_path(self, tmp_path):
        """fetch_article_content still returns (True, folder_path) after the fix."""
        from capcat.sources.builtin.custom.hn.source import HnSource

        source = HnSource(_hn_config())
        article = _make_article()

        mock_fetcher_cls = MagicMock()
        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch_article_content.return_value = (
            True,
            article.title,
            str(tmp_path),
        )

        with patch(
            "capcat.sources.builtin.custom.hn.source.NewsSourceArticleFetcher",
            mock_fetcher_cls,
        ):
            with patch.object(source, "fetch_comments"):
                success, path = source.fetch_article_content(article, str(tmp_path))

        assert success is True
        assert path == str(tmp_path)

    def test_no_duplicate_comments_files_in_folder(self, tmp_path):
        """fetch_article_content must not create any *-Comments.md files."""
        from capcat.sources.builtin.custom.hn.source import HnSource

        source = HnSource(_hn_config())
        article = _make_article()

        mock_fetcher_cls = MagicMock()
        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch_article_content.return_value = (
            True,
            article.title,
            str(tmp_path),
        )

        def _write_comments_file(**kwargs):
            folder = kwargs.get("article_folder_path", str(tmp_path))
            (Path(folder) / "Test-Article-Title-Comments.md").write_text("comments")

        with patch(
            "capcat.sources.builtin.custom.hn.source.NewsSourceArticleFetcher",
            mock_fetcher_cls,
        ):
            with patch.object(source, "fetch_comments", side_effect=_write_comments_file):
                source.fetch_article_content(article, str(tmp_path))

        comments_files = list(tmp_path.glob("*-Comments.md"))
        assert len(comments_files) == 0, (
            f"fetch_article_content must not create comments files; "
            f"found: {[f.name for f in comments_files]}"
        )


# ---------------------------------------------------------------------------
# LbSource: fetch_article_content must not write a comments file
# ---------------------------------------------------------------------------

class TestLbSourceNoInternalComments:
    """fetch_comments must NOT be called inside LbSource.fetch_article_content."""

    def test_fetch_article_content_does_not_call_fetch_comments(self, tmp_path):
        """fetch_comments must NOT be called inside fetch_article_content."""
        from capcat.sources.builtin.custom.lb.source import LbSource

        source = LbSource(_lb_config())
        article = _make_article(
            url="https://lobste.rs/s/example/test_article",
            comment_url="https://lobste.rs/s/example/test_article",
        )

        mock_fetcher_cls = MagicMock()
        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch_article_content.return_value = (
            True,
            article.title,
            str(tmp_path),
        )

        with patch(
            "capcat.sources.builtin.custom.lb.source.NewsSourceArticleFetcher",
            mock_fetcher_cls,
        ):
            with patch.object(source, "fetch_comments") as mock_fetch_comments:
                source.fetch_article_content(article, str(tmp_path))

        mock_fetch_comments.assert_not_called()

    def test_fetch_article_content_returns_folder_path(self, tmp_path):
        """fetch_article_content still returns (True, folder_path) after the fix."""
        from capcat.sources.builtin.custom.lb.source import LbSource

        source = LbSource(_lb_config())
        article = _make_article(
            url="https://lobste.rs/s/example/test_article",
            comment_url="https://lobste.rs/s/example/test_article",
        )

        mock_fetcher_cls = MagicMock()
        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch_article_content.return_value = (
            True,
            article.title,
            str(tmp_path),
        )

        with patch(
            "capcat.sources.builtin.custom.lb.source.NewsSourceArticleFetcher",
            mock_fetcher_cls,
        ):
            with patch.object(source, "fetch_comments"):
                success, path = source.fetch_article_content(article, str(tmp_path))

        assert success is True
        assert path == str(tmp_path)

    def test_no_duplicate_comments_files_in_folder(self, tmp_path):
        """fetch_article_content must not create any *-Comments.md files."""
        from capcat.sources.builtin.custom.lb.source import LbSource

        source = LbSource(_lb_config())
        article = _make_article(
            url="https://lobste.rs/s/example/test_article",
            comment_url="https://lobste.rs/s/example/test_article",
        )

        mock_fetcher_cls = MagicMock()
        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch_article_content.return_value = (
            True,
            article.title,
            str(tmp_path),
        )

        def _write_comments_file(**kwargs):
            folder = kwargs.get("article_folder_path", str(tmp_path))
            (Path(folder) / "Test-Article-Title-Comments.md").write_text("comments")

        with patch(
            "capcat.sources.builtin.custom.lb.source.NewsSourceArticleFetcher",
            mock_fetcher_cls,
        ):
            with patch.object(source, "fetch_comments", side_effect=_write_comments_file):
                source.fetch_article_content(article, str(tmp_path))

        comments_files = list(tmp_path.glob("*-Comments.md"))
        assert len(comments_files) == 0, (
            f"fetch_article_content must not create comments files; "
            f"found: {[f.name for f in comments_files]}"
        )
