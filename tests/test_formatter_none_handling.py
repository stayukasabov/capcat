#!/usr/bin/env python3
"""
Test formatter handles None elements gracefully.

This test verifies the fix for the bug:
"'NoneType' object has no attribute 'get'"

The bug occurred when malformed HTML caused None elements
to be passed to _convert_element(), specifically failing at
line 629 when processing ordered lists.
"""

import unittest
from core.formatter import html_to_markdown, _convert_element


class TestFormatterNoneHandling(unittest.TestCase):
    """Test formatter handles None elements without crashing."""

    def test_convert_element_handles_none(self):
        """_convert_element should handle None gracefully."""
        result = _convert_element(None)

        self.assertEqual(result, "")
        self.assertIsInstance(result, str)

    def test_malformed_html_with_none_elements(self):
        """HTML with None-like structures should not crash."""
        # Simulate HTML that might produce None elements
        test_cases = [
            "",  # Empty HTML
            "<div></div>",  # Empty div
            "<ol><li></li></ol>",  # Empty list item
            "<p><span></span></p>",  # Nested empty elements
        ]

        for html in test_cases:
            with self.subTest(html=html):
                result = html_to_markdown(html)
                # Should not crash, should return a string
                self.assertIsInstance(result, str)

    def test_ordered_list_without_start_attribute(self):
        """Ordered list without 'start' attribute should work."""
        html = "<ol><li>First</li><li>Second</li></ol>"

        result = html_to_markdown(html)

        self.assertIn("First", result)
        self.assertIn("Second", result)

    def test_ordered_list_with_start_attribute(self):
        """Ordered list with 'start' attribute should work."""
        html = '<ol start="5"><li>Fifth</li><li>Sixth</li></ol>'

        result = html_to_markdown(html)

        self.assertIn("Fifth", result)
        self.assertIn("Sixth", result)

    def test_nested_lists_with_malformed_structure(self):
        """Nested lists with potential None elements should not crash."""
        html = """
        <ul>
            <li>Item 1
                <ol>
                    <li>Nested 1</li>
                    <li></li>
                </ol>
            </li>
            <li></li>
        </ul>
        """

        # Should not crash
        result = html_to_markdown(html)
        self.assertIsInstance(result, str)
        self.assertIn("Item 1", result)
        self.assertIn("Nested 1", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
