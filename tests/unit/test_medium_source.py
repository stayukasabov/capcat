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

    def test_rejects_non_medium_at_url(self):
        # /@<user> pattern was matching non-Medium sites (e.g. Ghost blogs)
        assert not MediumSource.can_handle_url("https://someblog.com/@author/article")

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

        with patch.object(source, "_is_paywalled", return_value="none"), \
             patch.object(source, "_fetch_medium_content_direct", return_value=(True, fake_folder)):
            Path(fake_folder).mkdir(parents=True, exist_ok=True)
            (Path(fake_folder) / "article.md").write_text("# Test", encoding="utf-8")
            success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success is True
        assert folder is not None

    def test_fetch_returns_false_on_failure(self, tmp_path):
        """fetch_article_content should return (False, path) when internal fetch fails."""
        source = MediumSource(_config())
        article = Article(title="Test Article", url="https://medium.com/@user/test-abc")

        with patch.object(source, "_is_paywalled", return_value="none"), \
             patch.object(source, "_fetch_medium_content_direct", return_value=(False, None)):
            success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success is False


class TestMediumFallbackLoop:
    def test_failed_medium_fetch_does_not_recurse(self, tmp_path):
        """Regression: when Medium specialized fetch returns (False, None),
        the generic fallback must not re-enter the specialized handler.

        Bug: GenericArticleFetcher inherited ArticleFetcher's specialized-source
        check, so process_article -> medium fails -> generic fallback ->
        fetch_article_content -> process_article looped infinitely.
        """
        import requests
        from capcat.core.unified_article_processor import (
            UnifiedArticleProcessor,
            get_unified_processor,
        )

        call_count = [0]
        _orig = UnifiedArticleProcessor.process_article

        def _tracking(self_inst, url, title, index, base_folder, **kw):
            call_count[0] += 1
            if call_count[0] > 2:
                raise AssertionError(
                    f"Infinite loop: process_article called {call_count[0]} times"
                )
            return _orig(self_inst, url, title, index, base_folder, **kw)

        mock_session = MagicMock(spec=requests.Session)
        mock_session.get.side_effect = Exception("403 mocked")
        mock_session.head.side_effect = Exception("403 mocked")

        with patch.object(MediumSource, "fetch_article_content", return_value=(False, None)):
            with patch.object(UnifiedArticleProcessor, "process_article", _tracking):
                with patch("capcat.core.session_pool.get_global_session", return_value=mock_session):
                    get_unified_processor().process_article(
                        url="https://medium.com/@user/test-loop-regression",
                        title="Test Article",
                        index=0,
                        base_folder=str(tmp_path),
                    )

        assert call_count[0] == 1, (
            f"process_article called {call_count[0]} times — expected 1 (no recursion)"
        )
