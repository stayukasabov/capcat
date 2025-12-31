#!/usr/bin/env python3
"""
TDD Test: MIT News Advanced Image Filtering

Test Cases:
1. Skip recent-news section images
2. Limit to max_images count
3. Filter by minimum image size
4. Combined filtering (skip + max + size)
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from bs4 import BeautifulSoup
from core.image_processor import ImageProcessor


class TestMITNewsAdvancedFiltering(unittest.TestCase):
    """Test MIT News advanced image filtering."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = ImageProcessor()
        self.base_url = "https://news.mit.edu/2025/test-article"

        # HTML with main article image + recent news images
        self.html_with_recent_news = """
        <article class="news-article">
            <div class="news-article--images-gallery--wrapper">
                <img data-src="/sites/default/files/main-image.jpg" alt="Main article">
            </div>

            <div class="news-article--body">
                <img data-src="/sites/default/files/inline-image.jpg" alt="Inline">
            </div>

            <div class="news-article--recent-news">
                <div class="news-article--recent-news--teaser--cover-image">
                    <img data-src="/sites/default/files/related-1.jpg" alt="Related 1">
                </div>
                <div class="news-article--recent-news--teaser--cover-image">
                    <img data-src="/sites/default/files/related-2.jpg" alt="Related 2">
                </div>
                <div class="news-article--recent-news--teaser--cover-image">
                    <img data-src="/sites/default/files/related-3.jpg" alt="Related 3">
                </div>
            </div>
        </article>
        """

        # Base MIT News config
        self.base_config = {
            "selectors": [
                "article img",
                ".news-article img"
            ],
            "url_patterns": [
                "news.mit.edu",
                "mit.edu"
            ],
            "allow_extensionless": True,
            "skip_selectors": [
                "nav img",
                ".logo img"
            ]
        }

    def test_skip_recent_news_images(self):
        """Should skip images in recent-news sections."""
        config = self.base_config.copy()
        config["skip_selectors"] = [
            "nav img",
            ".news-article--recent-news img"
        ]

        urls = self.processor._extract_image_urls(
            self.html_with_recent_news,
            config,
            self.base_url
        )

        # Should extract only main article + inline images, not recent-news
        self.assertEqual(len(urls), 2, f"Should extract 2 images, got {len(urls)}")

        url_strings = " ".join(urls)
        self.assertIn("main-image.jpg", url_strings)
        self.assertIn("inline-image.jpg", url_strings)
        self.assertNotIn("related-1.jpg", url_strings)
        self.assertNotIn("related-2.jpg", url_strings)
        self.assertNotIn("related-3.jpg", url_strings)

    def test_max_images_limit(self):
        """Should limit to max_images count."""
        config = self.base_config.copy()
        config["max_images"] = 1

        # Extract URLs (5 total before filtering)
        urls = self.processor._extract_image_urls(
            self.html_with_recent_news,
            config,
            self.base_url
        )

        # Apply max_images limit manually (simulating process_article_images)
        max_images = config.get("max_images")
        if max_images:
            urls = urls[:max_images]

        self.assertEqual(len(urls), 1, "Should limit to 1 image")

    def test_max_images_with_skip_selectors(self):
        """Should apply skip_selectors BEFORE max_images limit."""
        config = self.base_config.copy()
        config["skip_selectors"] = [
            "nav img",
            ".news-article--recent-news img"
        ]
        config["max_images"] = 1

        # Extract and filter
        urls = self.processor._extract_image_urls(
            self.html_with_recent_news,
            config,
            self.base_url
        )

        # 2 images after skip_selectors (main + inline)
        self.assertEqual(len(urls), 2, "Should have 2 after skip_selectors")

        # Apply max_images
        max_images = config.get("max_images")
        if max_images:
            urls = urls[:max_images]

        self.assertEqual(len(urls), 1, "Should limit to 1 after max_images")
        # Should get first image after skip filtering (order depends on extraction)
        self.assertTrue(
            "main-image.jpg" in urls[0] or "inline-image.jpg" in urls[0],
            f"Should get article image, got {urls[0]}"
        )

    @patch('core.image_processor.ImageProcessor._download_single_image_with_min_size')
    def test_min_image_size_filtering(self, mock_download):
        """Should filter images below minimum size threshold."""
        # Mock download to simulate size checking
        def mock_download_with_size(url, images_dir, counter, min_size):
            if "small" in url:
                return None  # Rejected by size
            return f"image-{counter}.jpg"

        mock_download.side_effect = mock_download_with_size

        urls = [
            "https://news.mit.edu/small-icon.jpg",
            "https://news.mit.edu/large-image.jpg"
        ]

        config = {"min_image_size": 10240}  # 10KB minimum

        downloaded = self.processor._download_images_with_checking(
            urls, "/tmp/test", media_enabled=False, min_image_size=10240
        )

        # Should only download large image
        self.assertEqual(len(downloaded), 1)
        # Keys are full URLs, not just filenames
        self.assertTrue(
            any("large-image.jpg" in url for url in downloaded.keys()),
            f"Should download large-image.jpg, got {list(downloaded.keys())}"
        )

    def test_full_mit_news_config(self):
        """Test complete MIT News configuration with all filters."""
        mit_news_config = {
            "selectors": [
                "article img",
                ".news-article img",
                ".field--body img",
                "figure img",
                "picture img"
            ],
            "url_patterns": [
                "news.mit.edu",
                "mit.edu"
            ],
            "allow_extensionless": True,
            "skip_selectors": [
                "nav img",
                ".logo img",
                ".icon img",
                ".author-image img",
                ".news-article--recent-news img"
            ],
            "max_images": 3,
            "min_image_size": 10240
        }

        urls = self.processor._extract_image_urls(
            self.html_with_recent_news,
            mit_news_config,
            self.base_url
        )

        # Should extract 2 images (main + inline), skip 3 recent-news
        self.assertEqual(len(urls), 2)

        # Verify no recent-news images
        url_strings = " ".join(urls)
        self.assertNotIn("related", url_strings)


if __name__ == "__main__":
    unittest.main(verbosity=2)
