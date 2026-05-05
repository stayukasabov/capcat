#!/usr/bin/env python3
"""
Regression tests: HN fetch_comments must route through EthicalScrapingManager.request_hn_api.

After the Firebase API migration, all HN requests go through request_hn_api,
not request_with_backoff or session.get directly.
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
    """fetch_comments must call get_ethical_manager().request_hn_api()."""

    def setup_method(self):
        HnSource._hn_compliance_message_shown = False

    def teardown_method(self):
        HnSource._hn_compliance_message_shown = False

    def test_fetch_comments_calls_request_hn_api(self, tmp_path):
        """fetch_comments must use request_hn_api from the ethical manager."""
        source = _make_hn_source()

        mock_manager = MagicMock()
        mock_manager.request_hn_api.return_value = {
            "id": 201, "by": "u", "text": "<p>Test</p>", "type": "comment"
        }

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ), patch(
            "capcat.core.streamlined_comment_processor.create_optimized_comment_processor"
        ) as mock_pf:
            mock_p = MagicMock()
            mock_p.generate_inline_comments_markdown.return_value = "# C"
            mock_p.get_performance_metrics.return_value = {
                "comments_processed": 1, "links_processed": 0
            }
            mock_pf.return_value = mock_p

            source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=12345",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
                comment_ids=[201],
            )

        mock_manager.request_hn_api.assert_called()

    def test_fetch_comments_does_not_call_session_get_directly(self, tmp_path):
        """session.get() must NOT be called for comment fetching."""
        source = _make_hn_source()

        mock_manager = MagicMock()
        mock_manager.request_hn_api.return_value = {
            "id": 201, "by": "u", "text": "<p>Test</p>", "type": "comment"
        }

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ), patch(
            "capcat.core.streamlined_comment_processor.create_optimized_comment_processor"
        ) as mock_pf:
            mock_p = MagicMock()
            mock_p.generate_inline_comments_markdown.return_value = "# C"
            mock_p.get_performance_metrics.return_value = {
                "comments_processed": 1, "links_processed": 0
            }
            mock_pf.return_value = mock_p

            source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=12345",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
                comment_ids=[201],
            )

        source.session.get.assert_not_called()

    def test_fetch_comments_returns_true_on_api_success(self, tmp_path):
        """fetch_comments returns True when API requests succeed."""
        source = _make_hn_source()

        mock_manager = MagicMock()
        mock_manager.request_hn_api.return_value = {
            "id": 201, "by": "u", "text": "<p>Test</p>", "type": "comment"
        }

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ), patch(
            "capcat.core.streamlined_comment_processor.create_optimized_comment_processor"
        ) as mock_pf:
            mock_p = MagicMock()
            mock_p.generate_inline_comments_markdown.return_value = "# C"
            mock_p.get_performance_metrics.return_value = {
                "comments_processed": 1, "links_processed": 0
            }
            mock_pf.return_value = mock_p

            result = source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=12345",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
                comment_ids=[201],
            )

        assert result is True
