"""Regression test — create_comments_file: false must suppress comments fetching.

B7: unified_source_processor ignored create_comments_file config flag.
Comments were always fetched regardless of the setting.
"""
from unittest.mock import MagicMock, patch
from pathlib import Path

from capcat.core.config import FetchNewsConfig, ProcessingConfig


def _make_processor(create_comments: bool):
    """Return a UnifiedSourceProcessor with create_comments_file set."""
    from capcat.core.unified_source_processor import UnifiedSourceProcessor

    config = FetchNewsConfig()
    config.processing = ProcessingConfig(create_comments_file=create_comments)

    with patch("capcat.core.unified_source_processor.get_config", return_value=config):
        proc = UnifiedSourceProcessor()
        proc.config = config
    return proc


def _make_article(with_comment_url: bool = True):
    article = MagicMock()
    article.title = "Test Article"
    article.comment_url = "https://example.com/comments" if with_comment_url else None
    return article


def _make_source(has_comments: bool = True):
    source = MagicMock()
    source.config.name = "test"
    source.config.has_comments = has_comments
    source.fetch_comments = MagicMock(return_value=False)
    source.fetch_article_content = MagicMock(return_value=(True, "/tmp/test/article.md"))
    return source


class TestCreateCommentsFileFlag:
    def test_comments_skipped_when_flag_false(self, tmp_path):
        """fetch_comments must not be called when create_comments_file is False."""
        proc = _make_processor(create_comments=False)
        source = _make_source()
        article = _make_article()

        with (
            patch("capcat.core.unified_source_processor.find_article_md", return_value=None),
            patch("capcat.core.unified_source_processor.inject_frontmatter"),
        ):
            proc._process_single_article_new_system(source, article, str(tmp_path), False)

        source.fetch_comments.assert_not_called()

    def test_comments_fetched_when_flag_true(self, tmp_path):
        """fetch_comments must be called when create_comments_file is True."""
        proc = _make_processor(create_comments=True)
        source = _make_source()
        article = _make_article()

        with (
            patch("capcat.core.unified_source_processor.find_article_md", return_value=None),
            patch("capcat.core.unified_source_processor.find_comments_md", return_value=None),
            patch("capcat.core.unified_source_processor.inject_frontmatter"),
        ):
            proc._process_single_article_new_system(source, article, str(tmp_path), False)

        source.fetch_comments.assert_called_once()

    def test_comments_skipped_when_no_comment_url(self, tmp_path):
        """fetch_comments must not be called when article has no comment_url."""
        proc = _make_processor(create_comments=True)
        source = _make_source()
        article = _make_article(with_comment_url=False)

        with (
            patch("capcat.core.unified_source_processor.find_article_md", return_value=None),
            patch("capcat.core.unified_source_processor.inject_frontmatter"),
        ):
            proc._process_single_article_new_system(source, article, str(tmp_path), False)

        source.fetch_comments.assert_not_called()
