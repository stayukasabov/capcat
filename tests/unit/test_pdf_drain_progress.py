"""
Tests for PDF drain progress bar.

wait_until_idle() must use ProgressIndicator (not logger.info) to show
download progress. The indicator must only be created when there are
actual downloads to drain.
"""
import threading
from unittest.mock import MagicMock, patch

from capcat.core.async_pdf_manager import AsyncPDFManager


class TestDrainProgressIndicator:
    """wait_until_idle() must drive a ProgressIndicator, not log lines."""

    def test_indicator_started_and_error_called_on_timeout(self):
        """
        When downloads are active and drain times out, ProgressIndicator
        must be started and error() called - not logger.info.
        """
        manager = AsyncPDFManager(max_workers=1)
        manager.start()

        fake_url = "http://example.com/slow.pdf"
        with manager._lock:
            manager.active_downloads[fake_url] = threading.Event()

        mock_indicator = MagicMock()

        with patch(
            "capcat.core.async_pdf_manager.ProgressIndicator",
            return_value=mock_indicator,
        ) as mock_pi_class:
            drained = manager.wait_until_idle(timeout=0.3)

        manager.stop()

        assert not drained
        mock_pi_class.assert_called_once()
        args, kwargs = mock_pi_class.call_args
        assert args[0] == "Downloading PDFs"
        assert kwargs.get("total", args[1] if len(args) > 1 else None) >= 1
        mock_indicator.start.assert_called_once()
        mock_indicator.error.assert_called_once()
        mock_indicator.stop.assert_not_called()

    def test_indicator_started_and_stop_called_on_completion(self):
        """
        When all downloads complete before timeout, ProgressIndicator
        must be started and stop() called - not error().
        """
        manager = AsyncPDFManager(max_workers=1)
        manager.start()

        fake_url = "http://example.com/done.pdf"
        done_event = threading.Event()
        done_event.set()
        with manager._lock:
            manager.active_downloads[fake_url] = done_event
            manager.completed_downloads[fake_url] = "/tmp/done.pdf"

        mock_indicator = MagicMock()

        def fake_start():
            # Clear the active download so the next poll sees idle
            with manager._lock:
                manager.active_downloads.clear()

        mock_indicator.start.side_effect = fake_start

        with patch(
            "capcat.core.async_pdf_manager.ProgressIndicator",
            return_value=mock_indicator,
        ):
            drained = manager.wait_until_idle(timeout=5.0)

        manager.stop()

        assert drained
        mock_indicator.start.assert_called_once()
        mock_indicator.stop.assert_called_once()
        mock_indicator.error.assert_not_called()

    def test_no_indicator_when_already_idle(self):
        """
        When queue is empty and no active downloads, wait_until_idle must
        return True immediately without creating a ProgressIndicator.
        """
        manager = AsyncPDFManager(max_workers=1)
        manager.start()

        with patch(
            "capcat.core.async_pdf_manager.ProgressIndicator"
        ) as mock_pi_class:
            drained = manager.wait_until_idle(timeout=2.0)

        manager.stop()

        assert drained
        mock_pi_class.assert_not_called()

    def test_indicator_current_updated_as_downloads_complete(self):
        """
        During polling, indicator.current must be set to the completed_count.
        Set up 1 already-completed PDF and 1 stalled active PDF (times out).
        After timeout, indicator.current must equal 1 (the completed one).
        """
        manager = AsyncPDFManager(max_workers=1)
        manager.start()

        stalled_url = "http://example.com/slow.pdf"
        done_url = "http://example.com/done.pdf"
        with manager._lock:
            manager.active_downloads[stalled_url] = threading.Event()
            manager.completed_downloads[done_url] = "/tmp/done.pdf"

        mock_indicator = MagicMock()
        mock_indicator.current = 0

        with patch(
            "capcat.core.async_pdf_manager.ProgressIndicator",
            return_value=mock_indicator,
        ):
            drained = manager.wait_until_idle(timeout=0.3)

        manager.stop()

        assert not drained  # stalled download times out
        assert mock_indicator.current == 1, (
            f"Expected indicator.current == 1, got {mock_indicator.current}"
        )
