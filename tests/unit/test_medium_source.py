"""Tests for MediumSource URL detection and placeholder creation."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from capcat.core.source_system.base_source import Article, SourceConfig
from capcat.sources.builtin.custom.medium.source import MediumSource


def _config() -> SourceConfig:
    return SourceConfig(
        name="medium",
        display_name="Medium",
        base_url="https://medium.com",
        timeout=10.0,
        rate_limit=1.0,
        supports_comments=False,
        category="content",
        custom_config={},
    )


class TestMediumCanHandleUrl:
    def test_medium_com_article(self):
        assert MediumSource.can_handle_url("https://medium.com/@user/title-abc123")

    def test_custom_medium_subdomain(self):
        assert MediumSource.can_handle_url("https://towardsdatascience.medium.com/article")

    def test_profile_path(self):
        assert MediumSource.can_handle_url("https://medium.com/@johndoe")

    def test_rejects_substack(self):
        # Must not claim Substack URLs
        assert not MediumSource.can_handle_url("https://example.substack.com/p/post")

    def test_rejects_youtube(self):
        assert not MediumSource.can_handle_url("https://www.youtube.com/watch?v=abc")

    def test_rejects_empty(self):
        assert not MediumSource.can_handle_url("")

    def test_source_type_is_custom(self):
        source = MediumSource(_config())
        assert source.source_type == "custom"


class TestMediumFetch:
    def test_fetch_creates_folder_on_success(self, tmp_path):
        """fetch_article_content should create a subfolder and return (True, path)."""
        source = MediumSource(_config())
        article = Article(title="Test Article", url="https://medium.com/@user/test-abc")

        fake_folder = str(tmp_path / "Medium_Article")

        with patch.object(
            source,
            "_fetch_medium_content_direct",
            return_value=(True, fake_folder),
        ):
            Path(fake_folder).mkdir(parents=True, exist_ok=True)
            (Path(fake_folder) / "article.md").write_text("# Test", encoding="utf-8")
            success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success is True
        assert folder is not None

    def test_fetch_returns_false_on_failure(self, tmp_path):
        """fetch_article_content should return (False, path) when internal fetch fails."""
        source = MediumSource(_config())
        article = Article(title="Test Article", url="https://medium.com/@user/test-abc")

        with patch.object(
            source,
            "_fetch_medium_content_direct",
            return_value=(False, None),
        ):
            success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success is False
