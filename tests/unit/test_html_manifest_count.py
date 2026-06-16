"""Test that HTML index uses manifest count when available."""
import json
import os

import pytest

from capcat.htmlgen.generator import _manifest_article_count


class TestManifestArticleCount:
    def test_returns_none_when_no_manifest(self, tmp_path):
        result = _manifest_article_count(tmp_path)
        assert result is None

    def test_returns_count_from_manifest(self, tmp_path):
        data = {
            "https://a.com": "Article A",
            "https://b.com": "Article B",
            "https://c.com": "Article C",
        }
        (tmp_path / ".capcat_fetched.json").write_text(json.dumps(data))
        result = _manifest_article_count(tmp_path)
        assert result == 3

    def test_returns_none_on_corrupt_manifest(self, tmp_path):
        (tmp_path / ".capcat_fetched.json").write_text("broken{{{")
        result = _manifest_article_count(tmp_path)
        assert result is None

    def test_returns_none_on_empty_manifest(self, tmp_path):
        (tmp_path / ".capcat_fetched.json").write_text("{}")
        result = _manifest_article_count(tmp_path)
        assert result is None
