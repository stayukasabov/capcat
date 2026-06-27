"""Tests for MediumSource URL detection and placeholder creation."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from capcat.core.source_system.base_source import Article, ContentFetchError, SourceConfig
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
            f"process_article called {call_count[0]} times - expected 1 (no recursion)"
        )


class TestCreateLinkOnlyEntry:
    def test_creates_folder_and_markdown(self, tmp_path):
        """_create_link_only_entry creates a folder with a link-only .md file."""
        source = MediumSource(_config())
        article = Article(title="Blocked Article", url="https://medium.com/@user/blocked")
        success, folder = source._create_link_only_entry(
            article, str(tmp_path), "medium.com restricts automated access"
        )
        assert success is True
        assert folder is not None
        md_files = list(Path(folder).glob("*.md"))
        assert len(md_files) == 1
        content = md_files[0].read_text()
        assert "Blocked Article" in content
        assert "https://medium.com/@user/blocked" in content
        assert "restricts automated access" in content
        assert "ethical scraping" in content.lower()

    def test_returns_false_on_os_error(self, tmp_path):
        """_create_link_only_entry returns (False, None) if folder creation fails."""
        source = MediumSource(_config())
        article = Article(title="Test", url="https://medium.com/@user/test")
        with patch("os.makedirs", side_effect=OSError("disk full")):
            success, folder = source._create_link_only_entry(
                article, str(tmp_path), "access denied"
            )
        assert success is False
        assert folder is None


class TestMedium403LinkOnly:
    def test_fetch_creates_link_only_on_403(self, tmp_path):
        """When Medium returns 403, fetch_article_content creates a link-only entry."""
        source = MediumSource(_config())
        article = Article(title="Blocked Post", url="https://medium.com/@user/blocked-abc")

        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_resp
        )
        source.session = MagicMock()
        source.session.head.return_value = mock_resp
        source.session.get.return_value = mock_resp

        success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success is True
        assert folder is not None
        md_files = list(Path(folder).glob("*.md"))
        assert len(md_files) == 1
        content = md_files[0].read_text()
        assert "ethical scraping" in content.lower()
        assert "https://medium.com/@user/blocked-abc" in content

    def test_fetch_still_handles_paywall(self, tmp_path):
        """Paywall detection (non-403) must still work as before."""
        source = MediumSource(_config())
        article = Article(title="Paywalled Post", url="https://medium.com/@user/paywalled")

        with patch.object(source, "_is_paywalled", return_value="hard"), \
             patch.object(source, "_handle_paywalled_content", return_value=(True, str(tmp_path / "pw"))):
            success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success is True

    def test_fetch_non_403_error_returns_false(self, tmp_path):
        """Non-403 HTTP errors return (False, None), not a link-only entry."""
        source = MediumSource(_config())
        article = Article(title="Server Error", url="https://medium.com/@user/server-err")

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_resp
        )
        source.session = MagicMock()
        source.session.head.return_value = mock_resp
        source.session.get.return_value = mock_resp

        success, folder = source.fetch_article_content(article, str(tmp_path))
        assert success is False


class TestErrorArticle403Text:
    def test_error_article_403_mentions_ethical_scraping(self, tmp_path):
        """Generic error article for 403 must use ethical scraping language."""
        from capcat.core.article_fetcher import ArticleFetcher

        class _ConcreteFetcher(ArticleFetcher):
            def should_skip_url(self, url):
                return False

        session = MagicMock()
        fetcher = _ConcreteFetcher(session)
        success, title, folder = fetcher._create_error_article(
            title="Blocked Article",
            url="https://example.com/blocked",
            error_type="403 Forbidden",
            error_details="403 Client Error: Forbidden",
            base_folder=str(tmp_path),
        )
        assert success is True
        md_files = list(Path(folder).glob("*.md"))
        content = md_files[0].read_text()
        assert "ethical scraping" in content.lower()
        assert "cloudflare" not in content.lower()
