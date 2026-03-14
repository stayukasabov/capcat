"""Regression tests for feedparser-based feed parser (lxml removed)."""
import pytest
from capcat.core.source_system.feed_parser import FeedParserFactory, RSSParser, AtomParser

RSS_BYTES = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>T</title>
  <item>
    <title>Article One</title>
    <link>https://example.com/one</link>
    <pubDate>Mon, 10 Mar 2026 12:00:00 GMT</pubDate>
  </item>
  <item>
    <title>Article Two</title>
    <link>https://example.com/two</link>
  </item>
</channel></rss>"""

ATOM_BYTES = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>T</title>
  <entry>
    <title>Atom One</title>
    <link href="https://example.com/atom-one"/>
    <published>2026-03-10T12:00:00Z</published>
  </entry>
</feed>"""


def test_rss_parser_returns_items():
    items = RSSParser().parse(RSS_BYTES)
    assert len(items) == 2
    assert items[0].title == "Article One"
    assert items[0].url == "https://example.com/one"


def test_rss_parser_sorted_by_date():
    items = RSSParser().parse(RSS_BYTES)
    # Item with date comes before item without date
    assert items[0].published_date is not None


def test_atom_parser_returns_items():
    items = AtomParser().parse(ATOM_BYTES)
    assert len(items) == 1
    assert items[0].title == "Atom One"


def test_factory_detects_rss():
    items = FeedParserFactory.detect_and_parse(RSS_BYTES)
    assert len(items) == 2


def test_factory_detects_atom():
    items = FeedParserFactory.detect_and_parse(ATOM_BYTES)
    assert len(items) == 1


def test_factory_raises_on_garbage():
    with pytest.raises(ValueError):
        FeedParserFactory.detect_and_parse(b"not a feed")
