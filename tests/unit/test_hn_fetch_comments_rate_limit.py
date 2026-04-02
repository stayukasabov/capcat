#!/usr/bin/env python3
"""
Regression tests: HN fetch_comments must route through EthicalScrapingManager.

Bug: fetch_comments calls self.session.get() directly, bypassing the global
rate limiter. With 8 concurrent workers all fetching comments from
news.ycombinator.com, all requests fire simultaneously → 429.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from capcat.sources.builtin.custom.hn.source import HnSource


def _make_hn_source():
    """Create an HnSource with a minimal mock config."""
    config = MagicMock()
    config.name = "hn"
    config.display_name = "Hacker News"
    config.base_url = "https://news.ycombinator.com"
    config.timeout = 30
    config.rate_limit = 1.0
    config.custom_config = {}
    session = MagicMock()
    return HnSource(config=config, session=session)


class TestHNFetchCommentsUsesEthicalManager:
    """fetch_comments must call get_ethical_manager().request_with_backoff()."""

    def test_fetch_comments_calls_request_with_backoff(self, tmp_path):
        """
        fetch_comments must use request_with_backoff from the ethical manager,
        not self.session.get() directly.
        """
        source = _make_hn_source()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><table></table></body></html>"

        mock_manager = MagicMock()
        mock_manager.request_with_backoff.return_value = mock_response

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
            create=True,
        ):
            source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=12345",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
            )

        mock_manager.request_with_backoff.assert_called_once()
        call_args = mock_manager.request_with_backoff.call_args
        all_args = list(call_args[0]) + list(call_args[1].values())
        assert any("news.ycombinator.com" in str(a) for a in all_args), (
            "request_with_backoff must be called with the comment URL"
        )

    def test_fetch_comments_does_not_call_session_get_directly(self, tmp_path):
        """
        After the fix, self.session.get() must NOT be called for comment fetching.
        """
        source = _make_hn_source()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><table></table></body></html>"

        mock_manager = MagicMock()
        mock_manager.request_with_backoff.return_value = mock_response

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
            create=True,
        ):
            source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=12345",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
            )

        source.session.get.assert_not_called()

    def test_fetch_comments_returns_false_on_http_error(self, tmp_path):
        """
        fetch_comments must return False when request_with_backoff raises HTTPError.
        """
        source = _make_hn_source()

        error_response = MagicMock()
        error_response.status_code = 429
        http_error = requests.exceptions.HTTPError(response=error_response)

        mock_manager = MagicMock()
        mock_manager.request_with_backoff.side_effect = http_error

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
            create=True,
        ):
            result = source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=12345",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
            )

        assert result is False, (
            "fetch_comments must return False when HTTP error occurs after retries"
        )
