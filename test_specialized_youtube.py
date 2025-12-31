#!/usr/bin/env python3
"""
TDD Test Suite: YouTube Specialized Source

Test Cases:
1. URL pattern matching (youtube.com, youtu.be, m.youtube.com)
2. Placeholder article creation
3. Correct title generation ("YouTube Video")
4. Source URL preservation
5. Markdown content structure
6. Integration with specialized source registry
"""

import os
import tempfile
import shutil
import unittest
from unittest.mock import patch

from sources.specialized.youtube.source import YouTubeSource
from core.source_system.base_source import Article, ArticleDiscoveryError


class TestYouTubeSpecializedSource(unittest.TestCase):
    """Test YouTube specialized source."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

        # Create minimal config
        self.config = type('Config', (), {
            'name': 'YouTube',
            'source_id': 'youtube'
        })()

        self.source = YouTubeSource(self.config, None)

    def test_can_handle_youtube_com_urls(self):
        """Should detect youtube.com URLs."""
        test_urls = [
            "https://youtube.com/watch?v=abc123",
            "http://youtube.com/watch?v=def456",
            "https://www.youtube.com/watch?v=ghi789",
            "https://youtube.com/embed/jkl012",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                self.assertTrue(
                    YouTubeSource.can_handle_url(url),
                    f"Should handle {url}"
                )

    def test_can_handle_youtu_be_urls(self):
        """Should detect youtu.be short URLs."""
        test_urls = [
            "https://youtu.be/abc123",
            "http://youtu.be/def456",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                self.assertTrue(
                    YouTubeSource.can_handle_url(url),
                    f"Should handle {url}"
                )

    def test_can_handle_mobile_youtube_urls(self):
        """Should detect m.youtube.com mobile URLs."""
        test_urls = [
            "https://m.youtube.com/watch?v=abc123",
            "http://m.youtube.com/watch?v=def456",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                self.assertTrue(
                    YouTubeSource.can_handle_url(url),
                    f"Should handle {url}"
                )

    def test_rejects_non_youtube_urls(self):
        """Should reject URLs that are not YouTube."""
        test_urls = [
            "https://twitter.com/user/status/123",
            "https://vimeo.com/123456",
            "https://example.com/video",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                self.assertFalse(
                    YouTubeSource.can_handle_url(url),
                    f"Should not handle {url}"
                )

    def test_creates_placeholder_article(self):
        """Should create placeholder article with extracted title."""
        article = Article(
            title="Some YouTube Video",
            url="https://youtube.com/watch?v=test123",
            summary=""
        )

        # Mock title extraction to return a specific title
        with patch.object(self.source, '_extract_video_title', return_value="Amazing Video Title"):
            success, title = self.source.fetch_article_content(
                article, self.test_dir
            )

            self.assertTrue(success, "Should succeed")
            self.assertEqual(title, "Amazing Video Title")

            # Verify markdown file exists
            md_path = os.path.join(self.test_dir, "article.md")
            self.assertTrue(os.path.exists(md_path))

            # Verify content structure
            with open(md_path, 'r') as f:
                content = f.read()

            self.assertIn("# Amazing Video Title", content)
            self.assertIn(article.url, content)
            self.assertIn("Visit the original link", content)

    def test_creates_placeholder_with_fallback_title(self):
        """Should use fallback title when extraction fails."""
        article = Article(
            title="Some YouTube Video",
            url="https://youtube.com/watch?v=test123",
            summary=""
        )

        # Mock title extraction to return None (extraction failed)
        with patch.object(self.source, '_extract_video_title', return_value=None):
            success, title = self.source.fetch_article_content(
                article, self.test_dir
            )

            self.assertTrue(success, "Should succeed")
            self.assertEqual(title, "YouTube Video")

            # Verify markdown file exists
            md_path = os.path.join(self.test_dir, "article.md")
            self.assertTrue(os.path.exists(md_path))

            # Verify content structure
            with open(md_path, 'r') as f:
                content = f.read()

            self.assertIn("# YouTube Video", content)
            self.assertIn(article.url, content)
            self.assertIn("Visit the original link", content)

    def test_discovery_raises_error(self):
        """Should raise error for article discovery."""
        with self.assertRaises(ArticleDiscoveryError):
            self.source.discover_articles(10)

    def test_source_type_is_specialized(self):
        """Should identify as specialized source type."""
        self.assertEqual(self.source.source_type, "specialized")

    def test_placeholder_contains_source_url(self):
        """Should preserve original source URL in placeholder."""
        test_url = "https://youtu.be/dQw4w9WgXcQ"
        article = Article(
            title="Test",
            url=test_url,
            summary=""
        )

        self.source.fetch_article_content(article, self.test_dir)

        md_path = os.path.join(self.test_dir, "article.md")
        with open(md_path, 'r') as f:
            content = f.read()

        self.assertIn(test_url, content)
        self.assertIn(f"[{test_url}]({test_url})", content)


class TestYouTubeSourceRegistration(unittest.TestCase):
    """Test YouTube source registration in specialized registry."""

    def test_youtube_in_specialized_sources(self):
        """Should be registered in SPECIALIZED_SOURCES."""
        from sources.specialized import SPECIALIZED_SOURCES

        self.assertIn("youtube", SPECIALIZED_SOURCES)
        self.assertEqual(SPECIALIZED_SOURCES["youtube"], YouTubeSource)

    def test_get_specialized_source_for_youtube_url(self):
        """Should return YouTubeSource for YouTube URLs."""
        from sources.specialized import get_specialized_source_for_url

        test_urls = [
            "https://youtube.com/watch?v=abc123",
            "https://youtu.be/def456",
            "https://m.youtube.com/watch?v=ghi789",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                source_class, source_id = get_specialized_source_for_url(url)
                self.assertEqual(source_class, YouTubeSource)
                self.assertEqual(source_id, "youtube")


if __name__ == "__main__":
    unittest.main(verbosity=2)
