# tests/unit/test_htmlgen/test_svg_classifier.py
"""Tests for ArticleHTMLGenerator._classify_svg_elements — SVG icon vs illustration classifier."""
from __future__ import annotations
import base64
import urllib.parse
import pytest
from capcat.htmlgen.generator import ArticleHTMLGenerator


@pytest.fixture
def gen() -> ArticleHTMLGenerator:
    return ArticleHTMLGenerator()


def _has_icon_class(html: str) -> bool:
    """Return True if any element in html has class capcat-icon."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    return bool(soup.find(class_="capcat-icon"))


def _make_data_uri_percent(viewbox: str = "0 0 512 512") -> str:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"><path d="M0 0"/></svg>'
    return "data:image/svg+xml;charset=utf-8," + urllib.parse.quote(svg)


def _make_data_uri_base64(viewbox: str = "0 0 512 512") -> str:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"><path d="M0 0"/></svg>'
    encoded = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{encoded}"


# ── Test 1: Percent-encoded data URI icon in <li> with aria-label ────────────

def test_percent_encoded_icon_in_li_gets_icon_class(gen):
    src = _make_data_uri_percent("0 0 512 512")
    html = f'<ul><li><img src="{src}" aria-label="Mastodon" role="img"/></li></ul>'
    result = gen._classify_svg_elements(html)
    assert _has_icon_class(result), "Expected capcat-icon on social share icon"


# ── Test 2: Base64-encoded data URI icon in <li> ─────────────────────────────

def test_base64_icon_in_li_gets_icon_class(gen):
    src = _make_data_uri_base64("0 0 512 512")
    html = f'<ul><li><img src="{src}"/></li></ul>'
    result = gen._classify_svg_elements(html)
    assert _has_icon_class(result), "Expected capcat-icon on base64 data URI icon in list"


# ── Test 3: Inline <svg> in <a> inside <nav> ─────────────────────────────────

def test_inline_svg_in_nav_link_gets_icon_class(gen):
    html = '<nav><a href="#"><svg viewBox="0 0 24 24"><path d="M0 0"/></svg></a></nav>'
    result = gen._classify_svg_elements(html)
    assert _has_icon_class(result), "Expected capcat-icon on nav SVG icon"


# ── Test 4: Non-square illustration — no class ───────────────────────────────

def test_non_square_svg_gets_no_class(gen):
    html = '<p><img src="diagram.svg" width="800" height="400"/></p>'
    result = gen._classify_svg_elements(html)
    assert not _has_icon_class(result), "Non-square illustration should not get capcat-icon"


# ── Test 5: Sole-child illustration between paragraphs — no class ────────────

def test_sole_child_between_paragraphs_gets_no_class(gen):
    html = (
        '<p>Before text.</p>'
        '<p><img src="illustration.svg" width="400" height="400"/></p>'
        '<p>After text.</p>'
    )
    result = gen._classify_svg_elements(html)
    assert not _has_icon_class(result), "Sole-child illustration between paragraphs should not get capcat-icon"


# ── Test 6: No size info — fallback to illustration ──────────────────────────

def test_svg_with_no_size_info_gets_no_class(gen):
    html = '<p><img src="unknown.svg"/></p>'
    result = gen._classify_svg_elements(html)
    assert not _has_icon_class(result), "SVG with no size info should default to illustration"


# ── Test 7: Large square without accessibility/context — illustration ─────────

def test_large_square_no_context_gets_no_class(gen):
    html = '<p><img src="chart.svg" width="512" height="512"/></p>'
    result = gen._classify_svg_elements(html)
    assert not _has_icon_class(result), "Large square with no icon signals should not get capcat-icon"


# ── Test 8: Bare img (post-anchor-strip) large square — illustration ──────────

def test_bare_large_square_img_gets_no_class(gen):
    html = '<div><img src="diagram.svg" width="400" height="400"/></div>'
    result = gen._classify_svg_elements(html)
    assert not _has_icon_class(result), "Large square bare img should not get capcat-icon"


# ── Test 9: Existing class is preserved when capcat-icon is added ─────────────

def test_existing_class_preserved_on_icon(gen):
    src = _make_data_uri_percent("0 0 24 24")
    html = f'<ul><li><img src="{src}" class="social-icon" aria-label="Share"/></li></ul>'
    result = gen._classify_svg_elements(html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(result, "html.parser")
    img = soup.find("img")
    classes = img.get("class", [])
    assert "capcat-icon" in classes, "capcat-icon should be added"
    assert "social-icon" in classes, "existing class should be preserved"


# ── Test 10: Icon inside <p> also gets capcat-icon class ─────────────────────

def test_icon_inside_paragraph_gets_icon_class(gen):
    src = _make_data_uri_percent("0 0 24 24")
    html = f'<p>Share on <img src="{src}" aria-label="Mastodon"/> social media.</p>'
    result = gen._classify_svg_elements(html)
    assert _has_icon_class(result), "Icon inside paragraph with sibling text should get capcat-icon"
