"""Tests for Obsidian wikilink injection."""
import pytest
from pathlib import Path
from capcat.core.storage_manager import inject_comments_wikilink
from capcat.core.streamlined_comment_processor import create_optimized_comment_processor


def _make_article(folder: Path, stem: str, content: str) -> Path:
    """Write a .md file to folder and return its path."""
    p = folder / f"{stem}.md"
    p.write_text(content, encoding="utf-8")
    return p


def test_inject_adds_wikilink_at_top(tmp_path):
    """Line 1 of article.md becomes the comments wikilink after injection."""
    _make_article(tmp_path, "My-Article", "# My Article\n\nSome content.\n")
    inject_comments_wikilink(str(tmp_path), "My-Article-Comments")
    lines = (tmp_path / "My-Article.md").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "→ [[My-Article-Comments|Comments]]"


def test_inject_adds_wikilink_at_bottom(tmp_path):
    """Last non-blank line of article.md becomes the comments wikilink."""
    _make_article(tmp_path, "My-Article", "# My Article\n\nSome content.\n")
    inject_comments_wikilink(str(tmp_path), "My-Article-Comments")
    lines = [l for l in (tmp_path / "My-Article.md").read_text(encoding="utf-8").splitlines() if l.strip()]
    assert lines[-1] == "→ [[My-Article-Comments|Comments]]"


def test_inject_uses_exact_filename_stem(tmp_path):
    """Wikilink stem matches the actual .md file stem on disk."""
    _make_article(tmp_path, "Exact-Stem-Here", "# Title\n\nBody.\n")
    inject_comments_wikilink(str(tmp_path), "Exact-Stem-Here-Comments")
    content = (tmp_path / "Exact-Stem-Here.md").read_text(encoding="utf-8")
    assert "[[Exact-Stem-Here-Comments|Comments]]" in content


def test_inject_returns_false_if_no_article_md(tmp_path):
    """Returns False gracefully when folder contains no .md file."""
    result = inject_comments_wikilink(str(tmp_path), "Some-Comments")
    assert result is False


def test_inject_idempotent_on_second_call(tmp_path):
    """Calling inject twice does not duplicate the top wikilink."""
    _make_article(tmp_path, "My-Article", "# My Article\n\nSome content.\n")
    inject_comments_wikilink(str(tmp_path), "My-Article-Comments")
    inject_comments_wikilink(str(tmp_path), "My-Article-Comments")
    content = (tmp_path / "My-Article.md").read_text(encoding="utf-8")
    assert content.count("→ [[My-Article-Comments|Comments]]") == 2  # one top, one bottom


def _make_fake_comments():
    """Return a minimal list of comment dicts as produce by process_comments_flattened."""
    return [{"user": "bob", "user_link": "https://example.com/bob", "text": "Great article!"}]


def test_comments_md_has_article_wikilink_top(tmp_path):
    """generate_inline_comments_markdown prepends ← [[...|Article]] when article_folder_path given."""
    _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")
    processor = create_optimized_comment_processor(max_comments=None)
    md = processor.generate_inline_comments_markdown(
        _make_fake_comments(), "My Article", "https://example.com", str(tmp_path)
    )
    lines = md.splitlines()
    assert lines[0] == "← [[My-Article|Article]]"


def test_comments_md_has_article_wikilink_bottom(tmp_path):
    """generate_inline_comments_markdown appends ← [[...|Article]] at the end."""
    _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")
    processor = create_optimized_comment_processor(max_comments=None)
    md = processor.generate_inline_comments_markdown(
        _make_fake_comments(), "My Article", "https://example.com", str(tmp_path)
    )
    non_blank = [l for l in md.splitlines() if l.strip()]
    assert non_blank[-1] == "← [[My-Article|Article]]"


# ---------------------------------------------------------------------------
# Task 4 integration tests: unified_source_processor injection wiring
# ---------------------------------------------------------------------------

def _write_comments_file(folder: Path, article_stem: str) -> Path:
    """Write a minimal comments .md file and return its path."""
    p = folder / f"{article_stem}-Comments.md"
    p.write_text("# Comments\n\nSome comment.\n", encoding="utf-8")
    return p


def test_no_injection_when_fetch_comments_returns_false(tmp_path):
    """When fetch_comments returns False, article.md must not contain '→ [['."""
    from unittest.mock import MagicMock
    from capcat.core.unified_source_processor import UnifiedSourceProcessor

    article_path = _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")

    source = MagicMock()
    source.fetch_article_content.return_value = (True, str(tmp_path))
    source.config.has_comments = True
    source.fetch_comments.return_value = False

    article = MagicMock()
    article.title = "My Article"
    article.comment_url = "https://example.com/comments"

    usp = UnifiedSourceProcessor()
    usp._process_single_article_new_system(source, article, str(tmp_path), download_files=False)

    content = article_path.read_text(encoding="utf-8")
    assert "→ [[" not in content


