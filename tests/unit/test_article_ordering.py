"""Test that HTML generator sorts source-level articles by frontmatter date."""
import tempfile
from pathlib import Path

import pytest


class TestArticleOrdering:
    """HTML generator should sort articles by published date, newest first."""

    def _create_article_dir(self, parent: Path, name: str, date_str: str = None):
        """Create a mock article directory with frontmatter containing a date."""
        article_dir = parent / name
        article_dir.mkdir(parents=True)
        md_path = article_dir / f"{name}.md"

        frontmatter_lines = [
            "---",
            f"title: {name}",
            f"url: https://example.com/{name}",
        ]
        if date_str:
            frontmatter_lines.append(f"date: '{date_str}'")
        frontmatter_lines.append("captured: '2026-06-12'")
        frontmatter_lines.append("---")
        frontmatter_lines.append("")
        frontmatter_lines.append(f"# {name}")

        md_path.write_text("\n".join(frontmatter_lines), encoding="utf-8")
        return article_dir

    def test_articles_sorted_newest_first(self):
        """Articles with frontmatter dates sort newest first."""
        from capcat.htmlgen.generator import ArticleHTMLGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "Test-Source_12-06-2026"
            source_dir.mkdir()

            # Create articles in wrong chronological order
            self._create_article_dir(source_dir, "Old-Article", "2026-03-01 00:00:00+00:00")
            self._create_article_dir(source_dir, "Newest-Article", "2026-06-10 00:00:00+00:00")
            self._create_article_dir(source_dir, "Middle-Article", "2026-05-15 00:00:00+00:00")

            generator = ArticleHTMLGenerator()
            html = generator._generate_directory_listing(str(source_dir), is_root_level=False)

            # Find article order in generated HTML
            oldest_pos = html.find("Old-Article")
            middle_pos = html.find("Middle-Article")
            newest_pos = html.find("Newest-Article")

            assert newest_pos < middle_pos < oldest_pos, (
                f"Expected newest first. Positions: newest={newest_pos}, "
                f"middle={middle_pos}, oldest={oldest_pos}"
            )

    def test_articles_without_dates_sort_after_dated(self):
        """Articles without dates appear after dated articles."""
        from capcat.htmlgen.generator import ArticleHTMLGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "Test-Source_12-06-2026"
            source_dir.mkdir()

            self._create_article_dir(source_dir, "Dated-Article", "2026-06-01 00:00:00+00:00")
            self._create_article_dir(source_dir, "No-Date-Article", None)

            generator = ArticleHTMLGenerator()
            html = generator._generate_directory_listing(str(source_dir), is_root_level=False)

            dated_pos = html.find("Dated-Article")
            undated_pos = html.find("No-Date-Article")

            assert dated_pos < undated_pos, (
                f"Dated articles should appear before undated. "
                f"dated={dated_pos}, undated={undated_pos}"
            )
