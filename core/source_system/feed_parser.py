#!/usr/bin/env python3
"""
Feed parser abstraction for RSS and Atom feeds.
Provides clean separation of feed parsing logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from lxml import etree


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
        try:
            root = etree.fromstring(content)
            items = root.xpath('.//item')

            feed_items = []
            for item in items:
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')
                pub_date_elem = item.find('pubDate')

                if title_elem is None or link_elem is None:
                    continue

                title = self._get_text(title_elem)
                url = self._get_text(link_elem)
                description = self._get_text(desc_elem) if desc_elem is not None else None
                pub_date = self._parse_rss_date(pub_date_elem) if pub_date_elem is not None else None

                if title and url:
                    feed_items.append(FeedItem(
                        title=title,
                        url=url,
                        description=description,
                        published_date=pub_date
                    ))

            # Sort by date (most recent first), items without dates go to end
            feed_items.sort(
                key=lambda x: x.published_date if x.published_date else datetime.min,
                reverse=True
            )

            return feed_items

        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid RSS XML: {e}")

    @staticmethod
    def _get_text(element) -> str:
        """Extract and clean text from XML element."""
        return (element.text or "").strip()

    @staticmethod
    def _parse_rss_date(element) -> Optional[datetime]:
        """
        Parse RSS pubDate to datetime.

        RSS uses RFC 822/2822 format: "Mon, 08 Dec 2025 12:00:00 GMT"

        Args:
            element: XML element containing date

        Returns:
            datetime object or None if parsing fails
        """
        date_str = (element.text or "").strip()
        if not date_str:
            return None

        try:
            # Try RFC 2822 format (most common in RSS)
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            pass

        # Fallback: try ISO 8601 format
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None


class AtomParser(FeedParser):
    """Parser for Atom feeds."""

    ATOM_NS = {'atom': 'http://www.w3.org/2005/Atom'}

    def parse(self, content: bytes) -> List[FeedItem]:
        """
        Parse Atom feed content.

        Args:
            content: Raw Atom content as bytes

        Returns:
            List of FeedItem objects sorted by date (most recent first)
        """
        try:
            root = etree.fromstring(content)

            # Try with namespace first
            entries = root.xpath('.//atom:entry', namespaces=self.ATOM_NS)

            # Fallback without namespace
            if not entries:
                entries = root.xpath('.//entry')

            feed_items = []
            for entry in entries:
                title = self._extract_title(entry)
                url = self._extract_link(entry)
                description = self._extract_description(entry)
                pub_date = self._extract_date(entry)

                if title and url:
                    feed_items.append(FeedItem(
                        title=title,
                        url=url,
                        description=description,
                        published_date=pub_date
                    ))

            # Sort by date (most recent first), items without dates go to end
            feed_items.sort(
                key=lambda x: x.published_date if x.published_date else datetime.min,
                reverse=True
            )

            return feed_items

        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid Atom XML: {e}")

    def _extract_title(self, entry) -> Optional[str]:
        """Extract title from Atom entry."""
        # Try with namespace
        title_elem = entry.xpath('.//atom:title', namespaces=self.ATOM_NS)
        if not title_elem:
            # Fallback without namespace
            title_elem = entry.xpath('.//title')

        return self._get_text(title_elem[0]) if title_elem else None

    def _extract_link(self, entry) -> Optional[str]:
        """Extract link from Atom entry."""
        # Try with namespace - prefer alternate links
        link_elem = entry.xpath('.//atom:link[@rel="alternate"]/@href', namespaces=self.ATOM_NS)
        if not link_elem:
            # Try any link with namespace
            link_elem = entry.xpath('.//atom:link/@href', namespaces=self.ATOM_NS)
        if not link_elem:
            # Fallback without namespace
            link_elem = entry.xpath('.//link[@rel="alternate"]/@href')
        if not link_elem:
            link_elem = entry.xpath('.//link/@href')

        return link_elem[0].strip() if link_elem else None

    def _extract_description(self, entry) -> Optional[str]:
        """Extract description/summary from Atom entry."""
        # Try summary first
        desc_elem = entry.xpath('.//atom:summary', namespaces=self.ATOM_NS)
        if not desc_elem:
            # Try content
            desc_elem = entry.xpath('.//atom:content', namespaces=self.ATOM_NS)
        if not desc_elem:
            # Fallback without namespace
            desc_elem = entry.xpath('.//summary')
        if not desc_elem:
            desc_elem = entry.xpath('.//content')

        return self._get_text(desc_elem[0]) if desc_elem else None

    def _extract_date(self, entry) -> Optional[datetime]:
        """
        Extract publication date from Atom entry.

        Atom uses <published> and <updated> tags in ISO 8601 format.

        Args:
            entry: Atom entry element

        Returns:
            datetime object or None if parsing fails
        """
        # Try published first (preferred)
        date_elem = entry.xpath('.//atom:published', namespaces=self.ATOM_NS)
        if not date_elem:
            # Try updated
            date_elem = entry.xpath('.//atom:updated', namespaces=self.ATOM_NS)
        if not date_elem:
            # Fallback without namespace
            date_elem = entry.xpath('.//published')
        if not date_elem:
            date_elem = entry.xpath('.//updated')

        if not date_elem:
            return None

        date_str = self._get_text(date_elem[0])
        if not date_str:
            return None

        try:
            # Atom uses ISO 8601 format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _get_text(element) -> str:
        """Extract and clean text from XML element."""
        return (element.text or "").strip()


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
        try:
            root = etree.fromstring(content)

            # Check for RSS
            if root.tag == 'rss' or root.xpath('.//item'):
                return RSSParser().parse(content)

            # Check for Atom (with or without namespace)
            if (root.tag.endswith('feed') or
                root.xpath('.//entry') or
                root.xpath('.//{http://www.w3.org/2005/Atom}entry')):
                return AtomParser().parse(content)

            raise ValueError("Unrecognized feed format")

        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML feed: {e}")
