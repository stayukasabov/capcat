#!/usr/bin/env python3
"""
Unit tests for UnifiedArticleProcessor.

TDD Test Suite for unified article processing entry point.
Tests specialized source detection, URL validity checking, and update mode.
"""

import os
import tempfile
import shutil
import unittest
from unittest.mock import Mock, patch, MagicMock

from core.unified_article_processor import (
    UnifiedArticleProcessor,
    get_unified_processor
)
from core.source_system.base_source import Article


class TestUnifiedArticleProcessor(unittest.TestCase):
    """Test suite for unified article processing."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
        self.processor = UnifiedArticleProcessor()

    def test_twitter_url_activates_specialized(self):
        """Twitter URL should activate specialized handler."""
        # Mock the specialized manager at instance level
        mock_mgr_instance = MagicMock()
        mock_mgr_instance.can_handle_url.return_value = True

        # Mock Twitter source
        mock_twitter_source = MagicMock()
        mock_twitter_source.fetch_article_content.return_value = (True, "X.com post")
        mock_mgr_instance.get_source_for_url.return_value = (mock_twitter_source, "twitter")

        # Replace the specialized_manager attribute
        self.processor.specialized_manager = mock_mgr_instance

        success, title, path = self.processor.process_article(
            url="https://twitter.com/user/status/123",
            title="Test Tweet",
            index=1,
            base_folder=self.test_dir
        )

        self.assertTrue(success)
        self.assertEqual(title, "X.com post")
        mock_mgr_instance.can_handle_url.assert_called_with("https://twitter.com/user/status/123")

    def test_youtube_url_activates_specialized(self):
        """YouTube URL should activate specialized handler."""
        # Mock the specialized manager at instance level
        mock_mgr_instance = MagicMock()
        mock_mgr_instance.can_handle_url.return_value = True

        # Mock YouTube source
        mock_youtube_source = MagicMock()
        mock_youtube_source.fetch_article_content.return_value = (True, "YouTube Video")
        mock_mgr_instance.get_source_for_url.return_value = (mock_youtube_source, "youtube")

        # Replace the specialized_manager attribute
        self.processor.specialized_manager = mock_mgr_instance

        success, title, path = self.processor.process_article(
            url="https://youtube.com/watch?v=abc123",
            title="Test Video",
            index=1,
            base_folder=self.test_dir
        )

        self.assertTrue(success)
        self.assertEqual(title, "YouTube Video")

    def test_x_com_domain_detected(self):
        """x.com domain should be detected as Twitter."""
        mock_mgr_instance = MagicMock()
        mock_mgr_instance.can_handle_url.return_value = True

        mock_twitter_source = MagicMock()
        mock_twitter_source.fetch_article_content.return_value = (True, "X.com post")
        mock_mgr_instance.get_source_for_url.return_value = (mock_twitter_source, "twitter")

        self.processor.specialized_manager = mock_mgr_instance

        success, title, path = self.processor.process_article(
            url="https://x.com/user/status/123",
            title="Test X Post",
            index=1,
            base_folder=self.test_dir
        )

        self.assertTrue(success)

    def test_youtube_short_url_detected(self):
        """youtu.be short URL should be detected as YouTube."""
        mock_mgr_instance = MagicMock()
        mock_mgr_instance.can_handle_url.return_value = True

        mock_youtube_source = MagicMock()
        mock_youtube_source.fetch_article_content.return_value = (True, "YouTube Video")
        mock_mgr_instance.get_source_for_url.return_value = (mock_youtube_source, "youtube")

        self.processor.specialized_manager = mock_mgr_instance

        success, title, path = self.processor.process_article(
            url="https://youtu.be/abc123",
            title="Test Video",
            index=1,
            base_folder=self.test_dir
        )

        self.assertTrue(success)

    def test_url_validity_check_valid(self):
        """Valid URL should return True."""
        processor = UnifiedArticleProcessor()

        with patch('requests.head') as mock_head:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_head.return_value = mock_response

            is_valid = processor._check_url_validity("https://example.com")

            self.assertTrue(is_valid)
            mock_head.assert_called_once()

    def test_url_validity_check_404(self):
        """404 URL should return False."""
        processor = UnifiedArticleProcessor()

        with patch('requests.head') as mock_head:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_head.return_value = mock_response

            is_valid = processor._check_url_validity("https://example.com/404")

            self.assertFalse(is_valid)

    def test_url_validity_check_timeout(self):
        """Timeout should return False."""
        processor = UnifiedArticleProcessor()

        with patch('requests.head') as mock_head:
            import requests
            mock_head.side_effect = requests.Timeout()

            is_valid = processor._check_url_validity("http://192.0.2.1")

            self.assertFalse(is_valid)

    def test_update_mode_valid_url(self):
        """Update mode should update timestamp for valid URL."""
        # Create initial article
        article_dir = os.path.join(self.test_dir, "test_article")
        os.makedirs(article_dir, exist_ok=True)

        article_md = os.path.join(article_dir, "article.md")
        with open(article_md, "w") as f:
            f.write("# X.com post\n\nOriginal content")

        processor = UnifiedArticleProcessor()

        # Update timestamp
        processor._update_timestamp(article_dir)

        # Verify timestamp added
        with open(article_md, "r") as f:
            content = f.read()

        self.assertIn("Last Updated:", content)

    def test_update_mode_invalid_url_adds_warning(self):
        """Update mode should add warning for invalid URL."""
        # Create initial article
        article_dir = os.path.join(self.test_dir, "test_article")
        os.makedirs(article_dir, exist_ok=True)

        article_md = os.path.join(article_dir, "article.md")
        with open(article_md, "w") as f:
            f.write("# X.com post\n\nOriginal content")

        processor = UnifiedArticleProcessor()

        # Add URL warning
        test_url = "https://twitter.com/deleted/status/999"
        processor._add_url_warning(article_dir, test_url)

        # Verify warning added
        with open(article_md, "r") as f:
            content = f.read()

        self.assertIn("⚠️ Warning", content)
        self.assertIn("invalid or unreachable", content)
        self.assertIn(test_url, content)

    def test_update_timestamp_preserves_content(self):
        """Updating timestamp should preserve original content."""
        article_dir = os.path.join(self.test_dir, "test_article")
        os.makedirs(article_dir, exist_ok=True)

        original_content = "# X.com post\n\n**Source URL:** [url](url)\n\n---\n\nVisit the original publication.\n"

        article_md = os.path.join(article_dir, "article.md")
        with open(article_md, "w") as f:
            f.write(original_content)

        processor = UnifiedArticleProcessor()
        processor._update_timestamp(article_dir)

        with open(article_md, "r") as f:
            updated_content = f.read()

        # Original content should still be present
        self.assertIn("# X.com post", updated_content)
        self.assertIn("Visit the original publication", updated_content)
        # New timestamp should be added
        self.assertIn("Last Updated:", updated_content)

    def test_update_timestamp_updates_existing(self):
        """Updating timestamp should replace existing timestamp."""
        article_dir = os.path.join(self.test_dir, "test_article")
        os.makedirs(article_dir, exist_ok=True)

        content_with_timestamp = "# X.com post\n\n---\n\n**Last Updated:** 2025-01-01 00:00:00\n"

        article_md = os.path.join(article_dir, "article.md")
        with open(article_md, "w") as f:
            f.write(content_with_timestamp)

        processor = UnifiedArticleProcessor()
        processor._update_timestamp(article_dir)

        with open(article_md, "r") as f:
            updated_content = f.read()

        # Should have Last Updated, but not the old date
        self.assertIn("Last Updated:", updated_content)
        self.assertNotIn("2025-01-01 00:00:00", updated_content)
        # Should have only one "Last Updated" occurrence
        self.assertEqual(updated_content.count("Last Updated:"), 1)


class TestGetUnifiedProcessor(unittest.TestCase):
    """Test global instance getter."""

    def test_returns_singleton(self):
        """Should return singleton instance."""
        processor1 = get_unified_processor()
        processor2 = get_unified_processor()

        self.assertIs(processor1, processor2)

    def test_returns_unified_processor_instance(self):
        """Should return UnifiedArticleProcessor instance."""
        processor = get_unified_processor()

        self.assertIsInstance(processor, UnifiedArticleProcessor)


if __name__ == "__main__":
    unittest.main(verbosity=2)
