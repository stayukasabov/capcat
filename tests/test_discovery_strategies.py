#!/usr/bin/env python3
"""
Unit tests for discovery_strategies module.
Tests RSS and HTML discovery strategies.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from core.source_system.base_source import Article, ArticleDiscoveryError
from core.source_system.discovery_strategies import (
    DiscoveryStrategyFactory,
    HTMLDiscoveryStrategy,
    RSSDiscoveryStrategy,
)


class TestRSSDiscoveryStrategy:
    """Tests for RSS discovery strategy."""

    def test_discover_rss_success(self):
        """Test successful RSS discovery."""
        strategy = RSSDiscoveryStrategy()

        # Mock response
        mock_response = Mock()
        mock_response.content = b"""<?xml version="1.0"?>
<rss version="2.0">
    <channel>
        <item>
            <title>Test Article</title>
            <link>https://example.com/test</link>
            <description>Test description</description>
        </item>
    </channel>
</rss>"""
        mock_response.raise_for_status = Mock()

        # Mock session
        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_response)

        # Mock logger
        mock_logger = Mock()

        # Mock skip callback
        def should_skip(url, title):
            return False

        config = {
            "discovery": {"rss_url": "https://example.com/feed"},
            "skip_patterns": [],
            "name": "test_source"
        }

        articles = strategy.discover(
            count=10,
            config=config,
            session=mock_session,
            base_url="https://example.com",
            timeout=30,
            logger=mock_logger,
            should_skip_callback=should_skip
        )

        assert len(articles) == 1
        assert articles[0].title == "Test Article"
        assert articles[0].url == "https://example.com/test"
        assert articles[0].summary == "Test description"

    def test_discover_rss_missing_url(self):
        """Test RSS discovery without rss_url in config."""
        strategy = RSSDiscoveryStrategy()

        config = {
            "discovery": {},
            "name": "test_source"
        }

        with pytest.raises(ArticleDiscoveryError, match="RSS discovery requires rss_url"):
            strategy.discover(
                count=10,
                config=config,
                session=Mock(),
                base_url="https://example.com",
                timeout=30,
                logger=Mock(),
                should_skip_callback=lambda u, t: False
            )

    def test_discover_rss_network_error(self):
        """Test RSS discovery with network error."""
        strategy = RSSDiscoveryStrategy()

        mock_session = Mock()
        mock_session.get = Mock(side_effect=requests.ConnectionError("Connection failed"))

        config = {
            "discovery": {"rss_url": "https://example.com/feed"},
            "name": "test_source"
        }

        with pytest.raises(ArticleDiscoveryError, match="Could not access"):
            strategy.discover(
                count=10,
                config=config,
                session=mock_session,
                base_url="https://example.com",
                timeout=30,
                logger=Mock(),
                should_skip_callback=lambda u, t: False
            )

    def test_discover_rss_skip_patterns(self):
        """Test RSS discovery with skip patterns."""
        strategy = RSSDiscoveryStrategy()

        mock_response = Mock()
        mock_response.content = b"""<?xml version="1.0"?>
<rss version="2.0">
    <channel>
        <item>
            <title>Article 1</title>
            <link>https://example.com/video/test</link>
        </item>
        <item>
            <title>Article 2</title>
            <link>https://example.com/article/test</link>
        </item>
    </channel>
</rss>"""
        mock_response.raise_for_status = Mock()

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_response)

        config = {
            "discovery": {"rss_url": "https://example.com/feed"},
            "skip_patterns": ["/video/"],
            "name": "test_source"
        }

        articles = strategy.discover(
            count=10,
            config=config,
            session=mock_session,
            base_url="https://example.com",
            timeout=30,
            logger=Mock(),
            should_skip_callback=lambda u, t: False
        )

        assert len(articles) == 1
        assert articles[0].title == "Article 2"


class TestHTMLDiscoveryStrategy:
    """Tests for HTML discovery strategy."""

    def test_discover_html_success(self):
        """Test successful HTML discovery."""
        strategy = HTMLDiscoveryStrategy()

        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <article>
                    <a href="/article1">Article 1</a>
                </article>
                <article>
                    <a href="/article2">Article 2</a>
                </article>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_response)

        config = {
            "article_selectors": ["article a"],
            "skip_patterns": [],
            "name": "test_source"
        }

        articles = strategy.discover(
            count=10,
            config=config,
            session=mock_session,
            base_url="https://example.com",
            timeout=30,
            logger=Mock(),
            should_skip_callback=lambda u, t: False
        )

        assert len(articles) == 2
        assert articles[0].title == "Article 1"
        assert articles[0].url == "https://example.com/article1"

    def test_discover_html_missing_selectors(self):
        """Test HTML discovery without article_selectors."""
        strategy = HTMLDiscoveryStrategy()

        config = {
            "name": "test_source"
        }

        with pytest.raises(ArticleDiscoveryError, match="HTML discovery requires article_selectors"):
            strategy.discover(
                count=10,
                config=config,
                session=Mock(),
                base_url="https://example.com",
                timeout=30,
                logger=Mock(),
                should_skip_callback=lambda u, t: False
            )

    def test_discover_html_deduplicate_urls(self):
        """Test that duplicate URLs are filtered."""
        strategy = HTMLDiscoveryStrategy()

        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <a href="/article1">Article 1</a>
                <a href="/article1">Article 1 Duplicate</a>
                <a href="/article2">Article 2</a>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_response)

        config = {
            "article_selectors": ["a"],
            "skip_patterns": [],
            "name": "test_source"
        }

        articles = strategy.discover(
            count=10,
            config=config,
            session=mock_session,
            base_url="https://example.com",
            timeout=30,
            logger=Mock(),
            should_skip_callback=lambda u, t: False
        )

        assert len(articles) == 2
        urls = [a.url for a in articles]
        assert urls.count("https://example.com/article1") == 1


class TestDiscoveryStrategyFactory:
    """Tests for DiscoveryStrategyFactory."""

    def test_create_rss_strategy(self):
        """Test creating RSS strategy."""
        config = {"method": "rss"}
        strategy = DiscoveryStrategyFactory.create(config)

        assert isinstance(strategy, RSSDiscoveryStrategy)

    def test_create_html_strategy(self):
        """Test creating HTML strategy."""
        config = {"method": "html"}
        strategy = DiscoveryStrategyFactory.create(config)

        assert isinstance(strategy, HTMLDiscoveryStrategy)

    def test_create_default_strategy(self):
        """Test that default is HTML strategy."""
        config = {}
        strategy = DiscoveryStrategyFactory.create(config)

        assert isinstance(strategy, HTMLDiscoveryStrategy)

    def test_create_unsupported_strategy(self):
        """Test that unsupported method raises ValueError."""
        config = {"method": "unsupported"}

        with pytest.raises(ValueError, match="Unsupported discovery method"):
            DiscoveryStrategyFactory.create(config)
