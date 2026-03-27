"""Tests for FetchResult construction and summary rendering."""
import pytest
from capcat.core.unified_source_processor import FetchResult


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
