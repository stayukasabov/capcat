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


def test_comments_breadcrumb_has_no_article_level(generator) -> None:
    """Comments page must NOT have an 'Article' breadcrumb item — that
    navigation is handled by the Back to Article button."""
    crumbs = ["News 14-03-2026", "Hacker News", "Some Article", "Comments"]
    html = _call(generator, crumbs, html_subfolder=True, current_file="comments.html")
    # Should only show date and source (2 links)
    assert html.count("<a ") == 2


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
