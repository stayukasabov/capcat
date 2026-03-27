"""Tests for download_file retry and error handling."""
import requests
from unittest.mock import MagicMock, patch

from capcat.core.downloader import download_file


def _mock_4xx_response(status_code):
    resp = MagicMock()
    resp.status_code = status_code
    http_err = requests.exceptions.HTTPError(response=resp)
    resp.raise_for_status.side_effect = http_err
    return resp


def test_download_file_returns_none_on_403_without_retry(monkeypatch):
    """4xx response must return None immediately — no retry attempts."""
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
