"""Tests for SubstackSource URL detection, RSS discovery, and fetch."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from capcat.core.source_system.base_source import Article, ArticleDiscoveryError, SourceConfig
from capcat.sources.builtin.custom.substack.source import SubstackSource


def _config(base_url: str = "https://example.substack.com") -> SourceConfig:
    return SourceConfig(
        name="substack",
        display_name="Substack",
        base_url=base_url,
        timeout=10.0,
        rate_limit=1.0,
        supports_comments=False,
        category="content",
        custom_config={},
    )


class TestSubstackCanHandleUrl:
    def test_substack_post(self):
        assert SubstackSource.can_handle_url("https://example.substack.com/p/my-post")

    def test_substack_archive(self):
        assert SubstackSource.can_handle_url("https://example.substack.com/archive")

    def test_substack_root(self):
        assert SubstackSource.can_handle_url("https://example.substack.com")

    def test_rejects_medium(self):
        assert not SubstackSource.can_handle_url("https://medium.com/@user/article")

    def test_rejects_youtube(self):
        assert not SubstackSource.can_handle_url("https://www.youtube.com/watch?v=abc")

    def test_rejects_empty(self):
        assert not SubstackSource.can_handle_url("")

    def test_rejects_non_substack_archive_url(self):
        # /archive pattern was matching /archives/ on unrelated sites
        assert not SubstackSource.can_handle_url(
            "https://www.thehistoryblog.com/archives/75848"
        )

    def test_rejects_non_substack_slash_p_url(self):
        # /p/<slug> pattern was matching non-Substack /p/ paths
        assert not SubstackSource.can_handle_url(
            "https://example.com/p/some-article"
        )

    def test_source_type_is_custom(self):
        source = SubstackSource(_config())
        assert source.source_type == "custom"


class TestSubstackDiscoverRss:
    def _make_rss_response(self, items):
        item_xml = ""
        for title, url in items:
            item_xml += f"<item><title>{title}</title><link>{url}</link></item>\n"
        return f"<rss><channel>{item_xml}</channel></rss>".encode()

    def test_discover_returns_articles_from_rss(self):
        source = SubstackSource(_config("https://example.substack.com"))
        rss_bytes = self._make_rss_response([
            ("Post One", "https://example.substack.com/p/post-one"),
            ("Post Two", "https://example.substack.com/p/post-two"),
        ])

        mock_resp = MagicMock()
        mock_resp.content = rss_bytes
        mock_resp.raise_for_status = MagicMock()
        source.session = MagicMock()
        source.session.get.return_value = mock_resp

        articles = source.discover_articles(10)

        assert len(articles) == 2
        assert articles[0].title == "Post One"
        assert articles[1].title == "Post Two"

    def test_discover_respects_count_limit(self):
        source = SubstackSource(_config("https://example.substack.com"))
        items = [(f"Post {i}", f"https://example.substack.com/p/post-{i}") for i in range(10)]
        rss_bytes = self._make_rss_response(items)

        mock_resp = MagicMock()
        mock_resp.content = rss_bytes
        mock_resp.raise_for_status = MagicMock()
        source.session = MagicMock()
        source.session.get.return_value = mock_resp

        articles = source.discover_articles(3)

        assert len(articles) == 3

    def test_discover_raises_on_network_error(self):
        source = SubstackSource(_config("https://example.substack.com"))
        source.session = MagicMock()
        source.session.get.side_effect = Exception("timeout")

        with pytest.raises(ArticleDiscoveryError):
            source.discover_articles(5)


class TestSubstackFetch:
    def test_fetch_creates_folder_on_success(self, tmp_path):
        source = SubstackSource(_config())
        article = Article(title="Test Post", url="https://example.substack.com/p/test")

        fake_folder = str(tmp_path / "Test_Post")

        with patch.object(source, "_is_paywalled", return_value="none"), \
             patch.object(source, "_fetch_substack_content_direct", return_value=(True, fake_folder)):
            Path(fake_folder).mkdir(parents=True, exist_ok=True)
            (Path(fake_folder) / "article.md").write_text("# Test", encoding="utf-8")
            success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success is True
        assert folder is not None

    def test_fetch_returns_false_on_failure(self, tmp_path):
        source = SubstackSource(_config())
        article = Article(title="Test Post", url="https://example.substack.com/p/test")

        with patch.object(source, "_is_paywalled", return_value="none"), \
             patch.object(source, "_fetch_substack_content_direct", return_value=(False, None)):
            success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success is False


class TestSubstack403LinkOnly:
    def test_fetch_creates_link_only_on_403(self, tmp_path):
        """When Substack returns 403, fetch_article_content creates a link-only entry."""
        source = SubstackSource(_config())
        article = Article(title="Blocked Post", url="https://example.substack.com/p/blocked")

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
        assert "https://example.substack.com/p/blocked" in content

    def test_fetch_still_handles_paywall(self, tmp_path):
        """Paywall detection (non-403) must still work as before."""
        source = SubstackSource(_config())
        article = Article(title="Paywalled Post", url="https://example.substack.com/p/paid")

        with patch.object(source, "_is_paywalled", return_value="hard"), \
             patch.object(source, "_handle_paywalled_content", return_value=(True, str(tmp_path / "pw"))):
            success, folder = source.fetch_article_content(article, str(tmp_path))

        assert success is True

    def test_fetch_non_403_error_returns_false(self, tmp_path):
        """Non-403 HTTP errors return (False, None), not a link-only entry."""
        source = SubstackSource(_config())
        article = Article(title="Server Error", url="https://example.substack.com/p/err")

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
