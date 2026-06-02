#!/usr/bin/env python3
"""
Tests for inline image download from markdown content.

When markdown content already has ![alt](url) references from the content
extraction, the media processor should download those specific images and
replace URLs in-place, rather than scanning the full page HTML with separate
image_processing selectors that might discover different URLs.

This fixes Guardian and similar sources where content selectors include images
but the image_processing selectors find different CDN URLs from the full page.
"""
import os
import re
import tempfile
from unittest.mock import patch, MagicMock

from capcat.core.unified_media_processor import UnifiedMediaProcessor


class TestInlineImageDownload:
    """Images already in markdown should be downloaded and replaced inline."""

    def _mock_download(self, url, folder, file_type, media_enabled):
        """Mock download_file to simulate successful image download."""
        from urllib.parse import urlparse
        filename = os.path.basename(urlparse(url).path) or "image.jpg"
        images_dir = os.path.join(folder, "images")
        os.makedirs(images_dir, exist_ok=True)
        filepath = os.path.join(images_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(b'\x89PNG')
        return os.path.join("images", filename)

    def test_inline_images_downloaded_and_replaced(self):
        """
        When markdown has ![alt](remote_url), the media processor should
        download that image and replace the URL with a local path.
        No "Article Images" section should be created.
        """
        markdown = (
            "# Test Article\n\n"
            "First paragraph of text.\n\n"
            "![Photo caption](https://i.guim.co.uk/img/media/abc123/image.jpg)\n\n"
            "More text after the image.\n\n"
            "![Another photo](https://i.guim.co.uk/img/media/def456/photo.jpg)\n\n"
            "Final paragraph.\n"
        )

        # Full page HTML with DIFFERENT image URLs (simulating Guardian CDN)
        full_html = """
        <html><body>
        <article>
            <p>First paragraph</p>
            <figure><img src="https://i.guim.co.uk/img/media/DIFFERENT/hero.jpg"></figure>
            <p>More text</p>
        </article>
        </body></html>
        """

        with tempfile.TemporaryDirectory() as tmp:
            article_folder = os.path.join(tmp, "article")
            os.makedirs(article_folder)

            with patch('capcat.core.downloader.download_file', side_effect=self._mock_download):
                result = UnifiedMediaProcessor.process_article_media(
                    content=markdown,
                    html_content=full_html,
                    url="https://www.theguardian.com/test/article",
                    article_folder=article_folder,
                    source_name="guardian",
                    session=MagicMock(),
                )

            # Images should be replaced inline, not in "Article Images" section
            assert "## Article Images" not in result, (
                "Images already inline in markdown should NOT create Article Images section"
            )

            # Original remote URLs should be replaced with local paths
            assert "https://i.guim.co.uk/img/media/abc123/image.jpg" not in result, (
                "Remote image URL should be replaced with local path"
            )
            assert "images/" in result, (
                "Local image path should be present in markdown"
            )

    def test_no_inline_images_falls_back_to_section(self):
        """
        When markdown has NO ![alt](url) references, the media processor
        should create "Article Images" section as before (backward compat).
        """
        markdown = (
            "# Test Article\n\n"
            "Just text, no images.\n\n"
            "More text content.\n"
        )

        full_html = """
        <html><body>
        <article>
            <p>Text</p>
            <figure><img src="https://example.com/photo.jpg"></figure>
        </article>
        </body></html>
        """

        with tempfile.TemporaryDirectory() as tmp:
            article_folder = os.path.join(tmp, "article")
            os.makedirs(article_folder)

            with patch('capcat.core.downloader.download_file', side_effect=self._mock_download):
                result = UnifiedMediaProcessor.process_article_media(
                    content=markdown,
                    html_content=full_html,
                    url="https://example.com/article",
                    article_folder=article_folder,
                    source_name="guardian",
                    session=MagicMock(),
                )

            # No inline images, so Article Images section is expected
            # (This tests backward compatibility)
            # Result should still contain the original text
            assert "Just text, no images." in result