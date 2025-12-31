#!/usr/bin/env python3
"""
Unit tests for feed_parser module.
Tests RSS and Atom parsing functionality.
"""

import pytest

from core.source_system.feed_parser import (
    AtomParser,
    FeedItem,
    FeedParserFactory,
    RSSParser,
)


class TestRSSParser:
    """Tests for RSS feed parsing."""

    def test_parse_valid_rss(self):
        """Test parsing valid RSS 2.0 feed."""
        rss_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Test Feed</title>
        <item>
            <title>Article 1</title>
            <link>https://example.com/article1</link>
            <description>Description 1</description>
        </item>
        <item>
            <title>Article 2</title>
            <link>https://example.com/article2</link>
        </item>
    </channel>
</rss>"""

        parser = RSSParser()
        items = parser.parse(rss_content)

        assert len(items) == 2
        assert items[0].title == "Article 1"
        assert items[0].url == "https://example.com/article1"
        assert items[0].description == "Description 1"
        assert items[1].title == "Article 2"
        assert items[1].url == "https://example.com/article2"
        assert items[1].description is None

    def test_parse_empty_rss(self):
        """Test parsing RSS feed with no items."""
        rss_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Empty Feed</title>
    </channel>
</rss>"""

        parser = RSSParser()
        items = parser.parse(rss_content)

        assert len(items) == 0

    def test_parse_incomplete_items(self):
        """Test that incomplete items are skipped."""
        rss_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <item>
            <title>No Link</title>
        </item>
        <item>
            <link>https://example.com/no-title</link>
        </item>
        <item>
            <title>Complete</title>
            <link>https://example.com/complete</link>
        </item>
    </channel>
</rss>"""

        parser = RSSParser()
        items = parser.parse(rss_content)

        assert len(items) == 1
        assert items[0].title == "Complete"

    def test_parse_invalid_xml(self):
        """Test that invalid XML raises ValueError."""
        invalid_content = b"This is not XML"

        parser = RSSParser()
        with pytest.raises(ValueError, match="Invalid RSS XML"):
            parser.parse(invalid_content)


class TestAtomParser:
    """Tests for Atom feed parsing."""

    def test_parse_valid_atom_with_namespace(self):
        """Test parsing Atom feed with namespace."""
        atom_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Test Atom Feed</title>
    <entry>
        <title>Atom Article 1</title>
        <link rel="alternate" href="https://example.com/atom1"/>
        <summary>Atom Summary 1</summary>
    </entry>
    <entry>
        <title>Atom Article 2</title>
        <link href="https://example.com/atom2"/>
        <content>Atom Content 2</content>
    </entry>
</feed>"""

        parser = AtomParser()
        items = parser.parse(atom_content)

        assert len(items) == 2
        assert items[0].title == "Atom Article 1"
        assert items[0].url == "https://example.com/atom1"
        assert items[0].description == "Atom Summary 1"
        assert items[1].title == "Atom Article 2"
        assert items[1].url == "https://example.com/atom2"
        assert items[1].description == "Atom Content 2"

    def test_parse_atom_without_namespace(self):
        """Test parsing Atom feed without namespace prefix."""
        atom_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed>
    <entry>
        <title>No Namespace</title>
        <link href="https://example.com/test"/>
    </entry>
</feed>"""

        parser = AtomParser()
        items = parser.parse(atom_content)

        assert len(items) == 1
        assert items[0].title == "No Namespace"
        assert items[0].url == "https://example.com/test"

    def test_parse_invalid_atom_xml(self):
        """Test that invalid XML raises ValueError."""
        invalid_content = b"<feed><broken"

        parser = AtomParser()
        with pytest.raises(ValueError, match="Invalid Atom XML"):
            parser.parse(invalid_content)


class TestFeedParserFactory:
    """Tests for FeedParserFactory auto-detection."""

    def test_detect_rss_feed(self):
        """Test auto-detection of RSS feed."""
        rss_content = b"""<?xml version="1.0"?>
<rss version="2.0">
    <channel>
        <item>
            <title>RSS Test</title>
            <link>https://example.com/rss</link>
        </item>
    </channel>
</rss>"""

        items = FeedParserFactory.detect_and_parse(rss_content)

        assert len(items) == 1
        assert items[0].title == "RSS Test"
        assert items[0].url == "https://example.com/rss"

    def test_detect_atom_feed(self):
        """Test auto-detection of Atom feed."""
        atom_content = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <title>Atom Test</title>
        <link href="https://example.com/atom"/>
    </entry>
</feed>"""

        items = FeedParserFactory.detect_and_parse(atom_content)

        assert len(items) == 1
        assert items[0].title == "Atom Test"
        assert items[0].url == "https://example.com/atom"

    def test_detect_unrecognized_format(self):
        """Test that unrecognized format raises ValueError."""
        unknown_content = b"""<?xml version="1.0"?>
<unknown>
    <data>Not a feed</data>
</unknown>"""

        with pytest.raises(ValueError, match="Unrecognized feed format"):
            FeedParserFactory.detect_and_parse(unknown_content)

    def test_detect_invalid_xml(self):
        """Test that invalid XML raises ValueError."""
        invalid_content = b"Not XML at all"

        with pytest.raises(ValueError, match="Invalid XML feed"):
            FeedParserFactory.detect_and_parse(invalid_content)


class TestFeedItem:
    """Tests for FeedItem dataclass."""

    def test_create_feeditem(self):
        """Test creating FeedItem with all fields."""
        item = FeedItem(
            title="Test Title",
            url="https://example.com",
            description="Test Description"
        )

        assert item.title == "Test Title"
        assert item.url == "https://example.com"
        assert item.description == "Test Description"

    def test_create_feeditem_without_description(self):
        """Test creating FeedItem without description."""
        item = FeedItem(
            title="Test",
            url="https://example.com"
        )

        assert item.title == "Test"
        assert item.url == "https://example.com"
        assert item.description is None
