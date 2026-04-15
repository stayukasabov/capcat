"""Tests for PDF download behaviour relative to flags.

download_pdfs controls PDF downloads independently of download_files.
--media sets both download_files=True and download_pdfs=True at the CLI level.
When the user answers No to the PDF prompt, download_pdfs=False regardless of
download_files.
"""
from unittest.mock import MagicMock, patch
import pytest


class TestPdfDownloadsWithoutMediaFlag:
    """PDFs must be skipped when download_pdfs=False."""

    def setup_method(self):
        from capcat.core.async_pdf_manager import shutdown_pdf_manager
        shutdown_pdf_manager()

    def teardown_method(self):
        from capcat.core.async_pdf_manager import shutdown_pdf_manager
        shutdown_pdf_manager()

    def _make_fetcher(self, download_files: bool, download_pdfs: bool = False):
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
        """PDFs queue when download_files=True and download_pdfs=True (--media path)."""
        fetcher = self._make_fetcher(download_files=True, download_pdfs=True)
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


class TestPdfDirectUrlRespectsFlag:
    """When an article URL itself is a PDF, download_pdfs=False must skip download."""

    def setup_method(self):
        from capcat.core.async_pdf_manager import shutdown_pdf_manager
        shutdown_pdf_manager()

    def teardown_method(self):
        from capcat.core.async_pdf_manager import shutdown_pdf_manager
        shutdown_pdf_manager()

    def _make_fetcher(self, download_files: bool, download_pdfs: bool = False):
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

    def test_pdf_article_url_not_downloaded_without_media_flag(self, tmp_path):
        """When article URL is a PDF and download_files=False, must NOT download it."""
        fetcher = self._make_fetcher(download_files=False)
        pdf_url = "https://arxiv.org/pdf/2301.00001.pdf"

        with (
            patch(
                "capcat.core.unified_article_processor.get_unified_processor"
            ) as mock_proc,
            patch("capcat.core.article_fetcher.download_file") as mock_dl,
            patch.object(fetcher, "_fetch_web_content", return_value=(False, None, None)),
        ):
            mock_proc.return_value._registry.can_handle_url.return_value = False
            fetcher.fetch_article_content("Paper", pdf_url, 0, str(tmp_path))

        mock_dl.assert_not_called()

    def test_pdf_article_url_downloaded_with_media_flag(self, tmp_path):
        """When article URL is a PDF and download_pdfs=True, must download it."""
        fetcher = self._make_fetcher(download_files=True, download_pdfs=True)
        pdf_url = "https://arxiv.org/pdf/2301.00001.pdf"

        with (
            patch(
                "capcat.core.unified_article_processor.get_unified_processor"
            ) as mock_proc,
            patch("capcat.core.article_fetcher.download_file", return_value=None) as mock_dl,
        ):
            mock_proc.return_value._registry.can_handle_url.return_value = False
            fetcher.fetch_article_content("Paper", pdf_url, 0, str(tmp_path))

        mock_dl.assert_called()


class TestPdfContentLinksRespectFlag:
    """PDF links found in article HTML content must respect download_pdfs flag."""

    def setup_method(self):
        from capcat.core.async_pdf_manager import shutdown_pdf_manager
        shutdown_pdf_manager()

    def teardown_method(self):
        from capcat.core.async_pdf_manager import shutdown_pdf_manager
        shutdown_pdf_manager()

    def _make_fetcher(self, download_files: bool, download_pdfs: bool = False):
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

    def test_pdf_content_link_not_downloaded_without_media_flag(self, tmp_path):
        """PDF links found in article content must NOT be downloaded when download_files=False."""
        from bs4 import BeautifulSoup

        fetcher = self._make_fetcher(download_files=False)
        html = '<html><body><a href="https://example.com/paper.pdf">PDF</a></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        markdown = "[PDF](https://example.com/paper.pdf)\n\nSome content."

        with patch("capcat.core.article_fetcher.download_file") as mock_dl:
            fetcher._process_embedded_media_efficiently(
                soup, markdown, str(tmp_path), "https://example.com/"
            )

        mock_dl.assert_not_called()

    def test_pdf_content_link_downloaded_with_media_flag(self, tmp_path):
        """PDF links found in article content must be downloaded when download_pdfs=True."""
        from bs4 import BeautifulSoup

        fetcher = self._make_fetcher(download_files=True, download_pdfs=True)
        html = '<html><body><a href="https://example.com/paper.pdf">PDF</a></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        markdown = "[PDF](https://example.com/paper.pdf)\n\nSome content."

        with patch("capcat.core.article_fetcher.download_file", return_value=None) as mock_dl:
            fetcher._process_embedded_media_efficiently(
                soup, markdown, str(tmp_path), "https://example.com/"
            )

        mock_dl.assert_called()
