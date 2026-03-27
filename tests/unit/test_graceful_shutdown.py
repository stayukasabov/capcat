"""Tests for GracefulShutdown signal handler and singleton accessor."""
import signal
import sys
from unittest.mock import patch, MagicMock

import pytest

from capcat.core.shutdown import GracefulShutdown, get_shutdown


def test_sigint_calls_os_exit_immediately():
    """SIGINT must call os._exit(130) immediately — not set the event."""
    gs = GracefulShutdown()
    with patch("capcat.core.shutdown.os") as mock_os:
        gs._signal_handler(signal.SIGINT, None)
        mock_os._exit.assert_called_once_with(130)
    assert not gs.should_shutdown(), "shutdown_event must NOT be set for SIGINT"


def test_sigterm_sets_event_gracefully():
    """SIGTERM must set shutdown_event for cooperative shutdown."""
    gs = GracefulShutdown()
    gs._signal_handler(signal.SIGTERM, None)
    assert gs.should_shutdown(), "shutdown_event must be set after SIGTERM"


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

        with patch("capcat.commands.fetch.process_source_articles") as mock_fetch, \
             patch("os._exit") as mock_exit:
            mock_fetch.return_value = None
            from capcat.commands.fetch import process_sources
            process_sources(["hn", "lb"], args, config, logger, output_dir=str(tmp_path))

    mock_exit.assert_called_once_with(130)


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

        with patch("capcat.commands.fetch.process_source_articles"), \
             patch("os._exit"):
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


def test_usp_executor_shutdown_called_in_finally():
    """executor.shutdown(wait=False, cancel_futures=True) is called in the finally block."""
    from unittest.mock import patch, MagicMock
    from concurrent.futures import Future
    from capcat.core.unified_source_processor import UnifiedSourceProcessor

    usp = UnifiedSourceProcessor()

    mock_source = MagicMock()
    mock_source.config.display_name = "TestSource"
    mock_article = MagicMock()
    mock_article.url = "https://example.com/1"
    mock_article.title = "Test Article"
    articles = [mock_article]

    mock_executor = MagicMock()
    mock_future = MagicMock(spec=Future)
    mock_executor.submit.return_value = mock_future

    with patch("capcat.core.unified_source_processor.ThreadPoolExecutor", return_value=mock_executor), \
         patch("capcat.core.unified_source_processor.as_completed", return_value=iter([])), \
         patch("capcat.core.unified_source_processor.get_shutdown", return_value=None), \
         patch("capcat.core.unified_source_processor.get_batch_progress") as mock_progress_ctx:

        mock_progress = MagicMock()
        mock_progress.__enter__ = MagicMock(return_value=mock_progress)
        mock_progress.__exit__ = MagicMock(return_value=False)
        mock_progress_ctx.return_value = mock_progress

        usp._process_articles_with_new_system(
            mock_source, articles, "/tmp", False, False, False
        )

    mock_executor.shutdown.assert_called_with(wait=False, cancel_futures=True)


def test_usp_loop_breaks_on_shutdown():
    """as_completed loop breaks when should_shutdown() returns True."""
    from unittest.mock import patch, MagicMock
    from concurrent.futures import Future
    from capcat.core.unified_source_processor import UnifiedSourceProcessor

    usp = UnifiedSourceProcessor()

    mock_source = MagicMock()
    mock_source.config.display_name = "TestSource"
    mock_article = MagicMock()
    mock_article.url = "https://example.com/shutdown-test-unique"
    mock_article.title = "Art1"
    articles = [mock_article]

    future1 = MagicMock(spec=Future)
    future1.result.return_value = True

    def fake_as_completed(fs, timeout):
        for f in fs:
            yield f

    mock_executor = MagicMock()
    mock_executor.submit.return_value = future1

    mock_shutdown = MagicMock()
    mock_shutdown.should_shutdown.return_value = True  # always True → break immediately

    with patch("capcat.core.unified_source_processor.ThreadPoolExecutor", return_value=mock_executor), \
         patch("capcat.core.unified_source_processor.as_completed", side_effect=fake_as_completed), \
         patch("capcat.core.unified_source_processor.get_shutdown", return_value=mock_shutdown), \
         patch("capcat.core.unified_source_processor.get_batch_progress") as mock_progress_ctx:

        mock_progress = MagicMock()
        mock_progress.__enter__ = MagicMock(return_value=mock_progress)
        mock_progress.__exit__ = MagicMock(return_value=False)
        mock_progress_ctx.return_value = mock_progress

        usp._process_articles_with_new_system(
            mock_source, articles, "/tmp", False, False, False
        )

    # Loop broke before calling result()
    assert future1.result.call_count == 0, "result() must not be called after shutdown"
    # Finally block still ran
    mock_executor.shutdown.assert_called_with(wait=False, cancel_futures=True)
