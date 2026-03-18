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
