"""Tests for numeric suffix folder collision resolution."""
import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from unittest.mock import MagicMock, patch
from capcat.core.article_fetcher import NewsSourceArticleFetcher


def _make_fetcher():
    config = {"name": "test", "content_selectors": [], "skip_patterns": []}
    session = MagicMock()
    return NewsSourceArticleFetcher(config, session)


class TestGetUniqueFolderName:
    def test_no_collision_returns_base(self, tmp_path):
        fetcher = _make_fetcher()
        result = fetcher._get_unique_folder_name(str(tmp_path), "my-article")
        assert result == "my-article"

    def test_collision_returns_suffix_2(self, tmp_path):
        (tmp_path / "my-article").mkdir()
        fetcher = _make_fetcher()
        result = fetcher._get_unique_folder_name(str(tmp_path), "my-article")
        assert result == "my-article-2"

    def test_double_collision_returns_suffix_3(self, tmp_path):
        (tmp_path / "my-article").mkdir()
        (tmp_path / "my-article-2").mkdir()
        fetcher = _make_fetcher()
        result = fetcher._get_unique_folder_name(str(tmp_path), "my-article")
        assert result == "my-article-3"

    def test_no_collision_no_suffix(self, tmp_path):
        """Folders from previous runs are overwritten when there is no same-run collision."""
        # This directory exists but there's no other same-title folder - returns base
        fetcher = _make_fetcher()
        result = fetcher._get_unique_folder_name(str(tmp_path), "fresh-article")
        assert result == "fresh-article"
