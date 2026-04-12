"""Tests for PDF landing-page redirect and stub-article fallback.

When download_files=False and an article URL is a direct PDF link:
  - Known domains (arxiv, biorxiv, etc.) → redirect to HTML landing page
  - Unknown domains → stub article explaining the PDF with re-run instructions
"""
from unittest.mock import MagicMock, patch
import pytest


# ---------------------------------------------------------------------------
# Tests for resolve_pdf_to_landing_page()
# ---------------------------------------------------------------------------

class TestResolvePdfToLandingPage:
    """Unit tests for the URL rewrite helper."""

    def _resolve(self, url):
        from capcat.core.pdf_landing_resolver import resolve_pdf_to_landing_page
        return resolve_pdf_to_landing_page(url)

    def test_arxiv_pdf_resolves_to_abs(self):
        url = "https://arxiv.org/pdf/2301.00001.pdf"
        assert self._resolve(url) == "https://arxiv.org/abs/2301.00001"

    def test_arxiv_pdf_without_extension_resolves(self):
        url = "https://arxiv.org/pdf/2301.00001v2"
        assert self._resolve(url) == "https://arxiv.org/abs/2301.00001v2"

    def test_biorxiv_pdf_resolves_to_content(self):
        url = "https://www.biorxiv.org/content/10.1101/2021.01.01.000000v1.full.pdf"
        result = self._resolve(url)
        assert result == "https://www.biorxiv.org/content/10.1101/2021.01.01.000000v1"

    def test_medrxiv_pdf_resolves(self):
        url = "https://www.medrxiv.org/content/10.1101/2021.01.01.000000v1.full.pdf"
        result = self._resolve(url)
        assert result == "https://www.medrxiv.org/content/10.1101/2021.01.01.000000v1"

    def test_unknown_domain_returns_none(self):
        url = "https://example.com/research.pdf"
        assert self._resolve(url) is None

    def test_non_pdf_url_returns_none(self):
        url = "https://arxiv.org/abs/2301.00001"
        assert self._resolve(url) is None


# ---------------------------------------------------------------------------
# Tests for stub article creation
# ---------------------------------------------------------------------------

class TestPdfStubArticle:
    """Stub article must be created for unknown PDF domains when download_files=False."""

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

    def test_stub_created_for_unknown_pdf_domain(self, tmp_path):
        """Unknown PDF domain with download_files=False must produce a stub markdown file."""
        fetcher = self._make_fetcher(download_files=False)

        with (
            patch("capcat.core.unified_article_processor.get_unified_processor") as mock_proc,
            patch("capcat.core.article_fetcher.download_file"),
        ):
            mock_proc.return_value._registry.can_handle_url.return_value = False
            success, title, folder = fetcher.fetch_article_content(
                "Research Paper",
                "https://example.com/paper.pdf",
                0,
                str(tmp_path),
            )

        assert success is True
        assert folder is not None
        md_files = list(tmp_path.rglob("*.md"))
        assert len(md_files) == 1
        content = md_files[0].read_text()
        assert "direct link to a PDF" in content.lower() or "pdf" in content.lower()
        assert "--media" in content

    def test_stub_contains_source_url(self, tmp_path):
        """Stub article must include the original PDF URL."""
        fetcher = self._make_fetcher(download_files=False)
        pdf_url = "https://example.com/paper.pdf"

        with (
            patch("capcat.core.unified_article_processor.get_unified_processor") as mock_proc,
            patch("capcat.core.article_fetcher.download_file"),
        ):
            mock_proc.return_value._registry.can_handle_url.return_value = False
            fetcher.fetch_article_content(
                "Research Paper", pdf_url, 0, str(tmp_path)
            )

        md_files = list(tmp_path.rglob("*.md"))
        content = md_files[0].read_text()
        assert pdf_url in content

    def test_stub_does_not_download_pdf(self, tmp_path):
        """Stub path must not call download_file."""
        fetcher = self._make_fetcher(download_files=False)

        with (
            patch("capcat.core.unified_article_processor.get_unified_processor") as mock_proc,
            patch("capcat.core.article_fetcher.download_file") as mock_dl,
        ):
            mock_proc.return_value._registry.can_handle_url.return_value = False
            fetcher.fetch_article_content(
                "Research Paper",
                "https://example.com/paper.pdf",
                0,
                str(tmp_path),
            )

        mock_dl.assert_not_called()


# ---------------------------------------------------------------------------
# Tests for landing-page redirect in fetch_article_content
# ---------------------------------------------------------------------------

class TestPdfLandingPageRedirect:
    """Known PDF domains must redirect to HTML landing page instead of downloading."""

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

    def test_arxiv_pdf_fetches_landing_page(self, tmp_path):
        """arxiv PDF URL with download_files=False must fetch the /abs/ page, not download."""
        fetcher = self._make_fetcher(download_files=False)
        arxiv_pdf = "https://arxiv.org/pdf/2301.00001.pdf"
        arxiv_abs = "https://arxiv.org/abs/2301.00001"

        with (
            patch("capcat.core.unified_article_processor.get_unified_processor") as mock_proc,
            patch("capcat.core.article_fetcher.download_file") as mock_dl,
            patch.object(fetcher, "_fetch_web_content", return_value=(True, "title", str(tmp_path))) as mock_fwc,
        ):
            mock_proc.return_value._registry.can_handle_url.return_value = False
            fetcher.fetch_article_content("Paper", arxiv_pdf, 0, str(tmp_path))

        mock_dl.assert_not_called()
        # Must have been called with the resolved abs URL, not the pdf URL
        call_args = mock_fwc.call_args
        assert arxiv_abs in call_args[0] or arxiv_abs in str(call_args)
        assert arxiv_pdf not in str(call_args[0])
