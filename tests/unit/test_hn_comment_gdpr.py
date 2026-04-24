"""Tests: HN comment output includes permalink links via comment_permalink_fn."""
from __future__ import annotations
from bs4 import BeautifulSoup
from capcat.core.streamlined_comment_processor import create_optimized_comment_processor


def _make_hn_soup(comment_id: str, username: str, text: str) -> BeautifulSoup:
    """Minimal HN comment page HTML with one comment."""
    html = f"""
    <table class="comment-tree">
      <tr class="athing comtr" id="{comment_id}">
        <td>
          <table>
            <tr>
              <td class="ind"><img width="0"></td>
              <td class="votelinks"></td>
              <td class="default">
                <div class="comment-head">
                  <a href="user?id={username}" class="hnuser">{username}</a>
                </div>
                <div class="comment"><p>{text}</p></div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    """
    return BeautifulSoup(html, "html.parser")


_HN_SELECTORS_WITH_PERMALINK = {
    "comment_selector": ".comment-tree .athing",
    "user_selector": ".hnuser",
    "comment_text_selector": ".comment",
    "comment_permalink_fn": lambda cid: f"https://news.ycombinator.com/item?id={cid}",
}


class TestCommentPermalinkPresent:
    def test_user_link_is_permalink(self):
        """user_link is a direct comment permalink (not a profile URL)."""
        soup = _make_hn_soup("43000001", "seizethecheese", "Great point.")
        processor = create_optimized_comment_processor(max_comments=None)
        comments = processor.process_comments_flattened(soup, **_HN_SELECTORS_WITH_PERMALINK)
        assert len(comments) == 1
        link = comments[0]["user_link"]
        assert link == "https://news.ycombinator.com/item?id=43000001", (
            f"user_link must be the comment permalink, got: {link}"
        )

    def test_username_not_in_user_link(self):
        """Username must not appear in user_link (link uses comment ID, not username)."""
        soup = _make_hn_soup("43000002", "seizethecheese", "Interesting.")
        processor = create_optimized_comment_processor(max_comments=None)
        comments = processor.process_comments_flattened(soup, **_HN_SELECTORS_WITH_PERMALINK)
        link = comments[0]["user_link"]
        assert "seizethecheese" not in link, (
            f"Username must not appear in user_link, got: {link}"
        )

    def test_user_display_name_is_anonymous(self):
        """Display name must be Anonymous, not the real username."""
        soup = _make_hn_soup("43000003", "seizethecheese", "Hello.")
        processor = create_optimized_comment_processor(max_comments=None)
        comments = processor.process_comments_flattened(soup, **_HN_SELECTORS_WITH_PERMALINK)
        assert comments[0]["user"] == "Anonymous"

    def test_markdown_output_has_comment_link(self):
        """Markdown output contains [view on HN](permalink) link."""
        soup = _make_hn_soup("43000004", "seizethecheese", "Test comment.")
        processor = create_optimized_comment_processor(max_comments=None)
        comments = processor.process_comments_flattened(soup, **_HN_SELECTORS_WITH_PERMALINK)
        md = processor.generate_inline_comments_markdown(
            comments, "Test Article", "https://news.ycombinator.com/item?id=99", None,
            link_text="view on HN",
        )
        assert "[view on HN]" in md, "Markdown must include [view on HN] link"
        assert "news.ycombinator.com/item?id=43000004" in md, (
            "Markdown must link to comment permalink"
        )

    def test_markdown_output_contains_no_username(self):
        """Username must not appear anywhere in the markdown output."""
        soup = _make_hn_soup("43000005", "seizethecheese", "A comment.")
        processor = create_optimized_comment_processor(max_comments=None)
        comments = processor.process_comments_flattened(soup, **_HN_SELECTORS_WITH_PERMALINK)
        md = processor.generate_inline_comments_markdown(
            comments, "Test Article", "https://news.ycombinator.com/item?id=99", None
        )
        assert "seizethecheese" not in md, (
            "Username must not appear anywhere in markdown output"
        )

    def test_html_output_has_comment_link(self):
        """HTML output contains (comment) anchor to the permalink."""
        soup = _make_hn_soup("43000006", "seizethecheese", "HTML test.")
        processor = create_optimized_comment_processor(max_comments=None)
        comments = processor.process_comments_flattened(soup, **_HN_SELECTORS_WITH_PERMALINK)
        html = processor.generate_inline_comments_html(
            comments, "Test Article", "https://news.ycombinator.com/item?id=99"
        )
        assert "news.ycombinator.com/item?id=43000006" in html, (
            "HTML must include comment permalink"
        )

    def test_html_output_contains_no_username(self):
        """Username must not appear anywhere in the HTML output."""
        soup = _make_hn_soup("43000007", "seizethecheese", "Another.")
        processor = create_optimized_comment_processor(max_comments=None)
        comments = processor.process_comments_flattened(soup, **_HN_SELECTORS_WITH_PERMALINK)
        html = processor.generate_inline_comments_html(
            comments, "Test Article", "https://news.ycombinator.com/item?id=99"
        )
        assert "seizethecheese" not in html, (
            "Username must not appear anywhere in HTML output"
        )

    def test_process_comments_has_comment_permalink_fn(self):
        """process_comments_flattened accepts comment_permalink_fn parameter."""
        import inspect
        from capcat.core.streamlined_comment_processor import StreamlinedCommentProcessor
        sig = inspect.signature(StreamlinedCommentProcessor.process_comments_flattened)
        assert "comment_permalink_fn" in sig.parameters, (
            "comment_permalink_fn must be present in process_comments_flattened signature"
        )

    def test_hn_selectors_has_comment_permalink_fn(self):
        """_HN_SELECTORS must contain comment_permalink_fn."""
        from capcat.sources.builtin.custom.hn.source import _HN_SELECTORS as hn_sel
        assert "comment_permalink_fn" in hn_sel, (
            "_HN_SELECTORS must contain comment_permalink_fn"
        )
