#!/usr/bin/env python3
"""
Tests for YouTube and Vimeo specialized sources with yt-dlp integration.
"""

import os
import tempfile
import pytest

from sources.specialized.youtube.source import YouTubeSource
from sources.specialized.vimeo.source import VimeoSource
from core.source_system.base_source import Article


class TestYouTubeSource:
    """Test YouTube specialized source with yt-dlp."""

    @pytest.fixture
    def youtube_source(self):
        """Create a YouTube source instance."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "../sources/specialized/youtube/config.yaml"
        )
        return YouTubeSource(config_path)

    def test_can_handle_youtube_urls(self):
        """Test YouTube URL detection."""
        assert YouTubeSource.can_handle_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert YouTubeSource.can_handle_url("https://youtu.be/dQw4w9WgXcQ")
        assert YouTubeSource.can_handle_url("https://m.youtube.com/watch?v=dQw4w9WgXcQ")
        assert not YouTubeSource.can_handle_url("https://vimeo.com/123456")
        assert not YouTubeSource.can_handle_url("https://example.com")

    def test_extract_youtube_title(self, youtube_source):
        """Test extracting title from a real YouTube video using yt-dlp."""
        # Rick Astley - Never Gonna Give You Up (Official Video)
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        title = youtube_source._extract_video_title(test_url)

        assert title is not None
        assert len(title) > 0
        assert "Never Gonna Give You Up" in title or "Rick Astley" in title

    def test_fetch_article_content_with_title(self, youtube_source):
        """Test creating placeholder article with extracted title."""
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        article = Article(
            title="Test Video",
            url=test_url,
            author="Unknown",
            publish_date=None,
            summary=""
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            success, display_title = youtube_source.fetch_article_content(
                article, tmpdir
            )

            assert success
            assert display_title is not None
            assert display_title != "YouTube Video"  # Should have real title

            # Check article file was created
            article_path = os.path.join(tmpdir, "article.md")
            assert os.path.exists(article_path)

            # Check content
            with open(article_path, 'r') as f:
                content = f.read()
                assert display_title in content
                assert test_url in content


class TestVimeoSource:
    """Test Vimeo specialized source with yt-dlp."""

    @pytest.fixture
    def vimeo_source(self):
        """Create a Vimeo source instance."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "../sources/specialized/vimeo/config.yaml"
        )
        return VimeoSource(config_path)

    def test_can_handle_vimeo_urls(self):
        """Test Vimeo URL detection."""
        assert VimeoSource.can_handle_url("https://vimeo.com/148751763")
        assert VimeoSource.can_handle_url("https://www.vimeo.com/148751763")
        assert not VimeoSource.can_handle_url("https://youtube.com/watch?v=123")
        assert not VimeoSource.can_handle_url("https://example.com")

    def test_extract_vimeo_title(self, vimeo_source):
        """Test extracting title from a real Vimeo video using yt-dlp."""
        # Vimeo Staff Pick video
        test_url = "https://vimeo.com/148751763"

        title = vimeo_source._extract_video_title(test_url)

        assert title is not None
        assert len(title) > 0

    def test_fetch_article_content_with_title(self, vimeo_source):
        """Test creating placeholder article with extracted title."""
        test_url = "https://vimeo.com/148751763"
        article = Article(
            title="Test Video",
            url=test_url,
            author="Unknown",
            publish_date=None,
            summary=""
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            success, display_title = vimeo_source.fetch_article_content(
                article, tmpdir
            )

            assert success
            assert display_title is not None
            assert display_title != "Vimeo Video"  # Should have real title

            # Check article file was created
            article_path = os.path.join(tmpdir, "article.md")
            assert os.path.exists(article_path)

            # Check content
            with open(article_path, 'r') as f:
                content = f.read()
                assert display_title in content
                assert test_url in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
