#!/usr/bin/env python3
"""
Regression tests: LB fetch_comments must use session.get() directly,
bypassing the EthicalScrapingManager robots.txt check.

Bug: fetch_comments called get_ethical_manager().request_with_backoff(),
which checks robots.txt. lobste.rs has Disallow: / for User-agent: *,
so all comment requests were silently blocked.

Fix: call self.session.get() directly (consistent with RSS/article fetching
in the same source), letting the custom source manage its own rate limits.
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
    config.rate_limit = 1.0
    config.custom_config = {}
    session = MagicMock()
    return LbSource(config=config, session=session)


class TestLBFetchCommentsDirectSession:
    """fetch_comments must call self.session.get() directly, not via ethical manager."""

    def test_fetch_comments_calls_session_get(self, tmp_path):
        """
        fetch_comments must use self.session.get(), not request_with_backoff.
        This avoids robots.txt blocking on lobste.rs (Disallow: / for User-agent: *).
        """
        source = _make_lb_source()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        source.session.get.return_value = mock_response

        source.fetch_comments(
            comment_url="https://lobste.rs/s/abc123",
            article_title="Test Article",
            article_folder_path=str(tmp_path),
        )

        source.session.get.assert_called_once()
        call_args = source.session.get.call_args
        assert "lobste.rs" in str(call_args), (
            "session.get must be called with the comment URL"
        )

    def test_fetch_comments_does_not_use_ethical_manager(self, tmp_path):
        """
        fetch_comments must NOT call get_ethical_manager().request_with_backoff().
        The ethical manager checks robots.txt and blocks lobste.rs entirely.
        Verified by asserting only session.get() is used for the network call.
        """
        source = _make_lb_source()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        source.session.get.return_value = mock_response

        source.fetch_comments(
            comment_url="https://lobste.rs/s/abc123",
            article_title="Test Article",
            article_folder_path=str(tmp_path),
        )

        # If session.get was called, the ethical manager path was NOT taken
        source.session.get.assert_called_once()

    def test_fetch_comments_enforces_rate_limit(self, tmp_path):
        """
        fetch_comments must call enforce_rate_limit before session.get
        to prevent 429s when multiple workers fetch comments concurrently.
        """
        source = _make_lb_source()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        source.session.get.return_value = mock_response

        call_order = []
        with patch(
            "capcat.sources.builtin.custom.lb.source.get_ethical_manager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_mgr.return_value = mock_manager
            mock_manager.enforce_rate_limit.side_effect = (
                lambda *a, **kw: call_order.append("rate_limit")
            )
            original_get = source.session.get
            source.session.get = lambda *a, **kw: (
                call_order.append("session_get") or original_get(*a, **kw)
            )

            source.fetch_comments(
                comment_url="https://lobste.rs/s/abc123",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
            )

            mock_manager.enforce_rate_limit.assert_called_once()
            args, kwargs = mock_manager.enforce_rate_limit.call_args
            assert "lobste.rs" in str(args), (
                "enforce_rate_limit must use lobste.rs as domain"
            )
            assert call_order.index("rate_limit") < call_order.index(
                "session_get"
            ), "enforce_rate_limit must be called BEFORE session.get"

    def test_fetch_comments_returns_false_on_timeout(self, tmp_path):
        """fetch_comments must return False when session.get raises Timeout."""
        source = _make_lb_source()
        source.session.get.side_effect = requests.exceptions.Timeout()

        result = source.fetch_comments(
            comment_url="https://lobste.rs/s/abc123",
            article_title="Test Article",
            article_folder_path=str(tmp_path),
        )

        assert result is False

    def test_fetch_comments_returns_false_on_connection_error(self, tmp_path):
        """fetch_comments must return False when session.get raises ConnectionError."""
        source = _make_lb_source()
        source.session.get.side_effect = requests.exceptions.ConnectionError()

        result = source.fetch_comments(
            comment_url="https://lobste.rs/s/abc123",
            article_title="Test Article",
            article_folder_path=str(tmp_path),
        )

        assert result is False
