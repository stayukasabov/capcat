
import pytest
from unittest.mock import patch, MagicMock
import requests

from core.exceptions import NetworkError, InvalidFeedError
from core.source_system.rss_feed_introspector import RssFeedIntrospector

# --- Test Fixtures ---

@pytest.fixture
def mock_requests_get():
    """Fixture to patch requests.get."""
    with patch('requests.get') as mock_get:
        yield mock_get

@pytest.fixture
def valid_feed_content():
    """Provides content of a valid RSS feed for mocking."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Test Feed Title</title>
        <link>https://www.example.com/</link>
        <description>A test RSS feed.</description>
        <item>
            <title>Test Article</title>
            <link>https://www.example.com/article1</link>
            <description>This is a test article.</description>
        </item>
    </channel>
</rss>"""

@pytest.fixture
def invalid_feed_content():
    """Provides content of a non-feed HTML page."""
    return "<html><head><title>Not a feed</title></head><body><h1>Hello</h1></body></html>"


# --- Test Cases ---

def test_introspector_raises_network_error_on_connection_error(mock_requests_get):
    """
    Test 1.1 (Failure - Invalid URL): Asserts RssFeedIntrospector raises a NetworkError
    when given a malformed or unreachable URL.
    """
    url = "https://nonexistent.example.com/feed.rss"
    mock_requests_get.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(NetworkError, match=f"Could not access {url}"):
        RssFeedIntrospector(url)

def test_introspector_raises_network_error_on_http_error(mock_requests_get):
    """
    Test 1.1 (Failure - Invalid URL): Asserts RssFeedIntrospector raises a NetworkError
    for HTTP error status codes.
    """
    url = "https://example.com/feed.rss"
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests_get.return_value = mock_response

    with pytest.raises(NetworkError, match=f"Could not access {url}"):
        RssFeedIntrospector(url)

def test_introspector_raises_invalid_feed_error_for_non_feed_content(mock_requests_get, invalid_feed_content):
    """
    Test 1.2 (Failure - Not a Feed): Asserts the introspector raises an InvalidFeedError
    when the URL points to a valid webpage but not an RSS/Atom feed.
    """
    url = "https://example.com/not-a-feed.html"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = invalid_feed_content
    mock_requests_get.return_value = mock_response

    with pytest.raises(InvalidFeedError, match=f"The content at {url} doesn't appear to be a valid RSS or Atom feed."):
        RssFeedIntrospector(url)

def test_introspector_extracts_data_from_valid_feed(mock_requests_get, valid_feed_content):
    """
    Test 1.3 (Success): Asserts the introspector correctly extracts the feed's
    title and base URL from a valid RSS feed.
    """
    url = "https://example.com/feed.rss"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = valid_feed_content
    mock_requests_get.return_value = mock_response

    introspector = RssFeedIntrospector(url)

    assert introspector.feed_title == "Test Feed Title"
    assert introspector.base_url == "https://www.example.com/"
    assert introspector.url == url
