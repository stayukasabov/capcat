#!/usr/bin/env python3
"""
TDD Test Suite: Twitter Specialized Source

Test Cases:
1. URL pattern matching (twitter.com, x.com variations)
2. Placeholder article creation
3. Correct title generation ("X.com post")
4. Source URL preservation
5. Markdown content structure
6. Integration with specialized source registry
"""

import os
import tempfile
import shutil
import unittest

from sources.specialized.twitter.source import TwitterSource
from core.source_system.base_source import Article, ArticleDiscoveryError


class TestTwitterSpecializedSource(unittest.TestCase):
    """Test Twitter/X.com specialized source."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

        # Create minimal config
        self.config = type('Config', (), {
            'name': 'Twitter',
            'source_id': 'twitter'
        })()

        self.source = TwitterSource(self.config, None)

    def test_can_handle_twitter_com_urls(self):
        """Should detect twitter.com URLs."""
        test_urls = [
            "https://twitter.com/user/status/123",
            "http://twitter.com/user/status/456",
            "https://www.twitter.com/user/status/789",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                self.assertTrue(
                    TwitterSource.can_handle_url(url),
                    f"Should handle {url}"
                )

    def test_can_handle_x_com_urls(self):
        """Should detect x.com URLs."""
        test_urls = [
            "https://x.com/user/status/123",
            "http://x.com/user/status/456",
            "https://www.x.com/user/status/789",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                self.assertTrue(
                    TwitterSource.can_handle_url(url),
                    f"Should handle {url}"
                )

    def test_rejects_non_twitter_urls(self):
        """Should reject URLs that are not Twitter/X."""
        test_urls = [
            "https://youtube.com/watch?v=123",
            "https://facebook.com/post/123",
            "https://example.com/article",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                self.assertFalse(
                    TwitterSource.can_handle_url(url),
                    f"Should not handle {url}"
                )

    def test_creates_placeholder_article(self):
        """Should create placeholder article with correct structure."""
        article = Article(
            title="Some Twitter Post",
            url="https://twitter.com/user/status/123",
            summary=""
        )

        success, title = self.source.fetch_article_content(
            article, self.test_dir
        )

        self.assertTrue(success, "Should succeed")
        self.assertEqual(title, "X.com post")

        # Verify markdown file exists
        md_path = os.path.join(self.test_dir, "article.md")
        self.assertTrue(os.path.exists(md_path))

        # Verify content structure
        with open(md_path, 'r') as f:
            content = f.read()

        self.assertIn("# X.com post", content)
        self.assertIn(article.url, content)
        self.assertIn("Visit the original publication", content)

    def test_discovery_raises_error(self):
        """Should raise error for article discovery."""
        with self.assertRaises(ArticleDiscoveryError):
            self.source.discover_articles(10)

    def test_source_type_is_specialized(self):
        """Should identify as specialized source type."""
        self.assertEqual(self.source.source_type, "specialized")

    def test_placeholder_contains_source_url(self):
        """Should preserve original source URL in placeholder."""
        test_url = "https://x.com/elonmusk/status/999999"
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


class TestTwitterSourceRegistration(unittest.TestCase):
    """Test Twitter source registration in specialized registry."""

    def test_twitter_in_specialized_sources(self):
        """Should be registered in SPECIALIZED_SOURCES."""
        from sources.specialized import SPECIALIZED_SOURCES

        self.assertIn("twitter", SPECIALIZED_SOURCES)
        self.assertEqual(SPECIALIZED_SOURCES["twitter"], TwitterSource)

    def test_get_specialized_source_for_twitter_url(self):
        """Should return TwitterSource for Twitter URLs."""
        from sources.specialized import get_specialized_source_for_url

        test_urls = [
            "https://twitter.com/user/status/123",
            "https://x.com/user/status/456",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                source_class, source_id = get_specialized_source_for_url(url)
                self.assertEqual(source_class, TwitterSource)
                self.assertEqual(source_id, "twitter")


if __name__ == "__main__":
    unittest.main(verbosity=2)
