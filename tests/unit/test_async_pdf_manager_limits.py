"""Tests for PDF size/count enforcement in AsyncPDFManager."""
import threading
from unittest.mock import MagicMock, patch
import pytest
from capcat.core.config import PdfConfig
from capcat.core.async_pdf_manager import (
    AsyncPDFManager,
    pdf_exceeds_size_limit,
    initialize_pdf_manager,
    get_pdf_manager,
)


class TestPdfExceedsSizeLimit:
    def test_returns_true_when_content_length_exceeds_limit(self):
        session = MagicMock()
        response = MagicMock()
        response.headers = {"Content-Length": "10000000"}
        session.head.return_value = response
        assert pdf_exceeds_size_limit("http://example.com/file.pdf", session, 5_000_000) is True

    def test_returns_false_when_content_length_within_limit(self):
        session = MagicMock()
        response = MagicMock()
        response.headers = {"Content-Length": "1000"}
        session.head.return_value = response
        assert pdf_exceeds_size_limit("http://example.com/file.pdf", session, 5_000_000) is False

    def test_returns_false_when_no_content_length(self):
        session = MagicMock()
        response = MagicMock()
        response.headers = {}
        session.head.return_value = response
        assert pdf_exceeds_size_limit("http://example.com/file.pdf", session, 5_000_000) is False

    def test_returns_false_when_head_raises(self):
        session = MagicMock()
        session.head.side_effect = Exception("network error")
        assert pdf_exceeds_size_limit("http://example.com/file.pdf", session, 5_000_000) is False


class TestInitializePdfManager:
    def test_initialize_seeds_singleton_with_config(self):
        cfg = PdfConfig(max_pdf_size_bytes=999_999, max_pdf_per_article=5)
        mgr = initialize_pdf_manager(cfg)
        assert mgr.pdf_config.max_pdf_size_bytes == 999_999
        assert mgr.pdf_config.max_pdf_per_article == 5

    def test_get_pdf_manager_returns_initialized_singleton(self):
        cfg = PdfConfig(max_pdf_size_bytes=888_888, max_pdf_per_article=4)
        initialize_pdf_manager(cfg)
        mgr = get_pdf_manager()
        assert mgr.pdf_config.max_pdf_size_bytes == 888_888

    def test_get_pdf_manager_uses_defaults_if_never_initialized(self):
        import capcat.core.async_pdf_manager as apm
        apm._global_pdf_manager = None
        mgr = get_pdf_manager()
        assert mgr.pdf_config.max_pdf_size_bytes == 20_971_520


class TestCountCap:
    def test_extract_stops_after_max_pdf_per_article(self):
        cfg = PdfConfig(max_pdf_size_bytes=99_999_999, max_pdf_per_article=2)
        mgr = AsyncPDFManager(pdf_config=cfg)

        with patch.object(mgr, "_download_pdf", return_value=None):
            mgr.start()
            markdown = (
                "[PDF 1](http://example.com/1.pdf)\n"
                "[PDF 2](http://example.com/2.pdf)\n"
                "[PDF 3](http://example.com/3.pdf)\n"
            )
            _, count = mgr.extract_and_queue_pdf_links(markdown, "/tmp/article1")
            mgr.stop()

        assert count == 2  # capped at max_pdf_per_article=2
