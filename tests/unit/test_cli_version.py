"""
Tests for the --version CLI flag.

Per clig.dev: --version must print '<tool> <version>' to stdout and exit 0.
"""
from __future__ import annotations

import sys
from unittest.mock import patch

import pytest


def test_version_flag_prints_capcat_and_version(capsys) -> None:
    """'capcat --version' must print 'capcat <version>' to stdout."""
    with patch.object(sys, "argv", ["capcat", "--version"]):
        from capcat.cli import main
        main()

    out = capsys.readouterr().out.strip()
    assert out.startswith("capcat "), (
        f"--version output '{out}' does not start with 'capcat '"
    )


def test_version_flag_output_matches_package_version(capsys) -> None:
    """Version printed by --version must match capcat.__version__."""
    import capcat

    with patch.object(sys, "argv", ["capcat", "--version"]):
        from capcat.cli import main
        main()

    out = capsys.readouterr().out.strip()
    assert capcat.__version__ in out, (
        f"'capcat --version' printed '{out}' but __version__ is '{capcat.__version__}'"
    )


def test_version_flag_exits_cleanly() -> None:
    """'capcat --version' must not raise SystemExit or any exception."""
    with patch.object(sys, "argv", ["capcat", "--version"]):
        from capcat.cli import main
        try:
            main()
        except SystemExit as exc:
            pytest.fail(f"--version raised SystemExit({exc.code})")


def test_version_not_written_to_stderr(capsys) -> None:
    """Version output must go to stdout, not stderr (clig.dev standard)."""
    with patch.object(sys, "argv", ["capcat", "--version"]):
        from capcat.cli import main
        main()

    err = capsys.readouterr().err
    assert err == "", f"--version wrote to stderr: '{err}'"
