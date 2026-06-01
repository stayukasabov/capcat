"""Tests for HN comment paragraph separation and duplication prevention.

HN uses unclosed <p> tags which html.parser nests instead of auto-closing.
This causes two bugs:
1. All paragraphs smashed into one wall of text (no separation)
2. Potential cascading suffix duplication from nested <p> get_text()
"""

import pytest
from bs4 import BeautifulSoup

from capcat.core.streamlined_comment_processor import StreamlinedCommentProcessor


def _make_comment_div(commtext_html: str) -> BeautifulSoup:
    """Wrap commtext HTML in the standard HN .comment div structure."""
    html = (
        f'<div class="comment">'
        f'<div class="commtext c00">{commtext_html}</div>'
        f'<div class="reply"><p><font size="1"><u>'
        f'<a href="reply?id=1">reply</a></u></font></p></div>'
        f'</div>'
    )
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("div", class_="comment")


class TestParagraphSeparation:
    """Paragraphs in HN comments must be separated, not concatenated."""

    def test_multi_paragraph_comment_separated(self):
        """Multiple <p> tags should produce separate paragraphs."""
        comment_elem = _make_comment_div(
            "First paragraph."
            "<p>Second paragraph."
            "<p>Third paragraph."
            "<p>Fourth paragraph.</p></p></p>"
        )
        processor = StreamlinedCommentProcessor()
        text = processor._process_comment_text_streamlined(comment_elem)

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        assert len(paragraphs) == 4, (
            f"Expected 4 separate paragraphs, got {len(paragraphs)}: {paragraphs}"
        )
        assert paragraphs[0] == "First paragraph."
        assert paragraphs[1] == "Second paragraph."
        assert paragraphs[2] == "Third paragraph."
        assert paragraphs[3] == "Fourth paragraph."

    def test_no_cascading_suffix_duplication(self):
        """Each paragraph must contain only its own text, not all subsequent text."""
        comment_elem = _make_comment_div(
            "Alpha."
            "<p>Bravo."
            "<p>Charlie."
            "<p>Delta.</p></p></p>"
        )
        processor = StreamlinedCommentProcessor()
        text = processor._process_comment_text_streamlined(comment_elem)

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        # Each paragraph should contain ONLY its own sentence
        for para in paragraphs:
            sentences_in_para = [
                s for s in ["Alpha.", "Bravo.", "Charlie.", "Delta."]
                if s in para
            ]
            assert len(sentences_in_para) == 1, (
                f"Paragraph contains multiple sentences (duplication): {para!r}"
            )

    def test_inline_quotes_preserved(self):
        """HN inline quotes (> prefix) should be preserved in text."""
        comment_elem = _make_comment_div(
            "&gt; quoted text from parent"
            "<p>My response to the quote."
            "<p>&gt; another quote"
            "<p>Another response.</p></p></p>"
        )
        processor = StreamlinedCommentProcessor()
        text = processor._process_comment_text_streamlined(comment_elem)

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        assert len(paragraphs) == 4
        assert paragraphs[0].startswith(">")
        assert paragraphs[1] == "My response to the quote."

    def test_single_paragraph_unchanged(self):
        """A comment with no <p> tags should remain a single paragraph."""
        comment_elem = _make_comment_div("Just a simple comment.")
        processor = StreamlinedCommentProcessor()
        text = processor._process_comment_text_streamlined(comment_elem)

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        assert len(paragraphs) == 1
        assert paragraphs[0] == "Just a simple comment."

    def test_links_preserved_in_paragraphs(self):
        """Markdown links should survive paragraph extraction."""
        comment_elem = _make_comment_div(
            'Check out <a href="https://example.com">this link</a>.'
            "<p>Second paragraph.</p>"
        )
        processor = StreamlinedCommentProcessor()
        text = processor._process_comment_text_streamlined(comment_elem)

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        assert len(paragraphs) == 2
        assert "[this link](https://example.com)" in paragraphs[0]


class TestContentSelectorBreadth:
    """BBC and Guardian content selectors must include image containers."""

    def test_bbc_selectors_include_article(self):
        import yaml

        with open("sources/active/config_driven/configs/bbc.yaml") as f:
            cfg = yaml.safe_load(f)
        selectors = cfg["content_selectors"]
        # Must have a broad selector that captures images alongside text
        has_broad = any(
            s in ("article", "main article", "main")
            for s in selectors
        )
        assert has_broad, f"BBC selectors too narrow for images: {selectors}"

    def test_guardian_selectors_include_article(self):
        import yaml

        with open("sources/active/config_driven/configs/guardian.yaml") as f:
            cfg = yaml.safe_load(f)
        selectors = cfg["content_selectors"]
        has_broad = any(
            s in ("article", ".content__main-column", "div[class*='dcr-']")
            for s in selectors
        )
        assert has_broad, f"Guardian selectors too narrow for images: {selectors}"
