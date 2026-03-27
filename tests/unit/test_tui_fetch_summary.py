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
