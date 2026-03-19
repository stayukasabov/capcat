"""
Tests for _generate_breadcrumb depth and href correctness.

The breadcrumb physical depth is fixed by where the file lives in the
directory tree, NOT by the length of the breadcrumb path array. A wrong
depth causes links to open the wrong directory (observed prod bug: comments
page opened /News_DD-MM-YYYY/news.html instead of source/news.html).

Directory depths:
  news.html  (source_dir/)             → date = 1 up
  article.html (article_dir/)          → date = 2 up, source = 1 up
  html/article.html or comments.html   → date = 3 up, source = 2 up
"""
from __future__ import annotations

import pytest


@pytest.fixture()
def generator():
    """HTMLGenerator instance with access to the private breadcrumb method."""
    from capcat.core.html_generator import HTMLGenerator
    return HTMLGenerator()


def _call(generator, breadcrumb_path, html_subfolder=False, current_file=None):
    """Helper: call _generate_breadcrumb and return the raw HTML string."""
    return generator._generate_breadcrumb(
        breadcrumb_path,
        html_subfolder=html_subfolder,
        current_file_path=current_file,
    )


# ---------------------------------------------------------------------------
# news.html — source index page (1 level deep)
# ---------------------------------------------------------------------------

def test_source_index_date_link_is_one_level_up(generator) -> None:
    """news.html sits inside source_dir/ so date index is one level up."""
    crumbs = ["News 14-03-2026", "Hacker News"]
    html = _call(generator, crumbs, html_subfolder=False, current_file="news.html")
    # date link must be ../index.html (1 up)
    assert 'href="../index.html"' in html


def test_source_index_shows_only_date_link(generator) -> None:
    """news.html breadcrumb contains only the date level — source is the h1."""
    crumbs = ["News 14-03-2026", "Hacker News"]
    html = _call(generator, crumbs, html_subfolder=False, current_file="news.html")
    # Only one <a> tag expected
    assert html.count("<a ") == 1


# ---------------------------------------------------------------------------
# article.html — article directory (2 levels deep)
# ---------------------------------------------------------------------------

def test_article_date_link_is_two_levels_up(generator) -> None:
    """article.html is in article_dir/ so date index is 2 levels up."""
    crumbs = ["News 14-03-2026", "Hacker News"]
    html = _call(generator, crumbs, html_subfolder=False, current_file="article.html")
    assert 'href="../../index.html"' in html


def test_article_source_link_is_one_level_up(generator) -> None:
    """article.html source link must be 1 level up → ../news.html."""
    crumbs = ["News 14-03-2026", "Hacker News"]
    html = _call(generator, crumbs, html_subfolder=False, current_file="article.html")
    assert 'href="../news.html"' in html


def test_article_breadcrumb_has_two_links(generator) -> None:
    """article.html breadcrumb must have exactly 2 links: date and source."""
    crumbs = ["News 14-03-2026", "Hacker News"]
    html = _call(generator, crumbs, html_subfolder=False, current_file="article.html")
    assert html.count("<a ") == 2


# ---------------------------------------------------------------------------
# html/article.html and html/comments.html (3 levels deep)
# ---------------------------------------------------------------------------

def test_html_subfolder_article_date_link_is_three_levels_up(generator) -> None:
    """html/article.html date link must be 3 levels up → ../../../index.html."""
    crumbs = ["News 14-03-2026", "Hacker News"]
    html = _call(generator, crumbs, html_subfolder=True, current_file="article.html")
    assert 'href="../../../index.html"' in html


def test_html_subfolder_article_source_link_is_two_levels_up(generator) -> None:
    """html/article.html source link must be 2 levels up → ../../news.html."""
    crumbs = ["News 14-03-2026", "Hacker News"]
    html = _call(generator, crumbs, html_subfolder=True, current_file="article.html")
    assert 'href="../../news.html"' in html


def test_html_subfolder_comments_date_link_is_three_levels_up(generator) -> None:
    """html/comments.html is at the same depth as html/article.html."""
    crumbs = ["News 14-03-2026", "Hacker News"]
    html = _call(generator, crumbs, html_subfolder=True, current_file="comments.html")
    assert 'href="../../../index.html"' in html


