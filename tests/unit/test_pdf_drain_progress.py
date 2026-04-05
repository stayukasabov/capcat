"""
Regression test for PDF drain progress logging.

When PDFs are still downloading at end-of-source, the drain loop must
emit periodic INFO log messages so the user knows work is in progress
rather than seeing a silent freeze.
"""
import threading
from unittest.mock import MagicMock, patch

from capcat.core.async_pdf_manager import AsyncPDFManager


class TestDrainProgressLogging:
    """Drain must log progress every ~10s while downloads are active."""

    def test_drain_logs_progress_while_active(self):
        """
        While active_downloads is non-empty, drain must call logger.info
        with a 'Downloading PDFs' message.
        """
        manager = AsyncPDFManager(max_workers=1)
        manager.start()

        # Simulate a stalled download: add an entry to active_downloads
        # that is never removed (simulates a slow download).
        fake_url = "http://example.com/slow.pdf"
        with manager._lock:
            manager.active_downloads[fake_url] = threading.Event()

        mock_info = MagicMock()
        with patch.object(manager.logger, "info", mock_info):
            drained = manager.wait_until_idle(timeout=0.5)

        manager.stop()

        assert not drained  # should time out — download never completes
        calls = [str(c) for c in mock_info.call_args_list]
        assert any(
            "Downloading PDFs" in c for c in calls
        ), f"Expected 'Downloading PDFs' in logger.info calls, got: {calls}"

    def test_drain_does_not_log_when_already_idle(self):
        """
        When queue is empty and no active downloads, drain must return True
        immediately with no 'Downloading PDFs' log call.
        """
        manager = AsyncPDFManager(max_workers=1)
        manager.start()

        mock_info = MagicMock()
        with patch.object(manager.logger, "info", mock_info):
            drained = manager.wait_until_idle(timeout=2.0)

        manager.stop()

        assert drained
        calls = [str(c) for c in mock_info.call_args_list]
        assert not any(
            "Downloading PDFs" in c for c in calls
        ), f"Unexpected 'Downloading PDFs' log when idle: {calls}"
