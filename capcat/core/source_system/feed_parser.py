#!/usr/bin/env python3
"""
Feed parser abstraction for RSS and Atom feeds.
Provides clean separation of feed parsing logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import feedparser as _fp


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


def _parse_feedparser_date(time_struct) -> Optional[datetime]:
    """
    Convert a feedparser time_struct to datetime.

    Args:
        time_struct: A time.struct_time returned by feedparser

    Returns:
        datetime object or None
    """
    if time_struct is None:
        return None
    try:
        import calendar
        return datetime.utcfromtimestamp(calendar.timegm(time_struct))
    except Exception:
        return None


def _entries_to_feed_items(entries) -> List[FeedItem]:
    """
    Convert feedparser entries to FeedItem objects sorted by date.

    Args:
        entries: Sequence of feedparser entry objects

    Returns:
        List of FeedItem objects sorted by date (most recent first)
    """
    feed_items = []
    for entry in entries:
        title = (getattr(entry, 'title', None) or '').strip()
        url = (getattr(entry, 'link', None) or '').strip()
        if not title or not url:
            continue
        summary = (getattr(entry, 'summary', None) or '').strip() or None
        pub_date = _parse_feedparser_date(
            getattr(entry, 'published_parsed', None)
            or getattr(entry, 'updated_parsed', None)
        )
        feed_items.append(FeedItem(
            title=title,
            url=url,
            description=summary,
            published_date=pub_date,
        ))

    feed_items.sort(
        key=lambda x: x.published_date if x.published_date else datetime.min,
        reverse=True,
    )
    return feed_items


class RSSParser(FeedParser):
    """Parser for RSS 2.0 feeds."""

    def parse(self, content: bytes) -> List[FeedItem]:
        """
        Parse RSS feed content.

        Args:
            content: Raw RSS content as bytes

        Returns:
            List of FeedItem objects sorted by date (most recent first)

        Raises:
            ValueError: If the content cannot be parsed as RSS
        """
        parsed = _fp.parse(content)
        if parsed.bozo and not parsed.entries:
            raise ValueError(f"Invalid RSS feed: {parsed.bozo_exception}")
        return _entries_to_feed_items(parsed.entries)


class AtomParser(FeedParser):
    """Parser for Atom feeds."""

    def parse(self, content: bytes) -> List[FeedItem]:
        """
        Parse Atom feed content.

        Args:
            content: Raw Atom content as bytes

        Returns:
            List of FeedItem objects sorted by date (most recent first)

        Raises:
            ValueError: If the content cannot be parsed as Atom
        """
        parsed = _fp.parse(content)
        if parsed.bozo and not parsed.entries:
            raise ValueError(f"Invalid Atom feed: {parsed.bozo_exception}")
        return _entries_to_feed_items(parsed.entries)


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
        parsed = _fp.parse(content)
        if parsed.bozo and not parsed.entries:
            raise ValueError(
                f"Invalid or unrecognized feed: {parsed.bozo_exception}"
            )
        return _entries_to_feed_items(parsed.entries)
