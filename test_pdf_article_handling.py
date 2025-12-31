#!/usr/bin/env python3
"""
TDD Test: PDF Article Handling

Test Cases:
1. Detect PDF URLs (Content-Type and .pdf extension)
2. Save original PDF file
3. Extract text content
4. Generate markdown and HTML outputs
"""

import os
import unittest
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch
import requests


class TestPDFArticleHandling(unittest.TestCase):
    """Test PDF article URL handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

        # Mock PDF content (simplified)
        self.pdf_content = b"%PDF-1.5\n%Test PDF content\nSample PDF article text"
        self.pdf_text = "%PDF-1.5\n%Test PDF content\nSample PDF article text"

    def test_detect_pdf_by_content_type(self):
        """Should detect PDF by Content-Type header."""
        # Simulate response with PDF Content-Type
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_response.content = self.pdf_content
        mock_response.text = self.pdf_text

        url = "https://arxiv.org/pdf/2503.18813"

        # Test detection logic
        content_type = mock_response.headers.get('Content-Type', '').lower()
        is_pdf = 'application/pdf' in content_type or url.lower().endswith('.pdf')

        self.assertTrue(is_pdf, "Should detect PDF by Content-Type")

    def test_detect_pdf_by_extension(self):
        """Should detect PDF by .pdf extension."""
        mock_response = Mock()
        mock_response.headers = {}  # No Content-Type
        mock_response.content = self.pdf_content
        mock_response.text = self.pdf_text

        url = "https://example.com/document.pdf"

        # Test detection logic
        content_type = mock_response.headers.get('Content-Type', '').lower()
        is_pdf = 'application/pdf' in content_type or url.lower().endswith('.pdf')

        self.assertTrue(is_pdf, "Should detect PDF by .pdf extension")

    def test_pdf_file_saved(self):
        """Should save original PDF file when article URL is PDF."""
        from core.article_fetcher import NewsSourceArticleFetcher

        # Create fetcher instance
        config = {
            'name': 'Test Source',
            'source_id': 'test',
            'category': 'tech'
        }
        fetcher = NewsSourceArticleFetcher(config, requests.Session())

        # Mock response with PDF content
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_response.content = self.pdf_content
        mock_response.text = self.pdf_text
        mock_response.status_code = 200

        # Mock _fetch_url_with_retry to return our mock response
        with patch.object(fetcher, '_fetch_url_with_retry', return_value=mock_response):
            # Fetch article
            success, title, folder = fetcher._fetch_web_content(
                title="Test PDF Article",
                url="https://arxiv.org/pdf/2503.18813",
                index=0,
                base_folder=self.test_dir
            )

        # Verify success
        self.assertTrue(success, "PDF article fetch should succeed")
        self.assertIsNotNone(folder, "Should return article folder path")

        # Verify PDF file exists
        pdf_path = os.path.join(folder, "article.pdf")
        self.assertTrue(
            os.path.exists(pdf_path),
            f"PDF file should be saved at {pdf_path}"
        )

        # Verify PDF content
        with open(pdf_path, 'rb') as f:
            saved_content = f.read()

        self.assertEqual(
            saved_content, self.pdf_content,
            "Saved PDF should match original content"
        )

    def test_pdf_markdown_generated(self):
        """Should generate markdown from PDF content."""
        from core.article_fetcher import NewsSourceArticleFetcher

        config = {
            'name': 'Test Source',
            'source_id': 'test',
            'category': 'tech'
        }
        fetcher = NewsSourceArticleFetcher(config, requests.Session())

        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_response.content = self.pdf_content
        mock_response.text = self.pdf_text
        mock_response.status_code = 200

        with patch.object(fetcher, '_fetch_url_with_retry', return_value=mock_response):
            success, title, folder = fetcher._fetch_web_content(
                title="Test PDF Article",
                url="https://arxiv.org/pdf/2503.18813",
                index=0,
                base_folder=self.test_dir
            )

        # Verify markdown file exists
        md_path = os.path.join(folder, "article.md")
        self.assertTrue(
            os.path.exists(md_path),
            "Markdown file should be generated"
        )

        # Verify markdown content
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        self.assertIn("# Test PDF Article", md_content)
        self.assertIn("https://arxiv.org/pdf/2503.18813", md_content)
        self.assertIn("PDF", md_content)

    def test_non_pdf_not_affected(self):
        """Should not trigger PDF handling for regular HTML articles."""
        url_html = "https://example.com/article.html"
        content_type = "text/html"

        is_pdf = (
            'application/pdf' in content_type.lower() or
            url_html.lower().endswith('.pdf')
        )

        self.assertFalse(is_pdf, "HTML articles should not be detected as PDF")


if __name__ == "__main__":
    unittest.main(verbosity=2)
