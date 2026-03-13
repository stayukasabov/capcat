#!/usr/bin/env python3
"""
RSS/Atom feed discovery utilities.
Automatically discovers feed URLs from websites when configured feeds fail.
"""

from typing import List
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from ..logging_config import get_logger

logger = get_logger(__name__)


def discover_feed_urls(base_url: str, timeout: int = 10) -> List[str]:
    """
    Attempt to discover RSS/Atom feed URLs from a website.

    Looks for:
    - <link rel="alternate" type="application/rss+xml"> in HTML
    - <link rel="alternate" type="application/atom+xml"> in HTML
    - Common feed paths: /feed, /rss, /atom, /feed.xml, /rss.xml

    Args:
        base_url: Base URL of the website
        timeout: Request timeout in seconds

    Returns:
        List of discovered feed URLs (may be empty)
    """
    discovered = []

    try:
        logger.debug(f"Attempting feed discovery for {base_url}")

        # Fetch the homepage
        response = requests.get(
            base_url,
            timeout=timeout,
            headers={
                "User-Agent": "Capcat/2.0 (Personal news archiver; +https://github.com/capcat)"
            }
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find RSS/Atom feed links in HTML head
        feed_types = ['application/rss+xml', 'application/atom+xml', 'application/xml']

        for feed_type in feed_types:
            links = soup.find_all('link', {'type': feed_type})
            for link in links:
                if 'href' in link.attrs:
                    feed_url = urljoin(base_url, link['href'])
                    if feed_url not in discovered:
                        discovered.append(feed_url)
                        logger.debug(f"Discovered feed from HTML: {feed_url}")

        # Try common feed paths
        parsed_url = urlparse(base_url)
        base_path = f"{parsed_url.scheme}://{parsed_url.netloc}"

        common_paths = [
            '/feed',
            '/rss',
            '/atom',
            '/feed.xml',
            '/rss.xml',
            '/atom.xml',
            '/index.xml',
            '/feeds/posts/default',  # Blogger
            '/?feed=rss2',  # WordPress
            '/rss/',
            '/feed/',
        ]

        for path in common_paths:
            feed_url = base_path + path
            if feed_url not in discovered:
                discovered.append(feed_url)

        logger.info(f"Discovered {len(discovered)} potential feed URLs for {base_url}")

    except requests.RequestException as e:
        logger.debug(f"Could not fetch {base_url} for feed discovery: {e}")
    except Exception as e:
        logger.debug(f"Error during feed discovery for {base_url}: {e}")

    return discovered


def validate_feed(content: bytes) -> bool:
    """
    Quick validation that content is a valid RSS/Atom feed.

    Args:
        content: Raw feed content as bytes

    Returns:
        True if content appears to be a valid feed
    """
    try:
        # Try to parse as XML and check for feed indicators
        soup = BeautifulSoup(content, 'xml')

        # Check for RSS elements
        if soup.find('rss') or soup.find('channel'):
            return True

        # Check for Atom elements
        if soup.find('feed', {'xmlns': 'http://www.w3.org/2005/Atom'}):
            return True

        # Check for basic structure
        if soup.find('item') or soup.find('entry'):
            return True

        return False

    except Exception:
        return False


def test_feed_url(url: str, timeout: int = 10) -> bool:
    """
    Test if a URL returns a valid feed.

    Args:
        url: URL to test
        timeout: Request timeout in seconds

    Returns:
        True if URL returns a valid feed
    """
    try:
        logger.debug(f"Testing feed URL: {url}")

        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "Capcat/2.0 (Personal news archiver)"
            }
        )
        response.raise_for_status()

        is_valid = validate_feed(response.content)

        if is_valid:
            logger.debug(f"Valid feed found at {url}")
        else:
            logger.debug(f"Invalid feed at {url}")

        return is_valid

    except Exception as e:
        logger.debug(f"Failed to test feed URL {url}: {e}")
        return False


def find_working_feed_url(base_url: str, timeout: int = 10) -> str:
    """
    Discover and return first working feed URL for a website.

    Args:
        base_url: Base URL of the website
        timeout: Request timeout in seconds

    Returns:
        First working feed URL found

    Raises:
        ValueError: If no working feed URL is found
    """
    discovered_urls = discover_feed_urls(base_url, timeout)

    for url in discovered_urls:
        if test_feed_url(url, timeout):
            logger.info(f"Found working feed URL: {url}")
            return url

    raise ValueError(f"No working feed URL found for {base_url}")