def test_injection_called_when_fetch_comments_returns_true(tmp_path):
    """When fetch_comments returns True and comments file exists, article.md gets wikilink."""
    from unittest.mock import MagicMock
    from capcat.core.unified_source_processor import UnifiedSourceProcessor

    article_path = _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")
    _write_comments_file(tmp_path, "My-Article")

    source = MagicMock()
    source.fetch_article_content.return_value = (True, str(tmp_path))
    source.config.has_comments = True
    source.fetch_comments.return_value = True

    article = MagicMock()
    article.title = "My Article"
    article.comment_url = "https://example.com/comments"

    usp = UnifiedSourceProcessor()
    usp._process_single_article_new_system(source, article, str(tmp_path), download_files=False)

    content = article_path.read_text(encoding="utf-8")
    assert "→ [[My-Article-Comments|Comments]]" in content


# ---------------------------------------------------------------------------
# inject_frontmatter tests
# ---------------------------------------------------------------------------

from capcat.core.storage_manager import inject_frontmatter
import yaml as _yaml


def test_frontmatter_prepended_to_plain_article(tmp_path):
    """inject_frontmatter prepends --- block before existing content."""
    md = tmp_path / "My-Article.md"
    md.write_text("# My Article\n\nBody.\n", encoding="utf-8")
    inject_frontmatter(str(md), {"title": "My Article", "url": "https://example.com"})
    content = md.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "title:" in content
    assert "# My Article" in content


def test_frontmatter_is_valid_yaml(tmp_path):
    """The block between the --- delimiters parses as valid YAML."""
    md = tmp_path / "My-Article.md"
    md.write_text("# My Article\n\nBody.\n", encoding="utf-8")
    inject_frontmatter(
        str(md),
        {
            "title": "My Article: A Test",
            "url": "https://example.com/article",
            "source": "Hacker News",
            "source_code": "hn",
            "category": "tech",
            "captured": "2026-03-31",
            "tags": ["hn", "tech"],
        },
    )
    content = md.read_text(encoding="utf-8")
    lines = content.splitlines()
    end = lines.index("---", 1)
    parsed = _yaml.safe_load("\n".join(lines[1:end]))
    assert parsed["title"] == "My Article: A Test"
    assert parsed["source_code"] == "hn"
    assert "hn" in parsed["tags"]


def test_frontmatter_omits_none_date(tmp_path):
    """When date is None it must not appear in the frontmatter."""
    md = tmp_path / "My-Article.md"
    md.write_text("# My Article\n\nBody.\n", encoding="utf-8")
    inject_frontmatter(str(md), {"title": "My Article", "url": "https://x.com", "date": None})
    content = md.read_text(encoding="utf-8")
    assert "date:" not in content


def test_frontmatter_idempotent(tmp_path):
    """Calling inject_frontmatter twice does not double the --- block."""
    md = tmp_path / "My-Article.md"
    md.write_text("# My Article\n\nBody.\n", encoding="utf-8")
    meta = {"title": "My Article", "url": "https://x.com"}
    inject_frontmatter(str(md), meta)
    inject_frontmatter(str(md), meta)
    content = md.read_text(encoding="utf-8")
    # Exactly two lines that are solely '---'
    fence_lines = [l for l in content.splitlines() if l == "---"]
    assert len(fence_lines) == 2


def test_frontmatter_above_wikilink(tmp_path):
    """Frontmatter is the first block even when wikilink was injected first."""
    from capcat.core.storage_manager import inject_comments_wikilink
    _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")
    inject_comments_wikilink(str(tmp_path), "My-Article-Comments")
    article_md = tmp_path / "My-Article.md"
    inject_frontmatter(str(article_md), {"title": "My Article", "url": "https://x.com"})
    lines = article_md.read_text(encoding="utf-8").splitlines()
    # Line 0 must be the opening fence
    assert lines[0] == "---"
    # Wikilink must appear somewhere after the closing fence
    content = article_md.read_text(encoding="utf-8")
    closing = content.index("---\n\n")
    wikilink_pos = content.index("→ [[My-Article-Comments|Comments]]")
    assert wikilink_pos > closing


def test_frontmatter_returns_false_if_file_missing(tmp_path):
    """Returns False gracefully when the target file does not exist."""
    result = inject_frontmatter(str(tmp_path / "nonexistent.md"), {"title": "x"})
    assert result is False


# ---------------------------------------------------------------------------
# Frontmatter wiring integration tests
# ---------------------------------------------------------------------------

