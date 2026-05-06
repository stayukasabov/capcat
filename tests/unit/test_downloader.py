"""Tests for download_file retry and error handling."""
import requests
from unittest.mock import MagicMock, patch

from capcat.core.downloader import download_file
from capcat.core.config import PdfConfig


def _mock_4xx_response(status_code):
    resp = MagicMock()
    resp.status_code = status_code
    http_err = requests.exceptions.HTTPError(response=resp)
    resp.raise_for_status.side_effect = http_err
    return resp


def test_download_file_returns_none_on_403_without_retry(monkeypatch):
    """4xx response must return None immediately - no retry attempts."""
    mock_session = MagicMock()
    mock_session.head.side_effect = Exception("head blocked")
    mock_session.get.return_value = _mock_4xx_response(403)

    with patch("capcat.core.downloader.session", mock_session):
        result = download_file("https://springer.com/paper.pdf", "/tmp", "document")

    assert result is None
    assert mock_session.get.call_count == 1  # exactly one attempt, no retries


def test_download_file_returns_none_on_404_without_retry(monkeypatch):
    """404 must also return None without retry."""
    mock_session = MagicMock()
    mock_session.head.side_effect = Exception("head blocked")
    mock_session.get.return_value = _mock_4xx_response(404)

    with patch("capcat.core.downloader.session", mock_session):
        result = download_file("https://example.com/missing.pdf", "/tmp", "document")

    assert result is None
    assert mock_session.get.call_count == 1


def _head_response_with_length(content_length_bytes: int):
    resp = MagicMock()
    resp.headers = {"content-length": str(content_length_bytes), "content-type": "application/pdf"}
    resp.raise_for_status.return_value = None
    return resp


def test_download_file_skips_pdf_exceeding_config_limit(monkeypatch):
    """download_file must skip documents larger than PdfConfig.max_pdf_size_bytes."""
    mock_session = MagicMock()
    mock_session.head.return_value = _head_response_with_length(2_000_000)  # 2MB - over 500KB limit

    import capcat.core.downloader as dl
    original_config = dl.config
    dl.config = MagicMock()
    dl.config.network.head_request_timeout = 10
    dl.config.network.media_download_timeout = 60
    dl.config.pdf.max_pdf_size_bytes = 500_000
    try:
        with patch("capcat.core.downloader.session", mock_session):
            result = download_file("https://arxiv.org/pdf/1234.5678", "/tmp", "document")
    finally:
        dl.config = original_config

    assert result is None
    mock_session.get.assert_not_called()


def test_download_file_allows_pdf_within_config_limit(tmp_path):
    """download_file must proceed when document size is within PdfConfig.max_pdf_size_bytes."""
    mock_session = MagicMock()
    mock_session.head.return_value = _head_response_with_length(300_000)  # 300KB - under 500KB limit

    get_resp = MagicMock()
    get_resp.headers = {"content-type": "application/pdf"}
    get_resp.raise_for_status.return_value = None
    get_resp.iter_content.return_value = [b"PDF data"]
    mock_session.get.return_value = get_resp

    import capcat.core.downloader as dl
    original_config = dl.config
    dl.config = MagicMock()
    dl.config.network.head_request_timeout = 10
    dl.config.network.media_download_timeout = 60
    dl.config.pdf.max_pdf_size_bytes = 500_000
    try:
        with patch("capcat.core.downloader.session", mock_session):
            result = download_file("https://arxiv.org/pdf/1234.5678", str(tmp_path), "document")
    finally:
        dl.config = original_config

    assert result is not None
