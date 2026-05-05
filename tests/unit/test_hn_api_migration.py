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
