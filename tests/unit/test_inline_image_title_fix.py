"""Tests for Phase 1 inline image download handling title attributes."""

import os
from unittest.mock import MagicMock, patch

import pytest

from capcat.core.unified_media_processor import UnifiedMediaProcessor


class TestInlineImageTitleAttribute:
    """Phase 1 regex must handle ![alt](url "title") patterns."""

    def test_title_attribute_url_extracted_cleanly(self):
        """Regex must not include the title string in the captured URL."""
        content = '![Chart](https://cdn.example.com/image.png "A chart showing growth")'
        article_folder = "/tmp/test_article"

        with patch("capcat.core.downloader.download_file") as mock_dl:
            mock_dl.return_value = "images/image.png"
            result = UnifiedMediaProcessor._download_inline_images(
                content, article_folder, MagicMock(), {}, 10 * 1024 * 1024
            )

        mock_dl.assert_called_once_with(
            "https://cdn.example.com/image.png",
            article_folder,
            "image",
            False,
        )
        assert 'images/image.png "A chart showing growth"' in result
        assert "https://cdn.example.com/image.png" not in result

    def test_no_title_attribute_still_works(self):
        """Images without title attributes must still be processed."""
        content = "![Photo](https://cdn.example.com/photo.jpg)"
        article_folder = "/tmp/test_article"

        with patch("capcat.core.downloader.download_file") as mock_dl:
            mock_dl.return_value = "images/photo.jpg"
            result = UnifiedMediaProcessor._download_inline_images(
                content, article_folder, MagicMock(), {}, 10 * 1024 * 1024
            )

        mock_dl.assert_called_once_with(
            "https://cdn.example.com/photo.jpg",
            article_folder,
            "image",
            False,
        )
        assert "images/photo.jpg" in result

    def test_mixed_title_and_no_title_images(self):
        """Content with both titled and untitled images processed correctly."""
        content = (
            '![A](https://cdn.example.com/a.png "Title A")\n'
            "![B](https://cdn.example.com/b.png)\n"
            '![C](https://cdn.example.com/c.jpg "Title C")\n'
        )
        article_folder = "/tmp/test_article"

        def fake_download(url, folder, ftype, media):
            basename = os.path.basename(url)
            return f"images/{basename}"

        with patch("capcat.core.downloader.download_file") as mock_dl:
            mock_dl.side_effect = fake_download
            result = UnifiedMediaProcessor._download_inline_images(
                content, article_folder, MagicMock(), {}, 10 * 1024 * 1024
            )

        assert mock_dl.call_count == 3
        assert "https://cdn.example.com/a.png" not in result
        assert "https://cdn.example.com/b.png" not in result
        assert "https://cdn.example.com/c.jpg" not in result
        assert "images/a.png" in result
        assert "images/b.png" in result
        assert "images/c.jpg" in result

    def test_substack_cdn_url_with_title(self):
        """Real Substack CDN URL with title attribute extracted correctly."""
        cdn_url = (
            "https://substackcdn.com/image/fetch/"
            "w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/"
            "https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com"
            "%2Fpublic%2Fimages%2Fabc123.png"
        )
        content = f'![Screenshot]({cdn_url} "my screenshot")'
        article_folder = "/tmp/test_article"

        with patch("capcat.core.downloader.download_file") as mock_dl:
            mock_dl.return_value = "images/abc123.png"
            result = UnifiedMediaProcessor._download_inline_images(
                content, article_folder, MagicMock(), {}, 10 * 1024 * 1024
            )

        mock_dl.assert_called_once_with(
            cdn_url,
            article_folder,
            "image",
            False,
        )
        assert cdn_url not in result
        assert "images/abc123.png" in result
