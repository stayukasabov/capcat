
import requests
import feedparser
import validators
from urllib.parse import urlparse

from core.exceptions import NetworkError, InvalidFeedError, ValidationError

class RssFeedIntrospector:
    """
    Fetches, parses, and validates an RSS feed to extract key metadata.
    """

    def __init__(self, url: str):
        """
        Args:
            url: The URL of the RSS feed.

        Raises:
            ValidationError: If the URL is invalid.
            NetworkError: If there's a problem fetching the feed.
            InvalidFeedError: If the content is not a valid feed.
        """
        self.url = self._validate_url(url)
        self.raw_content = self._fetch_feed()
        self.feed = self._parse_feed()

        self.feed_title = self._extract_feed_title()
        self.base_url = self._extract_base_url()

    def _validate_url(self, url: str) -> str:
        """Validates the given URL."""
        if not validators.url(url):
            raise ValidationError("URL", url, "Must be a valid and accessible URL.")
        return url

    def _fetch_feed(self) -> str:
        """Fetches the raw content of the feed from the URL."""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise NetworkError(self.url, original_error=e) from e

    def _parse_feed(self):
        """Parses the raw feed content."""
        parsed_feed = feedparser.parse(self.raw_content)
        # feedparser is very lenient. A basic check for a title is a good heuristic.
        if "feed" not in parsed_feed or not parsed_feed.feed or "title" not in parsed_feed.feed:
            # Also check for bozo bit, which indicates a malformed feed
            if parsed_feed.bozo and isinstance(parsed_feed.bozo_exception, feedparser.CharacterEncodingOverride):
                 pass # Ignore character encoding issues, they are common.
            elif parsed_feed.bozo:
                raise InvalidFeedError(self.url, reason=str(parsed_feed.bozo_exception))

            if "feed" not in parsed_feed or not parsed_feed.feed or "title" not in parsed_feed.feed:
                 raise InvalidFeedError(self.url)

        return parsed_feed

    def _extract_feed_title(self) -> str:
        """Extracts the title from the parsed feed."""
        return self.feed.feed.get("title", "").strip()

    def _extract_base_url(self) -> str:
        """Extracts the base URL from the feed's link or the original URL."""
        if self.feed.feed.get("link"):
            return self.feed.feed.link

        # Fallback to the parsed URL components
        parsed_uri = urlparse(self.url)
        return f"{parsed_uri.scheme}://{parsed_uri.netloc}/"
