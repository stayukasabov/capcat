"""Unit tests for reporter.py."""
from pathlib import Path
from tests.acceptance.reporter import Reporter


def test_write_entry_appends_markdown(tmp_path):
    r = Reporter(tmp_path / "session.md")
    r.write_entry(
        id=12, group="fetch", cmd="capcat fetch hn --count 3",
        status="PASS", exit_code=0, expected_exit=0,
        duration=4.2, output_path="file:///tmp/out", file_count=3,
        analysis="Exit ✓", note="",
    )
    content = (tmp_path / "session.md").read_text()
    assert "## TEST 12 - fetch: capcat fetch hn --count 3" in content
    assert "**Status**: PASS" in content
    assert "0 (expected 0)  ✓" in content
    assert "**Duration**: 4.2s" in content
    assert "file:///tmp/out" in content
    assert "**Files created**: 3" in content


def test_write_entry_none_expected_exit_shows_question_mark(tmp_path):
    r = Reporter(tmp_path / "session.md")
    r.write_entry(
        id=57, group="remove-source", cmd="capcat remove-source",
        status="PASS", exit_code=0, expected_exit=None,
        duration=1.0, output_path=None, file_count=None,
        analysis="exit check skipped - user judges", note="",
    )
    content = (tmp_path / "session.md").read_text()
    assert "(expected ?)  ?" in content


def test_write_entry_no_output_path_omits_output_lines(tmp_path):
    r = Reporter(tmp_path / "session.md")
    r.write_entry(
        id=1, group="global", cmd="capcat --help",
        status="PASS", exit_code=0, expected_exit=0,
        duration=0.1, output_path=None, file_count=None,
        analysis="Exit ✓", note="",
    )
    content = (tmp_path / "session.md").read_text()
    assert "**Output**" not in content
    assert "**Files created**" not in content


def test_write_entry_with_note_fills_note_field(tmp_path):
    r = Reporter(tmp_path / "session.md")
    r.write_entry(
        id=3, group="global", cmd="capcat -h",
        status="PASS", exit_code=0, expected_exit=0,
        duration=0.1, output_path=None, file_count=None,
        analysis="Exit ✓", note="took longer than expected",
    )
    content = (tmp_path / "session.md").read_text()
    assert "took longer than expected" in content


def test_write_entry_empty_note_renders_dash(tmp_path):
    r = Reporter(tmp_path / "session.md")
    r.write_entry(
        id=1, group="global", cmd="capcat",
        status="PASS", exit_code=0, expected_exit=0,
        duration=0.1, output_path=None, file_count=None,
        analysis="Exit ✓", note="",
    )
    content = (tmp_path / "session.md").read_text()
    assert "**Note**: -" in content


def test_write_entry_fail_status(tmp_path):
    r = Reporter(tmp_path / "session.md")
    r.write_entry(
        id=25, group="fetch", cmd="capcat fetch hn,bbc --count 3",
        status="FAIL", exit_code=1, expected_exit=0,
        duration=2.0, output_path=None, file_count=None,
        analysis="Exit ✗ | Traceback found", note="",
    )
    content = (tmp_path / "session.md").read_text()
    assert "**Status**: FAIL" in content
    assert "1 (expected 0)  ✗" in content


def test_finalize_prepends_summary_before_entries(tmp_path):
    path = tmp_path / "session.md"
    r = Reporter(path)
    r.write_entry(
        id=1, group="global", cmd="capcat",
        status="PASS", exit_code=0, expected_exit=0,
        duration=0.1, output_path=None, file_count=None,
        analysis="Exit ✓", note="",
    )
    r.finalize(
        counts={"global": {"pass": 1, "fail": 0, "skip": 0}},
        failed_tests=[],
    )
    content = path.read_text()
    assert content.index("# Capcat Acceptance Test Run") < content.index("## TEST 1")


def test_finalize_shows_correct_totals(tmp_path):
    path = tmp_path / "session.md"
    r = Reporter(path)
    r.finalize(
        counts={
            "global": {"pass": 5, "fail": 1, "skip": 1},
            "fetch": {"pass": 3, "fail": 0, "skip": 0},
        },
        failed_tests=[],
    )
    content = path.read_text()
    assert "**Passed**: 8" in content
    assert "**Failed**: 1" in content
    assert "**Skipped**: 1" in content
    assert "**Total run**: 10" in content


def test_finalize_lists_failed_tests(tmp_path):
    path = tmp_path / "session.md"
    r = Reporter(path)
    r.finalize(
        counts={"fetch": {"pass": 0, "fail": 1, "skip": 0}},
        failed_tests=["TEST 25: fetch hn,bbc - Traceback in output"],
    )
    content = path.read_text()
    assert "### Failed Tests" in content
    assert "TEST 25" in content


def test_finalize_no_failed_tests_omits_section(tmp_path):
    path = tmp_path / "session.md"
    r = Reporter(path)
    r.finalize(
        counts={"global": {"pass": 7, "fail": 0, "skip": 0}},
        failed_tests=[],
    )
    content = path.read_text()
    assert "### Failed Tests" not in content
