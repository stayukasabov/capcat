#!/usr/bin/env python3
"""
TDD Tests for list command functionality.

Test-Driven Development approach:
1. RED: Write failing tests
2. GREEN: Implement minimal code to pass
3. REFACTOR: Improve implementation

Testing Requirements (from BUGS-CRITICAL.md):
- list sources: Shows categorized source list (TECH:, NEWS:, etc.)
- list bundles: Shows bundle information with sources
- list (all): Shows both sources and bundles
"""

import subprocess
import sys
import os
from pathlib import Path
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli import list_sources_and_bundles, get_available_sources, get_available_bundles


class TestListSourcesCommand(unittest.TestCase):
    """Test suite for 'list sources' command."""

    def test_list_sources_produces_output(self):
        """
        RED TEST: Verify list_sources_and_bundles() produces actual output.

        Current behavior: Prints "Listing sources and bundles..."
        Expected behavior: Prints categorized source list
        """
        # Capture stdout
        captured_output = StringIO()

        with patch('sys.stdout', captured_output):
            list_sources_and_bundles(what='sources')

        output = captured_output.getvalue()

        # Should NOT be the stub message
        self.assertNotEqual(output.strip(), "Listing sources and bundles...")

        # Should contain actual content
        self.assertGreater(len(output), 50,
            "Output should contain more than just a message")

    def test_list_sources_contains_categories(self):
        """
        RED TEST: Verify output contains category headers.

        Expected categories: TECH, NEWS, SCIENCE, etc.
        """
        captured_output = StringIO()

        with patch('sys.stdout', captured_output):
            list_sources_and_bundles(what='sources')

        output = captured_output.getvalue()

        # Should contain at least one category header
        # Categories are uppercase with colon
        self.assertTrue(
            any(category in output for category in ['TECH:', 'NEWS:', 'SCIENCE:', 'OTHER:']),
            f"Output should contain category headers. Got: {output[:200]}"
        )

    def test_list_sources_contains_source_ids(self):
        """
        RED TEST: Verify output contains actual source IDs.

        Expected format: "  - source_id    Display Name"
        """
        captured_output = StringIO()

        with patch('sys.stdout', captured_output):
            list_sources_and_bundles(what='sources')

        output = captured_output.getvalue()

        # Get known sources
        sources = get_available_sources()

        # Should contain at least one source ID
        source_found = False
        for source_id in list(sources.keys())[:3]:  # Check first 3 sources
            if source_id in output:
                source_found = True
                break

        self.assertTrue(source_found,
            f"Output should contain source IDs. Got: {output[:200]}")

    def test_list_sources_shows_total_count(self):
        """
        RED TEST: Verify output shows total source count.

        Expected format: "Total: N sources"
        """
        captured_output = StringIO()

        with patch('sys.stdout', captured_output):
            list_sources_and_bundles(what='sources')

        output = captured_output.getvalue()

        # Should contain total count
        self.assertIn('Total:', output,
            "Output should show total source count")

    def test_list_sources_format_matches_documentation(self):
        """
        RED TEST: Verify output format matches docs/quick-start.md:142-147.

        Expected format:
        TECH:
          - hn             Hacker News
          - lb             Lobsters
        """
        captured_output = StringIO()

        with patch('sys.stdout', captured_output):
            list_sources_and_bundles(what='sources')

        output = captured_output.getvalue()

        # Should use "  - " prefix for sources
        self.assertIn('  - ', output,
            "Sources should be prefixed with '  - '")

        # Should have category headers (uppercase, followed by colon)
        lines = output.split('\n')
        category_headers = [line for line in lines if line.strip() and
                           line.strip().endswith(':') and
                           line.strip().isupper()]

        self.assertGreater(len(category_headers), 0,
            "Should have at least one category header")


