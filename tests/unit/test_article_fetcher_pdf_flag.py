"""
Regression test: download_files=True must NOT imply download_pdfs=True.

Root cause:
    ArticleFetcher.__init__ had:
        self.download_pdfs = download_pdfs or download_files

    When config has download_images=True but download_pdfs=False, _resolve_media
    returns (download_files=True, download_pdfs=False).  The OR in the constructor
    overrode that and enabled PDF downloads regardless.

    This also broke the force_no_pdfs TUI fix: even with force_no_pdfs=True,
    resolved_pdfs was False but download_files was True, so self.download_pdfs=True.

Fix:
    self.download_pdfs = download_pdfs   (remove or download_files)

    The CLI already couples --media → PDFs via  pdfs = pdfs or media  in cli.py,
    so the or-download_files in the constructor was always redundant.
"""
import os
import struct
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from capcat.core.article_fetcher import NewsSourceArticleFetcher


_SOURCE_CONFIG = {
    "name": "test",
    "content_selectors": ["body"],
    "skip_patterns": [],
}


class TestArticleFetcherPdfFlagIndependentOfDownloadFiles:
    """download_files=True must NOT override download_pdfs=False."""

    def _make_session(self):
        session = MagicMock()
        session.timeout = None
        return session

    def _make_fetcher(self, download_files: bool, download_pdfs: bool):
        with patch("capcat.core.article_fetcher.get_config"), \
             patch("capcat.core.article_fetcher.initialize_pdf_manager"), \
             patch("capcat.core.ethical_scraping.get_ethical_manager"):
            return NewsSourceArticleFetcher(
                _SOURCE_CONFIG,
                self._make_session(),
                download_files=download_files,
                download_pdfs=download_pdfs,
            )

    def test_download_files_true_does_not_enable_pdfs(self):
        """download_files=True with download_pdfs=False → self.download_pdfs must be False."""
        fetcher = self._make_fetcher(download_files=True, download_pdfs=False)
        assert fetcher.download_pdfs is False, (
            "download_files=True must not enable PDF downloads. "
            "Config download_images=True + download_pdfs=False was downloading PDFs."
        )
        assert fetcher.download_pdfs is False, (
            "download_files=True must not enable PDF downloads. "
            "Config download_images=True + download_pdfs=False was downloading PDFs."
        )

    def test_download_files_false_download_pdfs_false(self):
        """Both False → download_pdfs remains False."""
        fetcher = self._make_fetcher(download_files=False, download_pdfs=False)
        assert fetcher.download_pdfs is False

    def test_download_pdfs_true_is_respected(self):
        """download_pdfs=True must still work when set explicitly."""
        fetcher = self._make_fetcher(download_files=False, download_pdfs=True)
        assert fetcher.download_pdfs is True

    def test_both_true_still_downloads_pdfs(self):
        """download_files=True + download_pdfs=True (--media flag path) → PDFs enabled."""
        fetcher = self._make_fetcher(download_files=True, download_pdfs=True)
        assert fetcher.download_pdfs is True
