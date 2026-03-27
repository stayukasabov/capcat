"""Tests for FetchResult construction and summary rendering."""
import pytest
from capcat.core.unified_source_processor import FetchResult
from capcat.core.tui_context import (
    reset_fetch_results,
    record_fetch_result,
    get_fetch_result,
)


def test_fetch_result_saved_only():
    fr = FetchResult(saved=5, skipped=[])
    assert fr.saved == 5
    assert fr.skipped == []


def test_fetch_result_with_skipped():
    fr = FetchResult(saved=3, skipped=[("blocked", 2), ("JS-rendered", 1)])
    assert fr.saved == 3
    assert ("blocked", 2) in fr.skipped


def test_fetch_result_all_skipped():
    fr = FetchResult(saved=0, skipped=[("no content", 3)])
    assert fr.saved == 0
    assert fr.skipped[0] == ("no content", 3)


def test_record_and_get_empty():
    reset_fetch_results()
    fr = get_fetch_result()
    assert fr.saved == 0
    assert fr.skipped == []


def test_record_successes():
    reset_fetch_results()
    record_fetch_result(True, None)
    record_fetch_result(True, None)
    fr = get_fetch_result()
    assert fr.saved == 2
    assert fr.skipped == []


def test_record_mixed():
    reset_fetch_results()
    record_fetch_result(True, None)
    record_fetch_result(False, "blocked")
    record_fetch_result(False, "JS-rendered")
    record_fetch_result(False, "blocked")
    fr = get_fetch_result()
    assert fr.saved == 1
    skipped_dict = dict(fr.skipped)
    assert skipped_dict["blocked"] == 2
    assert skipped_dict["JS-rendered"] == 1


def test_reset_clears_previous():
    reset_fetch_results()
    record_fetch_result(True, None)
    record_fetch_result(True, None)
    reset_fetch_results()
    fr = get_fetch_result()
    assert fr.saved == 0


import requests
from unittest.mock import patch, MagicMock
from capcat.core.tui_context import reset_fetch_results, get_fetch_result, set_tui_active


def _make_fetcher():
    """Create a minimal NewsSourceArticleFetcher for testing."""
    from capcat.core.article_fetcher import NewsSourceArticleFetcher
    session = MagicMock(spec=requests.Session)
    config = {
        "name": "test",
        "source_id": "test",
        "content_selectors": ["body"],
        "skip_patterns": [],
    }
    return NewsSourceArticleFetcher(config, session)


def test_tui_suppresses_timeout_warning():
    """In TUI mode, timeout does not emit WARNING and records reason."""
    fetcher = _make_fetcher()
    set_tui_active(True)
    reset_fetch_results()
    try:
        with patch.object(fetcher, "_fetch_url_with_retry",
                          side_effect=requests.exceptions.Timeout()):
            with patch.object(fetcher, "_check_pdf_size_and_prompt", return_value=False):
                fetcher.session.get = MagicMock(side_effect=requests.exceptions.Timeout())
                result = fetcher._fetch_web_content("T", "http://x.com/a", 0, "/tmp")
        fr = get_fetch_result()
        assert fr.skipped == [("timeout", 1)]
        assert result == (False, None, None)
    finally:
        set_tui_active(False)


def test_tui_suppresses_403_warning():
    """In TUI mode, HTTP 403 does not emit WARNING and records 'blocked'."""
    fetcher = _make_fetcher()
    set_tui_active(True)
    reset_fetch_results()
    try:
        http_err = requests.exceptions.HTTPError(response=MagicMock(status_code=403))
        fetcher.session.get = MagicMock(side_effect=http_err)
        with patch.object(fetcher, "_fetch_url_with_retry", side_effect=http_err):
            result = fetcher._fetch_web_content("T", "http://x.com/a", 0, "/tmp")
        fr = get_fetch_result()
        assert dict(fr.skipped)["blocked"] == 1
        assert result == (False, None, None)
    finally:
        set_tui_active(False)


def test_tui_records_spa_as_js_rendered():
    """SPA detection records 'JS-rendered' reason in TUI mode."""
    fetcher = _make_fetcher()
    set_tui_active(True)
    reset_fetch_results()
    try:
        spa_html = '<html><body><div id="root"></div></body></html>'
        mock_resp = MagicMock()
        mock_resp.text = spa_html
        mock_resp.headers = {"Content-Type": "text/html"}
        mock_resp.raise_for_status = MagicMock()
        fetcher.session.get = MagicMock(return_value=mock_resp)
        result = fetcher._fetch_web_content("T", "http://spa.com/a", 0, "/tmp")
        fr = get_fetch_result()
        assert dict(fr.skipped).get("JS-rendered", 0) == 1
    finally:
        set_tui_active(False)


def test_cli_mode_does_not_record():
    """Outside TUI mode, a failed fetch does NOT record anything."""
    # Ensure TUI is inactive (default)
    reset_fetch_results()
    fetcher = _make_fetcher()
    # Trigger a timeout failure without TUI active
    fetcher.session.get = MagicMock(side_effect=requests.exceptions.Timeout())
    fetcher._fetch_web_content("T", "http://x.com/a", 0, "/tmp")
    fr = get_fetch_result()
    # Nothing should be recorded — guard is conditional on is_tui_active()
    assert fr.saved == 0
    assert fr.skipped == []
