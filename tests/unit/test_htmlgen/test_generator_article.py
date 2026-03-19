"""Tests for ArticleHTMLGenerator article/comments page generation."""
from __future__ import annotations
from pathlib import Path
import pytest


@pytest.fixture
def article_md(tmp_path: Path) -> Path:
    """Minimal article markdown file."""
    f = tmp_path / "My-Title.md"
    f.write_text("# My Title\n\nSome content.\n")
    return f


@pytest.fixture
def article_with_comments(tmp_path: Path) -> Path:
    """Article markdown with a sibling Comments file."""
    article = tmp_path / "My-Title.md"
    article.write_text("# My Title\n\nSome content.\n")
    comments = tmp_path / "My-Title-Comments.md"
    comments.write_text("# Comments\n\n- User: good post\n")
    return article


SOURCE_CONFIG = {"template": {"variant": "article-no-comments"}}
BREADCRUMB = ["News_19-03-2026", "Hacker-News_19-03-2026"]


def test_generate_article_html_returns_html_string(article_md):
    from capcat.htmlgen import ArticleHTMLGenerator
    gen = ArticleHTMLGenerator()
    result = gen.generate_article_html_from_template(
        str(article_md), "My Title", BREADCRUMB, SOURCE_CONFIG,
        html_subfolder=True,
    )
    assert isinstance(result, str)
    assert "<html" in result
    assert "<body" in result


def test_generate_article_html_embeds_title(article_md):
    from capcat.htmlgen import ArticleHTMLGenerator
    gen = ArticleHTMLGenerator()
    result = gen.generate_article_html_from_template(
        str(article_md), "My Title", BREADCRUMB, SOURCE_CONFIG,
        html_subfolder=True,
    )
    assert "My Title" in result


def test_generate_article_html_comments_page_has_back_to_article_nav(tmp_path):
    from capcat.htmlgen import ArticleHTMLGenerator
    comments_md = tmp_path / "My-Title-Comments.md"
    comments_md.write_text("# Comments\n\n- User: nice\n")
    gen = ArticleHTMLGenerator()
    result = gen.generate_article_html_from_template(
        str(comments_md), "My Title - Comments",
        BREADCRUMB + ["My Title"],
        {"template": {"variant": "comments-with-navigation"}},
        html_subfolder=True,
    )
    assert 'class="index-link"' in result
    assert 'href="article.html"' in result


def test_generate_article_html_single_article_has_no_navigation(article_md):
    from capcat.htmlgen import ArticleHTMLGenerator
    gen = ArticleHTMLGenerator()
    result = gen.generate_article_html_from_template(
        str(article_md), "My Title", BREADCRUMB, SOURCE_CONFIG,
        html_subfolder=True, is_single_article=True,
    )
    assert 'class="navigation-container"' not in result


def test_generate_article_html_with_comments_md_shows_comments_button(article_with_comments):
    from capcat.htmlgen import ArticleHTMLGenerator
    gen = ArticleHTMLGenerator()
    result = gen.generate_article_html_from_template(
        str(article_with_comments), "My Title", BREADCRUMB,
        {"template": {"variant": "article-with-comments"}},
        html_subfolder=True,
    )
    assert 'href="comments.html"' in result


def test_generate_article_html_without_comments_md_hides_comments_button(article_md):
    from capcat.htmlgen import ArticleHTMLGenerator
    gen = ArticleHTMLGenerator()
    result = gen.generate_article_html_from_template(
        str(article_md), "My Title", BREADCRUMB, SOURCE_CONFIG,
        html_subfolder=True,
    )
    assert 'href="comments.html"' not in result
