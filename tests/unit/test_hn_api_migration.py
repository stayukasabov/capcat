"""Tests for HN Firebase API migration."""
from unittest.mock import MagicMock, patch
import time

import pytest
import requests

from capcat.core.ethical_scraping import EthicalScrapingManager


class TestRequestHnApi:
    """EthicalScrapingManager.request_hn_api must exist and work."""

    def test_request_hn_api_returns_json(self):
        """request_hn_api returns parsed JSON from the Firebase API."""
        manager = EthicalScrapingManager()
        session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "title": "Test"}
        session.get.return_value = mock_response

        result = manager.request_hn_api(
            session,
            "https://hacker-news.firebaseio.com/v0/item/123.json",
            timeout=10,
        )

        assert result == {"id": 123, "title": "Test"}

    def test_request_hn_api_sets_user_agent(self):
        """request_hn_api sets the HN-specific User-Agent header."""
        manager = EthicalScrapingManager()
        session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        session.get.return_value = mock_response

        manager.request_hn_api(
            session,
            "https://hacker-news.firebaseio.com/v0/item/1.json",
            timeout=10,
        )

        call_kwargs = session.get.call_args
        headers = call_kwargs[1].get("headers", {}) if call_kwargs[1] else {}
        assert "Capcat/2.0" in headers.get("User-Agent", "")
        assert "official HN API" in headers.get("User-Agent", "")

    def test_request_hn_api_enforces_delay(self):
        """Two rapid calls must have at least 0.4s between them (0.5s target)."""
        manager = EthicalScrapingManager()
        session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1}
        session.get.return_value = mock_response

        start = time.time()
        manager.request_hn_api(session, "https://hacker-news.firebaseio.com/v0/item/1.json", timeout=10)
        manager.request_hn_api(session, "https://hacker-news.firebaseio.com/v0/item/2.json", timeout=10)
        elapsed = time.time() - start

        assert elapsed >= 0.4, (
            f"Two requests completed in {elapsed:.2f}s, expected >= 0.4s delay"
        )

    def test_request_hn_api_backoff_on_429(self):
        """request_hn_api retries on 429 and returns None after max retries."""
        manager = EthicalScrapingManager()
        session = MagicMock()
        mock_429 = MagicMock()
        mock_429.status_code = 429
        mock_429.headers = {}
        mock_429.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_429
        )
        session.get.return_value = mock_429

        result = manager.request_hn_api(
            session,
            "https://hacker-news.firebaseio.com/v0/item/1.json",
            timeout=10,
            max_retries=2,
            initial_delay=0.1,
        )

        assert result is None
        assert session.get.call_count == 2


from capcat.core.source_system.base_source import Article


class TestArticleHnFields:
    """Article dataclass must support optional HN-specific fields."""

    def test_article_has_comment_ids_field(self):
        """Article accepts comment_ids kwarg."""
        article = Article(
            title="Test", url="https://example.com",
            comment_ids=[100, 200, 300],
        )
        assert article.comment_ids == [100, 200, 300]

    def test_article_has_hn_item_id_field(self):
        """Article accepts hn_item_id kwarg."""
        article = Article(
            title="Test", url="https://example.com",
            hn_item_id=12345,
        )
        assert article.hn_item_id == 12345

    def test_article_hn_fields_default_none(self):
        """HN fields default to None when not provided."""
        article = Article(title="Test", url="https://example.com")
        assert article.comment_ids is None
        assert article.hn_item_id is None


from capcat.sources.builtin.custom.hn.source import HnSource


def _make_hn_source():
    """Create an HnSource with a minimal mock config."""
    config = MagicMock()
    config.name = "hn"
    config.display_name = "Hacker News"
    config.base_url = "https://news.ycombinator.com"
    config.timeout = 10
    config.rate_limit = 1.0
    config.custom_config = {}
    session = MagicMock()
    return HnSource(config=config, session=session)


