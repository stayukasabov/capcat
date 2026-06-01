"""Regression: downloaded images must appear in markdown when content extraction
drops image references.

Bug: GenericArticleFetcher downloads images into /images/ but the HTML-to-markdown
conversion sometimes loses the ![alt](url) references (e.g. images inside sections
that get filtered). The final markdown has no image references even though the files
exist on disk.

Fix: after the final markdown is assembled, if it contains no image references but
downloaded images exist, append an "Article Images" section referencing them.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest


def _write_article_content(article_dir: Path, content: str, images: list[str]):
    """Helper to create a realistic article folder with images but no image refs."""
    article_dir.mkdir(parents=True, exist_ok=True)
    md_file = article_dir / "Test-Article.md"
    md_file.write_text(content, encoding="utf-8")

    if images:
        img_dir = article_dir / "images"
        img_dir.mkdir(exist_ok=True)
        for img_name in images:
            (img_dir / img_name).write_bytes(b"\x89PNG fake")

    return md_file


def test_orphan_images_appended_when_no_refs_in_markdown(tmp_path):
    """When markdown has no ![...] refs but images/ has files, append them."""
    from capcat.core.article_fetcher import _append_orphan_images

    article_dir = tmp_path / "article"
    md = _write_article_content(
        article_dir,
        "# Title\n\nSome text with no image references.\n",
        ["Hero_Image_abc123.png", "Diagram_def456.jpg"],
    )

    content = md.read_text(encoding="utf-8")
    result = _append_orphan_images(content, str(article_dir))

    assert "## Article Images" in result
    assert "![Hero Image Abc123](images/Hero_Image_abc123.png)" in result
    assert "![Diagram Def456](images/Diagram_def456.jpg)" in result


def test_no_orphan_section_when_images_already_referenced(tmp_path):
    """When markdown already has image references, do NOT append duplicates."""
    from capcat.core.article_fetcher import _append_orphan_images

    article_dir = tmp_path / "article"
    md = _write_article_content(
        article_dir,
        "# Title\n\n![hero](images/Hero_Image_abc123.png)\n\nText.\n",
        ["Hero_Image_abc123.png"],
    )

    content = md.read_text(encoding="utf-8")
    result = _append_orphan_images(content, str(article_dir))

    assert "## Article Images" not in result
    assert result == content


def test_no_orphan_section_when_no_images_folder(tmp_path):
    """When there is no images/ folder, nothing is appended."""
    from capcat.core.article_fetcher import _append_orphan_images

    article_dir = tmp_path / "article"
    article_dir.mkdir()
    content = "# Title\n\nText only.\n"

    result = _append_orphan_images(content, str(article_dir))
    assert result == content


def test_orphan_images_skips_non_image_files(tmp_path):
    """Only image extensions should be included, not .txt or .json."""
    from capcat.core.article_fetcher import _append_orphan_images

    article_dir = tmp_path / "article"
    img_dir = article_dir / "images"
    img_dir.mkdir(parents=True)
    (img_dir / "photo.png").write_bytes(b"\x89PNG")
    (img_dir / "metadata.json").write_text("{}")
    (img_dir / "notes.txt").write_text("notes")

    content = "# Title\n\nNo images.\n"
    result = _append_orphan_images(content, str(article_dir))

    assert "photo.png" in result
    assert "metadata.json" not in result
    assert "notes.txt" not in result
