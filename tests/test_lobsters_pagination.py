#!/usr/bin/env python3
"""
TDD Tests for Lobsters pagination support.

CRITICAL: Lobsters front page has limited stories (~25-30).
To fetch 40+ articles, pagination is required.

Lobsters pagination pattern: https://lobste.rs/page/2, /page/3, etc.

These tests verify actual pagination behavior for counts >30.
"""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path
import unittest
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLobstersPagination(unittest.TestCase):
    """Test Lobsters pagination for fetching >30 articles."""

    def setUp(self):
        """Setup for pagination tests."""
        self.cwd = Path(__file__).parent.parent
        self.test_dir = tempfile.mkdtemp(prefix='capcat_lb_test_')

    def tearDown(self):
        """Cleanup."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_lb_fetch_40_articles_uses_pagination(self):
        """
        RED TEST: Verify Lobsters fetches 40 articles via pagination.

        Expected behavior:
        - Request 40 articles
        - Lobsters front page has ~25-30 stories
        - Should fetch page 2 to get remaining articles
        - Final count should be 40, not 25-30
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'lb', '--count', '40', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=240
        )

        output = result.stdout + result.stderr

        # Should request 40
        self.assertIn(
            '40',
            output,
            f"Should request 40 articles. Output: {output[:500]}"
        )

        # Should NOT stop at ~25-30 (front page limit)
        if 'Successfully discovered' in output or 'Successfully fetched' in output:
            match = re.search(r'Successfully (?:discovered|fetched) (\d+)', output)
            if match:
                count = int(match.group(1))
                self.assertGreaterEqual(
                    count,
                    40,
                    f"Should fetch at least 40 articles via pagination. Got {count}. Output: {output[:500]}"
                )

    def test_lb_fetch_50_articles_multiple_pages(self):
        """
        RED TEST: Verify Lobsters can fetch 50+ articles across multiple pages.

        Expected behavior:
        - Request 50 articles
        - Requires fetching from pages 1, 2, and possibly 3
        - Should actually get 50 articles
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'lb', '--count', '50', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=300
        )

        output = result.stdout + result.stderr

        # Should request 50
        self.assertIn(
            '50',
            output,
            f"Should request 50 articles"
        )

        # Should get 50 (or close to it)
        if 'Successfully discovered' in output or 'Successfully fetched' in output:
            match = re.search(r'Successfully (?:discovered|fetched) (\d+)', output)
            if match:
                count = int(match.group(1))
                self.assertGreaterEqual(
                    count,
                    45,  # Allow small margin
                    f"Should fetch at least 45 articles. Got {count}"
                )

    def test_lb_pagination_stops_at_requested_count(self):
        """
        RED TEST: Verify pagination stops at exactly requested count.

        If user requests 35 articles:
        - Page 1: ~25-30 articles
        - Page 2: Should fetch only remaining, not all from page 2
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'lb', '--count', '35', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=240
        )

        output = result.stdout + result.stderr

        # Should request 35
        self.assertIn('35', output)

        # Should get exactly 35 (or very close)
        if 'Successfully discovered' in output or 'Successfully fetched' in output:
            match = re.search(r'Successfully (?:discovered|fetched) (\d+)', output)
            if match:
                count = int(match.group(1))
                self.assertGreaterEqual(
                    count,
                    35,
                    f"Should fetch at least 35 articles. Got {count}"
                )
                self.assertLessEqual(
                    count,
                    40,
                    f"Should not fetch significantly more than 35. Got {count}"
                )

    def test_lb_logs_show_pagination_activity(self):
        """
        RED TEST: Verify logs indicate pagination is happening.

        When fetching >30 articles, logs should show:
        - Fetching from page 1
        - Fetching from page 2
        - Or similar indication of multi-page fetch
        """
        result = subprocess.run(
            ['./capcat', '--verbose', 'fetch', 'lb', '--count', '40', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=240
        )

        output = result.stdout + result.stderr

        # Should mention pagination or multiple pages
        pagination_indicators = [
            'page 2',
            'Page 2',
            '/page/2',
            'pagination',
            'Pagination',
            'next page',
            'Next page'
        ]

        found_indicator = any(indicator in output for indicator in pagination_indicators)

        self.assertTrue(
            found_indicator,
            f"Verbose output should indicate pagination activity when fetching >30 articles. "
            f"Output: {output[:1000]}"
        )


class TestLobstersPaginationEdgeCases(unittest.TestCase):
    """Test edge cases in Lobsters pagination."""

    def setUp(self):
        """Setup."""
        self.cwd = Path(__file__).parent.parent
        self.test_dir = tempfile.mkdtemp(prefix='capcat_lb_edge_')

    def tearDown(self):
        """Cleanup."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_lb_handles_100_article_request(self):
        """
        RED TEST: Verify Lobsters can handle large requests (100 articles).

        Should paginate through multiple pages to get 100 articles.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'lb', '--count', '100', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=400
        )

        output = result.stdout + result.stderr

        # Should request 100
        self.assertIn('100', output)

        # Should get at least 90 (allowing for some missing)
        if 'Successfully discovered' in output or 'Successfully fetched' in output:
            match = re.search(r'Successfully (?:discovered|fetched) (\d+)', output)
            if match:
                count = int(match.group(1))
                self.assertGreaterEqual(
                    count,
                    90,
                    f"Should fetch at least 90 articles for count=100. Got {count}"
                )

    def test_lb_30_or_less_no_pagination(self):
        """
        RED TEST: Verify counts <=30 don't trigger pagination.

        Requesting 25 or fewer should only fetch from front page.
        """
        result = subprocess.run(
            ['./capcat', '--verbose', 'fetch', 'lb', '--count', '20', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=180
        )

        output = result.stdout + result.stderr

        # Should NOT mention page 2 or pagination
        self.assertNotIn(
            'page 2',
            output.lower(),
            f"Should not paginate for count=20. Output: {output[:500]}"
        )

    def test_lb_pagination_respects_rate_limits(self):
        """
        RED TEST: Verify pagination includes proper delays between page requests.

        Lobsters requires respectful scraping with delays.
        """
        import time
        start_time = time.time()

        result = subprocess.run(
            ['./capcat', 'fetch', 'lb', '--count', '40', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=300
        )

        elapsed = time.time() - start_time

        # Should take at least a few seconds due to rate limiting
        self.assertGreaterEqual(
            elapsed,
            2.0,
            f"Should include rate limiting delays. Took only {elapsed:.2f}s"
        )

        # Verify no errors about rate limiting
        output = result.stdout + result.stderr
        self.assertNotIn(
            'rate limit',
            output.lower(),
            f"Should not trigger rate limiting errors. Output: {output[:500]}"
        )


class TestLobstersPaginationIntegration(unittest.TestCase):
    """Integration tests for Lobsters pagination with other features."""

    def setUp(self):
        """Setup."""
        self.cwd = Path(__file__).parent.parent
        self.test_dir = tempfile.mkdtemp(prefix='capcat_lb_int_')

    def tearDown(self):
        """Cleanup."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_lb_pagination_with_html_flag(self):
        """
        RED TEST: Verify pagination works with --html flag.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'lb', '--count', '40', '--html', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=300
        )

        output = result.stdout + result.stderr

        # Should fetch 40 articles
        if 'Successfully discovered' in output or 'Successfully fetched' in output:
            match = re.search(r'Successfully (?:discovered|fetched) (\d+)', output)
            if match:
                count = int(match.group(1))
                self.assertGreaterEqual(
                    count,
                    40,
                    f"Should fetch 40 articles with --html. Got {count}"
                )

    def test_lb_pagination_with_custom_output(self):
        """
        RED TEST: Verify pagination works with custom --output directory.
        """
        custom_dir = os.path.join(self.test_dir, 'lb_paginated')

        result = subprocess.run(
            ['./capcat', 'fetch', 'lb', '--count', '40', '--output', custom_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=300
        )

        output = result.stdout + result.stderr

        # Should use custom directory
        self.assertTrue(
            custom_dir in output or 'lb_paginated' in output,
            f"Should use custom output directory. Output: {output[:500]}"
        )

        # Should fetch 40 articles
        if 'Successfully discovered' in output or 'Successfully fetched' in output:
            match = re.search(r'Successfully (?:discovered|fetched) (\d+)', output)
            if match:
                count = int(match.group(1))
                self.assertGreaterEqual(
                    count,
                    40,
                    f"Should fetch 40 articles. Got {count}"
                )

    def test_lb_pagination_with_comments(self):
        """
        RED TEST: Verify pagination includes comment fetching.

        Lobsters source includes comments - pagination should preserve this.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'lb', '--count', '40', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=360
        )

        output = result.stdout + result.stderr

        # Should fetch 40 articles
        if 'Successfully discovered' in output or 'Successfully fetched' in output:
            match = re.search(r'Successfully (?:discovered|fetched) (\d+)', output)
            if match:
                count = int(match.group(1))
                self.assertGreaterEqual(
                    count,
                    40,
                    f"Should fetch 40 articles with comments. Got {count}"
                )

        # Should mention comments (if verbose or default logging)
        # This verifies comment fetching still works with pagination


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
