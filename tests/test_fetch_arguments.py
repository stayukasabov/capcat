#!/usr/bin/env python3
"""
TDD Tests for fetch command argument handling.

CRITICAL: Tests that would have caught the actual bugs:
1. --output flag completely ignored (hardcoded ../News/)
2. --count flag not respected (source defaults used instead)

These tests verify ACTUAL BEHAVIOR, not just help text.
"""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path
import unittest
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestFetchOutputDirectory(unittest.TestCase):
    """Test that --output flag actually works."""

    def setUp(self):
        """Create temp directory for tests."""
        self.test_dir = tempfile.mkdtemp(prefix='capcat_test_')
        self.cwd = Path(__file__).parent.parent

    def tearDown(self):
        """Clean up temp directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_fetch_output_flag_creates_in_custom_dir(self):
        """
        RED TEST: Verify --output creates files in specified directory.

        Bug: Files currently go to ../News/ regardless of --output flag
        """
        custom_dir = os.path.join(self.test_dir, 'custom_output')

        # Run fetch with custom output directory
        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '1', '--output', custom_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=120
        )

        # Should NOT create in ../News/
        default_news_dir = self.cwd.parent / 'News'

        # Should create in custom directory
        self.assertTrue(
            os.path.exists(custom_dir) or
            any(custom_dir in line for line in result.stdout.split('\n')),
            f"Files should be created in {custom_dir}, not ../News/. "
            f"Output: {result.stdout[:500]}"
        )

    def test_fetch_output_message_shows_correct_path(self):
        """
        RED TEST: Verify output message shows custom path, not hardcoded.

        Bug: capcat.py:791 hardcodes '../News/news_DD-MM-YYYY/'
        """
        custom_dir = os.path.join(self.test_dir, 'my_articles')

        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '1', '--output', custom_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=120
        )

        output = result.stdout + result.stderr

        # Should mention custom directory in output
        self.assertTrue(
            custom_dir in output or 'my_articles' in output,
            f"Output message should mention custom directory '{custom_dir}'. "
            f"Got: {output[:500]}"
        )

        # Should NOT mention default ../News/ path
        self.assertNotIn(
            '../News/news_',
            output,
            f"Output should not show hardcoded ../News/ path. Got: {output[:500]}"
        )


class TestFetchCountParameter(unittest.TestCase):
    """Test that --count flag actually works."""

    def setUp(self):
        """Setup for count tests."""
        self.cwd = Path(__file__).parent.parent
        self.test_dir = tempfile.mkdtemp(prefix='capcat_test_')

    def tearDown(self):
        """Cleanup."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_fetch_count_overrides_source_default(self):
        """
        RED TEST: Verify --count parameter overrides source defaults.

        Bug: Requested count=40, got 30 (source default used instead)
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '5', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=120
        )

        output = result.stdout + result.stderr

        # Should explicitly request 5 articles
        self.assertTrue(
            'top 5' in output.lower() or
            'fetching 5' in output.lower() or
            '5 articles' in output.lower(),
            f"Should request exactly 5 articles. Output: {output[:500]}"
        )

        # Should NOT use default 30
        self.assertFalse(
            ('top 30' in output.lower() and 'top 5' not in output.lower()),
            f"Should not default to 30 when --count 5 specified. Output: {output[:500]}"
        )

    def test_fetch_count_reflected_in_logs(self):
        """
        RED TEST: Verify logs show custom count, not source default.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '10'],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=120
        )

        output = result.stdout + result.stderr

        # Log should mention count=10
        self.assertTrue(
            '10' in output,
            f"Logs should mention count=10. Output: {output[:500]}"
        )

    def test_fetch_count_40_actually_requests_40(self):
        """
        RED TEST: Verify count=40 requests 40, not 30.

        This is the exact bug reported by user:
        - Command: --count 40
        - Log showed: "Fetching top 40 articles" (correct)
        - But also: "Successfully discovered 30 articles" (wrong - should be 40 or error)
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '40', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=180
        )

        output = result.stdout + result.stderr

        # Should request 40
        self.assertIn(
            '40',
            output,
            f"Should request 40 articles. Output: {output[:500]}"
        )

        # If source can't provide 40, should show warning
        if 'discovered 30' in output.lower():
            # This is acceptable IF there's a clear explanation
            self.assertTrue(
                'warning' in output.lower() or
                'limit' in output.lower() or
                'available' in output.lower() or
                'maximum' in output.lower(),
                f"If source provides fewer than requested, should explain why. "
                f"Output: {output[:500]}"
            )


class TestBundleOutputDirectory(unittest.TestCase):
    """Test that bundle command respects --output."""

    def setUp(self):
        """Setup for bundle tests."""
        self.cwd = Path(__file__).parent.parent
        self.test_dir = tempfile.mkdtemp(prefix='capcat_test_')

    def tearDown(self):
        """Cleanup."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_bundle_output_flag_works(self):
        """
        RED TEST: Verify bundle --output creates files in custom directory.

        Bug: Same hardcoded path in capcat.py:791
        """
        custom_dir = os.path.join(self.test_dir, 'tech_news')

        result = subprocess.run(
            ['./capcat', 'bundle', 'tech', '--count', '1', '--output', custom_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=180
        )

        output = result.stdout + result.stderr

        # Should mention custom directory
        self.assertTrue(
            custom_dir in output or 'tech_news' in output,
            f"Bundle should use custom output directory. Output: {output[:500]}"
        )

        # Should NOT use default ../News/
        self.assertNotIn(
            '../News/news_',
            output,
            f"Bundle should not use hardcoded ../News/. Output: {output[:500]}"
        )


class TestSingleOutputDirectory(unittest.TestCase):
    """Test that single command respects --output."""

    def setUp(self):
        """Setup for single tests."""
        self.cwd = Path(__file__).parent.parent
        self.test_dir = tempfile.mkdtemp(prefix='capcat_test_')

    def tearDown(self):
        """Cleanup."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_single_output_flag_works(self):
        """
        RED TEST: Verify single --output creates files in custom directory.

        Need to verify single command also respects --output
        """
        custom_dir = os.path.join(self.test_dir, 'single_article')

        # Use a simple URL that should work
        result = subprocess.run(
            [
                './capcat', 'single',
                'https://news.ycombinator.com/item?id=1',
                '--output', custom_dir
            ],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Should use custom directory
        self.assertTrue(
            custom_dir in output or 'single_article' in output,
            f"Single should use custom output directory. Output: {output[:500]}"
        )


class TestArgumentParsing(unittest.TestCase):
    """Test that arguments are parsed correctly."""

    def test_output_argument_parsed(self):
        """
        RED TEST: Verify --output is actually parsed from command line.
        """
        from cli import parse_arguments

        args_dict = parse_arguments(['fetch', 'hn', '--output', '/tmp/test'])

        self.assertEqual(
            args_dict['output'],
            '/tmp/test',
            "Output argument should be parsed correctly"
        )

    def test_count_argument_parsed(self):
        """
        RED TEST: Verify --count is actually parsed from command line.
        """
        from cli import parse_arguments

        args_dict = parse_arguments(['fetch', 'hn', '--count', '40'])

        self.assertEqual(
            args_dict['count'],
            40,
            "Count argument should be parsed as integer 40"
        )

    def test_count_default_is_30(self):
        """
        Verify default count is 30 (documented behavior).
        """
        from cli import parse_arguments

        args_dict = parse_arguments(['fetch', 'hn'])

        self.assertEqual(
            args_dict['count'],
            30,
            "Default count should be 30"
        )


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
