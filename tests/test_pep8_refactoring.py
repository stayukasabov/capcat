#!/usr/bin/env python3
"""
TDD Tests for PEP 8 Refactoring - Sprint 2.

Following red-green-refactor cycle:
1. RED: Write tests for current functionality
2. GREEN: Verify tests pass with current code
3. REFACTOR: Fix PEP 8 violations while keeping tests green
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCapcatFunctions:
    """Test suite for capcat.py main functions."""

    def test_process_sources_returns_dict_structure(self):
        """Test process_sources returns expected dict structure."""
        # ARRANGE
        from capcat import process_sources

        sources = ["hn"]
        args = Mock()
        args.count = 5
        args.quiet = False
        args.verbose = False
        args.media = False
        config = Mock()
        logger = Mock()

        # ACT
        with patch('capcat.process_source_articles') as mock_process:
            mock_process.return_value = None
            result = process_sources(
                sources, args, config, logger,
                generate_html=False, output_dir="."
            )

        # ASSERT
        assert isinstance(result, dict)
        assert 'successful' in result
        assert 'failed' in result
        assert 'total' in result
        assert result['total'] == len(sources)

    def test_process_sources_handles_single_source_success(self):
        """Test successful processing of single source."""
        # ARRANGE
        from capcat import process_sources

        sources = ["hn"]
        args = Mock(count=5, quiet=False, verbose=False, media=False)
        config = Mock()
        logger = Mock()

        # ACT
        with patch('capcat.process_source_articles') as mock_process:
            mock_process.return_value = None  # Success
            result = process_sources(
                sources, args, config, logger,
                generate_html=False, output_dir="."
            )

        # ASSERT
        assert len(result['successful']) == 1
        assert len(result['failed']) == 0
        assert result['successful'][0] == "hn"

    def test_process_sources_handles_source_failure(self):
        """Test handling of source processing failure."""
        # ARRANGE
        from capcat import process_sources

        sources = ["invalid_source"]
        args = Mock(count=5, quiet=False, verbose=False, media=False)
        config = Mock()
        logger = Mock()

        # ACT
        with patch('capcat.process_source_articles') as mock_process:
            mock_process.side_effect = Exception("Source error")
            result = process_sources(
                sources, args, config, logger,
                generate_html=False, output_dir="."
            )

        # ASSERT
        assert len(result['successful']) == 0
        assert len(result['failed']) == 1
        assert result['failed'][0][0] == "invalid_source"

    def test_process_sources_continues_after_failure(self):
        """Test graceful degradation continues with remaining sources."""
        # ARRANGE
        from capcat import process_sources

        sources = ["fail_source", "success_source"]
        args = Mock(count=5, quiet=False, verbose=False, media=False)
        config = Mock()
        logger = Mock()

        # ACT
        with patch('capcat.process_source_articles') as mock_process:
            # First call fails, second succeeds
            mock_process.side_effect = [
                Exception("Failed"),
                None
            ]
            result = process_sources(
                sources, args, config, logger,
                generate_html=False, output_dir="."
            )

        # ASSERT
        assert len(result['successful']) == 1
        assert len(result['failed']) == 1
        assert result['total'] == 2


class TestScrapeSingleArticle:
    """Test suite for scrape_single_article function."""

    def test_scrape_single_article_returns_tuple(self):
        """Test scrape_single_article returns (bool, str) tuple."""
        # ARRANGE
        from capcat import scrape_single_article

        url = "https://example.com/article"
        output_dir = "."

        # ACT
        with patch('capcat.get_specialized_source_manager') as mock_manager:
            mock_manager.return_value.can_handle_url.return_value = False

            with patch('capcat.ArticleFetcher') as mock_fetcher:
                mock_instance = Mock()
                mock_instance.fetch_article.return_value = (True, ".")
                mock_fetcher.return_value = mock_instance

                result = scrape_single_article(
                    url, output_dir,
                    verbose=False, files=False,
                    generate_html=False, update_mode=False
                )

        # ASSERT
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)

    def test_scrape_single_article_detects_specialized_source(self):
        """Test specialized source detection for Medium/Substack."""
        # ARRANGE
        from capcat import scrape_single_article

        url = "https://medium.com/@user/article"
        output_dir = "."

        # ACT
        with patch('capcat.get_specialized_source_manager') as mock_manager:
            mock_manager.return_value.can_handle_url.return_value = True

            with patch('capcat._scrape_with_specialized_source') as mock_scrape:
                mock_scrape.return_value = (True, "./output")

                result = scrape_single_article(
                    url, output_dir,
                    verbose=False, files=False,
                    generate_html=False, update_mode=False
                )

        # ASSERT
        assert result[0] is True
        mock_scrape.assert_called_once()


class TestPEP8Compliance:
    """Tests to verify PEP 8 compliance after refactoring."""

    def test_line_length_compliance_capcat(self):
        """Verify capcat.py has no lines > 79 chars."""
        # ARRANGE
        capcat_path = Path(__file__).parent.parent / "capcat.py"

        # ACT
        with open(capcat_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        violations = []
        for i, line in enumerate(lines, start=1):
            if len(line.rstrip()) > 79:
                violations.append((i, len(line.rstrip())))

        # ASSERT
        assert len(violations) == 0, (
            f"Found {len(violations)} line length violations in capcat.py:\n"
            f"{violations[:5]}"
        )

    def test_line_length_compliance_cli(self):
        """Verify cli.py has no lines > 79 chars."""
        # ARRANGE
        cli_path = Path(__file__).parent.parent / "cli.py"

        # ACT
        with open(cli_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        violations = []
        for i, line in enumerate(lines, start=1):
            if len(line.rstrip()) > 79:
                violations.append((i, len(line.rstrip())))

        # ASSERT
        assert len(violations) == 0, (
            f"Found {len(violations)} line length violations in cli.py:\n"
            f"{violations[:5]}"
        )

    def test_no_trailing_whitespace(self):
        """Verify no trailing whitespace in refactored files."""
        # ARRANGE
        files_to_check = [
            Path(__file__).parent.parent / "capcat.py",
            Path(__file__).parent.parent / "cli.py",
            Path(__file__).parent.parent / "core" / "config.py",
        ]

        violations = []

        # ACT
        for file_path in files_to_check:
            if not file_path.exists():
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, start=1):
                if line.rstrip() != line.rstrip('\n'):
                    violations.append((str(file_path.name), i))

        # ASSERT
        assert len(violations) == 0, (
            f"Found trailing whitespace: {violations[:5]}"
        )


class TestImportsIntegrity:
    """Test that refactoring preserves import functionality."""

    def test_capcat_imports_successfully(self):
        """Test capcat.py imports without errors."""
        # ACT & ASSERT
        try:
            import capcat
            assert capcat is not None
        except ImportError as e:
            pytest.fail(f"Failed to import capcat: {e}")

    def test_cli_imports_successfully(self):
        """Test cli.py imports without errors."""
        # ACT & ASSERT
        try:
            import cli
            assert cli is not None
        except ImportError as e:
            pytest.fail(f"Failed to import cli: {e}")

    def test_core_modules_import_successfully(self):
        """Test core modules import without errors."""
        # ACT & ASSERT
        modules = [
            'core.config',
            'core.exceptions',
            'core.constants',
            'core.url_utils',
            'core.article_fetcher'
        ]

        for module_name in modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")


class TestFunctionSignatures:
    """Test that function signatures remain unchanged after refactoring."""

    def test_process_sources_signature(self):
        """Verify process_sources function signature is preserved."""
        # ARRANGE
        from capcat import process_sources
        import inspect

        # ACT
        sig = inspect.signature(process_sources)
        params = list(sig.parameters.keys())

        # ASSERT
        assert 'sources' in params
        assert 'args' in params
        assert 'config' in params
        assert 'logger' in params
        assert 'generate_html' in params
        assert 'output_dir' in params

    def test_scrape_single_article_signature(self):
        """Verify scrape_single_article function signature is preserved."""
        # ARRANGE
        from capcat import scrape_single_article
        import inspect

        # ACT
        sig = inspect.signature(scrape_single_article)
        params = list(sig.parameters.keys())

        # ASSERT
        assert 'url' in params
        assert 'output_dir' in params
        assert 'verbose' in params
        assert 'files' in params
        assert 'generate_html' in params
        assert 'update_mode' in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
