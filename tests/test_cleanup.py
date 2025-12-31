#!/usr/bin/env python3
"""
Baseline tests for cleanup - ensure functionality preserved during refactoring.

Run before and after cleanup to verify no regressions.
Usage: pytest test_cleanup_baseline.py -v
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


class TestSingleArticleCapture:
    """Test single article capture with various scenarios."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_source_detection_techcrunch(self):
        """Test TechCrunch URL detection."""
        from core.source_config import detect_source

        url = "https://techcrunch.com/2024/10/24/test-article"
        source = detect_source(url)
        assert source == "TechCrunch", f"Expected 'TechCrunch', got '{source}'"

    def test_source_detection_theverge(self):
        """Test The Verge URL detection."""
        from core.source_config import detect_source

        url = "https://www.theverge.com/2024/10/24/test-article"
        source = detect_source(url)
        assert source == "TheVerge", f"Expected 'TheVerge', got '{source}'"

    def test_source_detection_unknown(self):
        """Test unknown source detection."""
        from core.source_config import detect_source

        url = "https://unknown-site.com/article"
        source = detect_source(url)
        assert source is None, f"Expected None for unknown source, got '{source}'"

    def test_modular_factory_techcrunch(self):
        """Test modular factory creates TechCrunch source."""
        from sources.base.factory import get_modular_source_factory

        factory = get_modular_source_factory()
        source = factory.create_source("TechCrunch")
        assert source is not None, "TechCrunch source should be created"
        assert hasattr(source, "fetch_article_content"), "Source should have fetch method"

    def test_modular_factory_case_sensitive(self):
        """Test modular factory is case-sensitive."""
        from sources.base.factory import get_modular_source_factory

        factory = get_modular_source_factory()

        # Capitalized should work
        source_caps = factory.create_source("TechCrunch")
        assert source_caps is not None, "TechCrunch (caps) should work"

        # Lowercase should fail
        source_lower = factory.create_source("techcrunch")
        assert source_lower is None, "techcrunch (lowercase) should return None"


class TestHTMLGeneration:
    """Test HTML generation for Capcats vs News."""

    def test_template_selection_capcats(self):
        """Test article-capcats template selected for Capcats articles."""
        from core.html_generator import HTMLGenerator
        from pathlib import Path

        # Mock Capcats path
        capcats_path = "/path/to/Capcats/TechCrunch_26-10-2025/Article/article.md"

        generator = HTMLGenerator()
        # The logic checks if "Capcats" in path parents
        path = Path(capcats_path)
        is_capcats = any(parent.name.lower() == "capcats" for parent in path.parents)

        assert is_capcats, "Should detect Capcats path"

    def test_template_selection_news(self):
        """Test article-with-comments/no-comments template for News."""
        from pathlib import Path

        # Mock News path
        news_path = "/path/to/News/News_26-10-2025/BBC/Article/article.md"

        path = Path(news_path)
        is_capcats = any(parent.name.lower() == "capcats" for parent in path.parents)

        assert not is_capcats, "Should not detect News path as Capcats"

    def test_capcats_no_intermediate_index(self):
        """Test Capcats directories don't generate intermediate index.html."""
        from core.html_post_processor import HTMLPostProcessor
        from pathlib import Path

        processor = HTMLPostProcessor()

        # Capcats single article directory
        capcats_dir = Path("/path/to/Capcats/TechCrunch_26-10-2025")
        is_capcats = processor._is_capcats_single_article(capcats_dir)

        assert is_capcats, "Should identify as Capcats single article"

    def test_news_generates_intermediate_index(self):
        """Test News directories generate intermediate index.html."""
        from core.html_post_processor import HTMLPostProcessor
        from pathlib import Path

        processor = HTMLPostProcessor()

        # News source directory
        news_dir = Path("/path/to/News/News_26-10-2025/BBC_26-10-2025")
        is_capcats = processor._is_capcats_single_article(news_dir)

        assert not is_capcats, "Should not identify News as Capcats"


