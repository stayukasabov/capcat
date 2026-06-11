"""Test that RSS discovery populates Article.published_date."""
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import pytest


class TestRSSDiscoveryDate:

    def test_rss_article_has_published_date(self):
        from capcat.core.source_system.discovery_strategies import RSSDiscoveryStrategy
        from capcat.core.source_system.feed_parser import FeedItem

        feed_items = [
            FeedItem(
                title="Test Article",
                url="https://example.com/article-1",
                description="Summary",
                published_date=datetime(2026, 6, 10, 17, 0, 0, tzinfo=timezone.utc),
            ),
        ]

        strategy = RSSDiscoveryStrategy()

        with patch(
            "capcat.core.source_system.discovery_strategies._fetch_url_with_retry"
        ) as mock_fetch, patch(
            "capcat.core.source_system.discovery_strategies.validate_feed",
            return_value=True,
        ), patch(
            "capcat.core.source_system.discovery_strategies.FeedParserFactory.detect_and_parse",
            return_value=feed_items,
        ):
            mock_response = MagicMock()
            mock_response.content = b"<rss></rss>"
            mock_fetch.return_value = mock_response

            config = {
                "discovery": {"method": "rss", "rss_url": "https://example.com/rss"},
                "name": "test-source",
            }

            articles = strategy.discover(
                count=10,
                config=config,
                session=MagicMock(),
                base_url="https://example.com",
                timeout=10,
                logger=MagicMock(),
                should_skip_callback=lambda url, title: False,
            )

        assert len(articles) == 1
        assert articles[0].published_date == "2026-06-10 17:00:00+00:00"

    def test_rss_article_without_date_has_none(self):
        from capcat.core.source_system.discovery_strategies import RSSDiscoveryStrategy
        from capcat.core.source_system.feed_parser import FeedItem

        feed_items = [
            FeedItem(
                title="No Date Article",
                url="https://example.com/no-date",
                description="No date",
                published_date=None,
            ),
        ]

        strategy = RSSDiscoveryStrategy()

        with patch(
            "capcat.core.source_system.discovery_strategies._fetch_url_with_retry"
        ) as mock_fetch, patch(
            "capcat.core.source_system.discovery_strategies.validate_feed",
            return_value=True,
        ), patch(
            "capcat.core.source_system.discovery_strategies.FeedParserFactory.detect_and_parse",
            return_value=feed_items,
        ):
            mock_response = MagicMock()
            mock_response.content = b"<rss></rss>"
            mock_fetch.return_value = mock_response

            config = {
                "discovery": {"method": "rss", "rss_url": "https://example.com/rss"},
                "name": "test-source",
            }

            articles = strategy.discover(
                count=10,
                config=config,
                session=MagicMock(),
                base_url="https://example.com",
                timeout=10,
                logger=MagicMock(),
                should_skip_callback=lambda url, title: False,
            )

        assert len(articles) == 1
        assert articles[0].published_date is None