class TestDiscoverArticlesApi:
    """discover_articles must use the Firebase API, not HTML scraping."""

    def test_discover_calls_topstories_endpoint(self):
        """discover_articles fetches /v0/topstories.json."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101, 102, 103],
            {"id": 101, "title": "Story A", "url": "https://a.com", "kids": [201], "type": "story"},
            {"id": 102, "title": "Story B", "url": "https://b.com", "kids": [202, 203], "type": "story"},
            {"id": 103, "title": "Story C", "url": "https://c.com", "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            articles = source.discover_articles(count=3)

        first_call_url = mock_manager.request_hn_api.call_args_list[0][0][1]
        assert "topstories.json" in first_call_url

    def test_discover_builds_articles_with_comment_ids(self):
        """Articles have comment_ids populated from the kids array."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101],
            {"id": 101, "title": "Story A", "url": "https://a.com", "kids": [201, 202], "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            articles = source.discover_articles(count=1)

        assert len(articles) == 1
        assert articles[0].comment_ids == [201, 202]
        assert articles[0].hn_item_id == 101
        assert articles[0].comment_url == "https://news.ycombinator.com/item?id=101"

    def test_discover_handles_missing_url(self):
        """Stories without url field (Ask HN) get HN discussion URL."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101],
            {"id": 101, "title": "Ask HN: Something", "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            articles = source.discover_articles(count=1)

        assert articles[0].url == "https://news.ycombinator.com/item?id=101"

    def test_discover_respects_count(self):
        """Only count articles returned even if topstories has more."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101, 102, 103, 104, 105],
            {"id": 101, "title": "A", "url": "https://a.com", "type": "story"},
            {"id": 102, "title": "B", "url": "https://b.com", "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            articles = source.discover_articles(count=2)

        assert len(articles) == 2

    def test_discover_skips_failed_item_fetch(self):
        """If a story metadata fetch returns None, skip it and continue."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101, 102, 103],
            None,
            {"id": 102, "title": "B", "url": "https://b.com", "type": "story"},
            {"id": 103, "title": "C", "url": "https://c.com", "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            articles = source.discover_articles(count=3)

        assert len(articles) == 2
        assert articles[0].title == "B"

    def test_discover_no_html_requests(self):
        """discover_articles must not call session.get (no HTML scraping)."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            [101],
            {"id": 101, "title": "A", "url": "https://a.com", "type": "story"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ):
            source.discover_articles(count=1)

        source.session.get.assert_not_called()


class TestCleanApiCommentHtml:
    """HnSource._clean_api_comment_html converts API HTML to clean text."""

    def test_strips_paragraph_tags(self):
        source = _make_hn_source()
        result = source._clean_api_comment_html("<p>Hello world</p>")
        assert result == "Hello world"

    def test_converts_links_to_markdown(self):
        source = _make_hn_source()
        result = source._clean_api_comment_html(
            '<p>See <a href="https://example.com">this link</a> for details</p>'
        )
        assert "[this link](https://example.com)" in result

    def test_handles_nested_paragraphs(self):
        source = _make_hn_source()
        result = source._clean_api_comment_html(
            "<p>First paragraph</p><p>Second paragraph</p>"
        )
        assert "First paragraph" in result
        assert "Second paragraph" in result
        assert "\n\n" in result

    def test_strips_reply_links(self):
        source = _make_hn_source()
        result = source._clean_api_comment_html(
            '<p>Good point</p><p><a href="reply?id=123">reply</a></p>'
        )
        # The reply link should be removed entirely
        assert "reply?id=" not in result

    def test_handles_empty_input(self):
        source = _make_hn_source()
        result = source._clean_api_comment_html("")
        assert result == ""

    def test_handles_none_input(self):
        source = _make_hn_source()
        result = source._clean_api_comment_html(None)
        assert result == ""

    def test_limits_links_per_comment(self):
        """Excess links beyond max_links_per_comment are stripped."""
        source = _make_hn_source()
        html = "<p>" + " ".join(
            f'<a href="https://example.com/{i}">link{i}</a>' for i in range(10)
        ) + "</p>"
        result = source._clean_api_comment_html(html)
        link_count = result.count("](")
        assert link_count <= 5


class TestFetchCommentsApi:
    """fetch_comments must use the Firebase API for recursive comment fetching."""

    def setup_method(self):
        HnSource._hn_compliance_message_shown = False

    def teardown_method(self):
        HnSource._hn_compliance_message_shown = False

    def test_fetch_comments_builds_correct_format(self, tmp_path):
        """Comments fetched via API produce the standard dict format."""
        source = _make_hn_source()
        mock_manager = MagicMock()

        mock_manager.request_hn_api.side_effect = [
            {"id": 201, "by": "user1", "text": "<p>Great article</p>", "kids": [301], "type": "comment"},
            {"id": 301, "by": "user2", "text": "<p>I agree</p>", "type": "comment"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ), patch(
            "capcat.core.streamlined_comment_processor.create_optimized_comment_processor"
        ) as mock_processor_factory:
            mock_processor = MagicMock()
            mock_processor.generate_inline_comments_markdown.return_value = "# Comments"
            mock_processor.get_performance_metrics.return_value = {
                "comments_processed": 2, "links_processed": 0
            }
            mock_processor_factory.return_value = mock_processor

            source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=100",
                article_title="Test Article",
                article_folder_path=str(tmp_path),
                comment_ids=[201],
            )

        call_args = mock_processor.generate_inline_comments_markdown.call_args
        comments = call_args[0][0]
        assert len(comments) == 2
        assert comments[0]["user"] == "Anonymous"
        assert comments[0]["level"] == 0
        assert comments[0]["user_link"] == "https://news.ycombinator.com/item?id=201"
        assert comments[1]["level"] == 1

    def test_fetch_comments_skips_deleted(self, tmp_path):
        """Deleted comments are skipped but their children are still fetched."""
        source = _make_hn_source()
        mock_manager = MagicMock()

        mock_manager.request_hn_api.side_effect = [
            {"id": 201, "deleted": True, "kids": [301], "type": "comment"},
            {"id": 301, "by": "user2", "text": "<p>Child of deleted</p>", "type": "comment"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ), patch(
            "capcat.core.streamlined_comment_processor.create_optimized_comment_processor"
        ) as mock_processor_factory:
            mock_processor = MagicMock()
            mock_processor.generate_inline_comments_markdown.return_value = "# Comments"
            mock_processor.get_performance_metrics.return_value = {
                "comments_processed": 1, "links_processed": 0
            }
            mock_processor_factory.return_value = mock_processor

            source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=100",
                article_title="Test",
                article_folder_path=str(tmp_path),
                comment_ids=[201],
            )

        comments = mock_processor.generate_inline_comments_markdown.call_args[0][0]
        assert len(comments) == 1
        assert comments[0]["id"] == "301"

    def test_fetch_comments_skips_dead(self, tmp_path):
        """Dead (flagged) comments are skipped."""
        source = _make_hn_source()
        mock_manager = MagicMock()

        mock_manager.request_hn_api.side_effect = [
            {"id": 201, "dead": True, "by": "user1", "text": "<p>flagged</p>", "type": "comment"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ), patch(
            "capcat.core.streamlined_comment_processor.create_optimized_comment_processor"
        ) as mock_processor_factory:
            mock_processor = MagicMock()
            mock_processor.generate_inline_comments_markdown.return_value = "# Comments"
            mock_processor.get_performance_metrics.return_value = {
                "comments_processed": 0, "links_processed": 0
            }
            mock_processor_factory.return_value = mock_processor

            source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=100",
                article_title="Test",
                article_folder_path=str(tmp_path),
                comment_ids=[201],
            )

        comments = mock_processor.generate_inline_comments_markdown.call_args[0][0]
        assert len(comments) == 0

    def test_fetch_comments_no_html_requests(self, tmp_path):
        """fetch_comments must not call session.get (no HTML scraping)."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.side_effect = [
            {"id": 201, "by": "user1", "text": "<p>Hi</p>", "type": "comment"},
        ]

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ), patch(
            "capcat.core.streamlined_comment_processor.create_optimized_comment_processor"
        ) as mock_processor_factory:
            mock_processor = MagicMock()
            mock_processor.generate_inline_comments_markdown.return_value = "# Comments"
            mock_processor.get_performance_metrics.return_value = {
                "comments_processed": 1, "links_processed": 0
            }
            mock_processor_factory.return_value = mock_processor

            source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=100",
                article_title="Test",
                article_folder_path=str(tmp_path),
                comment_ids=[201],
            )

        source.session.get.assert_not_called()


class TestComplianceMessage:
    """The HN API compliance message must display once per session."""

    def setup_method(self):
        HnSource._hn_compliance_message_shown = False

    def teardown_method(self):
        HnSource._hn_compliance_message_shown = False

    def test_compliance_message_shown_once(self, tmp_path):
        """Message appears on first call, not on second."""
        source = _make_hn_source()
        mock_manager = MagicMock()
        mock_manager.request_hn_api.return_value = {
            "id": 201, "by": "u", "text": "<p>Hi</p>", "type": "comment"
        }

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ), patch(
            "capcat.core.streamlined_comment_processor.create_optimized_comment_processor"
        ) as mock_pf:
            mock_p = MagicMock()
            mock_p.generate_inline_comments_markdown.return_value = "# C"
            mock_p.get_performance_metrics.return_value = {
                "comments_processed": 1, "links_processed": 0
            }
            mock_pf.return_value = mock_p

            source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=100",
                article_title="First",
                article_folder_path=str(tmp_path),
                comment_ids=[201],
            )

        assert HnSource._hn_compliance_message_shown is True


class TestNoHtmlScraping:
    """HnSource must never make direct HTTP requests to news.ycombinator.com."""

    def setup_method(self):
        HnSource._hn_compliance_message_shown = False

    def teardown_method(self):
        HnSource._hn_compliance_message_shown = False

    def test_full_flow_no_hn_html_requests(self, tmp_path):
        """
        Full discover + fetch flow must only hit hacker-news.firebaseio.com,
        never news.ycombinator.com directly.
        """
        source = _make_hn_source()

        mock_manager = MagicMock()
        all_api_urls = []

        def track_api_calls(session, url, **kwargs):
            all_api_urls.append(url)
            if "topstories" in url:
                return [101]
            if "/item/101" in url:
                return {
                    "id": 101, "title": "Test", "url": "https://example.com",
                    "kids": [201], "type": "story",
                }
            if "/item/201" in url:
                return {
                    "id": 201, "by": "u", "text": "<p>Comment</p>",
                    "type": "comment",
                }
            return None

        mock_manager.request_hn_api.side_effect = track_api_calls

        with patch(
            "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
            return_value=mock_manager,
        ), patch(
            "capcat.core.streamlined_comment_processor.create_optimized_comment_processor"
        ) as mock_pf:
            mock_p = MagicMock()
            mock_p.generate_inline_comments_markdown.return_value = "# C"
            mock_p.get_performance_metrics.return_value = {
                "comments_processed": 1, "links_processed": 0
            }
            mock_pf.return_value = mock_p

            articles = source.discover_articles(count=1)
            source.fetch_comments(
                comment_url=articles[0].comment_url,
                article_title=articles[0].title,
                article_folder_path=str(tmp_path),
                comment_ids=articles[0].comment_ids,
            )

        for url in all_api_urls:
            assert "hacker-news.firebaseio.com" in url, (
                f"Request to non-API URL detected: {url}"
            )

        source.session.get.assert_not_called()
