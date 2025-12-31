#!/usr/bin/env python3
"""
Integration tests for batch processing with specialized sources.

Tests that fetch/bundle commands correctly detect and handle
Twitter/YouTube URLs found in source feeds (HN, BBC, etc.).
"""

import os
import tempfile
import shutil
import unittest
from unittest.mock import Mock, patch, MagicMock

from core.unified_source_processor import UnifiedSourceProcessor
from core.source_system.base_source import Article


class TestBatchSpecializedIntegration(unittest.TestCase):
    """Test batch commands with specialized sources."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
        self.processor = UnifiedSourceProcessor()

    def test_batch_processing_detects_twitter_url(self):
        """Batch processing should detect Twitter URL in article feed."""
        # Simulate article info from batch processing
        article_info = (
            1,  # index
            "Interesting Tweet",  # title
            "https://twitter.com/elonmusk/status/123456",  # url (Twitter!)
            None  # comment_url
        )

        source_config = {
            "display_name": "Hacker News"
        }

        # Mock the specialized source manager
        with patch('core.unified_article_processor.get_specialized_source_manager') as mock_mgr:
            mock_mgr_instance = MagicMock()
            mock_mgr_instance.can_handle_url.return_value = True

            # Mock Twitter source
            mock_twitter_source = MagicMock()
            mock_twitter_source.fetch_article_content.return_value = (True, "X.com post")
            mock_mgr_instance.get_source_for_url.return_value = (mock_twitter_source, "twitter")

            mock_mgr.return_value = mock_mgr_instance

            # Process article through batch pipeline
            success = self.processor._process_single_article(
                source_name="hn",
                source_config=source_config,
                article_info=article_info,
                base_dir=self.test_dir,
                download_files=False,
                progress_tracker=None
            )

            # Verify specialized source was activated
            self.assertTrue(success)
            mock_mgr_instance.can_handle_url.assert_called_with(
                "https://twitter.com/elonmusk/status/123456"
            )
            mock_twitter_source.fetch_article_content.assert_called_once()

    def test_batch_processing_detects_youtube_url(self):
        """Batch processing should detect YouTube URL in article feed."""
        article_info = (
            1,  # index
            "Cool Video",  # title
            "https://youtube.com/watch?v=dQw4w9WgXcQ",  # url (YouTube!)
            None  # comment_url
        )

        source_config = {
            "display_name": "BBC News"
        }

        # Mock the specialized source manager
        with patch('core.unified_article_processor.get_specialized_source_manager') as mock_mgr:
            mock_mgr_instance = MagicMock()
            mock_mgr_instance.can_handle_url.return_value = True

            # Mock YouTube source
            mock_youtube_source = MagicMock()
            mock_youtube_source.fetch_article_content.return_value = (True, "YouTube Video")
            mock_mgr_instance.get_source_for_url.return_value = (mock_youtube_source, "youtube")

            mock_mgr.return_value = mock_mgr_instance

            # Process article through batch pipeline
            success = self.processor._process_single_article(
                source_name="bbc",
                source_config=source_config,
                article_info=article_info,
                base_dir=self.test_dir,
                download_files=False,
                progress_tracker=None
            )

            # Verify specialized source was activated
            self.assertTrue(success)
            mock_mgr_instance.can_handle_url.assert_called_with(
                "https://youtube.com/watch?v=dQw4w9WgXcQ"
            )
            mock_youtube_source.fetch_article_content.assert_called_once()

    def test_batch_processing_detects_x_com_url(self):
        """Batch processing should detect x.com URL (new Twitter domain)."""
        article_info = (
            1,
            "X.com Post",
            "https://x.com/twitter/status/999999",  # x.com (new domain!)
            None
        )

        source_config = {"display_name": "Lobsters"}

        with patch('core.unified_article_processor.get_specialized_source_manager') as mock_mgr:
            mock_mgr_instance = MagicMock()
            mock_mgr_instance.can_handle_url.return_value = True

            mock_twitter_source = MagicMock()
            mock_twitter_source.fetch_article_content.return_value = (True, "X.com post")
            mock_mgr_instance.get_source_for_url.return_value = (mock_twitter_source, "twitter")

            mock_mgr.return_value = mock_mgr_instance

            success = self.processor._process_single_article(
                source_name="lobsters",
                source_config=source_config,
                article_info=article_info,
                base_dir=self.test_dir,
                download_files=False,
                progress_tracker=None
            )

            self.assertTrue(success)
            mock_mgr_instance.can_handle_url.assert_called_with(
                "https://x.com/twitter/status/999999"
            )

    def test_batch_processing_detects_youtu_be_short_url(self):
        """Batch processing should detect youtu.be short URLs."""
        article_info = (
            1,
            "Short Video Link",
            "https://youtu.be/abc123xyz",  # Short URL!
            None
        )

        source_config = {"display_name": "Hacker News"}

        with patch('core.unified_article_processor.get_specialized_source_manager') as mock_mgr:
            mock_mgr_instance = MagicMock()
            mock_mgr_instance.can_handle_url.return_value = True

            mock_youtube_source = MagicMock()
            mock_youtube_source.fetch_article_content.return_value = (True, "YouTube Video")
            mock_mgr_instance.get_source_for_url.return_value = (mock_youtube_source, "youtube")

            mock_mgr.return_value = mock_mgr_instance

            success = self.processor._process_single_article(
                source_name="hn",
                source_config=source_config,
                article_info=article_info,
                base_dir=self.test_dir,
                download_files=False,
                progress_tracker=None
            )

            self.assertTrue(success)
            mock_youtube_source.fetch_article_content.assert_called_once()

    def test_batch_processing_skips_specialized_for_regular_url(self):
        """Batch processing should skip specialized sources for regular URLs."""
        article_info = (
            1,
            "Regular Article",
            "https://example.com/article",  # Regular URL (not specialized)
            None
        )

        source_config = {
            "display_name": "Example Source",
            "module": "sources.generic"  # Has custom scraping
        }

        # Mock specialized manager to return False (not specialized)
        with patch('core.unified_article_processor.get_specialized_source_manager') as mock_mgr:
            mock_mgr_instance = MagicMock()
            mock_mgr_instance.can_handle_url.return_value = False  # Not specialized

            mock_mgr.return_value = mock_mgr_instance

            # Mock the generic processing path
            with patch.object(self.processor, '_process_article_custom') as mock_custom:
                mock_custom.return_value = True

                success = self.processor._process_single_article(
                    source_name="example",
                    source_config=source_config,
                    article_info=article_info,
                    base_dir=self.test_dir,
                    download_files=False,
                    progress_tracker=None
                )

                # Should use custom processing, not specialized
                mock_custom.assert_called_once()
                self.assertTrue(success)

    def test_batch_processing_with_mixed_urls(self):
        """Batch processing should handle mixed specialized and regular URLs."""
        articles = [
            (1, "Tweet", "https://twitter.com/user/status/1", None),
            (2, "Video", "https://youtube.com/watch?v=abc", None),
            (3, "Article", "https://example.com/article", None),
        ]

        source_config = {"display_name": "Test Source"}

        with patch('core.unified_article_processor.get_specialized_source_manager') as mock_mgr:
            mock_mgr_instance = MagicMock()

            # First two are specialized, third is not
            mock_mgr_instance.can_handle_url.side_effect = [True, True, False]

            # Mock specialized sources
            mock_twitter_source = MagicMock()
            mock_twitter_source.fetch_article_content.return_value = (True, "X.com post")

            mock_youtube_source = MagicMock()
            mock_youtube_source.fetch_article_content.return_value = (True, "YouTube Video")

            mock_mgr_instance.get_source_for_url.side_effect = [
                (mock_twitter_source, "twitter"),
                (mock_youtube_source, "youtube")
            ]

            mock_mgr.return_value = mock_mgr_instance

            # Mock generic processing for third article
            with patch.object(self.processor, '_process_article_generic') as mock_generic:
                mock_generic.return_value = True

                results = []
                for article_info in articles:
                    success = self.processor._process_single_article(
                        source_name="test",
                        source_config=source_config,
                        article_info=article_info,
                        base_dir=self.test_dir,
                        download_files=False,
                        progress_tracker=None
                    )
                    results.append(success)

                # All should succeed
                self.assertEqual(results, [True, True, True])

                # Specialized sources called for first two
                self.assertEqual(mock_twitter_source.fetch_article_content.call_count, 1)
                self.assertEqual(mock_youtube_source.fetch_article_content.call_count, 1)

                # Generic processing called for third
                mock_generic.assert_called_once()

    def test_batch_processing_respects_progress_callback(self):
        """Batch processing should pass progress callback to specialized sources."""
        article_info = (
            1,
            "Tweet with Progress",
            "https://twitter.com/user/status/123",
            None
        )

        source_config = {"display_name": "Test"}

        # Create mock progress tracker
        mock_progress_tracker = MagicMock()

        with patch('core.unified_article_processor.get_specialized_source_manager') as mock_mgr:
            mock_mgr_instance = MagicMock()
            mock_mgr_instance.can_handle_url.return_value = True

            mock_twitter_source = MagicMock()
            mock_twitter_source.fetch_article_content.return_value = (True, "X.com post")
            mock_mgr_instance.get_source_for_url.return_value = (mock_twitter_source, "twitter")

            mock_mgr.return_value = mock_mgr_instance

            success = self.processor._process_single_article(
                source_name="test",
                source_config=source_config,
                article_info=article_info,
                base_dir=self.test_dir,
                download_files=False,
                progress_tracker=mock_progress_tracker  # With tracker!
            )

            self.assertTrue(success)
            # Verify specialized handler was called
            mock_twitter_source.fetch_article_content.assert_called_once()


class TestArticleFetcherIntegration(unittest.TestCase):
    """Test ArticleFetcher integration with specialized sources."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def test_article_fetcher_detects_twitter_url(self):
        """ArticleFetcher should detect Twitter URLs."""
        from core.article_fetcher import ArticleFetcher
        from core.session_pool import get_global_session

        # Create a minimal ArticleFetcher subclass
        class TestArticleFetcher(ArticleFetcher):
            def should_skip_url(self, url: str, title: str) -> bool:
                return False

        session = get_global_session("test")
        fetcher = TestArticleFetcher(session, download_files=False)

        with patch('core.unified_article_processor.get_specialized_source_manager') as mock_mgr:
            mock_mgr_instance = MagicMock()
            mock_mgr_instance.can_handle_url.return_value = True

            mock_twitter_source = MagicMock()
            mock_twitter_source.fetch_article_content.return_value = (True, "X.com post")
            mock_mgr_instance.get_source_for_url.return_value = (mock_twitter_source, "twitter")

            mock_mgr.return_value = mock_mgr_instance

            # Mock get_global_update_mode to avoid import issues
            with patch('core.article_fetcher.get_global_update_mode') as mock_update_mode:
                mock_update_mode.return_value = False

                success, folder_path, title = fetcher.fetch_article_content(
                    title="Test Tweet",
                    url="https://twitter.com/user/status/123",
                    index=1,
                    base_folder=self.test_dir,
                    progress_callback=None
                )

                self.assertTrue(success)
                self.assertEqual(title, "X.com post")
                mock_twitter_source.fetch_article_content.assert_called_once()

    def test_article_fetcher_detects_youtube_url(self):
        """ArticleFetcher should detect YouTube URLs."""
        from core.article_fetcher import ArticleFetcher
        from core.session_pool import get_global_session

        class TestArticleFetcher(ArticleFetcher):
            def should_skip_url(self, url: str, title: str) -> bool:
                return False

        session = get_global_session("test")
        fetcher = TestArticleFetcher(session, download_files=False)

        with patch('core.unified_article_processor.get_specialized_source_manager') as mock_mgr:
            mock_mgr_instance = MagicMock()
            mock_mgr_instance.can_handle_url.return_value = True

            mock_youtube_source = MagicMock()
            mock_youtube_source.fetch_article_content.return_value = (True, "YouTube Video")
            mock_mgr_instance.get_source_for_url.return_value = (mock_youtube_source, "youtube")

            mock_mgr.return_value = mock_mgr_instance

            with patch('core.article_fetcher.get_global_update_mode') as mock_update_mode:
                mock_update_mode.return_value = False

                success, folder_path, title = fetcher.fetch_article_content(
                    title="Test Video",
                    url="https://youtube.com/watch?v=test123",
                    index=1,
                    base_folder=self.test_dir,
                    progress_callback=None
                )

                self.assertTrue(success)
                self.assertEqual(title, "YouTube Video")


if __name__ == "__main__":
    unittest.main(verbosity=2)
