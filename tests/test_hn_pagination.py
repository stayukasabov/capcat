#!/usr/bin/env python3
"""
TDD Tests for Hacker News pagination support.

CRITICAL: HN front page has only ~30 stories.
To fetch 40+ articles, pagination is required.

HN pagination pattern: https://news.ycombinator.com/?p=2, ?p=3, etc.

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


class TestHNPagination(unittest.TestCase):
    """Test HN pagination for fetching >30 articles."""

    def setUp(self):
        """Setup for pagination tests."""
        self.cwd = Path(__file__).parent.parent
        self.test_dir = tempfile.mkdtemp(prefix='capcat_hn_test_')

    def tearDown(self):
        """Cleanup."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_hn_fetch_40_articles_uses_pagination(self):
        """
        RED TEST: Verify HN fetches 40 articles via pagination.

        Expected behavior:
        - Request 40 articles
        - HN front page has ~30
        - Should fetch page 2 to get remaining 10
        - Final count should be 40, not 30
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '40', '--output', self.test_dir],
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

        # Should NOT stop at 30 (front page limit)
        # Look for final success count
        if 'Successfully discovered' in output or 'Successfully fetched' in output:
            # Extract the number mentioned
            match = re.search(r'Successfully (?:discovered|fetched) (\d+)', output)
            if match:
                count = int(match.group(1))
                self.assertGreaterEqual(
                    count,
                    40,
                    f"Should fetch at least 40 articles via pagination. Got {count}. Output: {output[:500]}"
                )

    def test_hn_fetch_50_articles_multiple_pages(self):
        """
        RED TEST: Verify HN can fetch 50+ articles across multiple pages.

        Expected behavior:
        - Request 50 articles
        - Requires fetching from pages 1, 2, and possibly 3
        - Should actually get 50 articles
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '50', '--output', self.test_dir],
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
                    45,  # Allow small margin for missing articles
                    f"Should fetch at least 45 articles. Got {count}"
                )

    def test_hn_pagination_stops_at_requested_count(self):
        """
        RED TEST: Verify pagination stops at exactly requested count.

        If user requests 35 articles:
        - Page 1: 30 articles
        - Page 2: Should fetch only 5 more, not all 30 from page 2
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '35', '--output', self.test_dir],
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

    def test_hn_logs_show_pagination_activity(self):
        """
        RED TEST: Verify logs indicate pagination is happening.

        When fetching >30 articles, logs should show:
        - Fetching from page 1
        - Fetching from page 2
        - Or similar indication of multi-page fetch
        """
        result = subprocess.run(
            ['./capcat', '--verbose', 'fetch', 'hn', '--count', '40', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=240
        )

        output = result.stdout + result.stderr

        # Should mention pagination or multiple pages
        # (Exact wording depends on implementation)
        pagination_indicators = [
            'page 2',
            'Page 2',
            '?p=2',
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


class TestHNPaginationEdgeCases(unittest.TestCase):
    """Test edge cases in HN pagination."""

    def setUp(self):
        """Setup."""
        self.cwd = Path(__file__).parent.parent
        self.test_dir = tempfile.mkdtemp(prefix='capcat_hn_edge_')

    def tearDown(self):
        """Cleanup."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_hn_handles_100_article_request(self):
        """
        RED TEST: Verify HN can handle large requests (100 articles).

        Should paginate through ~4 pages to get 100 articles.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '100', '--output', self.test_dir],
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

    def test_hn_30_or_less_no_pagination(self):
        """
        RED TEST: Verify counts <=30 don't trigger pagination.

        Requesting 30 or fewer should only fetch from front page.
        """
        result = subprocess.run(
            ['./capcat', '--verbose', 'fetch', 'hn', '--count', '20', '--output', self.test_dir],
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

    def test_hn_pagination_respects_rate_limits(self):
        """
        RED TEST: Verify pagination includes proper delays between page requests.

        HN requires respectful scraping with delays.
        """
        import time
        start_time = time.time()

        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '40', '--output', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=300
        )

        elapsed = time.time() - start_time

        # Should take at least a few seconds due to rate limiting
        # (Exact timing depends on implementation)
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


class TestHNPaginationIntegration(unittest.TestCase):
    """Integration tests for HN pagination with other features."""

    def setUp(self):
        """Setup."""
        self.cwd = Path(__file__).parent.parent
        self.test_dir = tempfile.mkdtemp(prefix='capcat_hn_int_')

    def tearDown(self):
        """Cleanup."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_hn_pagination_with_html_flag(self):
        """
        RED TEST: Verify pagination works with --html flag.
        """
        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '40', '--html', '--output', self.test_dir],
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

    def test_hn_pagination_with_custom_output(self):
        """
        RED TEST: Verify pagination works with custom --output directory.
        """
        custom_dir = os.path.join(self.test_dir, 'hn_paginated')

        result = subprocess.run(
            ['./capcat', 'fetch', 'hn', '--count', '40', '--output', custom_dir],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            timeout=300
        )

        output = result.stdout + result.stderr

        # Should use custom directory
        self.assertTrue(
            custom_dir in output or 'hn_paginated' in output,
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


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
