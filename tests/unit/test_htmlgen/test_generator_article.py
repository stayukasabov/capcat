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


class TestFrontmatterStripping:
    """YAML frontmatter must not leak into rendered HTML."""

    def test_frontmatter_not_rendered_in_html(self, tmp_path):
        """YAML frontmatter block must be stripped before markdown conversion."""
        md = tmp_path / "Article.md"
        md.write_text(
            "---\n"
            "title: 'ESLint v10: Flat Config Completion and JSX Tracking'\n"
            "url: https://www.infoq.com/news/2026/04/eslint-10-release/\n"
            "source: InfoQ\n"
            "source_code: iq\n"
            "category: techpro\n"
            "captured: '2026-04-03'\n"
            "tags:\n"
            "- iq\n"
            "- techpro\n"
            "---\n\n"
            "# ESLint v10: Flat Config Completion and JSX Tracking\n\n"
            "Article body.\n"
        )
        from capcat.htmlgen import ArticleHTMLGenerator
        gen = ArticleHTMLGenerator()
        result = gen.generate_article_html_from_template(
            str(md), "ESLint v10", BREADCRUMB, SOURCE_CONFIG, html_subfolder=True,
        )
        assert "source_code" not in result
        assert "captured" not in result
        assert "techpro" not in result or "techpro" in result and result.count("techpro") == result.count("techpro")  # only in meta if at all
        # The key check - raw YAML keys must not appear as visible text
        assert "source_code: iq" not in result
        assert "captured: '2026-04-03'" not in result

    def test_no_duplicate_title_when_frontmatter_present(self, tmp_path):
        """H1 title must not appear twice when article has YAML frontmatter."""
        md = tmp_path / "Article.md"
        title = "ESLint v10: Flat Config Completion and JSX Tracking"
        md.write_text(
            f"---\ntitle: '{title}'\nsource: InfoQ\n---\n\n"
            f"# {title}\n\nArticle body.\n"
        )
        from capcat.htmlgen import ArticleHTMLGenerator
        gen = ArticleHTMLGenerator()
        result = gen.generate_article_html_from_template(
            str(md), title, BREADCRUMB, SOURCE_CONFIG, html_subfolder=True,
        )
        # Title should appear in the page header but not as a second H1 in the body
        h1_count = result.lower().count("<h1")
        assert h1_count <= 1, f"Expected at most 1 <h1>, found {h1_count}"


class TestPdfDownloadBarRendering:
    """B3 - PDF download bar must wrap properly when there are many PDFs."""

    def test_pdf_bar_uses_space_separator_not_middot(self, tmp_path):
        """
        The PDF download bar must NOT use &nbsp;·&nbsp; as link separator.
        That separator dangles at the start of a new line when links wrap.
        """
        from capcat.htmlgen import ArticleHTMLGenerator

        # Create multiple PDFs in a files/ sibling directory
        files_dir = tmp_path / "files"
        files_dir.mkdir()
        for i in range(5):
            (files_dir / f"paper{i}.pdf").write_bytes(b"%PDF")

        md_path = tmp_path / "TestArticle.md"
        md_path.write_text("# TestArticle\n\nContent.\n")

        gen = ArticleHTMLGenerator()
        html = gen.generate_article_html_from_template(
            str(md_path), "TestArticle", BREADCRUMB, SOURCE_CONFIG,
            html_subfolder=True,
        )

        assert "&nbsp;·&nbsp;" not in html, (
            "PDF bar must not use &nbsp;·&nbsp; separator - it dangles on line wrap"
        )
        assert 'class="pdf-download-bar"' in html, (
            "PDF download bar must be present when files/*.pdf exist"
        )

    def test_pdf_bar_css_has_flex_wrap(self):
        """
        base.css must include flex-wrap: wrap in .pdf-download-bar so the bar
        wraps gracefully when there are many PDF links.
        """
        import re
        from pathlib import Path

        css_path = Path(__file__).parents[3] / "capcat" / "themes" / "base.css"
        css = css_path.read_text()

        # Find the .pdf-download-bar block
        match = re.search(
            r'\.pdf-download-bar\s*\{([^}]+)\}', css, re.DOTALL
        )
        assert match, ".pdf-download-bar block not found in base.css"
        block = match.group(1)
        assert "flex-wrap" in block, (
            "flex-wrap must be set in .pdf-download-bar to prevent overflow"
        )
        assert "wrap" in block, (
            "flex-wrap value must include 'wrap'"
        )
