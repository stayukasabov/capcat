"""Tests for PDF download behaviour relative to the --media flag.

PDFs respect the download_files flag: they are downloaded only when --media
is passed (download_files=True). When the user answers No to "Download media
files?", PDFs are skipped and the original links are preserved unchanged.
"""
from unittest.mock import MagicMock, patch
import pytest


class TestPdfDownloadsWithoutMediaFlag:
    """PDFs must be skipped when download_files=False (--media not passed)."""

    def setup_method(self):
        from capcat.core.async_pdf_manager import shutdown_pdf_manager
        shutdown_pdf_manager()

    def teardown_method(self):
        from capcat.core.async_pdf_manager import shutdown_pdf_manager
        shutdown_pdf_manager()

    def _make_fetcher(self, download_files: bool):
        import requests
        from capcat.core.article_fetcher import ArticleFetcher

        class _Fetcher(ArticleFetcher):
            def should_skip_url(self, url, title):
                return False

        session = requests.Session()
        with patch("capcat.core.ethical_scraping.get_ethical_manager") as mock_em:
            mock_em.return_value.configure = MagicMock()
            fetcher = _Fetcher(session, download_files=download_files)
        return fetcher

    def test_pdf_links_not_queued_without_media_flag(self, tmp_path):
        """Without --media, PDF links must NOT be queued; original link preserved."""
        fetcher = self._make_fetcher(download_files=False)
        markdown = "[Paper](https://example.com/research.pdf)\n\nSome content."

        result = fetcher._download_pdf_links_from_markdown(markdown, str(tmp_path))

        assert "downloading_research.pdf" not in result, (
            "PDF must NOT be queued when download_files=False"
        )
        assert "https://example.com/research.pdf" in result

    def test_pdf_links_queued_with_media_flag(self, tmp_path):
        """PDFs must also queue when download_files=True (baseline check)."""
        fetcher = self._make_fetcher(download_files=True)
        markdown = "[Paper](https://example.com/research.pdf)\n\nSome content."

        result = fetcher._download_pdf_links_from_markdown(markdown, str(tmp_path))

        assert "downloading_research.pdf" in result

    def test_pdf_not_queued_when_download_files_false(self, tmp_path):
        """When download_files=False, PDF links must NOT be queued."""
        fetcher = self._make_fetcher(download_files=False)
        markdown = "[Paper](https://example.com/research.pdf)\n\nSome content."

        result = fetcher._download_pdf_links_from_markdown(markdown, str(tmp_path))

        assert "downloading_research.pdf" not in result, (
            "PDF must NOT be queued when download_files=False"
        )
        assert "https://example.com/research.pdf" in result

    def test_non_pdf_links_unchanged_without_media_flag(self, tmp_path):
        """Non-PDF links must not be touched when download_files=False."""
        fetcher = self._make_fetcher(download_files=False)
        markdown = "[Image](https://example.com/photo.jpg)\n\nSome content."

        result = fetcher._download_pdf_links_from_markdown(markdown, str(tmp_path))

        assert "photo.jpg" in result
        assert "downloading_" not in result
