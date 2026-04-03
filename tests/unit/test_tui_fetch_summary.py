"""Tests for FetchResult construction and summary rendering."""
import requests
from unittest.mock import patch, MagicMock
from capcat.core.unified_source_processor import FetchResult
from capcat.core.tui_context import (
    reset_fetch_results,
    record_fetch_result,
    get_fetch_result,
    set_tui_active,
)
from capcat.core.article_fetcher import NewsSourceArticleFetcher


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
    reset_fetch_results()
    fetcher = _make_fetcher()
    fetcher.session.get = MagicMock(side_effect=requests.exceptions.Timeout())
    fetcher._fetch_web_content("T", "http://x.com/a", 0, "/tmp")
    fr = get_fetch_result()
    assert fr.saved == 0
    assert fr.skipped == []


def _run_show_completion(generate_html, success, fetch_result=None):
    """Run _show_completion_screen with menu choice patched to 'menu'."""
    with patch("questionary.select") as mock_q, \
         patch("capcat.core.interactive._find_latest_index_html", return_value=None), \
         patch("builtins.print") as mock_print:
        mock_q.return_value.ask.return_value = "menu"
        from capcat.core.interactive import _show_completion_screen
        _show_completion_screen(generate_html, success, fetch_result=fetch_result)
    return [str(c) for c in mock_print.call_args_list]


def test_completion_no_summary_when_no_fetch_result():
    """No summary line when fetch_result is None."""
    lines = _run_show_completion(False, True, fetch_result=None)
    assert not any("saved" in l for l in lines)


def test_completion_summary_saved_only():
    """'47 saved' shown when nothing skipped."""
    fr = FetchResult(saved=47, skipped=[])
    lines = _run_show_completion(False, True, fetch_result=fr)
    assert any("47 saved" in l for l in lines)
    assert not any("skipped" in l for l in lines)


def test_completion_summary_with_skipped():
    """'47 saved, 3 skipped (2 blocked, 1 JS-rendered)' shown when skipped > 0."""
    fr = FetchResult(saved=47, skipped=[("blocked", 2), ("JS-rendered", 1)])
    lines = _run_show_completion(False, True, fetch_result=fr)
    combined = " ".join(lines)
    assert "47 saved" in combined
    assert "3 skipped" in combined
    assert "blocked" in combined


def test_completion_no_summary_when_zero_zero():
    """No summary when saved=0 and skipped=0 (source returned no articles)."""
    fr = FetchResult(saved=0, skipped=[])
    lines = _run_show_completion(False, True, fetch_result=fr)
    assert not any("saved" in l for l in lines)


