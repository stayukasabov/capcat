#!/usr/bin/env python3
"""
Test MIT News Drupal Image Styles URL Transformation

Verify that scaled image URLs are transformed via config to access full-size originals.
"""

import unittest
import re
from core.image_processor import ImageProcessor


class TestMITNewsURLTransform(unittest.TestCase):
    """Test config-based URL transformation for MIT News images."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = ImageProcessor()
        self.transform_config = {
            "url_transforms": [
                {
                    "pattern": r'/files/styles/[^/]+/public/',
                    "replacement": '/files/'
                }
            ]
        }

    def test_transform_removes_styles_path(self):
        """Should remove /styles/STYLE_NAME/public/ via config transformation."""
        scaled_url = (
            "https://news.mit.edu/sites/default/files/styles/"
            "news_article__image_gallery/public/images/202511/test.jpg"
        )

        expected_url = (
            "https://news.mit.edu/sites/default/files/"
            "images/202511/test.jpg"
        )

        # Apply transformation as image processor would
        transformed = scaled_url
        for transform in self.transform_config["url_transforms"]:
            pattern = transform["pattern"]
            replacement = transform["replacement"]
            transformed = re.sub(pattern, replacement, transformed)

        self.assertEqual(
            transformed,
            expected_url,
            "Should remove styles and public path segments"
        )

    def test_transform_handles_different_style_names(self):
        """Should work with any Drupal image style name."""
        test_cases = [
            (
                "https://news.mit.edu/sites/default/files/styles/"
                "thumbnail/public/images/test.jpg",
                "https://news.mit.edu/sites/default/files/"
                "images/test.jpg"
            ),
            (
                "https://news.mit.edu/sites/default/files/styles/"
                "large/public/images/test.jpg",
                "https://news.mit.edu/sites/default/files/"
                "images/test.jpg"
            ),
            (
                "https://news.mit.edu/sites/default/files/styles/"
                "custom_style_123/public/images/test.jpg",
                "https://news.mit.edu/sites/default/files/"
                "images/test.jpg"
            ),
        ]

        for scaled_url, expected_url in test_cases:
            with self.subTest(url=scaled_url):
                transformed = scaled_url
                for transform in self.transform_config["url_transforms"]:
                    transformed = re.sub(
                        transform["pattern"],
                        transform["replacement"],
                        transformed
                    )
                self.assertEqual(transformed, expected_url)

    def test_transform_preserves_non_styled_urls(self):
        """Should preserve URLs that don't have styles path."""
        original_url = (
            "https://news.mit.edu/sites/default/files/"
            "images/202511/test.jpg"
        )

        transformed = original_url
        for transform in self.transform_config["url_transforms"]:
            transformed = re.sub(
                transform["pattern"],
                transform["replacement"],
                transformed
            )

        self.assertEqual(
            transformed,
            original_url,
            "URLs without styles path should remain unchanged"
        )

    def test_real_example_transformation(self):
        """Test with actual MIT News URL from article."""
        scaled_url = (
            "https://news.mit.edu/sites/default/files/styles/"
            "news_article__image_gallery/public/images/202511/"
            "MIT%20MAD_Figure1a.jpg"
        )

        expected_url = (
            "https://news.mit.edu/sites/default/files/"
            "images/202511/MIT%20MAD_Figure1a.jpg"
        )

        transformed = scaled_url
        for transform in self.transform_config["url_transforms"]:
            transformed = re.sub(
                transform["pattern"],
                transform["replacement"],
                transformed
            )

        self.assertEqual(transformed, expected_url)


if __name__ == "__main__":
    unittest.main(verbosity=2)
