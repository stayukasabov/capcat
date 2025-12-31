#!/usr/bin/env python3
"""
TDD Test Suite for Index Filename Detection
Tests the logic for determining correct index filename (index.html vs news.html)
based on output directory structure (batch vs custom --output).
"""

import pytest
import tempfile
from pathlib import Path
from core.html_post_processor import HTMLPostProcessor


class TestIndexFilenameDetection:
    """Test suite for index filename detection logic."""

    def setup_method(self):
        """Setup test fixtures."""
        self.processor = HTMLPostProcessor()

    def test_batch_mode_standard_news_folder(self):
        """Batch mode: news_DD-MM-YYYY structure should use news.html"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create standard batch structure: news_23-12-2025/Source_Name/Article/
            root = Path(tmpdir) / "news_23-12-2025" / "Hacker News" / "Test Article"
            root.mkdir(parents=True)

            output_mode = self.processor._detect_output_mode(root)
            assert output_mode == "batch", "Should detect batch mode for news_DD-MM-YYYY"

            index_filename = self.processor._get_index_filename(output_mode)
            assert index_filename == "news.html", "Batch mode should use news.html"

    def test_custom_output_mode(self):
        """Custom --output mode: non-standard directories should use index.html"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create custom output structure: Newstest/Article/
            root = Path(tmpdir) / "Newstest" / "Test Article"
            root.mkdir(parents=True)

            output_mode = self.processor._detect_output_mode(root)
            assert output_mode == "custom", "Should detect custom mode for non-standard dirs"

            index_filename = self.processor._get_index_filename(output_mode)
            assert index_filename == "index.html", "Custom mode should use index.html"

    def test_batch_mode_source_folder_pattern(self):
        """Batch mode: source_DD-MM-YYYY pattern should use news.html"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source-specific batch structure: hn_23-12-2025/Article/
            root = Path(tmpdir) / "hn_23-12-2025" / "Test Article"
            root.mkdir(parents=True)

            output_mode = self.processor._detect_output_mode(root)
            assert output_mode == "batch", "Should detect batch mode for source_DD-MM-YYYY"

            index_filename = self.processor._get_index_filename(output_mode)
            assert index_filename == "news.html", "Batch mode should use news.html"

    def test_capcats_folder_uses_index(self):
        """Capcats folder should use index.html"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Capcats structure: Capcats/cc_DD-MM-YYYY-Article/
            root = Path(tmpdir) / "Capcats" / "cc_23-12-2025-Test"
            root.mkdir(parents=True)

            output_mode = self.processor._detect_output_mode(root)
            assert output_mode == "custom", "Capcats should be detected as custom mode"

            index_filename = self.processor._get_index_filename(output_mode)
            assert index_filename == "index.html", "Capcats should use index.html"

    def test_deeply_nested_custom_output(self):
        """Deep custom paths should still detect as custom mode"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create deeply nested custom structure
            root = Path(tmpdir) / "MyArchive" / "Tech" / "2025" / "Article"
            root.mkdir(parents=True)

            output_mode = self.processor._detect_output_mode(root)
            assert output_mode == "custom", "Deep custom paths should be custom mode"

            index_filename = self.processor._get_index_filename(output_mode)
            assert index_filename == "index.html", "Custom paths should use index.html"

    def test_get_index_filename_batch(self):
        """Direct test: _get_index_filename returns news.html for batch"""
        index_filename = self.processor._get_index_filename("batch")
        assert index_filename == "news.html"

    def test_get_index_filename_custom(self):
        """Direct test: _get_index_filename returns index.html for custom"""
        index_filename = self.processor._get_index_filename("custom")
        assert index_filename == "index.html"

    def test_get_index_filename_defaults_to_index(self):
        """Unknown modes should default to index.html for safety"""
        index_filename = self.processor._get_index_filename("unknown")
        assert index_filename == "index.html"


class TestTemplateContextIndexFilename:
    """Test that index_filename is passed to template context."""

    def setup_method(self):
        """Setup test fixtures."""
        from core.html_generator import HTMLGenerator
        self.generator = HTMLGenerator()

    def test_template_context_includes_index_filename(self):
        """Template context should include index_filename variable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test markdown file
            md_path = Path(tmpdir) / "test.md"
            md_path.write_text("# Test Article\n\nContent here.")

            # Mock source config
            source_config = {"template": {"variant": "article-no-comments"}}

            # Generate HTML (this will call template renderer)
            # We need to check if index_filename is in context
            # This test verifies the integration point
            html_output = self.generator.generate_article_html_from_template(
                str(md_path),
                "Test Article",
                ["Test"],
                source_config,
                html_subfolder=True,
                html_output_path=str(tmpdir),
            )

            # The HTML should contain either news.html or index.html in navigation
            assert "index-link" in html_output, "Should have index link in output"
            # This will pass when implementation is complete


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
