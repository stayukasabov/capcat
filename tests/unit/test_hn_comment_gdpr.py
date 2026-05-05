"""Tests: HN comment output includes permalink links, user is Anonymous."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from capcat.core.streamlined_comment_processor import create_optimized_comment_processor
from capcat.sources.builtin.custom.hn.source import HnSource


def _make_hn_source():
    config = MagicMock()
    config.name = "hn"
    config.display_name = "Hacker News"
    config.base_url = "https://news.ycombinator.com"
    config.timeout = 10
    config.rate_limit = 1.0
    config.custom_config = {}
    session = MagicMock()
    return HnSource(config=config, session=session)


def _build_api_comments(source):
    """Build comment dicts using the same logic as the HN source."""
    mock_manager = MagicMock()
    mock_manager.request_hn_api.side_effect = [
        {
            "id": 43000001,
            "by": "seizethecheese",
            "text": "<p>Great point.</p>",
            "type": "comment",
        },
    ]

    with patch(
        "capcat.sources.builtin.custom.hn.source.get_ethical_manager",
        return_value=mock_manager,
    ):
        comments = source._fetch_comment_tree(mock_manager, [43000001], depth=0)

    return comments


class TestCommentPermalinkPresent:
    def setup_method(self):
        HnSource._hn_compliance_message_shown = False

    def teardown_method(self):
        HnSource._hn_compliance_message_shown = False

    def test_user_link_is_permalink(self):
        """user_link is a direct comment permalink (not a profile URL)."""
        source = _make_hn_source()
        comments = _build_api_comments(source)
        assert len(comments) == 1
        link = comments[0]["user_link"]
        assert link == "https://news.ycombinator.com/item?id=43000001"

    def test_username_not_in_user_link(self):
        """Username must not appear in user_link."""
        source = _make_hn_source()
        comments = _build_api_comments(source)
        link = comments[0]["user_link"]
        assert "seizethecheese" not in link

    def test_user_display_name_is_anonymous(self):
        """Display name must be Anonymous."""
        source = _make_hn_source()
        comments = _build_api_comments(source)
        assert comments[0]["user"] == "Anonymous"

    def test_markdown_output_has_comment_link(self):
        """Markdown output contains [view on HN](permalink) link."""
        source = _make_hn_source()
        comments = _build_api_comments(source)
        processor = create_optimized_comment_processor(max_comments=None)
        md = processor.generate_inline_comments_markdown(
            comments, "Test Article",
            "https://news.ycombinator.com/item?id=99", None,
            link_text="view on HN",
        )
        assert "[view on HN]" in md
        assert "news.ycombinator.com/item?id=43000001" in md

    def test_markdown_output_contains_no_username(self):
        """Username must not appear anywhere in the markdown output."""
        source = _make_hn_source()
        comments = _build_api_comments(source)
        processor = create_optimized_comment_processor(max_comments=None)
        md = processor.generate_inline_comments_markdown(
            comments, "Test Article",
            "https://news.ycombinator.com/item?id=99", None,
        )
        assert "seizethecheese" not in md

    def test_html_output_has_comment_link(self):
        """HTML output contains anchor to the permalink."""
        source = _make_hn_source()
        comments = _build_api_comments(source)
        processor = create_optimized_comment_processor(max_comments=None)
        html = processor.generate_inline_comments_html(
            comments, "Test Article",
            "https://news.ycombinator.com/item?id=99",
        )
        assert "news.ycombinator.com/item?id=43000001" in html

    def test_html_output_contains_no_username(self):
        """Username must not appear anywhere in the HTML output."""
        source = _make_hn_source()
        comments = _build_api_comments(source)
        processor = create_optimized_comment_processor(max_comments=None)
        html = processor.generate_inline_comments_html(
            comments, "Test Article",
            "https://news.ycombinator.com/item?id=99",
        )
        assert "seizethecheese" not in html