def test_article_gets_frontmatter_after_processing(tmp_path):
    """After _process_single_article_new_system, article.md has YAML frontmatter."""
    from unittest.mock import MagicMock
    from capcat.core.unified_source_processor import UnifiedSourceProcessor
    import yaml as _yaml

    _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")

    source = MagicMock()
    source.fetch_article_content.return_value = (True, str(tmp_path))
    source.config.has_comments = False
    source.config.name = "hn"
    source.config.display_name = "Hacker News"
    source.config.category = "tech"

    article = MagicMock()
    article.title = "My Article"
    article.url = "https://example.com/article"
    article.comment_url = None
    article.published_date = "2026-03-28"
    article.tags = []

    usp = UnifiedSourceProcessor()
    usp._process_single_article_new_system(source, article, str(tmp_path), download_files=False)

    content = (tmp_path / "My-Article.md").read_text(encoding="utf-8")
    assert content.startswith("---\n")
    lines = content.splitlines()
    end = lines.index("---", 1)
    fm = _yaml.safe_load("\n".join(lines[1:end]))
    assert fm["source_code"] == "hn"
    assert fm["category"] == "tech"
    assert fm["title"] == "My Article"
    assert fm["url"] == "https://example.com/article"
    assert "captured" in fm


def test_article_frontmatter_omits_none_date(tmp_path):
    """When published_date is None, 'date' key is absent from frontmatter."""
    from unittest.mock import MagicMock
    from capcat.core.unified_source_processor import UnifiedSourceProcessor

    _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")

    source = MagicMock()
    source.fetch_article_content.return_value = (True, str(tmp_path))
    source.config.has_comments = False
    source.config.name = "lb"
    source.config.display_name = "Lobsters"
    source.config.category = "tech"

    article = MagicMock()
    article.title = "My Article"
    article.url = "https://lobste.rs/s/abc"
    article.comment_url = None
    article.published_date = None
    article.tags = []

    usp = UnifiedSourceProcessor()
    usp._process_single_article_new_system(source, article, str(tmp_path), download_files=False)

    content = (tmp_path / "My-Article.md").read_text(encoding="utf-8")
    assert "date:" not in content


def test_comments_get_frontmatter_after_processing(tmp_path):
    """Comments.md gets YAML frontmatter with comments tag and source_code."""
    from unittest.mock import MagicMock
    from capcat.core.unified_source_processor import UnifiedSourceProcessor
    import yaml as _yaml

    _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")
    _write_comments_file(tmp_path, "My-Article")

    source = MagicMock()
    source.fetch_article_content.return_value = (True, str(tmp_path))
    source.config.has_comments = True
    source.config.name = "hn"
    source.config.display_name = "Hacker News"
    source.config.category = "tech"
    source.fetch_comments.return_value = True

    article = MagicMock()
    article.title = "My Article"
    article.url = "https://news.ycombinator.com/item?id=123"
    article.comment_url = "https://news.ycombinator.com/item?id=123"
    article.published_date = None
    article.tags = []

    usp = UnifiedSourceProcessor()
    usp._process_single_article_new_system(source, article, str(tmp_path), download_files=False)

    content = (tmp_path / "My-Article-Comments.md").read_text(encoding="utf-8")
    assert content.startswith("---\n")
    lines = content.splitlines()
    end = lines.index("---", 1)
    fm = _yaml.safe_load("\n".join(lines[1:end]))
    assert "comments" in fm["tags"]
    assert fm["source_code"] == "hn"


def test_frontmatter_above_wikilink_in_integration(tmp_path):
    """After full processing, frontmatter is above the wikilink in article.md."""
    from unittest.mock import MagicMock
    from capcat.core.unified_source_processor import UnifiedSourceProcessor

    _make_article(tmp_path, "My-Article", "# My Article\n\nBody.\n")
    _write_comments_file(tmp_path, "My-Article")

    source = MagicMock()
    source.fetch_article_content.return_value = (True, str(tmp_path))
    source.config.has_comments = True
    source.config.name = "hn"
    source.config.display_name = "Hacker News"
    source.config.category = "tech"
    source.fetch_comments.return_value = True

    article = MagicMock()
    article.title = "My Article"
    article.url = "https://example.com"
    article.comment_url = "https://example.com/comments"
    article.published_date = None
    article.tags = []

    usp = UnifiedSourceProcessor()
    usp._process_single_article_new_system(source, article, str(tmp_path), download_files=False)

    content = (tmp_path / "My-Article.md").read_text(encoding="utf-8")
    assert content.startswith("---\n")
    closing_fence = content.index("---\n\n")
    wikilink_pos = content.find("→ [[")
    assert wikilink_pos > closing_fence, "Wikilink must appear after closing --- fence"
