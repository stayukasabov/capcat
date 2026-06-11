"""Tests for capcat.core.date_extractor."""
import pytest
from bs4 import BeautifulSoup


class TestExtractPublishDate:
    """Tests for extract_publish_date."""

    def test_json_ld_date_published(self):
        html = """<html><head>
        <script type="application/ld+json">
        {"@type": "Article", "datePublished": "2026-06-10T17:34:55+00:00"}
        </script>
        </head><body></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        from capcat.core.date_extractor import extract_publish_date
        assert extract_publish_date(soup) == "2026-06-10T17:34:55+00:00"

    def test_json_ld_nested_in_list(self):
        html = """<html><head>
        <script type="application/ld+json">
        [{"@type": "Article", "datePublished": "2026-05-01T10:00:00+00:00"}]
        </script>
        </head><body></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        from capcat.core.date_extractor import extract_publish_date
        assert extract_publish_date(soup) == "2026-05-01T10:00:00+00:00"

    def test_meta_article_published_time(self):
        html = """<html><head>
        <meta property="article:published_time" content="2026-04-15T12:00:00Z">
        </head><body></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        from capcat.core.date_extractor import extract_publish_date
        assert extract_publish_date(soup) == "2026-04-15T12:00:00Z"

    def test_time_datetime_attribute(self):
        html = """<html><body>
        <time datetime="2026-03-20T08:30:00Z">March 20, 2026</time>
        </body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        from capcat.core.date_extractor import extract_publish_date
        assert extract_publish_date(soup) == "2026-03-20T08:30:00Z"

    def test_no_date_returns_none(self):
        html = "<html><body><p>No dates here</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        from capcat.core.date_extractor import extract_publish_date
        assert extract_publish_date(soup) is None

    def test_json_ld_priority_over_meta(self):
        html = """<html><head>
        <script type="application/ld+json">
        {"@type": "Article", "datePublished": "2026-06-10T00:00:00Z"}
        </script>
        <meta property="article:published_time" content="2026-06-09T00:00:00Z">
        </head><body></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        from capcat.core.date_extractor import extract_publish_date
        assert extract_publish_date(soup) == "2026-06-10T00:00:00Z"

    def test_malformed_json_ld_skipped(self):
        html = """<html><head>
        <script type="application/ld+json">NOT VALID JSON</script>
        <meta property="article:published_time" content="2026-04-01T00:00:00Z">
        </head><body></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        from capcat.core.date_extractor import extract_publish_date
        assert extract_publish_date(soup) == "2026-04-01T00:00:00Z"

    def test_empty_datetime_attribute_skipped(self):
        html = """<html><body>
        <time datetime="">No real date</time>
        </body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        from capcat.core.date_extractor import extract_publish_date
        assert extract_publish_date(soup) is None
