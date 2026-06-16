"""Tests for URL manifest deduplication in unified_source_processor."""
import json
import os
from unittest.mock import MagicMock, patch

import pytest

from capcat.core.unified_source_processor import (
    load_manifest,
    save_manifest,
    filter_already_fetched,
)


def _make_article(title, url):
    from capcat.core.source_system.base_source import Article
    return Article(title=title, url=url)


class TestLoadManifest:
    def test_returns_empty_dict_when_no_file(self, tmp_path):
        result = load_manifest(str(tmp_path))
        assert result == {}

    def test_loads_existing_manifest(self, tmp_path):
        data = {"https://example.com/1": "Article-One", "https://example.com/2": "Article-Two"}
        (tmp_path / ".capcat_fetched.json").write_text(json.dumps(data))
        result = load_manifest(str(tmp_path))
        assert result == data

    def test_returns_empty_dict_on_corrupt_json(self, tmp_path):
        (tmp_path / ".capcat_fetched.json").write_text("not json{{{")
        result = load_manifest(str(tmp_path))
        assert result == {}


class TestSaveManifest:
    def test_writes_manifest_file(self, tmp_path):
        data = {"https://example.com/1": "Article-One"}
        save_manifest(str(tmp_path), data)
        written = json.loads((tmp_path / ".capcat_fetched.json").read_text())
        assert written == data

    def test_overwrites_existing_manifest(self, tmp_path):
        old = {"https://old.com": "Old"}
        new = {"https://old.com": "Old", "https://new.com": "New"}
        save_manifest(str(tmp_path), old)
        save_manifest(str(tmp_path), new)
        written = json.loads((tmp_path / ".capcat_fetched.json").read_text())
        assert written == new


class TestFilterAlreadyFetched:
    def test_all_new_returns_all(self):
        articles = [_make_article("A", "https://a.com"), _make_article("B", "https://b.com")]
        manifest = {}
        new, skipped = filter_already_fetched(articles, manifest)
        assert len(new) == 2
        assert skipped == 0

    def test_all_existing_returns_none(self):
        articles = [_make_article("A", "https://a.com")]
        manifest = {"https://a.com": "A"}
        new, skipped = filter_already_fetched(articles, manifest)
        assert len(new) == 0
        assert skipped == 1

    def test_mixed_filters_correctly(self):
        articles = [
            _make_article("A", "https://a.com"),
            _make_article("B", "https://b.com"),
            _make_article("C", "https://c.com"),
        ]
        manifest = {"https://a.com": "A", "https://c.com": "C"}
        new, skipped = filter_already_fetched(articles, manifest)
        assert len(new) == 1
        assert new[0].url == "https://b.com"
        assert skipped == 2


class TestManifestIntegration:
    """Test that _process_articles_with_new_system updates the manifest."""

    @patch("capcat.core.unified_source_processor.get_config")
    @patch("capcat.core.unified_source_processor.get_batch_progress")
    def test_manifest_updated_after_successful_fetch(self, mock_progress, mock_config, tmp_path):
        from capcat.core.unified_source_processor import UnifiedSourceProcessor, load_manifest

        mock_config.return_value.processing.max_workers = 1

        progress_cm = MagicMock()
        progress_cm.__enter__ = MagicMock(return_value=progress_cm)
        progress_cm.__exit__ = MagicMock(return_value=False)
        mock_progress.return_value = progress_cm

        processor = UnifiedSourceProcessor.__new__(UnifiedSourceProcessor)
        processor.logger = MagicMock()
        processor.config = mock_config.return_value

        source = MagicMock()
        source.config.display_name = "Test"
        source.fetch_article_content.return_value = (True, str(tmp_path / "article"))

        articles = [_make_article("New Article", "https://new.com")]
        manifest = {}

        processor._process_articles_with_new_system(
            source, articles, str(tmp_path), False, False, False, False, manifest
        )

        saved = load_manifest(str(tmp_path))
        assert "https://new.com" in saved
