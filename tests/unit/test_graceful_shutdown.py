"""Tests for GracefulShutdown signal handler and singleton accessor."""
import signal
import sys
from unittest.mock import patch, MagicMock

import pytest

from capcat.core.shutdown import GracefulShutdown, get_shutdown


def test_signal_handler_sets_event_only():
    """_signal_handler sets shutdown_event and does NOT call sys.exit or time.sleep."""
    gs = GracefulShutdown()
    with patch("sys.exit") as mock_exit, patch("time.sleep") as mock_sleep:
        gs._signal_handler(signal.SIGINT, None)
    assert gs.should_shutdown(), "shutdown_event must be set after signal"
    mock_exit.assert_not_called()
    mock_sleep.assert_not_called()


def test_signal_handler_no_cleanup_func_parameter():
    """GracefulShutdown.__init__ must not accept a cleanup_func parameter."""
    import inspect
    params = inspect.signature(GracefulShutdown.__init__).parameters
    assert "cleanup_func" not in params, (
        "cleanup_func parameter must be removed — it creates a path for "
        "executor calls from the signal handler (deadlock risk)"
    )


def test_get_shutdown_returns_none_outside_context():
    """get_shutdown() returns None when no GracefulShutdown context is active."""
    assert get_shutdown() is None


def test_get_shutdown_returns_instance_inside_context():
    """get_shutdown() returns the active GracefulShutdown inside a with block."""
    with GracefulShutdown() as gs:
        result = get_shutdown()
    assert result is gs, "get_shutdown() must return the active instance"


def test_get_shutdown_returns_none_after_context_exits():
    """get_shutdown() returns None after the with block exits."""
    with GracefulShutdown():
        pass
    assert get_shutdown() is None


def test_graceful_shutdown_restores_original_handlers():
    """__exit__ restores original SIGINT handler after context manager exits."""
    original = signal.getsignal(signal.SIGINT)
    with GracefulShutdown():
        assert signal.getsignal(signal.SIGINT) != original
    assert signal.getsignal(signal.SIGINT) == original


def test_process_sources_exits_130_on_cancel(tmp_path):
    """process_sources exits with code 130 when shutdown is triggered."""
    from unittest.mock import patch, MagicMock
    import argparse

    args = argparse.Namespace(count=5, quiet=True, verbose=False, media=False)
    config = MagicMock()
    logger = MagicMock()

    with patch("capcat.commands.fetch.GracefulShutdown") as MockGS:
        mock_gs = MagicMock()
        mock_gs.__enter__ = MagicMock(return_value=mock_gs)
        mock_gs.__exit__ = MagicMock(return_value=False)
        # should_shutdown called 3 times: loop entry for hn (False), loop entry for lb (True → break),
        # post-loop check (True → print + exit 130)
        mock_gs.should_shutdown.side_effect = [False, True, True]
        MockGS.return_value = mock_gs

        with patch("capcat.commands.fetch.process_source_articles") as mock_fetch:
            mock_fetch.return_value = None
            with pytest.raises(SystemExit) as exc_info:
                from capcat.commands.fetch import process_sources
                process_sources(["hn", "lb"], args, config, logger, output_dir=str(tmp_path))

    assert exc_info.value.code == 130


def test_process_sources_prints_cancel_message(tmp_path, capsys):
    """process_sources prints how many sources were fetched before cancel."""
    from unittest.mock import patch, MagicMock
    import argparse

    args = argparse.Namespace(count=5, quiet=True, verbose=False, media=False)
    config = MagicMock()
    logger = MagicMock()

    with patch("capcat.commands.fetch.GracefulShutdown") as MockGS:
        mock_gs = MagicMock()
        mock_gs.__enter__ = MagicMock(return_value=mock_gs)
        mock_gs.__exit__ = MagicMock(return_value=False)
        # hn loop entry: False → process hn (completed=1)
        # lb loop entry: True → break (lb not processed, completed stays 1)
        # post-loop check: True → print "Cancelled — fetched 1 of 2 sources." + exit 130
        mock_gs.should_shutdown.side_effect = [False, True, True]
        MockGS.return_value = mock_gs

        with patch("capcat.commands.fetch.process_source_articles"):
            with pytest.raises(SystemExit):
                from capcat.commands.fetch import process_sources
                process_sources(["hn", "lb"], args, config, logger, output_dir=str(tmp_path))

    captured = capsys.readouterr()
    assert "Cancelled" in captured.out
    assert "1 of 2" in captured.out


def test_process_sources_returns_normally_without_cancel(tmp_path):
    """process_sources returns a dict normally when no cancellation occurs."""
    from unittest.mock import patch, MagicMock
    import argparse

    args = argparse.Namespace(count=5, quiet=True, verbose=False, media=False)
    config = MagicMock()
    logger = MagicMock()

    with patch("capcat.commands.fetch.GracefulShutdown") as MockGS:
        mock_gs = MagicMock()
        mock_gs.__enter__ = MagicMock(return_value=mock_gs)
        mock_gs.__exit__ = MagicMock(return_value=False)
        mock_gs.should_shutdown.return_value = False
        MockGS.return_value = mock_gs

        with patch("capcat.commands.fetch.process_source_articles"):
            from capcat.commands.fetch import process_sources
            result = process_sources(["hn"], args, config, logger, output_dir=str(tmp_path))

    assert isinstance(result, dict)
    assert "successful" in result
