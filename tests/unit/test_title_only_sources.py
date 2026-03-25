"""Tests for title-only (placeholder) sources: Twitter/X, YouTube, Vimeo.

These sources create a structured placeholder folder instead of scraping
full article content. Tests cover URL detection and basic source behaviour.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from capcat.core.source_system.base_source import Article, SourceConfig
from capcat.sources.builtin.custom.twitter.source import TwitterSource
from capcat.sources.builtin.custom.youtube.source import YouTubeSource
from capcat.sources.builtin.custom.vimeo.source import VimeoSource


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config(name: str, base_url: str) -> SourceConfig:
    return SourceConfig(
        name=name,
        display_name=name.title(),
        base_url=base_url,
        timeout=10.0,
        rate_limit=1.0,
        supports_comments=False,
        category="social",
        custom_config={},
    )


# ---------------------------------------------------------------------------
# TwitterSource
# ---------------------------------------------------------------------------

class TestTwitterCanHandleUrl:
    def test_twitter_com(self):
        assert TwitterSource.can_handle_url("https://twitter.com/user/status/123")

    def test_x_com(self):
        assert TwitterSource.can_handle_url("https://x.com/user/status/456")

    def test_mobile_twitter(self):
        assert TwitterSource.can_handle_url("https://mobile.twitter.com/user/status/789")

    def test_rejects_youtube(self):
        assert not TwitterSource.can_handle_url("https://www.youtube.com/watch?v=abc")

    def test_rejects_plain_text(self):
        assert not TwitterSource.can_handle_url("not a url")

    def test_rejects_empty(self):
        assert not TwitterSource.can_handle_url("")


class TestTwitterFetchCreatesFolder:
    def test_creates_subfolder_not_flat_file(self, tmp_path):
        """Regression: TwitterSource must write into a subfolder, not directly
        into output_dir (which caused HN source dir to be misidentified)."""
        config = _make_config("twitter", "https://twitter.com")
        source = TwitterSource(config)
        article = Article(title="Test tweet", url="https://x.com/user/status/1")

        success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success
        assert folder is not None
        # The returned path must be a subdirectory of tmp_path, not tmp_path itself
        assert Path(folder).parent == tmp_path or str(folder) != str(tmp_path)
        # An .md file must exist inside the returned folder
        md_files = list(Path(folder).glob("*.md"))
        assert md_files, f"No .md file found in {folder}"


# ---------------------------------------------------------------------------
# YouTubeSource
# ---------------------------------------------------------------------------

class TestYouTubeCanHandleUrl:
    def test_youtube_watch(self):
        assert YouTubeSource.can_handle_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_youtu_be_short(self):
        assert YouTubeSource.can_handle_url("https://youtu.be/dQw4w9WgXcQ")

    def test_youtube_shorts(self):
        assert YouTubeSource.can_handle_url("https://www.youtube.com/shorts/abc123")

    def test_rejects_twitter(self):
        assert not YouTubeSource.can_handle_url("https://twitter.com/user/status/1")

    def test_rejects_vimeo(self):
        assert not YouTubeSource.can_handle_url("https://vimeo.com/123456")

    def test_rejects_empty(self):
        assert not YouTubeSource.can_handle_url("")


class TestYouTubeFetchCreatesPlaceholder:
    def test_creates_md_placeholder(self, tmp_path):
        config = _make_config("youtube", "https://youtube.com")
        source = YouTubeSource(config)
        article = Article(title="Test video", url="https://www.youtube.com/watch?v=abc")

        success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success
        assert folder is not None
        md_files = list(Path(folder).glob("*.md"))
        assert md_files, f"No .md file found in {folder}"


# ---------------------------------------------------------------------------
# VimeoSource
# ---------------------------------------------------------------------------

class TestVimeoCanHandleUrl:
    def test_vimeo_video(self):
        assert VimeoSource.can_handle_url("https://vimeo.com/123456789")

    def test_vimeo_with_path(self):
        assert VimeoSource.can_handle_url("https://www.vimeo.com/channels/test/123")

    def test_rejects_youtube(self):
        assert not VimeoSource.can_handle_url("https://www.youtube.com/watch?v=abc")

    def test_rejects_twitter(self):
        assert not VimeoSource.can_handle_url("https://twitter.com/user/status/1")

    def test_rejects_empty(self):
        assert not VimeoSource.can_handle_url("")


class TestVimeoFetchCreatesPlaceholder:
    def test_creates_md_placeholder(self, tmp_path):
        config = _make_config("vimeo", "https://vimeo.com")
        source = VimeoSource(config)
        article = Article(title="Test vimeo", url="https://vimeo.com/123456789")

        success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success
        assert folder is not None
        md_files = list(Path(folder).glob("*.md"))
        assert md_files, f"No .md file found in {folder}"
