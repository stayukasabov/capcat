#!/usr/bin/env python3
"""
TDD Tests: Hash-based Theme Persistence

Test Cases:
1. Links should have hash appended with current theme
2. External links should not be modified
3. Hash should be preserved in navigation
4. Template rendering includes theme in all internal links
"""

import unittest
from unittest.mock import Mock, patch
import re

from core.theme_utils import inject_theme_hash, parse_theme_from_hash


class TestThemeHashInjection(unittest.TestCase):
    """Test theme hash injection into HTML links."""

    def test_inject_theme_hash_to_relative_link(self):
        """Should append #theme=light to relative links."""
        html = '<a href="article.html">Article</a>'
        result = inject_theme_hash(html, 'light')
        self.assertIn('href="article.html#theme=light"', result)

    def test_inject_theme_hash_to_multiple_links(self):
        """Should append hash to all relative links."""
        html = '''
        <a href="page1.html">Page 1</a>
        <a href="page2.html">Page 2</a>
        '''
        result = inject_theme_hash(html, 'dark')
        self.assertIn('href="page1.html#theme=dark"', result)
        self.assertIn('href="page2.html#theme=dark"', result)

    def test_preserve_existing_hash(self):
        """Should preserve existing hash anchors."""
        html = '<a href="article.html#section">Article</a>'
        result = inject_theme_hash(html, 'light')
        # Should preserve #section and add &theme=light or similar
        self.assertIn('article.html#section', result)
        self.assertIn('theme=light', result)

    def test_skip_external_links(self):
        """Should not modify external links."""
        html = '<a href="https://example.com/page.html">External</a>'
        result = inject_theme_hash(html, 'light')
        self.assertEqual(html, result)  # Should be unchanged

    def test_skip_mailto_links(self):
        """Should not modify mailto links."""
        html = '<a href="mailto:test@example.com">Email</a>'
        result = inject_theme_hash(html, 'light')
        self.assertEqual(html, result)

    def test_skip_javascript_links(self):
        """Should not modify javascript: links."""
        html = '<a href="javascript:void(0)">Toggle</a>'
        result = inject_theme_hash(html, 'light')
        self.assertEqual(html, result)

    def test_handle_links_with_query_params(self):
        """Should handle links with query parameters."""
        html = '<a href="search.html?q=test">Search</a>'
        result = inject_theme_hash(html, 'light')
        self.assertIn('search.html?q=test#theme=light', result)

    def test_handle_relative_paths(self):
        """Should handle ../ relative paths."""
        html = '<a href="../index.html">Back</a>'
        result = inject_theme_hash(html, 'dark')
        self.assertIn('../index.html#theme=dark', result)

    def test_handle_root_relative_paths(self):
        """Should handle ./ paths."""
        html = '<a href="./article.html">Article</a>'
        result = inject_theme_hash(html, 'light')
        self.assertIn('./article.html#theme=light', result)


class TestThemeHashDetection(unittest.TestCase):
    """Test JavaScript theme detection logic."""

    def test_parse_theme_from_hash_light(self):
        """Should extract 'light' from #theme=light."""
        hash_value = "#theme=light"
        theme = parse_theme_from_hash(hash_value)
        self.assertEqual(theme, "light")

    def test_parse_theme_from_hash_dark(self):
        """Should extract 'dark' from #theme=dark."""
        hash_value = "#theme=dark"
        theme = parse_theme_from_hash(hash_value)
        self.assertEqual(theme, "dark")

    def test_parse_theme_from_hash_with_anchor(self):
        """Should extract theme from #section&theme=light."""
        hash_value = "#section&theme=light"
        theme = parse_theme_from_hash(hash_value)
        self.assertEqual(theme, "light")

    def test_parse_theme_returns_none_when_missing(self):
        """Should return None when no theme in hash."""
        hash_value = "#section"
        theme = parse_theme_from_hash(hash_value)
        self.assertIsNone(theme)

    def test_parse_theme_returns_none_for_empty_hash(self):
        """Should return None for empty hash."""
        hash_value = ""
        theme = parse_theme_from_hash(hash_value)
        self.assertIsNone(theme)


if __name__ == "__main__":
    unittest.main(verbosity=2)
