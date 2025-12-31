#!/usr/bin/env python3
"""
TDD Test: MIT News AI Image Extraction

Test Case: Lazy-loaded image extraction from MIT News articles
Expected: Extract data-src URLs, not placeholder src URLs
Status: RED - Current implementation fetches placeholders
"""

import unittest
from unittest.mock import Mock
from bs4 import BeautifulSoup
from core.image_processor import ImageProcessor


class TestMITNewsImageExtraction(unittest.TestCase):
    """Test MIT News lazy-loaded image extraction."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = ImageProcessor()
        self.base_url = "https://news.mit.edu/2025/test-article"

        # Realistic MIT News HTML with lazy-loaded images
        self.html_content = """
        <article class="news-article">
            <div class="field--body">
                <img loading="lazy"
                     src="/themes/mit/src/img/placeholder/placeholder--news-article--image-gallery.jpg"
                     width="900" height="506"
                     alt="Robotic arm"
                     class="ondemand"
                     data-src="/sites/default/files/styles/news_article__image_gallery/public/images/202511/robot.jpg?itok=abc123">

                <img loading="lazy"
                     src="/themes/mit/src/img/placeholder/placeholder--news-article--image-gallery.jpg"
                     width="900" height="444"
                     alt="Assembly grid"
                     class="ondemand"
                     data-src="/sites/default/files/styles/news_article__image_gallery/public/images/202511/assembly.jpg?itok=def456">

                <img src="https://i1.ytimg.com/vi/GJQD86H9Nok/maxresdefault.jpg" alt="YouTube thumbnail">
            </div>
        </article>
        """

        # MIT News source configuration
        self.source_config = {
            "image_processing": {
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
                    ".author-image img"
                ]
            }
        }

    def test_extracts_data_src_over_placeholder_src(self):
        """
        RED TEST: Should extract data-src URLs for lazy-loaded images.

        Current behavior: Extracts placeholder src URLs
        Expected behavior: Extract data-src URLs when present
        """
        urls = self.processor._extract_image_urls(
            self.html_content,
            self.source_config["image_processing"],
            self.base_url
        )

        # Should extract data-src URLs, not placeholders
        # Note: YouTube URL filtered by url_patterns (only mit.edu allowed)
        self.assertEqual(len(urls), 2, "Should extract 2 MIT-hosted images")

        # Verify NO placeholder URLs
        placeholder_urls = [u for u in urls if "placeholder" in u]
        self.assertEqual(
            len(placeholder_urls), 0,
            f"Should not extract placeholder URLs, but found: {placeholder_urls}"
        )

        # Verify actual MIT image URLs are extracted (YouTube filtered out)
        expected_images = [
            "https://news.mit.edu/sites/default/files/styles/news_article__image_gallery/public/images/202511/robot.jpg?itok=abc123",
            "https://news.mit.edu/sites/default/files/styles/news_article__image_gallery/public/images/202511/assembly.jpg?itok=def456"
        ]

        for expected in expected_images:
            self.assertIn(
                expected, urls,
                f"Should extract {expected}"
            )

        # Verify external URLs filtered out per configuration
        youtube_urls = [u for u in urls if "ytimg.com" in u]
        self.assertEqual(
            len(youtube_urls), 0,
            "YouTube URLs should be filtered by url_patterns configuration"
        )

    def test_handles_images_with_only_src(self):
        """
        GREEN TEST: Should handle images with only src attribute.

        Images without data-src should use src attribute.
        """
        html = """
        <article>
            <img src="https://news.mit.edu/sites/default/files/direct-image.jpg" alt="Direct">
        </article>
        """

        urls = self.processor._extract_image_urls(
            html,
            self.source_config["image_processing"],
            self.base_url
        )

        self.assertEqual(len(urls), 1)
        self.assertIn("direct-image.jpg", urls[0])

    def test_prioritizes_data_src_when_both_present(self):
        """
        RED TEST: When both src and data-src present, prioritize data-src.

        This is the core fix needed for lazy-loaded images.
        """
        html = """
        <article>
            <img src="/placeholder.jpg"
                 data-src="https://news.mit.edu/sites/default/files/real-image.jpg"
                 alt="Lazy loaded">
        </article>
        """

        urls = self.processor._extract_image_urls(
            html,
            self.source_config["image_processing"],
            self.base_url
        )

        self.assertEqual(len(urls), 1)
        self.assertIn("real-image.jpg", urls[0])
        self.assertNotIn("placeholder.jpg", urls[0])

    def test_resolves_relative_data_src_urls(self):
        """
        GREEN TEST: Should resolve relative data-src URLs correctly.
        """
        html = """
        <article>
            <img src="/placeholder.jpg"
                 data-src="/sites/default/files/relative.jpg"
                 alt="Relative">
        </article>
        """

        urls = self.processor._extract_image_urls(
            html,
            self.source_config["image_processing"],
            self.base_url
        )

        self.assertEqual(len(urls), 1)
        self.assertTrue(
            urls[0].startswith("https://news.mit.edu/"),
            f"Should resolve to absolute URL, got: {urls[0]}"
        )
        self.assertIn("relative.jpg", urls[0])

    def test_filters_by_url_patterns_on_resolved_url(self):
        """
        GREEN TEST: URL pattern filtering should apply to resolved URL.

        After resolving data-src, the URL should pass pattern filtering.
        """
        html = """
        <article>
            <img data-src="/sites/default/files/mit-image.jpg" alt="MIT">
            <img data-src="https://external.com/image.jpg" alt="External">
        </article>
        """

        urls = self.processor._extract_image_urls(
            html,
            self.source_config["image_processing"],
            self.base_url
        )

        # Should only get MIT URL (matches url_patterns)
        self.assertEqual(len(urls), 1)
        self.assertIn("news.mit.edu", urls[0])
        self.assertNotIn("external.com", urls[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
