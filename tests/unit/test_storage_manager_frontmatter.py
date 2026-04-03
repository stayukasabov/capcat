"""Tests for update_frontmatter_pdfs in storage_manager."""


class TestUpdateFrontmatterPdfs:

    def test_adds_pdfs_key_to_existing_frontmatter(self, tmp_path):
        """pdfs key must be added when frontmatter exists but has no pdfs key."""
        md = tmp_path / "Article.md"
        md.write_text(
            "---\ntitle: Test Article\nsource: hn\n---\n\n# Test Article\n\nBody.\n"
        )

        from capcat.core.storage_manager import update_frontmatter_pdfs
        result = update_frontmatter_pdfs(str(md), ["files/paper.pdf"])

        assert result is True
        content = md.read_text()
        assert "pdfs:" in content
        assert "files/paper.pdf" in content

    def test_replaces_existing_pdfs_key(self, tmp_path):
        """pdfs key must be replaced when it already exists."""
        md = tmp_path / "Article.md"
        md.write_text(
            "---\ntitle: Test\npdfs:\n- files/old.pdf\n---\n\n# Test\n\nBody.\n"
        )

        from capcat.core.storage_manager import update_frontmatter_pdfs
        update_frontmatter_pdfs(str(md), ["files/new.pdf"])

        content = md.read_text()
        assert "files/new.pdf" in content
        assert "files/old.pdf" not in content

    def test_preserves_body_after_update(self, tmp_path):
        """Article body must be unchanged after frontmatter update."""
        md = tmp_path / "Article.md"
        md.write_text(
            "---\ntitle: Test\n---\n\n# Test\n\nOriginal body content.\n"
        )

        from capcat.core.storage_manager import update_frontmatter_pdfs
        update_frontmatter_pdfs(str(md), ["files/paper.pdf"])

        assert "Original body content." in md.read_text()

    def test_noop_when_pdf_paths_empty(self, tmp_path):
        """Must return True and not modify file when pdf_paths is empty."""
        md = tmp_path / "Article.md"
        original = "---\ntitle: Test\n---\n\n# Test\n\nBody.\n"
        md.write_text(original)

        from capcat.core.storage_manager import update_frontmatter_pdfs
        result = update_frontmatter_pdfs(str(md), [])

        assert result is True
        assert md.read_text() == original

    def test_noop_when_no_frontmatter(self, tmp_path):
        """Must return False and not modify file when no frontmatter block exists."""
        md = tmp_path / "Article.md"
        original = "# Test\n\nNo frontmatter here.\n"
        md.write_text(original)

        from capcat.core.storage_manager import update_frontmatter_pdfs
        result = update_frontmatter_pdfs(str(md), ["files/paper.pdf"])

        assert result is False
        assert md.read_text() == original

    def test_returns_false_when_file_not_found(self, tmp_path):
        """Must return False without raising when file does not exist."""
        from capcat.core.storage_manager import update_frontmatter_pdfs
        result = update_frontmatter_pdfs(str(tmp_path / "missing.md"), ["files/paper.pdf"])
        assert result is False
