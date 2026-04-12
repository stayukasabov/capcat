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


class TestPdfDirectUrlRespectsFlag:
    """When an article URL itself is a PDF, download_files=False must skip download."""

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
        """When article URL is a PDF and download_files=True, must download it."""
        fetcher = self._make_fetcher(download_files=True)
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
    """PDF links found in article HTML content must respect download_files flag."""

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
        """PDF links found in article content must be downloaded when download_files=True."""
        from bs4 import BeautifulSoup

        fetcher = self._make_fetcher(download_files=True)
        html = '<html><body><a href="https://example.com/paper.pdf">PDF</a></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        markdown = "[PDF](https://example.com/paper.pdf)\n\nSome content."

        with patch("capcat.core.article_fetcher.download_file", return_value=None) as mock_dl:
            fetcher._process_embedded_media_efficiently(
                soup, markdown, str(tmp_path), "https://example.com/"
            )

        mock_dl.assert_called()
