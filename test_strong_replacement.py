#!/usr/bin/env python3
"""
Comprehensive Test Suite for Strong to H4 Tag Replacement

Tests all aspects of the replacement functionality including:
- Single strong tags per line
- Multiple strong tags per line (newline insertion)
- Tags with attributes
- Nested HTML content
- Edge cases and error handling
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from replace_strong_with_h4 import StrongToH4Replacer, ReplacementStats


class TestStrongToH4Replacement(unittest.TestCase):
    """Test suite for strong to h4 tag replacement."""

    def setUp(self):
        """Create temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.docs_dir = Path(self.test_dir) / "website" / "docs"
        self.docs_dir.mkdir(parents=True)
        self.replacer = StrongToH4Replacer(docs_dir=str(self.docs_dir))

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_single_strong_tag_per_line(self):
        """Test replacement of single strong tag per line."""
        input_line = "<p><strong>Location:</strong> core/source_system/</p>\n"
        expected = "<p><h4>Location:</h4> core/source_system/</p>\n"

        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertEqual(result, expected)
        self.assertEqual(count, 2)  # open + close
        self.assertFalse(has_multiple)

    def test_multiple_strong_tags_newline_insertion(self):
        """Test newline insertion for multiple strong tags on same line."""
        input_line = "<strong>Location:</strong> core/source_system/source_factory.py <strong>Purpose:</strong> Unified source creation\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        # Should insert newline before second <h4>
        self.assertIn('\n', result)
        self.assertTrue(has_multiple)
        self.assertEqual(count, 4)  # 2 opens + 2 closes

        # Check that both tags are replaced
        self.assertIn('<h4>Location:</h4>', result)
        self.assertIn('<h4>Purpose:</h4>', result)

        # Check newline is before second tag
        lines = result.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertIn('<h4>Location:</h4>', lines[0])
        self.assertIn('<h4>Purpose:</h4>', lines[1])

    def test_three_strong_tags_newlines(self):
        """Test handling of three strong tags on the same line."""
        input_line = "<strong>A:</strong> text1 <strong>B:</strong> text2 <strong>C:</strong> text3\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertTrue(has_multiple)
        self.assertEqual(count, 6)  # 3 opens + 3 closes

        # Should have 3 lines
        lines = result.split('\n')
        self.assertEqual(len(lines), 3)
        self.assertIn('<h4>A:</h4>', lines[0])
        self.assertIn('<h4>B:</h4>', lines[1])
        self.assertIn('<h4>C:</h4>', lines[2])

    def test_strong_tag_with_attributes(self):
        """Test replacement of strong tags with attributes."""
        input_line = '<strong class="bold" id="test">Text</strong>\n'
        expected = '<h4 class="bold" id="test">Text</h4>\n'

        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertEqual(result, expected)
        self.assertEqual(count, 2)
        self.assertFalse(has_multiple)

    def test_nested_html_content(self):
        """Test strong tags containing nested HTML."""
        input_line = "<strong>Link: <a href='test.html'>Click</a></strong>\n"
        expected = "<h4>Link: <a href='test.html'>Click</a></h4>\n"

        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertEqual(result, expected)
        self.assertEqual(count, 2)
        self.assertFalse(has_multiple)

    def test_preserve_indentation_single_tag(self):
        """Test that indentation is preserved for single tags."""
        input_line = "    <strong>Indented</strong> content\n"
        expected = "    <h4>Indented</h4> content\n"

        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertEqual(result, expected)
        self.assertFalse(has_multiple)

    def test_preserve_indentation_multiple_tags(self):
        """Test that indentation is preserved when inserting newlines."""
        input_line = "    <strong>First:</strong> text <strong>Second:</strong> more\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertTrue(has_multiple)

        # Both lines should have same indentation
        lines = result.split('\n')
        self.assertTrue(lines[0].startswith('    '))
        self.assertTrue(lines[1].startswith('    '))

    def test_no_strong_tags(self):
        """Test line with no strong tags."""
        input_line = "<p>Regular paragraph text</p>\n"

        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertEqual(result, input_line)
        self.assertEqual(count, 0)
        self.assertFalse(has_multiple)

    def test_case_insensitive_replacement(self):
        """Test that replacement works regardless of case."""
        input_line = "<STRONG>Upper</STRONG> and <Strong>Mixed</Strong>\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertIn('<h4', result)
        self.assertIn('</h4>', result)
        self.assertTrue(has_multiple)
        self.assertEqual(count, 4)

    def test_mixed_case_closing_tags(self):
        """Test mixed case closing tags."""
        input_line = "<strong>Text</STRONG>\n"
        expected = "<h4>Text</h4>\n"

        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertEqual(result, expected)
        self.assertEqual(count, 2)

    def test_multiple_tags_with_nested_content(self):
        """Test multiple tags where tags contain complex nested content."""
        input_line = "<strong>Link: <a href='#'>test</a></strong> <strong>Code: <code>var</code></strong>\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertTrue(has_multiple)
        self.assertEqual(count, 4)

        # Check both nested elements preserved
        self.assertIn("<a href='#'>test</a>", result)
        self.assertIn("<code>var</code>", result)

    def test_empty_strong_tags(self):
        """Test replacement of empty strong tags."""
        input_line = "<strong></strong>\n"
        expected = "<h4></h4>\n"

        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertEqual(result, expected)
        self.assertEqual(count, 2)

    def test_strong_tags_with_newlines_inside(self):
        """Test that strong tags on different lines are not treated as multiple."""
        input_line = "<strong>Text on one line</strong>\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertFalse(has_multiple)
        self.assertEqual(count, 2)

    def test_adjacent_strong_tags_no_space(self):
        """Test adjacent strong tags with no space between."""
        input_line = "<strong>First</strong><strong>Second</strong>\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertTrue(has_multiple)
        self.assertEqual(count, 4)

        # Should split into two lines
        lines = result.split('\n')
        self.assertEqual(len(lines), 2)

    def test_whitespace_preservation(self):
        """Test that all whitespace is preserved."""
        input_line = "<strong>Before:</strong>   multiple   spaces   <strong>After:</strong>  text\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        # Check spaces are preserved in first line
        lines = result.split('\n')
        self.assertIn('   multiple   spaces   ', lines[0])

    def test_file_processing_stats(self):
        """Test file processing with statistics tracking."""
        test_html = """<html>
<body>
<p><strong>Single</strong> tag here</p>
<p><strong>Multiple:</strong> text <strong>Tags:</strong> here</p>
<p>No tags here</p>
</body>
</html>"""

        test_file = self.docs_dir / "test.html"
        test_file.write_text(test_html)

        content, replacements, modified_lines, multiple_lines = self.replacer.process_file(test_file)

        self.assertEqual(replacements, 6)  # 3 tags * 2 (open+close)
        self.assertEqual(modified_lines, 2)  # 2 lines with tags
        self.assertEqual(multiple_lines, 1)  # 1 line with multiple tags

    def test_directory_processing_dry_run(self):
        """Test directory processing in dry-run mode."""
        # Create test files
        (self.docs_dir / "file1.html").write_text("<strong>Test1</strong>")
        (self.docs_dir / "file2.html").write_text("<strong>Test2</strong>")
        (self.docs_dir / "file3.html").write_text("No tags")

        stats = self.replacer.process_directory(dry_run=True)

        self.assertEqual(stats.files_processed, 3)
        self.assertEqual(stats.files_modified, 2)
        self.assertEqual(stats.total_replacements, 4)  # 2 files * 2 tags

    def test_backup_creation(self):
        """Test that backups are created correctly."""
        test_file = self.docs_dir / "test.html"
        test_file.write_text("<strong>Test</strong>")

        backup_dir = Path(self.test_dir) / "backup"
        success = self.replacer.create_backup(test_file, backup_dir)

        self.assertTrue(success)
        self.assertTrue((backup_dir / "test.html").exists())

    def test_unicode_content_handling(self):
        """Test handling of unicode content in tags."""
        input_line = "<strong>Español:</strong> coñe <strong>日本語:</strong> テスト\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertTrue(has_multiple)
        self.assertIn('Español:', result)
        self.assertIn('日本語:', result)
        self.assertEqual(count, 4)

    def test_special_html_entities(self):
        """Test handling of HTML entities within tags."""
        input_line = "<strong>&lt;code&gt;:</strong> value &amp; stuff\n"
        expected = "<h4>&lt;code&gt;:</h4> value &amp; stuff\n"

        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertEqual(result, expected)
        self.assertEqual(count, 2)

    def test_quoted_attributes_preservation(self):
        """Test that quoted attributes are preserved exactly."""
        input_line = '<strong data-value="test\'s quote">Text</strong>\n'
        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertIn('data-value="test\'s quote"', result)
        self.assertEqual(count, 2)

    def test_real_world_example_from_docs(self):
        """Test with real example from the documentation."""
        input_line = "<strong>Location:</strong> core/source_system/source_factory.py <strong>Purpose:</strong> Unified source creation\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        # Expected transformation
        lines = result.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertIn('<h4>Location:</h4> core/source_system/source_factory.py', lines[0])
        self.assertIn('<h4>Purpose:</h4> Unified source creation', lines[1])
        self.assertTrue(has_multiple)

    def test_list_items_with_multiple_tags(self):
        """Test list items containing multiple strong tags."""
        input_line = "<li><strong>Before</strong>: <code>add_source()</code> handled 7 different responsibilities</li>\n"
        result, count, has_multiple = self.replacer.process_line(input_line)

        self.assertEqual(count, 2)
        self.assertFalse(has_multiple)
        self.assertIn('<h4>Before</h4>', result)

    def test_error_recovery_invalid_file(self):
        """Test error handling for invalid file paths."""
        invalid_path = Path(self.test_dir) / "nonexistent.html"
        content, replacements, modified_lines, multiple_lines = self.replacer.process_file(invalid_path)

        self.assertEqual(content, "")
        self.assertEqual(replacements, 0)
        self.assertTrue(len(self.replacer.stats.errors) > 0)


class TestReplacementStats(unittest.TestCase):
    """Test the ReplacementStats dataclass."""

    def test_stats_initialization(self):
        """Test that stats initialize with correct defaults."""
        stats = ReplacementStats()

        self.assertEqual(stats.files_processed, 0)
        self.assertEqual(stats.files_modified, 0)
        self.assertEqual(stats.total_replacements, 0)
        self.assertEqual(stats.lines_with_multiple_tags, 0)
        self.assertEqual(stats.lines_modified, 0)
        self.assertIsInstance(stats.errors, list)
        self.assertEqual(len(stats.errors), 0)

    def test_stats_accumulation(self):
        """Test stats accumulation."""
        stats = ReplacementStats()
        stats.files_processed = 5
        stats.files_modified = 3
        stats.total_replacements = 12

        self.assertEqual(stats.files_processed, 5)
        self.assertEqual(stats.files_modified, 3)
        self.assertEqual(stats.total_replacements, 12)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestStrongToH4Replacement))
    suite.addTests(loader.loadTestsFromTestCase(TestReplacementStats))

    # Run with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run:     {result.testsRun}")
    print(f"Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
