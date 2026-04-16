"""
Regression tests for per-source PDF settings.

Spec: docs/superpowers/specs/2026-04-16-per-source-pdf-settings-design.md
"""
from unittest.mock import MagicMock, patch


def _make_fetcher(source_config):
    with (
        patch("capcat.core.article_fetcher.get_config"),
        patch("capcat.core.article_fetcher.initialize_pdf_manager"),
        patch("capcat.core.ethical_scraping.get_ethical_manager"),
    ):
        from capcat.core.article_fetcher import NewsSourceArticleFetcher
        return NewsSourceArticleFetcher(source_config, MagicMock())


class TestSourceMaxPdfBytes:
    """_source_max_pdf_bytes returns per-source override or global fallback."""

    def test_returns_per_source_bytes_when_yaml_has_max_pdf_size_mb(self):
        fetcher = _make_fetcher({"name": "test", "media": {"max_pdf_size_mb": 5}})
        assert fetcher._source_max_pdf_bytes() == 5 * 1024 * 1024

    def test_returns_global_bytes_when_no_yaml_entry(self):
        mock_config = MagicMock()
        mock_config.pdf.max_pdf_size_bytes = 12345678
        with patch("capcat.core.article_fetcher.get_config", return_value=mock_config):
            fetcher = _make_fetcher({"name": "test"})
            assert fetcher._source_max_pdf_bytes() == 12345678