class TestListBundlesCommand(unittest.TestCase):
    """Test suite for 'list bundles' command."""

    def test_list_bundles_produces_output(self):
        """
        RED TEST: Verify list bundles produces actual output.
        """
        captured_output = StringIO()

        with patch('sys.stdout', captured_output):
            list_sources_and_bundles(what='bundles')

        output = captured_output.getvalue()

        # Should NOT be the stub message
        self.assertNotEqual(output.strip(), "Listing sources and bundles...")

        # Should contain actual content
        self.assertGreater(len(output), 50)

    def test_list_bundles_contains_bundle_names(self):
        """
        RED TEST: Verify output contains bundle names.

        Expected bundles: tech, news, science, ai, sports
        """
        captured_output = StringIO()

        with patch('sys.stdout', captured_output):
            list_sources_and_bundles(what='bundles')

        output = captured_output.getvalue().lower()

        # Get known bundles
        bundles = get_available_bundles()

        # Should contain at least one bundle name
        bundle_found = False
        for bundle_id in list(bundles.keys())[:3]:
            if bundle_id in output:
                bundle_found = True
                break

        self.assertTrue(bundle_found,
            f"Output should contain bundle names. Got: {output[:200]}")

    def test_list_bundles_shows_sources_in_bundle(self):
        """
        RED TEST: Verify bundles show their sources.

        Expected format: "Sources: source1, source2, ..."
        """
        captured_output = StringIO()

        with patch('sys.stdout', captured_output):
            list_sources_and_bundles(what='bundles')

        output = captured_output.getvalue()

        # Should show sources for bundles
        self.assertIn('Sources:', output,
            "Should show sources for each bundle")


class TestListAllCommand(unittest.TestCase):
    """Test suite for 'list' command (both sources and bundles)."""

    def test_list_all_shows_sources(self):
        """
        RED TEST: Verify 'list all' shows sources section.
        """
        captured_output = StringIO()

        with patch('sys.stdout', captured_output):
            list_sources_and_bundles(what='all')

        output = captured_output.getvalue()

        # Should contain sources section
        self.assertIn('Available Sources', output,
            "Should show sources section")

    def test_list_all_shows_bundles(self):
        """
        RED TEST: Verify 'list all' shows bundles section.
        """
        captured_output = StringIO()

        with patch('sys.stdout', captured_output):
            list_sources_and_bundles(what='all')

        output = captured_output.getvalue()

        # Should contain bundles section
        self.assertIn('Available Bundles', output,
            "Should show bundles section")


class TestListCommandCLI(unittest.TestCase):
    """Integration tests for CLI command execution."""

    def test_cli_list_sources_exits_cleanly(self):
        """
        RED TEST: Verify CLI command exits with code 0.
        """
        result = subprocess.run(
            ['./capcat', 'list', 'sources'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertEqual(result.returncode, 0,
            f"Command should exit cleanly. stderr: {result.stderr}")

    def test_cli_list_sources_output_format(self):
        """
        RED TEST: Verify CLI output matches expected format.
        """
        result = subprocess.run(
            ['./capcat', 'list', 'sources'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        output = result.stdout

        # Should contain category headers
        self.assertTrue(
            any(cat in output for cat in ['TECH:', 'NEWS:', 'SCIENCE:']),
            f"Should contain categories. Got: {output[:200]}"
        )

        # Should NOT be stub message
        self.assertNotIn('Listing sources and bundles...', output,
            "Should not be stub message")


class TestListCommandEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_list_with_no_sources(self):
        """
        RED TEST: Verify graceful handling when no sources available.
        """
        captured_output = StringIO()

        # Mock empty sources
        with patch('cli.get_available_sources', return_value={}):
            with patch('sys.stdout', captured_output):
                list_sources_and_bundles(what='sources')

        output = captured_output.getvalue()

        # Should indicate no sources found
        self.assertIn('0', output,
            "Should indicate zero sources")

    def test_list_sources_handles_missing_category(self):
        """
        RED TEST: Verify handling of sources without category.
        """
        # Mock sources with missing category
        mock_sources = {'test_source': 'Test Source'}
        mock_registry = MagicMock()
        mock_config = MagicMock()
        mock_config.category = None
        mock_registry.get_source_config.return_value = mock_config

        captured_output = StringIO()

        with patch('cli.get_available_sources', return_value=mock_sources):
            with patch('core.source_system.source_registry.get_source_registry',
                      return_value=mock_registry):
                with patch('sys.stdout', captured_output):
                    list_sources_and_bundles(what='sources')

        output = captured_output.getvalue()

        # Should still produce output (possibly under OTHER category)
        self.assertGreater(len(output), 20,
            "Should handle sources without category")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
