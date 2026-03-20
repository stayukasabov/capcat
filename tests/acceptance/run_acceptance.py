#!/usr/bin/env python3
"""Capcat human-in-the-loop acceptance test runner.

Usage:
    python tests/acceptance/run_acceptance.py
    python tests/acceptance/run_acceptance.py --group fetch
    python tests/acceptance/run_acceptance.py --from 22
    python tests/acceptance/run_acceptance.py --only 25,30,46
    python tests/acceptance/run_acceptance.py --timeout 60
"""
from __future__ import annotations

import argparse
import datetime
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ── Platform single-keypress ──────────────────────────────────────────────────

if sys.platform == "win32":
    import msvcrt

    def _getch() -> str:
        return msvcrt.getch().decode("utf-8", errors="replace")

else:
    import tty
    import termios

    def _getch() -> str:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch


# ── Paths ─────────────────────────────────────────────────────────────────────

_HERE = Path(__file__).parent
_FIXTURES = _HERE / "fixtures"
_RESULTS = _HERE / "results"


# ── Sentinel replacement ──────────────────────────────────────────────────────

def _resolve_cmd(cmd: list[str], tmp_dir: str, fixture: str | None) -> list[str]:
    """Replace __TMP__ and __FIXTURE_URL__ sentinels in cmd."""
    fixture_url = ""
    if fixture:
        fixture_url = "file://" + str(Path(tmp_dir) / fixture)

    result = []
    for arg in cmd:
        if arg == "__TMP__":
            result.append(tmp_dir)
        elif "__TMP__/" in arg:
            result.append(arg.replace("__TMP__", tmp_dir))
        elif arg == "__FIXTURE_URL__":
            result.append(fixture_url)
        else:
            result.append(arg)
    return result


# ── Fixture setup ─────────────────────────────────────────────────────────────

def _copy_fixture(fixture: str, tmp_dir: str) -> None:
    src = _FIXTURES / fixture
    shutil.copy(src, Path(tmp_dir) / fixture)


# ── Silent init ───────────────────────────────────────────────────────────────