def test_html_subfolder_comments_source_link_is_two_levels_up(generator) -> None:
    """html/comments.html source link → ../../news.html (same as article)."""
    crumbs = ["News 14-03-2026", "Hacker News"]
    html = _call(generator, crumbs, html_subfolder=True, current_file="comments.html")
    assert 'href="../../news.html"' in html


def test_comments_breadcrumb_has_article_level(generator) -> None:
    """comments.html with 3-element path must render 3 breadcrumbs including article link."""
    crumbs = ["News 14-03-2026", "Hacker-News 14-03-2026", "Some Article"]
    html = _call(generator, crumbs, html_subfolder=True, current_file="comments.html")
    assert html.count("<a ") == 3
    assert 'href="article.html"' in html


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_breadcrumb_returns_empty_string(generator) -> None:
    """Empty breadcrumb path must return empty string without raising."""
    assert _call(generator, []) == ""
    assert _call(generator, None) == ""


def test_single_item_breadcrumb_returns_empty_string(generator) -> None:
    """Fewer than 2 items provides no useful navigation — return empty."""
    assert _call(generator, ["News 14-03-2026"]) == ""


# ---------------------------------------------------------------------------
# Phase 2: Level 0 — date folder formatting
# ---------------------------------------------------------------------------

def test_level0_formats_date_as_news_d_month_yyyy(generator) -> None:
    """Date folder 'News 15-03-2026' must render as 'News 15 March 2026'."""
    crumbs = ["News 15-03-2026", "Hacker-News 15-03-2026"]
    html = _call(generator, crumbs, html_subfolder=False, current_file="article.html")
    assert "News 15 March 2026" in html


def test_level0_does_not_show_raw_dd_mm_yyyy(generator) -> None:
    """Raw DD-MM-YYYY must not appear in the date breadcrumb anchor."""
    crumbs = ["News 15-03-2026", "Hacker-News 15-03-2026"]
    html = _call(generator, crumbs, html_subfolder=False, current_file="article.html")
    first_anchor = html.split("</a>")[0]
    assert "15-03-2026" not in first_anchor


# ---------------------------------------------------------------------------
# Phase 2: Level 1 — source folder formatting
# ---------------------------------------------------------------------------

def test_level1_strips_date_and_normalises_hyphens(generator) -> None:
    """Source folder 'Hacker-News 15-03-2026' must render as 'Hacker News'."""
    crumbs = ["News 15-03-2026", "Hacker-News 15-03-2026"]
    html = _call(generator, crumbs, html_subfolder=False, current_file="article.html")
    assert "Hacker News" in html


def test_level1_has_no_trailing_date(generator) -> None:
    """Source breadcrumb must contain no date portion."""
    crumbs = ["News 15-03-2026", "Hacker-News 15-03-2026"]
    html = _call(generator, crumbs, html_subfolder=False, current_file="article.html")
    anchors = html.split("</a>")
    source_anchor = anchors[1] if len(anchors) > 1 else ""
    assert "15-03-2026" not in source_anchor


# ---------------------------------------------------------------------------
# Phase 2: Level 2 — comments page article breadcrumb
# ---------------------------------------------------------------------------

def test_comments_third_link_points_to_article(generator) -> None:
    """Third breadcrumb on comments page must link to article.html (same html/ dir)."""
    crumbs = ["News 15-03-2026", "Hacker-News 15-03-2026", "My Article Title"]
    html = _call(generator, crumbs, html_subfolder=True, current_file="comments.html")
    assert 'href="article.html"' in html


def test_comments_third_link_shows_article_title(generator) -> None:
    """Third breadcrumb must display the article title text."""
    crumbs = ["News 15-03-2026", "Hacker-News 15-03-2026", "My Article Title"]
    html = _call(generator, crumbs, html_subfolder=True, current_file="comments.html")
    assert "My Article Title" in html


def test_html_subfolder_article_still_has_two_links(generator) -> None:
    """html/article.html (not comments) must still render exactly 2 breadcrumbs."""
    crumbs = ["News 15-03-2026", "Hacker-News 15-03-2026"]
    html = _call(generator, crumbs, html_subfolder=True, current_file="article.html")
    assert html.count("<a ") == 2
