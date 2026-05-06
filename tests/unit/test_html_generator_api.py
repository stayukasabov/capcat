"""
Tests for HTMLGenerator public API contract.

These tests verify that every method called externally exists with the
correct signature. A missing method here is the class of bug that caused
the 'HTMLGenerator has no attribute generate_html_file' failure in prod.
"""
from __future__ import annotations

import inspect
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def generator():
    """Return a bare HTMLGenerator instance (no file I/O)."""
    from capcat.htmlgen import ArticleHTMLGenerator as HTMLGenerator
    return HTMLGenerator()


# ---------------------------------------------------------------------------
# Public method existence
# ---------------------------------------------------------------------------

def test_generate_article_html_from_template_exists(generator) -> None:
    """generate_article_html_from_template must exist - it is the primary entry
    point called by HTMLPostProcessor for every article and comments page."""
    assert hasattr(generator, "generate_article_html_from_template"), (
        "HTMLGenerator is missing generate_article_html_from_template. "
        "Any call to this method will raise AttributeError at runtime."
    )
    assert callable(generator.generate_article_html_from_template)


def test_generate_article_html_from_template_signature(generator) -> None:
    """Signature must accept the arguments HTMLPostProcessor passes."""
    sig = inspect.signature(generator.generate_article_html_from_template)
    params = list(sig.parameters)
    # Required positional params (besides self)
    for required in ("markdown_path", "article_title", "breadcrumb_path", "source_config"):
        assert required in params, (
            f"generate_article_html_from_template is missing parameter '{required}'"
        )


def test_generate_directory_index_exists(generator) -> None:
    """generate_directory_index must exist - called for index.html generation."""
    assert hasattr(generator, "generate_directory_index")
    assert callable(generator.generate_directory_index)


def test_generate_article_html_exists(generator) -> None:
    """generate_article_html must exist - used by article_fetcher PDF path."""
    assert hasattr(generator, "generate_article_html")
    assert callable(generator.generate_article_html)


def test_no_generate_html_file_method(generator) -> None:
    """generate_html_file must NOT exist - it was a ghost method that caused
    the prod breakage. If someone adds it, this test enforces the right name."""
    assert not hasattr(generator, "generate_html_file"), (
        "generate_html_file should not exist on HTMLGenerator. "
        "The correct method is generate_article_html_from_template."
    )


# ---------------------------------------------------------------------------
# generate_article_html_from_template basic output
# ---------------------------------------------------------------------------

def test_generate_article_html_from_template_returns_html(
    tmp_path, generator
) -> None:
    """Must return a non-empty string containing an HTML doctype."""
    md_file = tmp_path / "article.md"
    md_file.write_text("# Test Article\n\nSome content.", encoding="utf-8")

    source_config = {"template": {"variant": "article-no-comments"}}
    result = generator.generate_article_html_from_template(
        markdown_path=str(md_file),
        article_title="Test Article",
        breadcrumb_path=["News 14-03-2026", "Hacker News"],
        source_config=source_config,
        html_subfolder=True,
    )

    assert isinstance(result, str)
    assert len(result) > 100
    assert "<!DOCTYPE" in result or "<html" in result


def test_generate_article_html_from_template_includes_title(
    tmp_path, generator
) -> None:
    """Generated HTML must include the article title."""
    md_file = tmp_path / "article.md"
    md_file.write_text("# My Test Title\n\nBody.", encoding="utf-8")

    source_config = {"template": {"variant": "article-no-comments"}}
    result = generator.generate_article_html_from_template(
        markdown_path=str(md_file),
        article_title="My Test Title",
        breadcrumb_path=["News 14-03-2026", "Test Source"],
        source_config=source_config,
        html_subfolder=True,
    )

    assert "My Test Title" in result


def test_generate_article_html_from_template_comments_variant(
    tmp_path, generator
) -> None:
    """comments.md path must trigger comments template and produce HTML."""
    md_file = tmp_path / "comments.md"
    md_file.write_text("# Comments\n\n**User**: Great article.", encoding="utf-8")

    source_config = {"template": {"variant": "comments-with-navigation"}}
    result = generator.generate_article_html_from_template(
        markdown_path=str(md_file),
        article_title="Test Article - Comments",
        breadcrumb_path=["News 14-03-2026", "Hacker News"],
        source_config=source_config,
        html_subfolder=True,
    )

    assert isinstance(result, str)
    assert len(result) > 100


# ---------------------------------------------------------------------------
# URL truncation
# ---------------------------------------------------------------------------

def test_source_url_truncated_in_html(tmp_path, generator) -> None:
    """URLs longer than 80 chars must be truncated in anchor text while
    keeping the full href intact."""
    long_url = "https://example.com/" + "a" * 90
    md_content = f"# Article\n\n**Source URL:** [{long_url}]({long_url})\n\nBody."
    md_file = tmp_path / "article.md"
    md_file.write_text(md_content, encoding="utf-8")

    source_config = {"template": {"variant": "article-no-comments"}}
    result = generator.generate_article_html_from_template(
        markdown_path=str(md_file),
        article_title="Article",
        breadcrumb_path=["News 14-03-2026", "Example"],
        source_config=source_config,
        html_subfolder=True,
    )

    # Full URL must still be in href
    assert long_url in result
    # Anchor text must be truncated (not the full long URL as visible text)
    assert "..." in result
