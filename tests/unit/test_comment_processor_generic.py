"""
Tests that StreamlinedCommentProcessor is a pure generic engine:
- No source-specific wrapper methods
- process_comments_flattened works correctly with HN and LB selector configs (as dicts unpacked with **)
"""
from bs4 import BeautifulSoup
from capcat.core.streamlined_comment_processor import StreamlinedCommentProcessor


def test_wrapper_methods_removed():
    """Source-specific wrapper methods must not exist on the processor."""
    processor = StreamlinedCommentProcessor()
    removed = [
        "process_hacker_news_comments_optimized",
        "process_lobsters_comments_optimized",
        "process_lesswrong_comments_optimized",
        "process_hacker_news_comments_html_optimized",
        "process_lobsters_comments_html_optimized",
    ]
    for method in removed:
        assert not hasattr(processor, method), (
            f"Method {method} should have been removed from StreamlinedCommentProcessor"
        )


_HN_HTML = """
<table class="comment-tree">
  <tr class="athing comtr" id="c1">
    <td>
      <span class="hnuser">alice</span>
      <div class="comment"><span class="c00">Great article!</span></div>
    </td>
  </tr>
</table>
"""

_LB_HTML = """
<div class="comment" id="c2">
  <a class="user" href="/u/bob">bob</a>
  <div class="comment_text"><p>Interesting read.</p></div>
</div>
"""

_HN_SELECTORS = {
    "comment_selector": ".comment-tree .athing",
    "user_selector": ".hnuser",
    "comment_text_selector": ".comment",
}

_LB_SELECTORS = {
    "comment_selector": ".comment",
    "user_selector": ".user",
    "comment_text_selector": ".comment_text",
}


def test_hn_selectors_via_generic_interface():
    """process_comments_flattened(**HN_SELECTORS) returns a list of comment dicts."""
    soup = BeautifulSoup(_HN_HTML, "html.parser")
    processor = StreamlinedCommentProcessor()
    comments = processor.process_comments_flattened(soup, **_HN_SELECTORS)
    assert isinstance(comments, list)
    assert len(comments) == 1
    assert comments[0]["text"]  # non-empty text


def test_lb_selectors_via_generic_interface():
    """process_comments_flattened(**LB_SELECTORS) returns a list of comment dicts."""
    soup = BeautifulSoup(_LB_HTML, "html.parser")
    processor = StreamlinedCommentProcessor()
    comments = processor.process_comments_flattened(soup, **_LB_SELECTORS)
    assert isinstance(comments, list)
    assert len(comments) == 1


def test_generate_inline_comments_markdown_uses_comment_list():
    """generate_inline_comments_markdown accepts a list[dict] and returns a string."""
    processor = StreamlinedCommentProcessor()
    comments = [{"id": "c1", "user": "Anonymous", "user_link": "#", "text": "Test", "level": 0}]
    result = processor.generate_inline_comments_markdown(
        comments, "My Article", "https://example.com/comments"
    )
    assert isinstance(result, str)
    assert "My Article" in result
    assert "Test" in result


def test_generate_inline_comments_html_uses_comment_list():
    """generate_inline_comments_html accepts a list[dict] and returns a string."""
    processor = StreamlinedCommentProcessor()
    comments = [{"id": "c1", "user": "Anonymous", "user_link": "#", "text": "Test", "level": 0}]
    result = processor.generate_inline_comments_html(
        comments, "My Article", "https://example.com/comments"
    )
    assert isinstance(result, str)
    assert "My Article" in result


def test_processor_without_depth_fn_defaults_level_to_zero():
    """Without depth_fn, all comments get level=0 (backward compat). Uses local test fixture, not source selectors."""
    soup = BeautifulSoup(_HN_HTML, "html.parser")
    processor = StreamlinedCommentProcessor()
    comments = processor.process_comments_flattened(soup, **_HN_SELECTORS)
    assert all(c["level"] == 0 for c in comments)


def test_depth_fn_sets_correct_level():
    """depth_fn return value is stored in comment['level']."""
    _HN_HTML_DEEP = """
    <table class="comment-tree">
      <tr class="athing comtr" id="c1">
        <td><table><tr>
          <td class="ind"><img src="s.gif" height="1" width="0"></td>
          <td class="default">
            <span class="comhead"><span class="hnuser">alice</span></span>
            <div class="comment"><span class="c00">Top level</span></div>
          </td>
        </tr></table></td>
      </tr>
      <tr class="athing comtr" id="c2">
        <td><table><tr>
          <td class="ind"><img src="s.gif" height="1" width="40"></td>
          <td class="default">
            <span class="comhead"><span class="hnuser">bob</span></span>
            <div class="comment"><span class="c00">Reply</span></div>
          </td>
        </tr></table></td>
      </tr>
      <tr class="athing comtr" id="c3">
        <td><table><tr>
          <td class="ind"><img src="s.gif" height="1" width="80"></td>
          <td class="default">
            <span class="comhead"><span class="hnuser">carol</span></span>
            <div class="comment"><span class="c00">Reply to reply</span></div>
          </td>
        </tr></table></td>
      </tr>
    </table>
    """

    def hn_depth(elem):
        img = elem.select_one("td.ind img")
        if img and img.get("width") is not None:
            try:
                return int(img["width"]) // 40
            except (ValueError, TypeError):
                return 0
        return 0

    soup = BeautifulSoup(_HN_HTML_DEEP, "html.parser")
    processor = StreamlinedCommentProcessor()
    selectors = dict(_HN_SELECTORS)
    selectors["depth_fn"] = hn_depth
    comments = processor.process_comments_flattened(soup, **selectors)
    assert len(comments) == 3
    assert comments[0]["level"] == 0
    assert comments[1]["level"] == 1
    assert comments[2]["level"] == 2
