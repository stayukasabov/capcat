#!/usr/bin/env python3
"""
Test feed parser date extraction and sorting.

Verifies that RSS and Atom feeds are sorted by publication date
with most recent articles first.
"""

import unittest
from datetime import datetime

from core.source_system.feed_parser import RSSParser, AtomParser


class TestRSSDateSorting(unittest.TestCase):
    """Test RSS feed date extraction and sorting."""

    def test_rss_extracts_and_sorts_by_date(self):
        """RSS parser should extract dates and sort by most recent first."""
        rss_content = b"""<?xml version="1.0"?>
<rss version="2.0">
    <channel>
        <title>Test Feed</title>
        <item>
            <title>Old Article</title>
            <link>https://example.com/old</link>
            <pubDate>Mon, 01 Dec 2025 12:00:00 GMT</pubDate>
        </item>
        <item>
            <title>Newest Article</title>
            <link>https://example.com/newest</link>
            <pubDate>Mon, 08 Dec 2025 12:00:00 GMT</pubDate>
        </item>
        <item>
            <title>Middle Article</title>
            <link>https://example.com/middle</link>
            <pubDate>Wed, 04 Dec 2025 12:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>"""

        parser = RSSParser()
        items = parser.parse(rss_content)

        # Should be 3 items
        self.assertEqual(len(items), 3)

        # Should be sorted by date, most recent first
        self.assertEqual(items[0].title, "Newest Article")
        self.assertEqual(items[1].title, "Middle Article")
        self.assertEqual(items[2].title, "Old Article")

        # Dates should be extracted
        self.assertIsNotNone(items[0].published_date)
        self.assertIsNotNone(items[1].published_date)
        self.assertIsNotNone(items[2].published_date)

        # Verify dates are in descending order
        self.assertGreater(items[0].published_date, items[1].published_date)
        self.assertGreater(items[1].published_date, items[2].published_date)


class TestAtomDateSorting(unittest.TestCase):
    """Test Atom feed date extraction and sorting."""

    def test_atom_extracts_and_sorts_by_date(self):
        """Atom parser should extract dates and sort by most recent first."""
        atom_content = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Test Feed</title>
    <entry>
        <title>Old Article</title>
        <link href="https://example.com/old"/>
        <published>2025-12-01T12:00:00Z</published>
    </entry>
    <entry>
        <title>Newest Article</title>
        <link href="https://example.com/newest"/>
        <published>2025-12-08T12:00:00Z</published>
    </entry>
    <entry>
        <title>Middle Article</title>
        <link href="https://example.com/middle"/>
        <published>2025-12-04T12:00:00Z</published>
    </entry>
</feed>"""

        parser = AtomParser()
        items = parser.parse(atom_content)

        # Should be 3 items
        self.assertEqual(len(items), 3)

        # Should be sorted by date, most recent first
        self.assertEqual(items[0].title, "Newest Article")
        self.assertEqual(items[1].title, "Middle Article")
        self.assertEqual(items[2].title, "Old Article")

        # Dates should be extracted
        self.assertIsNotNone(items[0].published_date)
        self.assertIsNotNone(items[1].published_date)
        self.assertIsNotNone(items[2].published_date)

        # Verify dates are in descending order
        self.assertGreater(items[0].published_date, items[1].published_date)
        self.assertGreater(items[1].published_date, items[2].published_date)


if __name__ == "__main__":
    unittest.main(verbosity=2)
