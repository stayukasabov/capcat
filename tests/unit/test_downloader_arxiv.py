#!/usr/bin/env python3
"""
Regression test: download_file must send Accept: application/pdf for document
downloads so content-negotiating servers (e.g. ArXiv) serve PDF, not HTML.
"""

from unittest.mock import MagicMock, patch

from capcat.core.downloader import download_file

ARXIV_PDF_URL = "https://arxiv.org/pdf/1808.00823.pdf"
IMAGE_URL = "https://example.com/photo.jpg"


def _make_head_response(content_type: str, status_code: int = 200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = {"content-type": content_type}
    resp.raise_for_status = MagicMock()
    return resp


def _make_get_response(content_type: str, status_code: int = 200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = {"content-type": content_type, "content-length": "1024"}
    resp.raise_for_status = MagicMock()
    resp.iter_content = MagicMock(return_value=[b"%PDF-1.4 test"])
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    resp.close = MagicMock()
    return resp


class TestDocumentDownloadAcceptHeader:
    """download_file must pass Accept: application/pdf for document type."""

    def test_head_request_includes_accept_pdf_for_document(self, tmp_path):
        """
        When file_type == 'document', HEAD request must include
        Accept: application/pdf so ArXiv serves PDF not HTML.
        """
        head_resp = _make_head_response("application/pdf")
        get_resp = _make_get_response("application/pdf")

        with patch("capcat.core.downloader.session") as mock_session:
            mock_session.head.return_value = head_resp
            mock_session.get.return_value = get_resp

            download_file(
                ARXIV_PDF_URL,
                str(tmp_path),
                "document",
                True,
            )

            head_call_kwargs = mock_session.head.call_args
            headers_sent = head_call_kwargs[1].get("headers", {})
            assert "Accept" in headers_sent, (
                "HEAD request for document must include Accept header"
            )
            assert "application/pdf" in headers_sent["Accept"], (
                "Accept header must include application/pdf"
            )

    def test_get_request_includes_accept_pdf_for_document(self, tmp_path):
        """
        When file_type == 'document', GET request must include
        Accept: application/pdf.
        """
        head_resp = _make_head_response("application/pdf")
        get_resp = _make_get_response("application/pdf")

        with patch("capcat.core.downloader.session") as mock_session:
            mock_session.head.return_value = head_resp
            mock_session.get.return_value = get_resp

            download_file(
                ARXIV_PDF_URL,
                str(tmp_path),
                "document",
                True,
            )

            get_call_kwargs = mock_session.get.call_args
            headers_sent = get_call_kwargs[1].get("headers", {})
            assert "Accept" in headers_sent, (
                "GET request for document must include Accept header"
            )
            assert "application/pdf" in headers_sent["Accept"], (
                "Accept header must include application/pdf"
            )

    def test_html_content_type_from_head_causes_skip_without_accept(self, tmp_path):
        """
        If server still returns text/html even with Accept header, download_file
        returns None (graceful skip).
        """
        head_resp = _make_head_response("text/html")

        with patch("capcat.core.downloader.session") as mock_session:
            mock_session.head.return_value = head_resp
            mock_session.get.return_value = _make_get_response("text/html")

            result = download_file(
                ARXIV_PDF_URL,
                str(tmp_path),
                "document",
                True,
            )

            assert result is None, "download_file must return None when server returns text/html"

    def test_image_head_does_not_include_accept_pdf(self, tmp_path):
        """
        Accept: application/pdf must NOT be sent for image downloads - only documents.
        """
        head_resp = _make_head_response("image/jpeg")
        get_resp = _make_get_response("image/jpeg")

        with patch("capcat.core.downloader.session") as mock_session:
            mock_session.head.return_value = head_resp
            mock_session.get.return_value = get_resp

            download_file(
                IMAGE_URL,
                str(tmp_path),
                "image",
                False,
            )

            head_call_kwargs = mock_session.head.call_args
            headers_sent = head_call_kwargs[1].get("headers", {})
            accept = headers_sent.get("Accept", "")
            assert "application/pdf" not in accept, (
                "image downloads must not send Accept: application/pdf"
            )
