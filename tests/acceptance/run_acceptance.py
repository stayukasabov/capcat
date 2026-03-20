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