def _silent_init(tmp_dir: str) -> None:
    result = subprocess.run(
        ["capcat", "init"],
        cwd=tmp_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        print(f"\n[RUNNER ERROR] Silent init failed in {tmp_dir} (exit {result.returncode})")
        sys.exit(1)


# ── Subprocess execution ──────────────────────────────────────────────────────

def _run_captured(
    cmd: list[str], cwd: str, timeout: int
) -> tuple[int | None, str, float, bool]:
    """Run cmd, stream output live, capture it too. Returns (exit_code, output, duration, timed_out)."""
    start = time.monotonic()
    timed_out = False
    output_lines: list[str] = []

    print(f"\n{'━'*54} LIVE OUTPUT {'━'*54}")
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        try:
            for line in proc.stdout:  # type: ignore[union-attr]
                sys.stdout.write(line)
                sys.stdout.flush()
                output_lines.append(line)
            proc.wait(timeout=max(0, timeout - (time.monotonic() - start)))
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            timed_out = True
    except FileNotFoundError:
        print("[ERROR] 'capcat' not found on PATH. Install with: pipx install capcat")
        return None, "", time.monotonic() - start, False

    print(f"{'━'*121}")
    duration = time.monotonic() - start
    return proc.returncode, "".join(output_lines), duration, timed_out


def _run_passthrough(
    cmd: list[str], cwd: str, timeout: int
) -> tuple[int | None, float, bool]:
    """Run cmd with no capture — output goes directly to terminal. Returns (exit_code, duration, timed_out)."""
    start = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.Popen(cmd, cwd=cwd)
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            timed_out = True
    except FileNotFoundError:
        print("[ERROR] 'capcat' not found on PATH.")
        return None, time.monotonic() - start, False
    return proc.returncode, time.monotonic() - start, timed_out


# ── Output path detection ─────────────────────────────────────────────────────

def _find_output_path(tmp_dir: str) -> str | None:
    """Return file:// link to the first interesting output directory in tmp_dir."""
    skip = {".capcat", "Config"}
    for entry in sorted(Path(tmp_dir).iterdir()):
        if entry.name not in skip and entry.is_dir():
            return "file://" + str(entry.resolve())
    return None


def _count_output_files(tmp_dir: str) -> int:
    skip = {".capcat", "Config"}
    return sum(1 for e in Path(tmp_dir).iterdir() if e.name not in skip)


# ── Auto-analysis ─────────────────────────────────────────────────────────────

ERROR_STRINGS = ("Traceback", "Error:", "CRITICAL")


def _auto_analyze(
    test: dict,
    exit_code: int | None,
    output: str,
    tmp_dir: str,
    timed_out: bool,
    global_timeout: int | None,
) -> tuple[str, str | None, int | None]:
    """Return (analysis_str, output_path, file_count)."""
    parts: list[str] = []
    output_path: str | None = None
    file_count: int | None = None
    effective_timeout = global_timeout if global_timeout is not None else test["timeout"]

    if timed_out:
        parts.append(f"TIMEOUT after {effective_timeout}s ✗")
        return " | ".join(parts), None, None

    # Exit code
    expected = test["expected_exit"]
    if expected is None:
        parts.append("exit check skipped — user judges")
    elif exit_code == expected:
        parts.append(f"Exit {exit_code} ✓")
    else:
        parts.append(f"Exit {exit_code} ✗ (expected {expected})")

    # For passthrough/TUI — no output to analyze further
    if test["is_tui"] or test["passthrough"]:
        parts.append("(output passed through — no capture)")
        return " | ".join(parts), None, None

    # Expected strings
    for s in test["expected_in_output"]:
        if s in output:
            parts.append(f'"{s}" ✓')
        else:
            parts.append(f'"{s}" NOT FOUND ✗')

    # Error string scan (only when expected exit is 0)
    if expected == 0:
        found_errors = [e for e in ERROR_STRINGS if e in output]
        if found_errors:
            parts.append(f"error strings found: {', '.join(found_errors)} ✗")
        else:
            parts.append("no error strings ✓")

    # Log file check
    if "-L" in test["cmd"]:
        idx = test["cmd"].index("-L")
        if idx + 1 < len(test["cmd"]):
            log_path_raw = test["cmd"][idx + 1].replace("__TMP__", tmp_dir)
            log_p = Path(log_path_raw)
            if log_p.exists() and log_p.stat().st_size > 0:
                parts.append("log file written ✓")
            else:
                parts.append("log file missing or empty ✗")

    # File count
    if test["creates_files"]:
        file_count = _count_output_files(tmp_dir)
        output_path = _find_output_path(tmp_dir)
        parts.append(f"{file_count} output item(s) in tmp dir")
    elif output_path is None:
        output_path = _find_output_path(tmp_dir)

    return " | ".join(parts), output_path, file_count


# ── Screen helpers ────────────────────────────────────────────────────────────

def _clear() -> None:
    print("\033[2J\033[H", end="", flush=True)


def _print_header(test: dict, total: int) -> None:
    label = " ".join(test["cmd"])
    bar = "═" * 62
    print(f"\n{bar}")
    print(f"TEST {test['id']}/{total}  [{test['group']}]   {label}")
    print(f"{bar}\n")


def _print_result_cli(
    test: dict,
    exit_code: int | None,
    duration: float,
    analysis: str,
    output_path: str | None,
    file_count: int | None,
    timed_out: bool,
) -> None:
    expected = test["expected_exit"]
    if timed_out:
        exit_line = f"  Exit code : TIMEOUT  ✗"
    elif exit_code is None:
        exit_line = f"  Exit code : ?  (expected {expected if expected is not None else '?'})"
    elif expected is None:
        exit_line = f"  Exit code : {exit_code}  ?  (expected ?)"
    elif exit_code == expected:
        exit_line = f"  Exit code : {exit_code}  ✓  (expected {expected})"
    else:
        exit_line = f"  Exit code : {exit_code}  ✗  (expected {expected})"

    print("\nRESULT")
    print(exit_line)
    print(f"  Duration  : {duration:.1f}s")
    if output_path:
        print(f"  Output    : {output_path}   ← open in browser")
    if file_count is not None:
        print(f"  Files     : {file_count} item(s) created")
    print(f"  Analysis  : {analysis}")
    print()
    print("[Enter] Pass   [f] Fail   [n] Note+Pass   [s] Skip   [q] Quit")


def _print_result_passthrough(
    test: dict,
    exit_code: int | None,
    duration: float,
    timed_out: bool,
    analysis: str,
) -> None:
    expected = test["expected_exit"]
    if timed_out:
        exit_line = "  Exit code : TIMEOUT  ✗"
    elif exit_code is None:
        exit_line = "  Exit code : ?  (expected ?)"
    elif expected is None:
        exit_line = f"  Exit code : {exit_code}  ?  (expected ?)"
    elif exit_code == expected:
        exit_line = f"  Exit code : {exit_code}  ✓  (expected {expected})"
    else:
        exit_line = f"  Exit code : {exit_code}  ✗  (expected {expected})"

    print("\nRESULT")
    print(exit_line)
    print(f"  Duration  : {duration:.1f}s")
    print(f"  Analysis  : {analysis}")
    print()
    print("[Enter] Pass   [f] Fail   [n] Note+Pass   [s] Skip   [q] Quit")


def _print_tui_header(test: dict, total: int, fixture_url: str) -> None:
    _print_header(test, total)
    print("MANUAL TEST — you drive this one.\n")
    if fixture_url:
        print(f"  URL to enter when prompted: {fixture_url}\n")
    print("Steps to follow:")
    for i, step in enumerate(test.get("steps", []), 1):
        print(f"  {i}. {step}")
    print()
    print("Press [Enter] to launch TUI, interact, then return here.")
    input()


# ── Verdict handler ───────────────────────────────────────────────────────────

def _wait_verdict() -> tuple[str, str]:
    """Return (verdict, note). verdict is one of: pass, fail, skip, quit."""
    while True:
        ch = _getch().lower()
        if ch in ("\r", "\n", " "):
            return "pass", ""
        if ch == "f":
            return "fail", ""
        if ch == "n":
            # Restore normal terminal for line input
            note = input("\nNote: ")
            return "pass", note
        if ch == "s":
            return "skip", ""
        if ch == "q":
            return "quit", ""


# ── Per-test runner ───────────────────────────────────────────────────────────

def _run_one_test(
    test: dict,
    total: int,
    reporter,
    counts: dict,
    failed_tests: list[str],
    global_timeout: int | None,
) -> str:
    """Execute one test. Returns 'quit' to signal session end, else 'continue'."""
    tmp_dir = tempfile.mkdtemp(prefix=f"cap_t{test['id']}_")

    # Pre-setup: copy fixture
    if test["fixture"]:
        _copy_fixture(test["fixture"], tmp_dir)

    # Pre-setup: silent init
    if test["needs_init"] or test["pre_init"]:
        _silent_init(tmp_dir)

    # Resolve cmd (substitute sentinels)
    resolved_cmd = _resolve_cmd(test["cmd"], tmp_dir, test["fixture"])
    effective_timeout = global_timeout if global_timeout is not None else test["timeout"]

    group = test["group"]
    counts.setdefault(group, {"pass": 0, "fail": 0, "skip": 0})

    # ── TUI flow ──────────────────────────────────────────────────────────────
    if test["is_tui"]:
        fixture_url = ""
        if test["fixture"]:
            fixture_url = "file://" + str(Path(tmp_dir) / test["fixture"])
        _print_tui_header(test, total, fixture_url)
        exit_code, duration, timed_out = _run_passthrough(
            resolved_cmd, tmp_dir, effective_timeout
        )
        analysis, _, _ = _auto_analyze(test, exit_code, "", tmp_dir, timed_out, global_timeout)
        _print_result_passthrough(test, exit_code, duration, timed_out, analysis)
        verdict, note = _wait_verdict()

    # ── Passthrough flow ──────────────────────────────────────────────────────
    elif test["passthrough"]:
        _print_header(test, total)
        print("Running...  (interactive — output direct to terminal)\n")
        exit_code, duration, timed_out = _run_passthrough(
            resolved_cmd, tmp_dir, effective_timeout
        )
        analysis, _, _ = _auto_analyze(test, exit_code, "", tmp_dir, timed_out, global_timeout)
        _print_result_passthrough(test, exit_code, duration, timed_out, analysis)
        verdict, note = _wait_verdict()

    # ── Captured flow ─────────────────────────────────────────────────────────
    else:
        _print_header(test, total)
        print(f"Running...  (timeout: {effective_timeout}s)")
        exit_code, output, duration, timed_out = _run_captured(
            resolved_cmd, tmp_dir, effective_timeout
        )
        analysis, output_path, file_count = _auto_analyze(
            test, exit_code, output, tmp_dir, timed_out, global_timeout
        )
        _print_result_cli(
            test, exit_code, duration, analysis, output_path, file_count, timed_out
        )
        verdict, note = _wait_verdict()

    # ── Handle verdict ────────────────────────────────────────────────────────
    if verdict == "quit":
        return "quit"

    if verdict == "skip":
        counts[group]["skip"] += 1
        _clear()
        return "continue"

    status = "PASS" if verdict == "pass" else "FAIL"
    if verdict == "fail":
        counts[group]["fail"] += 1
        failed_tests.append(
            f"TEST {test['id']}: {test['group']} {test['label']}"
            + (f" — {note}" if note else "")
        )
    else:
        counts[group]["pass"] += 1

    output_path_for_report = None
    file_count_for_report = None
    if not test["is_tui"] and not test["passthrough"]:
        # Re-derive for report (analysis already has it, but we need the raw values)
        output_path_for_report = _find_output_path(tmp_dir)
        if test["creates_files"]:
            file_count_for_report = _count_output_files(tmp_dir)

    cmd_str = " ".join(test["cmd"]).replace("__TMP__", "<tmp>").replace("__FIXTURE_URL__", "<fixture_url>")
    reporter.write_entry(
        id=test["id"],
        group=test["group"],
        cmd=cmd_str,
        status=status,
        exit_code=exit_code,
        expected_exit=test["expected_exit"],
        duration=duration,
        output_path=output_path_for_report,
        file_count=file_count_for_report,
        analysis=analysis,
        note=note,
    )
    _clear()
    return "continue"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    from tests.acceptance.catalog import TESTS
    from tests.acceptance.reporter import Reporter

    parser = argparse.ArgumentParser(
        description="Capcat human-in-the-loop acceptance test runner"
    )
    group_filter = parser.add_mutually_exclusive_group()
    group_filter.add_argument("--group", metavar="NAME",
        help="Run only tests in this group (e.g. fetch, add-source)")
    group_filter.add_argument("--from", dest="from_id", type=int, metavar="N",
        help="Resume from test #N")
    group_filter.add_argument("--only", metavar="N,N,...",
        help="Run only these test IDs (comma-separated)")
    parser.add_argument("--timeout", type=int, metavar="SECONDS",
        help="Override timeout for all tests")
    args = parser.parse_args()

    # Build active test list
    tests = list(TESTS)
    if args.group:
        tests = [t for t in tests if t["group"] == args.group]
        if not tests:
            print(f"Error: no tests found for group '{args.group}'")
            sys.exit(1)
    elif args.from_id:
        tests = [t for t in tests if t["id"] >= args.from_id]
    elif args.only:
        ids = {int(x) for x in args.only.split(",")}
        tests = [t for t in tests if t["id"] in ids]

    total = len(tests)
    if total == 0:
        print("No tests selected.")
        sys.exit(0)

    # Create results dir and session file
    _RESULTS.mkdir(parents=True, exist_ok=True)
    session_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + ".md"
    session_path = _RESULTS / session_name
    reporter = Reporter(session_path)

    counts: dict[str, dict[str, int]] = {}
    failed_tests: list[str] = []

    _clear()
    print(f"Capcat Acceptance Test Runner")
    print(f"Session: {session_path}")
    print(f"Tests to run: {total}")
    print(f"\nPress [Enter] to begin...")
    input()

    for test in tests:
        result = _run_one_test(
            test, total, reporter, counts, failed_tests, args.timeout
        )
        if result == "quit":
            break

    reporter.finalize(counts, failed_tests)
    print(f"\nSession ended. Report saved to:\nfile://{session_path.resolve()}")


if __name__ == "__main__":
    main()
