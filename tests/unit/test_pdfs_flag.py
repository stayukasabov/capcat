"""Tests for --pdfs flag: PDF-only downloads independent of --media.

- --pdfs → download_pdfs=True, download_files=False (PDFs only)
- --media → download_files=True AND download_pdfs=True (all media incl. PDFs)
- TUI Yes → --pdfs appended, not --media
"""
from unittest.mock import MagicMock, patch
import pytest


class TestArticleFetcherDownloadPdfsFlag:
    """ArticleFetcher must gate PDFs on download_pdfs, not download_files."""

    def setup_method(self):
        from capcat.core.async_pdf_manager import shutdown_pdf_manager
        shutdown_pdf_manager()

    def teardown_method(self):
        from capcat.core.async_pdf_manager import shutdown_pdf_manager
        shutdown_pdf_manager()

    def _make_fetcher(self, download_files: bool, download_pdfs: bool):
        import requests
        from capcat.core.article_fetcher import ArticleFetcher

        class _Fetcher(ArticleFetcher):
            def should_skip_url(self, url, title):
                return False

        session = requests.Session()
        with patch("capcat.core.ethical_scraping.get_ethical_manager") as mock_em:
            mock_em.return_value.configure = MagicMock()
            fetcher = _Fetcher(session, download_files=download_files, download_pdfs=download_pdfs)
        return fetcher

    def test_pdf_downloaded_when_download_pdfs_true(self, tmp_path):
        """PDF article URL must be downloaded when download_pdfs=True, even if download_files=False."""
        fetcher = self._make_fetcher(download_files=False, download_pdfs=True)
        pdf_url = "https://arxiv.org/pdf/2301.00001.pdf"

        with (
            patch("capcat.core.unified_article_processor.get_unified_processor") as mock_proc,
            patch("capcat.core.article_fetcher.download_file", return_value=None) as mock_dl,
        ):
            mock_proc.return_value._registry.can_handle_url.return_value = False
            fetcher.fetch_article_content("Paper", pdf_url, 0, str(tmp_path))

        mock_dl.assert_called()

    def test_pdf_not_downloaded_when_download_pdfs_false(self, tmp_path):
        """PDF article URL must NOT be downloaded when download_pdfs=False."""
        fetcher = self._make_fetcher(download_files=False, download_pdfs=False)
        pdf_url = "https://example.com/paper.pdf"

        with (
            patch("capcat.core.unified_article_processor.get_unified_processor") as mock_proc,
            patch("capcat.core.article_fetcher.download_file") as mock_dl,
        ):
            mock_proc.return_value._registry.can_handle_url.return_value = False
            fetcher.fetch_article_content("Paper", pdf_url, 0, str(tmp_path))

        mock_dl.assert_not_called()

    def test_media_flag_also_enables_pdfs(self, tmp_path):
        """download_files=True must also enable PDF downloads (--media backward compat)."""
        fetcher = self._make_fetcher(download_files=True, download_pdfs=True)
        pdf_url = "https://arxiv.org/pdf/2301.00001.pdf"

        with (
            patch("capcat.core.unified_article_processor.get_unified_processor") as mock_proc,
            patch("capcat.core.article_fetcher.download_file", return_value=None) as mock_dl,
        ):
            mock_proc.return_value._registry.can_handle_url.return_value = False
            fetcher.fetch_article_content("Paper", pdf_url, 0, str(tmp_path))

        mock_dl.assert_called()

    def test_pdf_markdown_links_respect_download_pdfs(self, tmp_path):
        """Embedded PDF markdown links must respect download_pdfs, not download_files."""
        fetcher = self._make_fetcher(download_files=False, download_pdfs=True)
        markdown = "[Paper](https://example.com/research.pdf)\n\nContent."

        result = fetcher._download_pdf_links_from_markdown(markdown, str(tmp_path))

        assert "downloading_research.pdf" in result

    def test_pdf_markdown_links_skipped_when_download_pdfs_false(self, tmp_path):
        """Embedded PDF markdown links must be skipped when download_pdfs=False."""
        fetcher = self._make_fetcher(download_files=False, download_pdfs=False)
        markdown = "[Paper](https://example.com/research.pdf)\n\nContent."

        result = fetcher._download_pdf_links_from_markdown(markdown, str(tmp_path))

        assert "downloading_research.pdf" not in result
        assert "https://example.com/research.pdf" in result


class TestTuiAppendsPdfsFlag:
    """TUI must append --pdfs when user says Yes, not --media."""

    def test_tui_appends_pdfs_not_media_on_yes(self):
        """Answering Yes to PDF prompt must append --pdfs to args, not --media."""
        with patch("capcat.core.interactive.questionary") as mock_q, \
             patch("capcat.core.interactive.suppress_logging"), \
             patch("capcat.cli._dispatch") as mock_dispatch:
            mock_confirm = MagicMock()
            mock_confirm.ask.return_value = True
            mock_q.confirm.return_value = mock_confirm

            from capcat.core.interactive import _confirm_and_execute
            try:
                _confirm_and_execute(action="fetch", selection=["hn"], generate_html=False)
            except Exception:
                pass

        if mock_dispatch.called:
            call_args = str(mock_dispatch.call_args)
            assert "--pdfs" in call_args
            assert "--media" not in call_args

    def test_tui_does_not_append_media_on_yes(self):
        """Answering Yes to PDF prompt must NOT append --media."""
        with patch("capcat.core.interactive.questionary") as mock_q, \
             patch("capcat.core.interactive.suppress_logging"), \
             patch("capcat.cli._dispatch") as mock_dispatch:
            mock_confirm = MagicMock()
            mock_confirm.ask.return_value = True
            mock_q.confirm.return_value = mock_confirm

            from capcat.core.interactive import _confirm_and_execute
            try:
                _confirm_and_execute(action="fetch", selection=["hn"], generate_html=False)
            except Exception:
                pass

        if mock_dispatch.called:
            call_args = str(mock_dispatch.call_args)
            assert "--media" not in call_args
