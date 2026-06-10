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


class TestLinkedImageWebUrls:
    """Linked images [![alt](local)](weburl) must replace outer web URL with local path."""

    def test_linked_image_outer_url_replaced(self):
        """[![alt](images/local.png "title")](https://web/local.png) -> link to local."""
        content = (
            '[![Hero](images/hero_1920x1080.png "Hero Image")]'
            "(https://substackcdn.com/image/fetch/f_auto/https%3A%2F%2Fexample.com%2Fimages%2Fhero_1920x1080.png)"
        )
        result = UnifiedMediaProcessor._replace_linked_image_urls(content)
        assert "https://substackcdn.com" not in result
        assert "[![Hero](images/hero_1920x1080.png" in result
        assert "](images/hero_1920x1080.png)" in result

    def test_linked_image_no_match_left_alone(self):
        """Linked images where filenames don't match are left alone."""
        content = (
            '[![Alt](images/local.png "title")]'
            "(https://example.com/unrelated-page)"
        )
        result = UnifiedMediaProcessor._replace_linked_image_urls(content)
        assert "https://example.com/unrelated-page" in result

    def test_multiple_linked_images(self):
        """Multiple linked images all get outer URLs replaced."""
        content = (
            '[![A](images/a_100x100.png "A")](https://cdn.example.com/fetch/a_100x100.png)\n'
            "Some text\n"
            '[![B](images/b_200x200.jpg "B")](https://cdn.example.com/fetch/q_auto/https%3A%2F%2Fmedia.com%2Fb_200x200.jpg)\n'
        )
        result = UnifiedMediaProcessor._replace_linked_image_urls(content)
        assert "https://cdn.example.com" not in result
        assert "](images/a_100x100.png)" in result
        assert "](images/b_200x200.jpg)" in result

    def test_plain_images_not_affected(self):
        """Non-linked images ![alt](path) are not modified."""
        content = '![Plain](images/photo.png "Photo")\nSome text.'
        result = UnifiedMediaProcessor._replace_linked_image_urls(content)
        assert content == result

    def test_integrated_with_download_inline_images(self):
        """Full pipeline: download + link replacement works end to end."""
        # Substack pattern: <a href="cdn_url_A"><img src="cdn_url_B" title="..."></a>
        # markdownify produces: [![alt](cdn_url_B "title")](cdn_url_A)
        cdn_img = "https://substackcdn.com/image/fetch/w_1456,c_limit/https%3A%2F%2Fmedia.com%2Fimages%2Fphoto_1920x1080.png"
        cdn_link = "https://substackcdn.com/image/fetch/f_auto/https%3A%2F%2Fmedia.com%2Fimages%2Fphoto_1920x1080.png"
        content = f'[![Shot]({cdn_img} "my shot")]({cdn_link})'
        article_folder = "/tmp/test_article"

        with patch("capcat.core.downloader.download_file") as mock_dl:
            mock_dl.return_value = "images/photo_1920x1080.png"
            result = UnifiedMediaProcessor._download_inline_images(
                content, article_folder, MagicMock(), {}, 10 * 1024 * 1024
            )

        # After Phase 1, inner URL replaced but outer link still web
        # _replace_linked_image_urls fixes the outer link
        result = UnifiedMediaProcessor._replace_linked_image_urls(result)
        assert "substackcdn.com" not in result
        assert "[![Shot](images/photo_1920x1080.png" in result
        assert "](images/photo_1920x1080.png)" in result
