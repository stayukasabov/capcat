"""Test CLI routing and command dispatch."""
from __future__ import annotations
import sys
from unittest.mock import patch, MagicMock
import pytest


def test_catch_routes_to_tui():
    """'capcat catch' must invoke tui.run()."""
    with patch("capcat.tui.run") as mock_run:
        with patch.object(sys, "argv", ["capcat", "catch"]):
            from capcat import cli
            import importlib
            importlib.reload(cli)
            cli.main()
    mock_run.assert_called_once()


def test_init_routes_to_init_command(tmp_path):
    """'capcat init' must invoke init_project on cwd."""
    with patch("capcat.commands.init.init_project") as mock_init:
        with patch.object(sys, "argv", ["capcat", "init"]):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                from capcat.cli import main
                main()
    mock_init.assert_called_once()


def test_unknown_command_exits_nonzero():
    """Unknown command must exit with non-zero code."""
    with patch.object(sys, "argv", ["capcat", "unknowncmd123"]):
        from capcat.cli import main
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1


def test_help_flag_exits_cleanly():
    """'capcat --help' must print help and exit cleanly."""
    with patch.object(sys, "argv", ["capcat", "--help"]):
        from capcat.cli import main
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 0 or exc.code is None
