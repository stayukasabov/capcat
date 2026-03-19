"""Tests for TwitterSource subfolder creation.

Regression: TwitterSource was writing X.com-post.md directly into output_dir
instead of creating a subfolder. This caused article detection to misidentify
the HN source directory as an article directory.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from capcat.core.source_system.base_source import Article, SourceConfig
from capcat.sources.specialized.twitter.source import TwitterSource


@pytest.fixture
def twitter_source(tmp_path):
    config = SourceConfig(
        name="twitter",
        display_name="Twitter",
        base_url="https://x.com",
        timeout=10,
    )
    source = TwitterSource(config)
    return source


def test_twitter_creates_subfolder(twitter_source, tmp_path):
    """TwitterSource must write markdown into a subfolder, not into output_dir."""
    article = Article(title="Test Tweet", url="https://twitter.com/user/status/123")
    success, folder = twitter_source.fetch_article_content(article, str(tmp_path))

    assert success is True
    # folder must be a subdirectory of tmp_path, not tmp_path itself
    assert folder != str(tmp_path)
    assert Path(folder).parent == tmp_path


def test_twitter_returns_folder_path_not_title(twitter_source, tmp_path):
    """fetch_article_content must return the folder path, not the display title string."""
    article = Article(title="Test Tweet", url="https://x.com/user/status/456")
    success, folder = twitter_source.fetch_article_content(article, str(tmp_path))

    assert success is True
    assert Path(folder).exists()
    assert Path(folder).is_dir()


def test_twitter_markdown_inside_subfolder(twitter_source, tmp_path):
    """The .md file must live inside the subfolder, not in output_dir."""
    article = Article(title="Test Tweet", url="https://twitter.com/Waymo/status/999")
    _, folder = twitter_source.fetch_article_content(article, str(tmp_path))

    md_files = list(Path(folder).glob("*.md"))
    assert len(md_files) == 1
    # Confirm there is no .md in output_dir itself
    assert list(tmp_path.glob("*.md")) == []


def test_twitter_no_md_at_output_dir_root(twitter_source, tmp_path):
    """Regression: X.com-post.md must NOT appear at the source directory level."""
    article = Article(title="X.com post", url="https://x.com/user/status/1")
    twitter_source.fetch_article_content(article, str(tmp_path))

    assert not (tmp_path / "X.com-post.md").exists()
