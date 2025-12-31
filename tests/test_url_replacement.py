#!/usr/bin/env python3
"""
Unit tests for URL replacement helper method in ArticleFetcher.

Tests the _create_markdown_link_replacement() method that consolidates
duplicate URL replacement logic and prevents f-string syntax errors.
"""

import unittest
from unittest.mock import Mock
import requests

# Import the class to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.article_fetcher import ArticleFetcher


class MockArticleFetcher(ArticleFetcher):
    """Mock implementation for testing purposes."""

    def should_skip_url(self, url: str, title: str) -> bool:
        """Mock implementation."""
        return False

    def fetch_article_content(self, url: str, title: str, article_folder_path: str):
        """Mock implementation."""
        pass


class TestURLReplacement(unittest.TestCase):
    """Test suite for _create_markdown_link_replacement() method."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = requests.Session()
        self.fetcher = MockArticleFetcher(
            session=self.session,
            download_files=False,
            source_code="test"
        )

    def tearDown(self):
        """Clean up after tests."""
        self.session.close()

    def test_basic_image_replacement(self):
        """Test basic image URL replacement."""
        content = "![](http://example.com/img.jpg)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "![image](images/img.jpg)")

    def test_basic_link_replacement(self):
        """Test basic link URL replacement."""
        content = "[](http://example.com/doc.pdf)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/doc.pdf",
            "files/doc.pdf",
            "document",
            is_image=False
        )
        self.assertEqual(result, "[document](files/doc.pdf)")

    def test_image_with_alt_text(self):
        """Test image replacement preserving existing alt text."""
        content = "![Photo of mountains](http://example.com/img.jpg)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "![Photo of mountains](images/img.jpg)")

    def test_link_with_text(self):
        """Test link replacement preserving existing link text."""
        content = "[Download Report](http://example.com/doc.pdf)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/doc.pdf",
            "files/doc.pdf",
            "document",
            is_image=False
        )
        self.assertEqual(result, "[Download Report](files/doc.pdf)")

    def test_multiple_occurrences(self):
        """Test replacement of multiple instances of same URL."""
        content = (
            "![](http://example.com/img.jpg) and "
            "![](http://example.com/img.jpg)"
        )
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        expected = (
            "![image](images/img.jpg) and "
            "![image](images/img.jpg)"
        )
        self.assertEqual(result, expected)

    def test_url_with_special_regex_characters(self):
        """Test URL with special regex characters (parentheses, dots, etc.)."""
        content = "![](http://example.com/path?query=1&param=2)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/path?query=1&param=2",
            "images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "![image](images/img.jpg)")

    def test_direct_url_in_parentheses(self):
        """Test replacement of direct URL in markdown parentheses."""
        content = "Check this ](http://example.com/img.jpg)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "Check this ](images/img.jpg)")

    def test_standalone_url_replacement(self):
        """Test replacement of standalone URL in text."""
        content = "The image is at http://example.com/img.jpg here"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "The image is at images/img.jpg here")

    def test_empty_alt_text_uses_fallback(self):
        """Test that empty alt text uses fallback text."""
        content = "![](http://example.com/img.jpg)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "Custom Fallback",
            is_image=True
        )
        self.assertEqual(result, "![Custom Fallback](images/img.jpg)")

    def test_preserves_non_matching_content(self):
        """Test that non-matching content is preserved."""
        content = (
            "# Title\n\n"
            "Some text here.\n\n"
            "![](http://example.com/img.jpg)\n\n"
            "More text here."
        )
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        expected = (
            "# Title\n\n"
            "Some text here.\n\n"
            "![image](images/img.jpg)\n\n"
            "More text here."
        )
        self.assertEqual(result, expected)

    def test_mixed_image_and_link_syntax(self):
        """Test handling of both image and link syntax for same URL."""
        # When processing an image with is_image=True, only ![url] is replaced
        # Regular [url] link syntax is preserved as-is
        content = (
            "![Original](http://example.com/img.jpg) and "
            "[Link](http://example.com/img.jpg)"
        )
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        # Image syntax should be replaced with local path
        self.assertIn("![Original](images/img.jpg)", result)
        # Link syntax should also be replaced (Strategy 3 replaces all instances)
        self.assertIn("[Link](images/img.jpg)", result)

    def test_complex_url_with_path_and_query(self):
        """Test complex URL with path segments and query parameters."""
        url = "https://cdn.example.com/media/2024/01/image-name.jpg?size=large&format=webp"
        content = f"![Photo]({url})"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            url,
            "images/image-name.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "![Photo](images/image-name.jpg)")

    def test_relative_local_path(self):
        """Test with relative local path."""
        content = "![](http://example.com/img.jpg)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "../images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "![image](../images/img.jpg)")

    def test_absolute_local_path(self):
        """Test with absolute local path."""
        content = "![](http://example.com/img.jpg)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "/var/www/images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "![image](/var/www/images/img.jpg)")

    def test_document_link_not_converted_to_image(self):
        """Test that document links maintain link syntax."""
        content = "[Download](http://example.com/doc.pdf)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/doc.pdf",
            "files/doc.pdf",
            "document",
            is_image=False
        )
        # Should be link syntax, not image syntax
        self.assertEqual(result, "[Download](files/doc.pdf)")
        self.assertNotIn("![", result)

    def test_no_replacement_when_url_not_found(self):
        """Test that content is unchanged when URL not found."""
        content = "![Different](http://other.com/img.jpg)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        # Content should be unchanged
        self.assertEqual(result, content)

    def test_unicode_characters_in_alt_text(self):
        """Test handling of Unicode characters in alt text."""
        content = "![Café ☕ photo](http://example.com/img.jpg)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "![Café ☕ photo](images/img.jpg)")

    def test_protocol_relative_url(self):
        """Test handling of protocol-relative URLs."""
        content = "![](//cdn.example.com/img.jpg)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "//cdn.example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "![image](images/img.jpg)")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = requests.Session()
        self.fetcher = MockArticleFetcher(
            session=self.session,
            download_files=False,
            source_code="test"
        )

    def tearDown(self):
        """Clean up after tests."""
        self.session.close()

    def test_empty_content(self):
        """Test with empty content string."""
        result = self.fetcher._create_markdown_link_replacement(
            "",
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "")

    def test_empty_url(self):
        """Test with empty URL (should not crash)."""
        content = "![Test]()"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "",
            "images/img.jpg",
            "image",
            is_image=True
        )
        # Should handle gracefully
        self.assertIsInstance(result, str)

    def test_whitespace_in_alt_text(self):
        """Test alt text with whitespace."""
        content = "![  Multiple   Spaces  ](http://example.com/img.jpg)"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "![  Multiple   Spaces  ](images/img.jpg)")

    def test_newlines_in_content(self):
        """Test content with various newline styles."""
        content = "Text\n![](http://example.com/img.jpg)\nMore"
        result = self.fetcher._create_markdown_link_replacement(
            content,
            "http://example.com/img.jpg",
            "images/img.jpg",
            "image",
            is_image=True
        )
        self.assertEqual(result, "Text\n![image](images/img.jpg)\nMore")


def run_tests():
    """Run all tests and display results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestURLReplacement))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code based on results
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())
