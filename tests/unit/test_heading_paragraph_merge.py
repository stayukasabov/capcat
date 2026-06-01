"""Regression: headings inside div wrappers must not merge with following content.

Many modern sites wrap headings in div containers (e.g. <div class="section">).
When _convert_element processes these divs at depth > 0, children_content.strip()
removes trailing newlines from the heading markdown, causing the heading text to
concatenate directly with the next sibling's content.

Fix: div handling must preserve block-level spacing regardless of depth.
"""
from __future__ import annotations

from capcat.core.formatter import html_to_markdown


def test_heading_not_merged_with_next_div_content():
    """H2 inside a wrapper div must not merge with text in the following sibling div.

    Real-world structure: sites wrap headings in div wrappers and body text in
    sibling divs, nested 5+ levels deep. At high depth the div handler must
    still preserve trailing newlines from headings.

    No whitespace between closing/opening div tags to simulate minified HTML.
    """
    html = (
        "<html><body><main><div><div>"
        '<div class="content">'
        '<div class="section"><h2>Challenge and Context</h2></div>'
        '<div class="text"><p>I read across several sources a week.</p></div>'
        "</div>"
        "</div></div></main></body></html>"
    )
    md = html_to_markdown(html)

    assert "## Challenge and Context" in md
    # The heading must NOT merge with the paragraph on the same line
    assert "ContextI read" not in md
    assert "Context\nI read" not in md, "need blank line, not just newline"


def test_heading_not_merged_with_sibling_paragraph():
    """H2 followed by a paragraph in the same parent must stay separate."""
    html = """
    <div class="wrapper">
        <h2>Summary</h2>
        <p>Capcat is a dual-mode command-line tool.</p>
    </div>
    """
    md = html_to_markdown(html)

    assert "## Summary" in md
    assert "SummaryCapcat" not in md


def test_heading_spacing_at_depth_zero():
    """Headings at the top level must also have proper spacing."""
    html = """
    <h2>Title</h2>
    <p>Paragraph text follows.</p>
    """
    md = html_to_markdown(html)

    assert "## Title" in md
    assert "TitleParagraph" not in md


def test_nested_heading_divs_preserve_spacing():
    """Multiple heading+content pairs in sequence must all stay separate."""
    html = (
        "<html><body><main><div><div>"
        '<div class="content">'
        '<div class="section"><h2>First</h2></div>'
        '<div class="text"><p>First paragraph.</p></div>'
        '<div class="section"><h2>Second</h2></div>'
        '<div class="text"><p>Second paragraph.</p></div>'
        "</div>"
        "</div></div></main></body></html>"
    )
    md = html_to_markdown(html)

    assert "FirstFirst paragraph" not in md
    assert "SecondSecond paragraph" not in md
    assert "## First" in md
    assert "## Second" in md
