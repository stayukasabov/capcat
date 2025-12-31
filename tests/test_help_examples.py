#!/usr/bin/env python3
"""
TDD Tests for CLI help system enhancements.

Requirements:
- All commands should have practical examples
- Examples should use real source/bundle names
- Examples should demonstrate common use cases
- Format should be consistent across commands
"""

import subprocess
import sys
import os
from pathlib import Path
import unittest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli import get_available_sources, get_available_bundles


class TestHelpSystemStructure(unittest.TestCase):
    """Test that help system has proper structure."""

    def test_main_help_has_examples_section(self):
        """
        RED TEST: Main help should have Examples section.
        """
        result = subprocess.run(
            ['./capcat', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertIn('Examples:', result.stdout,
            "Main help should have Examples section")

    def test_single_help_has_examples(self):
        """
        RED TEST: single command help should have examples.
        """
        result = subprocess.run(
            ['./capcat', 'single', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertIn('Examples:', result.stdout,
            "Single command help should have Examples section")

    def test_fetch_help_has_examples(self):
        """
        RED TEST: fetch command help should have examples.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertIn('Examples:', result.stdout,
            "Fetch command help should have Examples section")

    def test_bundle_help_has_examples(self):
        """
        RED TEST: bundle command help should have examples.
        """
        result = subprocess.run(
            ['./capcat', 'bundle', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertIn('Examples:', result.stdout,
            "Bundle command help should have Examples section")

    def test_list_help_has_examples(self):
        """
        RED TEST: list command help should have examples.
        """
        result = subprocess.run(
            ['./capcat', 'list', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertIn('Examples:', result.stdout,
            "List command help should have Examples section")


class TestHelpExamplesContent(unittest.TestCase):
    """Test that help examples contain actual, usable content."""

    def test_single_help_uses_real_url(self):
        """
        RED TEST: single help should show real URL examples.
        """
        result = subprocess.run(
            ['./capcat', 'single', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        # Should contain example URLs
        self.assertTrue(
            'https://' in result.stdout or 'http://' in result.stdout,
            "Single help should show actual URL examples"
        )

    def test_fetch_help_uses_real_sources(self):
        """
        RED TEST: fetch help should use actual source names.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        sources = get_available_sources()

        # Should contain at least one real source name
        found_source = False
        for source_id in list(sources.keys())[:5]:  # Check first 5 sources
            if source_id in result.stdout:
                found_source = True
                break

        self.assertTrue(found_source,
            f"Fetch help should use real source names. "
            f"Available: {list(sources.keys())[:5]}")

    def test_bundle_help_uses_real_bundles(self):
        """
        RED TEST: bundle help should use actual bundle names.
        """
        result = subprocess.run(
            ['./capcat', 'bundle', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        bundles = get_available_bundles()

        # Should contain at least one real bundle name
        found_bundle = False
        for bundle_id in list(bundles.keys())[:3]:
            if bundle_id in result.stdout:
                found_bundle = True
                break

        self.assertTrue(found_bundle,
            f"Bundle help should use real bundle names. "
            f"Available: {list(bundles.keys())[:3]}")

    def test_list_help_shows_usage(self):
        """
        RED TEST: list help should show list sources/bundles usage.
        """
        result = subprocess.run(
            ['./capcat', 'list', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        # Should demonstrate the three list commands
        self.assertTrue(
            ('list sources' in result.stdout or
             'list bundles' in result.stdout),
            "List help should show list sources/bundles examples"
        )


class TestHelpExamplesCompleteness(unittest.TestCase):
    """Test that help examples are comprehensive."""

    def test_single_help_shows_multiple_options(self):
        """
        RED TEST: single help should show various option combinations.
        """
        result = subprocess.run(
            ['./capcat', 'single', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        # Should show different option combinations
        self.assertIn('--html', result.stdout,
            "Single help should show --html usage")
        self.assertIn('--media', result.stdout,
            "Single help should show --media usage")

    def test_fetch_help_shows_multiple_sources(self):
        """
        RED TEST: fetch help should show single and multiple source examples.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        # Should show comma-separated sources example
        self.assertTrue(
            ',' in result.stdout,
            "Fetch help should show multiple sources with commas"
        )

    def test_fetch_help_shows_count_option(self):
        """
        RED TEST: fetch help should demonstrate --count usage.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertIn('--count', result.stdout,
            "Fetch help should show --count usage")

    def test_bundle_help_shows_count_option(self):
        """
        RED TEST: bundle help should demonstrate --count usage.
        """
        result = subprocess.run(
            ['./capcat', 'bundle', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertIn('--count', result.stdout,
            "Bundle help should show --count usage")


class TestHelpExamplesFormatting(unittest.TestCase):
    """Test that help examples are well-formatted."""

    def test_examples_have_comments(self):
        """
        RED TEST: Examples should have explanatory comments.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        # Examples should have # comments
        if 'Examples:' in result.stdout:
            examples_section = result.stdout.split('Examples:')[1]
            self.assertIn('#', examples_section,
                "Examples should include # comments for clarity")

    def test_examples_properly_indented(self):
        """
        RED TEST: Examples should be indented consistently.
        """
        result = subprocess.run(
            ['./capcat', 'single', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if 'Examples:' in result.stdout:
            examples_section = result.stdout.split('Examples:')[1]
            lines = examples_section.split('\n')

            # At least one line should be indented (example lines)
            indented_lines = [l for l in lines if l.startswith('  ')]
            self.assertGreater(len(indented_lines), 0,
                "Examples should have indented lines")


class TestHelpExamplesUsability(unittest.TestCase):
    """Test that examples are actually usable."""

    def test_main_help_quick_start_example(self):
        """
        RED TEST: Main help should have quick start example.
        """
        result = subprocess.run(
            ['./capcat', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        # Should show a simple getting-started command
        self.assertTrue(
            ('bundle tech' in result.stdout or
             'list sources' in result.stdout or
             'catch' in result.stdout),
            "Main help should show quick start examples"
        )

    def test_single_help_shows_output_option(self):
        """
        RED TEST: single help should show --output usage.
        """
        result = subprocess.run(
            ['./capcat', 'single', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertIn('--output', result.stdout,
            "Single help should show --output usage")

    def test_fetch_help_shows_list_sources_hint(self):
        """
        RED TEST: fetch help should mention 'list sources' for discovery.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        # Should hint at list command for source discovery
        self.assertTrue(
            ('list sources' in result.stdout or
             'list' in result.stdout),
            "Fetch help should mention list sources command"
        )


class TestHelpConsistency(unittest.TestCase):
    """Test consistency across help pages."""

    def test_all_commands_use_capcat_prefix(self):
        """
        RED TEST: All examples should use 'capcat' prefix.
        """
        commands = ['single', 'fetch', 'bundle', 'list']

        for cmd in commands:
            result = subprocess.run(
                ['./capcat', cmd, '--help'],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            if 'Examples:' in result.stdout:
                examples = result.stdout.split('Examples:')[1]
                # Should contain 'capcat' in examples
                self.assertIn('capcat', examples.lower(),
                    f"{cmd} help should use 'capcat' in examples")

    def test_consistent_option_formatting(self):
        """
        RED TEST: Options should be formatted consistently (--option).
        """
        result = subprocess.run(
            ['./capcat', 'fetch', '--help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if 'Examples:' in result.stdout:
            examples = result.stdout.split('Examples:')[1]
            # Should use -- for long options
            if '--' in examples:
                # Verify they're actually option flags
                import re
                options = re.findall(r'--\w+', examples)
                self.assertGreater(len(options), 0,
                    "Should use --option format consistently")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