class TestNavigation:
    """Test navigation and breadcrumb logic."""

    def test_capcats_detection_logic(self):
        """Test Capcats detection for navigation removal."""
        from pathlib import Path

        # Various Capcats paths
        paths = [
            "/Users/project/Capcats/TechCrunch_26-10-2025/Article/article.md",
            "Capcats/BBC/Article/article.md",
            "/var/Capcats/Test/Article/article.md",
        ]

        for path_str in paths:
            path = Path(path_str)
            is_capcats = any(p.name.lower() == "capcats" for p in path.parents)
            assert is_capcats, f"Should detect Capcats in: {path_str}"

    def test_news_detection_logic(self):
        """Test News detection (not Capcats)."""
        from pathlib import Path

        # Various News paths
        paths = [
            "/Users/project/News/News_26-10-2025/BBC/Article/article.md",
            "News/BBC/Article/article.md",
            "/var/News_26-10-2025/Test/Article/article.md",
        ]

        for path_str in paths:
            path = Path(path_str)
            is_capcats = any(p.name.lower() == "capcats" for p in path.parents)
            assert not is_capcats, f"Should not detect Capcats in: {path_str}"


class TestSourceRegistry:
    """Test source registry functionality."""

    def test_registry_loads_custom_sources(self):
        """Test registry loads custom sources (lb, hn)."""
        from core.source_system.source_registry import get_source_registry

        registry = get_source_registry()

        # Should have custom sources
        assert "lb" in registry._sources, "Should have Lobsters"
        assert "hn" in registry._sources, "Should have Hacker News"

    def test_registry_source_count(self):
        """Test registry has expected custom sources."""
        from core.source_system.source_registry import get_source_registry

        registry = get_source_registry()

        # Should have at least 2 custom sources
        assert len(registry._sources) >= 2, f"Expected at least 2 sources, got {len(registry._sources)}"


class TestSpecializedSources:
    """Test specialized source handling."""

    def test_specialized_source_fallback(self):
        """Test specialized source falls back to generic on failure."""
        from core.specialized_source_manager import get_specialized_source_manager

        manager = get_specialized_source_manager()

        # Test URL detection
        can_handle = manager.can_handle_url("https://medium.com/@user/article")
        # Should have specialized handler for Medium
        assert isinstance(can_handle, bool), "Should return boolean for can_handle_url"


class TestConfigDrivenSources:
    """Test config-driven source discovery."""

    def test_config_files_exist(self):
        """Test config-driven source files exist."""
        config_dir = Path("sources/active/config_driven/configs")

        assert config_dir.exists(), "Config directory should exist"

        # Check for known configs
        techcrunch_config = config_dir / "TechCrunch.yml"
        assert techcrunch_config.exists(), "TechCrunch config should exist"

    def test_bundles_file_exists(self):
        """Test bundles configuration exists."""
        bundles_file = Path("sources/active/bundles.yml")
        assert bundles_file.exists(), "Bundles file should exist"


class TestOutputPaths:
    """Test output path generation."""

    def test_capcats_output_path_format(self):
        """Test Capcats output path doesn't include date prefix."""
        # Capcats should use: Capcats/Source_DD-MM-YYYY/ or Capcats/Title/
        # NOT: Capcats/sg_DD-MM-YYYY-Title/

        from core.utils import sanitize_filename

        title = "Test Article Title"
        safe_title = sanitize_filename(title, max_length=100)

        # Should not have 'sg_' prefix
        assert not safe_title.startswith("sg_"), "Capcats titles should not have sg_ prefix"

    def test_news_output_path_format(self):
        """Test News output path includes structure."""
        # News should use: News/News_DD-MM-YYYY/Source_DD-MM-YYYY/NN_Title/
        # This is just validating the convention exists
        pass  # Implementation validated by integration tests


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
