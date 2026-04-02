#!/usr/bin/env python3
"""
Regression tests: LB fetch_comments must route through EthicalScrapingManager.

Bug: fetch_comments has an inline retry loop with time.sleep(rate_limit) and
manual 429 exponential backoff — duplicates EthicalScrapingManager and ignores
the global per-domain rate limiter.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests


def _make_lb_source():
    """Create an LbSource with a minimal mock config."""
    from capcat.sources.builtin.custom.lb.source import LbSource
    config = MagicMock()
    config.name = "lb"
    config.display_name = "Lobsters"
    config.base_url = "https://lobste.rs"
    config.timeout = 30
    config.rate_limit = 0.0  # No delay for tests
    config.custom_config = {}
    session = MagicMock()
    return LbSource(config=config, session=session)


class TestLBFetchCommentsUsesEthicalManager:
    """fetch_comments must call get_ethical_manager().request_with_backoff()."""

    def test_fetch_comments_calls_request_with_backoff(self, tmp_path):
        """
        fetch_comments must use request_with_backoff from the ethical manager,
        not the inline retry loop with time.sleep(rate_limit).
        """
        source = _make_lb_source()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"

        mock_manager = MagicMock()
        mock_manager.request_with_backoff.return_value = mock_response

        with patch(
            "capcat.sources.builtin.custom.lb.source.get_ethical_manager",
            return_value=mock_manager,
            create=True,
        ):
            source.fetch_comments(
                comment_url="https://lobste.rs/s/abc123",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
            )

        mock_manager.request_with_backoff.assert_called_once()
        call_args = mock_manager.request_with_backoff.call_args
        all_args = list(call_args[0]) + list(call_args[1].values())
        assert any("lobste.rs" in str(a) for a in all_args), (
            "request_with_backoff must be called with the comment URL"
        )

    def test_fetch_comments_does_not_call_session_get_directly(self, tmp_path):
        """
        After the fix, self.session.get() must NOT be called from the retry loop.
        """
        source = _make_lb_source()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"

        mock_manager = MagicMock()
        mock_manager.request_with_backoff.return_value = mock_response

        with patch(
            "capcat.sources.builtin.custom.lb.source.get_ethical_manager",
            return_value=mock_manager,
            create=True,
        ):
            source.fetch_comments(
                comment_url="https://lobste.rs/s/abc123",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
            )

        source.session.get.assert_not_called()

    def test_fetch_comments_returns_false_on_http_error(self, tmp_path):
        """
        fetch_comments must return False when request_with_backoff raises HTTPError.
        """
        source = _make_lb_source()

        error_response = MagicMock()
        error_response.status_code = 429
        http_error = requests.exceptions.HTTPError(response=error_response)

        mock_manager = MagicMock()
        mock_manager.request_with_backoff.side_effect = http_error

        with patch(
            "capcat.sources.builtin.custom.lb.source.get_ethical_manager",
            return_value=mock_manager,
            create=True,
        ):
            result = source.fetch_comments(
                comment_url="https://lobste.rs/s/abc123",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
            )

        assert result is False
