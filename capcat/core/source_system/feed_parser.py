#!/usr/bin/env python3
"""
Feed parser abstraction for RSS and Atom feeds.
Provides clean separation of feed parsing logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import feedparser as _feedparser


@dataclass
class FeedItem:
    """Represents a single item from a feed."""
    title: str
    url: str
    description: Optional[str] = None
    published_date: Optional[datetime] = None


class FeedParser(ABC):
    """Base class for feed parsers."""

    @abstractmethod
    def parse(self, content: bytes) -> List[FeedItem]:
        """
        Parse feed content into FeedItem objects.

        Args:
            content: Raw feed content as bytes

        Returns:
            List of FeedItem objects
        """
        pass


def _parse_feedparser_entries(entries) -> List[FeedItem]:
    """Convert feedparser entries to FeedItem list sorted newest-first.

    Args:
        entries: Sequence of feedparser entry dicts.

    Returns:
        List of FeedItem objects sorted by date descending.
    """
    items = []
    for entry in entries:
        title = entry.get('title', '').strip()
        url = entry.get('link', '').strip()
        if not title or not url:
            continue

        description = (
            entry.get('summary') or entry.get('content', [{}])[0].get('value', '')
        ).strip() or None

        pub_date = None
        time_struct = entry.get('published_parsed') or entry.get('updated_parsed')
        if time_struct:
            try:
                pub_date = datetime(*time_struct[:6])
            except (TypeError, ValueError):
                pass

        items.append(FeedItem(
            title=title,
            url=url,
            description=description,
            published_date=pub_date,
        ))

    items.sort(
        key=lambda x: x.published_date if x.published_date else datetime.min,
        reverse=True,
    )
    return items


class RSSParser(FeedParser):
    """Parser for RSS 2.0 feeds."""

    def parse(self, content: bytes) -> List[FeedItem]:
        """
        Parse RSS feed content.

        Args:
            content: Raw RSS content as bytes

        Returns:
            List of FeedItem objects sorted by date (most recent first)
        """
        parsed = _feedparser.parse(content)
        if parsed.get('bozo') and not parsed.get('entries'):
            raise ValueError(f"Invalid RSS feed: {parsed.get('bozo_exception')}")
        return _parse_feedparser_entries(parsed.entries)


class AtomParser(FeedParser):
    """Parser for Atom feeds."""

    def parse(self, content: bytes) -> List[FeedItem]:
        """
        Parse Atom feed content.

        Args:
            content: Raw Atom content as bytes

        Returns:
            List of FeedItem objects sorted by date (most recent first)
        """
        parsed = _feedparser.parse(content)
        if parsed.get('bozo') and not parsed.get('entries'):
            raise ValueError(f"Invalid Atom feed: {parsed.get('bozo_exception')}")
        return _parse_feedparser_entries(parsed.entries)


class FeedParserFactory:
    """Factory for creating appropriate feed parsers."""

    @staticmethod
    def detect_and_parse(content: bytes) -> List[FeedItem]:
        """
        Auto-detect feed type and parse.

        Args:
            content: Raw feed content as bytes

        Returns:
            List of FeedItem objects

        Raises:
            ValueError: If feed format is unrecognized or invalid
        """
        parsed = _feedparser.parse(content)
        if not parsed.get('entries') and parsed.get('bozo'):
            raise ValueError(
                f"Invalid XML feed: {parsed.get('bozo_exception')}"
            )
        return _parse_feedparser_entries(parsed.entries)
