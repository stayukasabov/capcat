"""Test that HTML index uses manifest count and filters duplicates."""
import json
import os
import re

import pytest

from capcat.htmlgen.generator import _manifest_article_count, _is_duplicate_folder


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


class TestIsDuplicateFolder:
    def test_not_duplicate_when_no_suffix(self, tmp_path):
        (tmp_path / "My-Article").mkdir()
        assert _is_duplicate_folder("My-Article", tmp_path) is False

    def test_duplicate_when_suffix_and_base_exists(self, tmp_path):
        (tmp_path / "My-Article").mkdir()
        (tmp_path / "My-Article-2").mkdir()
        assert _is_duplicate_folder("My-Article-2", tmp_path) is True

    def test_not_duplicate_when_suffix_but_no_base(self, tmp_path):
        (tmp_path / "My-Article-2").mkdir()
        assert _is_duplicate_folder("My-Article-2", tmp_path) is False

    def test_duplicate_with_higher_suffix(self, tmp_path):
        (tmp_path / "My-Article").mkdir()
        (tmp_path / "My-Article-15").mkdir()
        assert _is_duplicate_folder("My-Article-15", tmp_path) is True

    def test_not_duplicate_when_name_naturally_ends_with_number(self, tmp_path):
        # "Article-2026" should NOT be treated as duplicate of "Article"
        # because the suffix must be a short number (2-99)
        (tmp_path / "Article").mkdir()
        (tmp_path / "Article-2026").mkdir()
        assert _is_duplicate_folder("Article-2026", tmp_path) is False

    def test_not_duplicate_no_manifest(self, tmp_path):
        # No manifest means dedup hasn't been used, don't filter
        (tmp_path / "My-Article").mkdir()
        (tmp_path / "My-Article-2").mkdir()
        assert _is_duplicate_folder("My-Article-2", tmp_path, require_manifest=True) is False
