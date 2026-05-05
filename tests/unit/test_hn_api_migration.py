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
