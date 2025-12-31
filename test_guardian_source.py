"""
Test suite for The Guardian news source.

Following TDD Red-Green-Refactor methodology.
These tests should FAIL initially until implementation is complete.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.source_system.source_registry import get_source_registry


class TestGuardianSourceDiscovery(unittest.TestCase):
    """Test Guardian source registration and discovery."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = get_source_registry()

    def test_guardian_source_exists(self):
        """Test that guardian source is registered in the system."""
        available = self.registry.get_available_sources()
        self.assertIn(
            'guardian',
            available,
            "Guardian source should be discoverable in source registry"
        )

    def test_guardian_source_instantiation(self):
        """Test that guardian source can be instantiated."""
        source = self.registry.get_source('guardian')
        self.assertIsNotNone(source, "Guardian source should instantiate")

    def test_guardian_config_values(self):
        """Test guardian configuration has correct values."""
        source = self.registry.get_source('guardian')

        # Display name
        self.assertEqual(
            source.config.display_name,
            "The Guardian",
            "Display name should be 'The Guardian'"
        )

        # Category
        self.assertEqual(
            source.config.category,
            "news",
            "Guardian should be categorized as news"
        )

        # Base URL
        self.assertTrue(
            source.config.base_url.startswith('https://'),
            "Base URL must use HTTPS"
        )
        self.assertIn(
            'theguardian.com',
            source.config.base_url,
            "Base URL should point to theguardian.com"
        )

    def test_guardian_rate_limiting(self):
        """Test that guardian respects ethical rate limiting."""
        source = self.registry.get_source('guardian')
        self.assertGreaterEqual(
            source.config.rate_limit,
            1.0,
            "Rate limit should be at least 1 second (ethical scraping)"
        )


class TestGuardianRSSIntegration(unittest.TestCase):
    """Test Guardian RSS feed integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = get_source_registry()
        self.source = self.registry.get_source('guardian')

    def test_guardian_has_rss_config(self):
        """Test that guardian source has RSS configuration."""
        self.assertIsNotNone(
            self.source.config.custom_config.get('rss_config'),
            "Guardian should have RSS configuration"
        )

    def test_guardian_rss_feed_url(self):
        """Test that RSS feed URL is correctly configured."""
        rss_config = self.source.config.custom_config.get('rss_config', {})
        feed_url = rss_config.get('feed_url', '')

        self.assertIn(
            'theguardian.com',
            feed_url,
            "RSS feed URL should point to theguardian.com"
        )
        self.assertIn(
            '/rss',
            feed_url,
            "RSS feed URL should contain /rss path"
        )


class TestGuardianArticleFetching(unittest.TestCase):
    """Test Guardian article fetching functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = get_source_registry()
        self.source = self.registry.get_source('guardian')

    def test_guardian_fetch_articles(self):
        """Test fetching articles from Guardian."""
        articles = self.source.get_articles(count=5)

        # Should return articles
        self.assertGreater(
            len(articles),
            0,
            "Should fetch at least one article"
        )

        # Should not exceed requested count
        self.assertLessEqual(
            len(articles),
            5,
            "Should not exceed requested article count"
        )

    def test_guardian_article_structure(self):
        """Test that fetched articles have correct structure."""
        articles = self.source.get_articles(count=3)

        self.assertGreater(len(articles), 0, "Should have articles to test")

        for article in articles:
            # Required fields
            self.assertIn('title', article, "Article must have title")
            self.assertIn('url', article, "Article must have URL")

            # Title should not be empty
            self.assertTrue(
                article['title'],
                "Article title should not be empty"
            )

            # URL should be valid Guardian URL
            self.assertTrue(
                article['url'].startswith('https://'),
                "Article URL should use HTTPS"
            )
            self.assertIn(
                'theguardian.com',
                article['url'],
                "Article URL should be from theguardian.com"
            )

    def test_guardian_fetch_article_content(self):
        """Test fetching individual article content."""
        articles = self.source.get_articles(count=1)

        self.assertGreater(
            len(articles),
            0,
            "Need at least one article to test content fetching"
        )

        article_url = articles[0]['url']
        content = self.source.get_article_content(article_url)

        # Content should exist
        self.assertIsNotNone(
            content,
            "Article content should not be None"
        )

        # Content should be substantial
        self.assertGreater(
            len(content),
            200,
            "Article content should be substantial (>200 characters)"
        )

    def test_guardian_no_comments_support(self):
        """Test that guardian source does not claim to support comments."""
        # Guardian robots.txt disallows /discussion/*
        # So we should not support comments
        self.assertFalse(
            self.source.config.supports_comments,
            "Guardian should not support comments (robots.txt restriction)"
        )


class TestGuardianBundleIntegration(unittest.TestCase):
    """Test Guardian integration with news bundle."""

    def test_guardian_in_news_bundle(self):
        """Test that guardian is included in news bundle."""
        # Read bundles configuration
        bundles_file = Path(__file__).parent / 'sources' / 'active' / 'bundles.yml'

        self.assertTrue(
            bundles_file.exists(),
            "Bundles configuration file should exist"
        )

        import yaml
        with open(bundles_file, 'r') as f:
            bundles = yaml.safe_load(f)

        # Check news bundle exists
        self.assertIn('news', bundles, "News bundle should exist")

        # Check guardian in news bundle sources
        news_sources = bundles['news'].get('sources', [])
        self.assertIn(
            'guardian',
            news_sources,
            "Guardian should be in news bundle sources"
        )


class TestGuardianEthicalCompliance(unittest.TestCase):
    """Test Guardian source follows ethical scraping practices."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = get_source_registry()
        self.source = self.registry.get_source('guardian')

    def test_guardian_uses_https(self):
        """Test that all Guardian URLs use HTTPS."""
        self.assertTrue(
            self.source.config.base_url.startswith('https://'),
            "Base URL must use HTTPS for security"
        )

    def test_guardian_has_timeout(self):
        """Test that Guardian requests have timeout configured."""
        self.assertIsNotNone(
            self.source.config.timeout,
            "Timeout should be configured"
        )
        self.assertGreater(
            self.source.config.timeout,
            0,
            "Timeout should be positive"
        )

    def test_guardian_respects_skip_patterns(self):
        """Test that Guardian skips inappropriate content types."""
        # Guardian should skip galleries, videos, live blogs per ethical scraping
        articles = self.source.get_articles(count=20)

        if articles:
            for article in articles:
                url = article['url']

                # Should skip live blogs
                self.assertNotIn(
                    '/live/',
                    url,
                    "Should skip live blog URLs"
                )

                # Should skip galleries
                self.assertNotIn(
                    '/gallery/',
                    url,
                    "Should skip gallery URLs"
                )

                # Should skip video pages
                self.assertNotIn(
                    '/video/',
                    url,
                    "Should skip video URLs"
                )


class TestGuardianValidation(unittest.TestCase):
    """Test Guardian source passes validation checks."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = get_source_registry()

    def test_guardian_config_validation(self):
        """Test that Guardian configuration passes validation."""
        errors = self.registry.validate_all_sources(deep_validation=False)
        guardian_errors = errors.get('guardian', [])

        self.assertEqual(
            len(guardian_errors),
            0,
            f"Guardian configuration should have no errors, got: {guardian_errors}"
        )


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
