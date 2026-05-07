"""Tests for HN source config abstraction."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from unittest.mock import MagicMock
from capcat.core.source_system.base_source import SourceConfig


def _make_hn_source(hn_overrides=None):
    """Build an HnSource with optional hn: config block."""
    from Config.sources.active.custom.hn.source import HnSource

    custom = {
        "display_name": "Hacker News",
        "base_url": "https://news.ycombinator.com",
        "category": "techpro",
        "article_count": 30,
        "rate_limit": 1.0,
        "supports_comments": True,
        "has_comments": True,
        "timeout": 10,
    }
    if hn_overrides is not None:
        custom["hn"] = hn_overrides

    config = SourceConfig(
        name="hn",
        display_name="Hacker News",
        base_url="https://news.ycombinator.com",
        timeout=10.0,
        rate_limit=1.0,
        supports_comments=True,
        has_comments=True,
        category="techpro",
        custom_config=custom,
    )
    return HnSource(config=config)


class TestHnCfgDefaults:
    def test_default_max_comments(self):
        src = _make_hn_source()
        assert src._hn_cfg("max_comments_per_article", 200) == 200

    def test_default_max_depth(self):
        src = _make_hn_source()
        assert src._hn_cfg("max_comment_depth", 4) == 4

    def test_default_workers(self):
        src = _make_hn_source()
        assert src._hn_cfg("concurrent_workers", 5) == 5

    def test_default_max_links(self):
        src = _make_hn_source()
        assert src._hn_cfg("max_links_per_comment", 5) == 5


class TestHnCfgOverrides:
    def test_override_max_comments(self):
        src = _make_hn_source({"max_comments_per_article": 50})
        assert src._hn_cfg("max_comments_per_article", 200) == 50

    def test_override_max_depth(self):
        src = _make_hn_source({"max_comment_depth": 2})
        assert src._hn_cfg("max_comment_depth", 4) == 2

    def test_override_workers(self):
        src = _make_hn_source({"concurrent_workers": 10})
        assert src._hn_cfg("concurrent_workers", 5) == 10

    def test_override_max_links(self):
        src = _make_hn_source({"max_links_per_comment": 1})
        assert src._hn_cfg("max_links_per_comment", 5) == 1

    def test_absent_hn_block_uses_default(self):
        """No hn: key at all - must not raise, must return default."""
        src = _make_hn_source(hn_overrides=None)
        assert src._hn_cfg("max_comments_per_article", 200) == 200
