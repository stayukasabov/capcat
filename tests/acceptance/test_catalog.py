"""Structural validation tests for catalog.py — ensures all 74 entries are well-formed."""
import pytest

REQUIRED_FIELDS = {
    "id", "group", "label", "cmd", "expected_exit",
    "expected_in_output", "creates_files", "needs_init",
    "pre_init", "is_tui", "passthrough", "timeout", "fixture",
}
VALID_GROUPS = {
    "global", "init", "single", "fetch", "bundle", "list",
    "add-source", "remove-source", "generate-config", "tui",
}


def get_tests():
    from tests.acceptance.catalog import TESTS
    return TESTS


def test_total_count_is_74():
    assert len(get_tests()) == 74, f"Expected 74, got {len(get_tests())}"


def test_all_entries_have_required_fields():
    for t in get_tests():
        for field in REQUIRED_FIELDS:
            assert field in t, f"Test {t.get('id', '?')} missing field '{field}'"


def test_ids_are_sequential_from_one():
    ids = [t["id"] for t in get_tests()]
    assert ids == list(range(1, len(ids) + 1)), f"IDs not sequential: {ids}"


def test_all_groups_are_valid():
    for t in get_tests():
        assert t["group"] in VALID_GROUPS, \
            f"Test {t['id']} has invalid group '{t['group']}'"


def test_no_passthrough_with_creates_files():
    for t in get_tests():
        if t["passthrough"]:
            assert not t["creates_files"], \
                f"Test {t['id']}: passthrough=True but creates_files=True"


def test_no_passthrough_with_expected_in_output():
    for t in get_tests():
        if t["passthrough"]:
            assert t["expected_in_output"] == [], \
                f"Test {t['id']}: passthrough=True but expected_in_output non-empty"


def test_no_both_needs_init_and_pre_init():
    for t in get_tests():
        assert not (t["needs_init"] and t["pre_init"]), \
            f"Test {t['id']}: both needs_init and pre_init are True"


def test_cmd_starts_with_capcat():
    for t in get_tests():
        assert t["cmd"][0] == "capcat", \
            f"Test {t['id']} cmd doesn't start with 'capcat': {t['cmd']}"


def test_tui_tests_have_timeout_120():
    for t in get_tests():
        if t["is_tui"]:
            assert t["timeout"] == 120, \
                f"TUI test {t['id']} should have timeout=120, got {t['timeout']}"


def test_tui_tests_use_catch_subcommand():
    for t in get_tests():
        if t["is_tui"]:
            assert t["cmd"] == ["capcat", "catch"], \
                f"TUI test {t['id']} cmd should be ['capcat', 'catch']"


def test_no_fixture_url_sentinel_in_any_test():
    for t in get_tests():
        assert "__FIXTURE_URL__" not in t["cmd"], \
            f"Test {t['id']}: unexpected __FIXTURE_URL__ sentinel (use real URLs)"


def test_tmp_sentinel_in_expected_tests():
    # Tests that reference tmp dir in their cmd
    tmp_tests = {5, 17, 30, 44, 62, 66}
    for t in get_tests():
        has_tmp = any("__TMP__" in arg for arg in t["cmd"])
        if t["id"] in tmp_tests:
            assert has_tmp, f"Test {t['id']} should contain __TMP__ sentinel"
