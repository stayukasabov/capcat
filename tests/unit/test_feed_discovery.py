"""Regression tests for lxml-free feed validation."""
import pytest
from capcat.core.source_system.feed_discovery import validate_feed

RSS_BYTES = b"""<?xml version="1.0"?>
<rss version="2.0"><channel>
  <title>Test</title>
  <item><title>A</title><link>https://example.com/a</link></item>
</channel></rss>"""

ATOM_BYTES = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test</title>
  <entry><title>A</title><link href="https://example.com/a"/></entry>
</feed>"""

GARBAGE = b"\x00\x01\x02\x03garbage not xml"


def test_validate_rss_feed():
    assert validate_feed(RSS_BYTES) is True


def test_validate_atom_feed():
    assert validate_feed(ATOM_BYTES) is True


def test_reject_garbage():
    assert validate_feed(GARBAGE) is False


def test_reject_empty():
    assert validate_feed(b"") is False
