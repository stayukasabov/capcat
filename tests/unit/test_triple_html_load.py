"""
Tests that response.text is read only once per _fetch_web_content call.

Bug: response.text was accessed multiple times in both ArticleFetcher and
NewsSourceArticleFetcher._fetch_web_content, creating duplicate copies of
the full HTML in memory. With 8 parallel workers and a 50 MB page, peak
memory can reach 1.2 GB from HTML alone.

Fix: read response.text once into a local variable and reuse it.
"""
from unittest.mock import MagicMock, PropertyMock, patch

import pytest


_HTML = "<html><body><article><p>Hello world</p></article></body></html>"

_SOURCE_CONFIG = {
    "name": "test",
    "content_selectors": ["article"],
    "skip_patterns": [],
    "timeout": 5,
}


def _make_response(html=_HTML, status=200):
    """Create a mock response with a tracked .text property."""
    resp = MagicMock()
    resp.status_code = status
    resp.raise_for_status = MagicMock()
    resp.headers = {"Content-Type": "text/html"}
    resp.url = "https://example.com/article"
    # Use PropertyMock to track access count
    text_mock = PropertyMock(return_value=html)
    type(resp).text = text_mock
    return resp, text_mock


def _make_news_source_fetcher(session):
    """Create a NewsSourceArticleFetcher with mocked dependencies."""
    with (
        patch("capcat.core.article_fetcher.get_config") as mock_config,
        patch("capcat.core.article_fetcher.initialize_pdf_manager"),
        patch("capcat.core.ethical_scraping.get_ethical_manager"),
    ):
        mock_config.return_value.processing.remove_style_tags = True
        mock_config.return_value.processing.remove_nav_tags = True
        mock_config.return_value.network.read_timeout = 30
        from capcat.core.article_fetcher import NewsSourceArticleFetcher
        return NewsSourceArticleFetcher(_SOURCE_CONFIG, session)


class TestResponseTextAccessCount:
    """response.text must be read exactly once per _fetch_web_content call."""

    def test_news_source_fetcher_reads_response_text_once(self, tmp_path):
        """NewsSourceArticleFetcher._fetch_web_content should access
        response.text only once, storing it in a local variable."""
        resp, text_mock = _make_response()
        session = MagicMock()
        session.get.return_value = resp

        fetcher = _make_news_source_fetcher(session)

        with (
            patch("capcat.core.article_fetcher.get_config") as mock_config,
            patch("capcat.core.article_fetcher.convert_html_with_timeout",
                  return_value="converted markdown"),
            patch("capcat.core.article_fetcher.is_tui_active", return_value=False),
            patch("capcat.core.article_fetcher.UnifiedMediaProcessor") as mock_media,
        ):
            mock_config.return_value.processing.remove_style_tags = True
            mock_config.return_value.processing.remove_nav_tags = True
            mock_media.process_article_media.return_value = "final markdown"

            fetcher._fetch_web_content(
                "Test Article", "https://example.com/article", 0, str(tmp_path)
            )

        # response.text must be accessed at most once
        assert text_mock.call_count <= 1, (
            f"response.text accessed {text_mock.call_count} times, expected 1. "
            "Each access creates a full copy of the HTML in memory."
        )

    def test_base_fetcher_reads_response_text_once(self, tmp_path):
        """ArticleFetcher._fetch_web_content (inherited by HN/Lobsters)
        should access response.text only once."""
        resp, text_mock = _make_response()
        session = MagicMock()
        session.get.return_value = resp

        with (
            patch("capcat.core.article_fetcher.get_config") as mock_config,
            patch("capcat.core.article_fetcher.initialize_pdf_manager"),
            patch("capcat.core.ethical_scraping.get_ethical_manager"),
        ):
            mock_config.return_value.processing.remove_style_tags = True
            mock_config.return_value.processing.remove_nav_tags = True
            from capcat.core.article_fetcher import HackerNewsArticleFetcher
            fetcher = HackerNewsArticleFetcher(session)

        with (
            patch("capcat.core.article_fetcher.get_config") as mock_config,
            patch("capcat.core.article_fetcher.convert_html_with_timeout",
                  return_value="converted markdown"),
            patch("capcat.core.article_fetcher.is_tui_active", return_value=False),
            patch("capcat.core.article_fetcher.UnifiedMediaProcessor") as mock_media,
        ):
            mock_config.return_value.processing.remove_style_tags = True
            mock_config.return_value.processing.remove_nav_tags = True
            mock_media.process_article_media.return_value = "final markdown"

            fetcher._fetch_web_content(
                "Test Article", "https://example.com/article", 0, str(tmp_path)
            )

        # response.text must be accessed at most once
        assert text_mock.call_count <= 1, (
            f"response.text accessed {text_mock.call_count} times, expected 1. "
            "Each access creates a full copy of the HTML in memory."
        )
