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


class TestHNApiCommentParagraphs:
    """HN API path (_clean_api_comment_html) must also avoid duplication."""

    def _clean(self, html: str) -> str:
        """Call _clean_api_comment_html on the HN source."""
        from unittest.mock import MagicMock
        from capcat.sources.builtin.custom.hn.source import HnSource
        src = HnSource.__new__(HnSource)
        src.config = MagicMock()
        src.config.custom_config = {"hn": {}}
        return src._clean_api_comment_html(html)

    def test_nested_p_no_cascading_suffix(self):
        """Nested <p> from API must not produce cascading suffix duplication."""
        html = (
            'First paragraph.'
            '<p>Second paragraph.'
            '<p>Third paragraph.</p></p>'
        )
        result = self._clean(html)
        paragraphs = [p.strip() for p in result.split("\n\n") if p.strip()]
        assert len(paragraphs) == 3
        assert paragraphs[0] == "First paragraph."
        assert paragraphs[1] == "Second paragraph."
        assert paragraphs[2] == "Third paragraph."

    def test_api_comment_with_link_in_nested_p(self):
        """Links inside nested <p> must appear only once."""
        html = (
            'Intro text.'
            '<p>Middle text.'
            '<p><a href="https://example.com">https://example.com</a></p></p>'
        )
        result = self._clean(html)
        paragraphs = [p.strip() for p in result.split("\n\n") if p.strip()]
        assert len(paragraphs) == 3
        assert "example.com" not in paragraphs[0]
        assert "example.com" not in paragraphs[1]
        assert "example.com" in paragraphs[2]

    def test_api_comment_single_paragraph(self):
        """API comment with no <p> tags is a single paragraph."""
        html = 'Just a plain comment with no paragraphs.'
        result = self._clean(html)
        paragraphs = [p.strip() for p in result.split("\n\n") if p.strip()]
        assert len(paragraphs) == 1
        assert paragraphs[0] == "Just a plain comment with no paragraphs."


class TestContentSelectorBreadth:
    """BBC and Guardian content selectors must include image containers."""

    def test_bbc_first_selector_captures_images(self):
        """BBC first selector must grab both text and image blocks."""
        import yaml

        with open("capcat/sources/builtin/config_driven/configs/bbc.yaml") as f:
            cfg = yaml.safe_load(f)
        first = cfg["content_selectors"][0]

        # Simulate BBC article structure
        html = (
            '<div data-component="text-block"><p>Paragraph one.</p></div>'
            '<div data-component="image-block"><figure><img src="photo.jpg"></figure></div>'
            '<div data-component="text-block"><p>Paragraph two.</p></div>'
        )
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.select(first)

        # Must find text AND image blocks
        has_text = any("text-block" in str(e.get("data-component", "")) for e in elements)
        has_img = any("image-block" in str(e.get("data-component", "")) for e in elements)
        assert has_text, f"Selector {first!r} missed text-block elements"
        assert has_img, f"Selector {first!r} missed image-block elements"

    def test_bbc_selectors_include_article(self):
        import yaml

        with open("capcat/sources/builtin/config_driven/configs/bbc.yaml") as f:
            cfg = yaml.safe_load(f)
        selectors = cfg["content_selectors"]
        has_broad = any(
            s in ("article", "main article", "main")
            for s in selectors
        )
        assert has_broad, f"BBC selectors too narrow for images: {selectors}"

    def test_guardian_selectors_include_article(self):
        import yaml

        with open("capcat/sources/builtin/config_driven/configs/guardian.yaml") as f:
            cfg = yaml.safe_load(f)
        selectors = cfg["content_selectors"]
        has_broad = any(
            s in ("article", ".content__main-column", "div[class*='dcr-']")
            for s in selectors
        )
        assert has_broad, f"Guardian selectors too narrow for images: {selectors}"

    def test_combined_selector_preserves_document_order(self):
        """Images between text blocks must appear between paragraphs in extraction."""
        html = (
            '<div data-component="text-block"><p>Before image.</p></div>'
            '<div data-component="image-block"><figure><img src="mid.jpg" alt="mid"></figure></div>'
            '<div data-component="text-block"><p>After image.</p></div>'
        )
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.select(
            '[data-component="text-block"], [data-component="image-block"]'
        )
        # Elements must be in document order: text, image, text
        types = [e.get("data-component") for e in elements]
        assert types == ["text-block", "image-block", "text-block"]
