"""Tests for HN Firebase API migration."""
from unittest.mock import MagicMock, patch
import time

import pytest
import requests

from capcat.core.ethical_scraping import EthicalScrapingManager


class TestRequestHnApi:
    """EthicalScrapingManager.request_hn_api must exist and work."""

    def test_request_hn_api_returns_json(self):
        """request_hn_api returns parsed JSON from the Firebase API."""
        manager = EthicalScrapingManager()
        session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "title": "Test"}
        session.get.return_value = mock_response

        result = manager.request_hn_api(
            session,
            "https://hacker-news.firebaseio.com/v0/item/123.json",
            timeout=10,
        )

        assert result == {"id": 123, "title": "Test"}

    def test_request_hn_api_sets_user_agent(self):
        """request_hn_api sets the HN-specific User-Agent header."""
        manager = EthicalScrapingManager()
        session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        session.get.return_value = mock_response

        manager.request_hn_api(
            session,
            "https://hacker-news.firebaseio.com/v0/item/1.json",
            timeout=10,
        )

        call_kwargs = session.get.call_args
        headers = call_kwargs[1].get("headers", {}) if call_kwargs[1] else {}
        assert "Capcat/2.0" in headers.get("User-Agent", "")
        assert "official HN API" in headers.get("User-Agent", "")

    def test_request_hn_api_enforces_delay(self):
        """Two rapid calls must have at least 0.4s between them (0.5s target)."""
        manager = EthicalScrapingManager()
        session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1}
        session.get.return_value = mock_response

        start = time.time()
        manager.request_hn_api(session, "https://hacker-news.firebaseio.com/v0/item/1.json", timeout=10)
        manager.request_hn_api(session, "https://hacker-news.firebaseio.com/v0/item/2.json", timeout=10)
        elapsed = time.time() - start

        assert elapsed >= 0.4, (
            f"Two requests completed in {elapsed:.2f}s, expected >= 0.4s delay"
        )

    def test_request_hn_api_backoff_on_429(self):
        """request_hn_api retries on 429 and returns None after max retries."""
        manager = EthicalScrapingManager()
        session = MagicMock()
        mock_429 = MagicMock()
        mock_429.status_code = 429
        mock_429.headers = {}
        mock_429.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_429
        )
        session.get.return_value = mock_429

        result = manager.request_hn_api(
            session,
            "https://hacker-news.firebaseio.com/v0/item/1.json",
            timeout=10,
            max_retries=2,
            initial_delay=0.1,
        )

        assert result is None
        assert session.get.call_count == 2


from capcat.core.source_system.base_source import Article


class TestArticleHnFields:
    """Article dataclass must support optional HN-specific fields."""

    def test_article_has_comment_ids_field(self):
        """Article accepts comment_ids kwarg."""
        article = Article(
            title="Test", url="https://example.com",
            comment_ids=[100, 200, 300],
        )
        assert article.comment_ids == [100, 200, 300]

    def test_article_has_hn_item_id_field(self):
        """Article accepts hn_item_id kwarg."""
        article = Article(
            title="Test", url="https://example.com",
            hn_item_id=12345,
        )
        assert article.hn_item_id == 12345

    def test_article_hn_fields_default_none(self):
        """HN fields default to None when not provided."""
        article = Article(title="Test", url="https://example.com")
        assert article.comment_ids is None
        assert article.hn_item_id is None


from capcat.sources.builtin.custom.hn.source import HnSource


def _make_hn_source():
    """Create an HnSource with a minimal mock config."""
    config = MagicMock()
    config.name = "hn"
    config.display_name = "Hacker News"
    config.base_url = "https://news.ycombinator.com"
    config.timeout = 10
    config.rate_limit = 1.0
    config.custom_config = {}
    session = MagicMock()
    return HnSource(config=config, session=session)


class TestDiscoverArticlesApi:
    """discover_articles must use the Firebase API, not HTML scraping."""

    def test_discover_calls_topstories_endpoint(self):
        """discover_articles fetches /v0/topstories.json."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101, 102, 103],
            {"id": 101, "title": "Story A", "url": "https://a.com", "kids": [201], "type": "story"},
            {"id": 102, "title": "Story B", "url": "https://b.com", "kids": [202, 203], "type": "story"},
            {"id": 103, "title": "Story C", "url": "https://c.com", "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            articles = source.discover_articles(count=3)

        first_call_url = mock_manager.request_hn_api.call_args_list[0][0][1]
        assert "topstories.json" in first_call_url

    def test_discover_builds_articles_with_comment_ids(self):
        """Articles have comment_ids populated from the kids array."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101],
            {"id": 101, "title": "Story A", "url": "https://a.com", "kids": [201, 202], "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            articles = source.discover_articles(count=1)

        assert len(articles) == 1
        assert articles[0].comment_ids == [201, 202]
        assert articles[0].hn_item_id == 101
        assert articles[0].comment_url == "https://news.ycombinator.com/item?id=101"

    def test_discover_handles_missing_url(self):
        """Stories without url field (Ask HN) get HN discussion URL."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101],
            {"id": 101, "title": "Ask HN: Something", "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            articles = source.discover_articles(count=1)

        assert articles[0].url == "https://news.ycombinator.com/item?id=101"

    def test_discover_respects_count(self):
        """Only count articles returned even if topstories has more."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101, 102, 103, 104, 105],
            {"id": 101, "title": "A", "url": "https://a.com", "type": "story"},
            {"id": 102, "title": "B", "url": "https://b.com", "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            articles = source.discover_articles(count=2)

        assert len(articles) == 2

    def test_discover_skips_failed_item_fetch(self):
        """If a story metadata fetch returns None, skip it and continue."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101, 102, 103],
            None,
            {"id": 102, "title": "B", "url": "https://b.com", "type": "story"},
            {"id": 103, "title": "C", "url": "https://c.com", "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            articles = source.discover_articles(count=3)

        assert len(articles) == 2
        assert articles[0].title == "B"

    def test_discover_no_html_requests(self):
        """discover_articles must not call session.get (no HTML scraping)."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101],
            {"id": 101, "title": "A", "url": "https://a.com", "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            source.discover_articles(count=1)

        source.session.get.assert_not_called()
