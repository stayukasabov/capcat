"""
Tests that audio/video MIME types are derived from file extension, not hardcoded.

Bug: _handle_media_file hardcodes audio/mpeg and video/mp4 in HTML tags.
Files served as .ogg, .wav, .webm, .mov produce non-functional players.

Fix: use mimetypes.guess_type() to derive the correct MIME type.
"""
from unittest.mock import MagicMock, patch
import os

import pytest


def _make_fetcher():
    """Create an ArticleFetcher subclass with mocked dependencies."""
    with (
        patch("capcat.core.article_fetcher.get_config"),
        patch("capcat.core.article_fetcher.initialize_pdf_manager"),
        patch("capcat.core.ethical_scraping.get_ethical_manager"),
    ):
        from capcat.core.article_fetcher import HackerNewsArticleFetcher
        return HackerNewsArticleFetcher(MagicMock())


class TestDynamicMimeTypes:
    """Audio/video HTML tags must use MIME types matching the file extension."""

    @pytest.mark.parametrize("url,expected_mime", [
        ("https://example.com/podcast.ogg", "audio/ogg"),
        ("https://example.com/podcast.mp3", "audio/mpeg"),
    ])
    def test_audio_mime_type_matches_extension(self, tmp_path, url, expected_mime):
        """Audio tag type attribute must match the file's actual MIME type."""
        fetcher = _make_fetcher()

        # Mock download_file to return a local path
        ext = os.path.splitext(url)[1]
        local_path = f"files/podcast{ext}"

        with patch("capcat.core.article_fetcher.download_file", return_value=local_path):
            success, title, folder = fetcher._handle_media_file(
                "Test Audio", url, 0, str(tmp_path), "audio"
            )

        assert success
        md_path = os.path.join(folder, os.listdir(folder)[0])
        content = open(md_path).read()
        assert f'type="{expected_mime}"' in content, (
            f"Expected MIME type {expected_mime} for {url}, got hardcoded type in:\n{content}"
        )

    @pytest.mark.parametrize("url,expected_mime", [
        ("https://example.com/clip.webm", "video/webm"),
        ("https://example.com/clip.mov", "video/quicktime"),
        ("https://example.com/clip.mp4", "video/mp4"),
        ("https://example.com/clip.ogv", "video/ogg"),
    ])
    def test_video_mime_type_matches_extension(self, tmp_path, url, expected_mime):
        """Video tag type attribute must match the file's actual MIME type."""
        fetcher = _make_fetcher()

        ext = os.path.splitext(url)[1]
        local_path = f"files/clip{ext}"

        with patch("capcat.core.article_fetcher.download_file", return_value=local_path):
            success, title, folder = fetcher._handle_media_file(
                "Test Video", url, 0, str(tmp_path), "video"
            )

        assert success
        md_path = os.path.join(folder, os.listdir(folder)[0])
        content = open(md_path).read()
        assert f'type="{expected_mime}"' in content, (
            f"Expected MIME type {expected_mime} for {url}, got hardcoded type in:\n{content}"
        )
