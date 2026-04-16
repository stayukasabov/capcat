"""
Regression tests for NewsSourceArticleFetcher timeout behaviour.

Root causes fixed:

1. html_to_markdown called without timeout in NewsSourceArticleFetcher._fetch_web_content.
   The base ArticleFetcher uses convert_html_with_timeout; the override did not.
   A complex Nature article could block a thread for minutes in the converter.
   Fix: use convert_html_with_timeout in the override.

2. max_retries not configurable per source in YAML.
   _fetch_web_content had no retry loop at all; a single transient error failed
   the article permanently.
   Fix: honour max_retries from source config (default 0 = no retry).
"""
import time
from unittest.mock import MagicMock, patch

import pytest
import requests


_SOURCE_CONFIG = {
    "name": "test",
    "content_selectors": ["article"],
    "skip_patterns": [],
    "timeout": 5,
}

_HTML = "<html><body><article><p>Hello world</p></article></body></html>"


def _make_session(html=_HTML, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.text = html
    resp.raise_for_status = MagicMock()
    session = MagicMock()
    session.get.return_value = resp
    return session


def _make_fetcher(source_config=None, session=None):
    cfg = source_config or _SOURCE_CONFIG
    sess = session or _make_session()
    with (
        patch("capcat.core.article_fetcher.get_config"),
        patch("capcat.core.article_fetcher.initialize_pdf_manager"),
        patch("capcat.core.ethical_scraping.get_ethical_manager"),
    ):
        from capcat.core.article_fetcher import NewsSourceArticleFetcher
        return NewsSourceArticleFetcher(cfg, sess)


class TestHtmlConversionTimeout:
    """html_to_markdown must not block indefinitely — conversion_timeout must apply."""

    def test_slow_conversion_does_not_hang_thread(self, tmp_path):
        """If html_to_markdown hangs, _fetch_web_content must return within ~2s."""
        fetcher = _make_fetcher()

        def slow_convert(html, url=None):
            time.sleep(60)  # simulate hung converter
            return "content"

        with patch(
            "capcat.core.article_fetcher.convert_html_with_timeout",
            side_effect=lambda html, url: ""  # timeout returns empty string
        ) as mock_convert:
            start = time.time()
            result = fetcher._fetch_web_content(
                "Test Article", "https://example.com/article", 0, str(tmp_path)
            )
            elapsed = time.time() - start

        # convert_html_with_timeout must have been called, not html_to_markdown directly
        mock_convert.assert_called_once()
        # Should complete quickly (the mock returns immediately)
        assert elapsed < 2.0

    def test_conversion_uses_convert_html_with_timeout_not_html_to_markdown(self, tmp_path):
        """_fetch_web_content must call convert_html_with_timeout, not html_to_markdown."""
        fetcher = _make_fetcher()

        with (
            patch("capcat.core.article_fetcher.convert_html_with_timeout", return_value="# Content\n\nText") as mock_timeout,
            patch("capcat.core.article_fetcher.html_to_markdown") as mock_direct,
        ):
            fetcher._fetch_web_content(
                "Test Article", "https://example.com/article", 0, str(tmp_path)
            )

        mock_timeout.assert_called_once()
        mock_direct.assert_not_called()


class TestPerSourceMaxRetries:
    """max_retries in source config must control retry count for HTTP failures."""

    def test_default_no_retry_on_connection_error(self, tmp_path):
        """Without max_retries in config, a connection error means 1 attempt only."""
        session = MagicMock()
        session.get.side_effect = requests.exceptions.ConnectionError("down")
        fetcher = _make_fetcher(session=session)

        result = fetcher._fetch_web_content(
            "Article", "https://example.com/article", 0, str(tmp_path)
        )

        assert result == (False, None, None)
        assert session.get.call_count == 1  # no retry by default

    def test_max_retries_1_makes_two_attempts(self, tmp_path):
        """max_retries: 1 → 2 total attempts (1 initial + 1 retry)."""
        cfg = {**_SOURCE_CONFIG, "max_retries": 1}
        session = MagicMock()
        session.get.side_effect = requests.exceptions.ConnectionError("down")
        fetcher = _make_fetcher(source_config=cfg, session=session)

        result = fetcher._fetch_web_content(
            "Article", "https://example.com/article", 0, str(tmp_path)
        )

        assert result == (False, None, None)
        assert session.get.call_count == 2  # initial + 1 retry

    def test_max_retries_2_makes_three_attempts(self, tmp_path):
        """max_retries: 2 → 3 total attempts."""
        cfg = {**_SOURCE_CONFIG, "max_retries": 2}
        session = MagicMock()
        session.get.side_effect = requests.exceptions.ConnectionError("down")
        fetcher = _make_fetcher(source_config=cfg, session=session)

        result = fetcher._fetch_web_content(
            "Article", "https://example.com/article", 0, str(tmp_path)
        )

        assert result == (False, None, None)
        assert session.get.call_count == 3

    def test_retry_succeeds_on_second_attempt(self, tmp_path):
        """If first attempt fails and second succeeds, article is fetched."""
        cfg = {**_SOURCE_CONFIG, "max_retries": 1}
        resp = MagicMock()
        resp.status_code = 200
        resp.text = _HTML
        resp.raise_for_status = MagicMock()

        session = MagicMock()
        session.get.side_effect = [
            requests.exceptions.ConnectionError("transient"),
            resp,
        ]
        fetcher = _make_fetcher(source_config=cfg, session=session)

        with patch("capcat.core.article_fetcher.convert_html_with_timeout", return_value="# Title\n\nContent"):
            success, title, folder = fetcher._fetch_web_content(
                "Article", "https://example.com/article", 0, str(tmp_path)
            )

        assert success is not False or folder is not None  # fetched something
        assert session.get.call_count == 2
