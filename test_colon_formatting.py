#!/usr/bin/env python3
"""
test_colon_formatting.py

Comprehensive test suite for fix_colon_formatting.py
Tests pattern matching, edge cases, and preservation logic.

Usage:
    python3 test_colon_formatting.py
    pytest test_colon_formatting.py -v
"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Mock pytest.fixture for standalone mode
    def pytest_fixture_mock(func):
        return func

    class pytest:
        fixture = staticmethod(pytest_fixture_mock)

from fix_colon_formatting import ColonFormattingFixer


class TestColonFormattingFixer:
    """Test suite for ColonFormattingFixer."""

    @pytest.fixture
    def fixer(self):
        """Create fixer instance for testing."""
        return ColonFormattingFixer(dry_run=True, create_backup=False)

    def test_line_starting_with_colon(self, fixer):
        """Test: Line starting with colon should be fixed."""
        line = ": htmlgen/base/templates/ using clean {{}} syntax\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "htmlgen/base/templates/ using clean {{}} syntax\n"

    def test_line_starting_with_colon_no_newline(self, fixer):
        """Test: Line starting with colon without newline."""
        line = ": content here"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "content here"

    def test_line_with_whitespace_then_colon(self, fixer):
        """Test: Line with indentation then colon."""
        line = "    : htmlgen/[source]/templates/ for custom layouts\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "    htmlgen/[source]/templates/ for custom layouts\n"

    def test_line_with_tabs_then_colon(self, fixer):
        """Test: Line with tabs then colon."""
        line = "\t\t: Some content\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "\t\tSome content\n"

    def test_colon_in_middle_of_line(self, fixer):
        """Test: Colon in middle of line should NOT be modified."""
        line = "This is a line: with colon in middle\n"
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_multiple_colons_not_at_start(self, fixer):
        """Test: Multiple colons not at start should NOT be modified."""
        line = "URL: https://example.com:8080/path\n"
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_url_with_colons(self, fixer):
        """Test: URLs with colons should NOT be modified."""
        line = "Visit https://example.com for more info\n"
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_code_block_with_colon(self, fixer):
        """Test: Code blocks with colons should NOT be modified."""
        line = "def function(arg: str) -> None:\n"
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_empty_line_after_colon(self, fixer):
        """Test: Line with only colon and whitespace."""
        line = "  :\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "  \n"

    def test_colon_only(self, fixer):
        """Test: Line with only colon."""
        line = ":\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "\n"

    def test_colon_with_space_after(self, fixer):
        """Test: Colon with space after should remove both."""
        line = ": content\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "content\n"

    def test_colon_with_multiple_spaces_after(self, fixer):
        """Test: Colon with multiple spaces after."""
        line = ":    content with spaces\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "   content with spaces\n"

    def test_indentation_preservation_spaces(self, fixer):
        """Test: Preserve exact space indentation."""
        line = "        : deeply indented content\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "        deeply indented content\n"
        assert result.startswith("        ")

    def test_indentation_preservation_mixed(self, fixer):
        """Test: Preserve mixed whitespace indentation."""
        line = "\t  \t: mixed indent\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "\t  \tmixed indent\n"

    def test_html_with_colon_attribute(self, fixer):
        """Test: HTML attributes with colons should NOT be modified."""
        line = '<div class="item" data-value="test:value">\n'
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_css_style_with_colon(self, fixer):
        """Test: CSS styles with colons should NOT be modified."""
        line = "color: #333; font-size: 14px;\n"
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_normal_text_no_colon(self, fixer):
        """Test: Normal text without colon."""
        line = "This is normal text\n"
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_empty_line(self, fixer):
        """Test: Empty line should remain unchanged."""
        line = "\n"
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_whitespace_only_line(self, fixer):
        """Test: Whitespace-only line should remain unchanged."""
        line = "    \n"
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_real_world_example_1(self, fixer):
        """Test: Real-world example from docs."""
        line = ": htmlgen/base/templates/ using clean {{}} syntax\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "htmlgen/base/templates/ using clean {{}} syntax\n"
        assert not result.startswith(":")

    def test_real_world_example_2(self, fixer):
        """Test: Real-world example with indentation."""
        line = "  : htmlgen/[source]/templates/ for custom layouts\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "  htmlgen/[source]/templates/ for custom layouts\n"
        assert result.startswith("  ")
        assert not result.strip().startswith(":")

    def test_colon_with_content_containing_colons(self, fixer):
        """Test: Leading colon removed, internal colons preserved."""
        line = ": URL format is https://example.com:8080\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "URL format is https://example.com:8080\n"
        assert "https://example.com:8080" in result

    def test_json_like_structure(self, fixer):
        """Test: JSON-like structure should NOT be modified."""
        line = '"key": "value",\n'
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_time_format(self, fixer):
        """Test: Time formats should NOT be modified."""
        line = "Time: 10:30:45 AM\n"
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_ratio_format(self, fixer):
        """Test: Ratio formats should NOT be modified."""
        line = "Aspect ratio 16:9\n"
        result, modified = fixer.fix_line(line)
        assert modified is False
        assert result == line

    def test_heading_followed_by_colon_line(self, fixer):
        """Test: Process each line independently."""
        lines = [
            "<h4>Base Templates</h4>\n",
            ": htmlgen/base/templates/ using clean {{}} syntax\n"
        ]
        results = [fixer.fix_line(line) for line in lines]

        # First line unchanged
        assert results[0][1] is False
        assert results[0][0] == lines[0]

        # Second line fixed
        assert results[1][1] is True
        assert results[1][0] == "htmlgen/base/templates/ using clean {{}} syntax\n"

    def test_consecutive_colon_lines(self, fixer):
        """Test: Multiple consecutive colon lines."""
        lines = [
            ": First line\n",
            ": Second line\n",
            ": Third line\n"
        ]
        results = [fixer.fix_line(line) for line in lines]

        for i, (result, modified) in enumerate(results):
            assert modified is True
            assert result == f"{['First', 'Second', 'Third'][i]} line\n"


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.fixture
    def fixer(self):
        """Create fixer instance."""
        return ColonFormattingFixer(dry_run=True, create_backup=False)

    def test_unicode_content(self, fixer):
        """Test: Unicode content after colon."""
        line = ": Content with unicode: 你好世界 🌍\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "Content with unicode: 你好世界 🌍\n"

    def test_very_long_line(self, fixer):
        """Test: Very long line processing."""
        content = "x" * 1000
        line = f": {content}\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == f"{content}\n"
        assert len(result) == len(content) + 1

    def test_special_html_entities(self, fixer):
        """Test: HTML entities should be preserved."""
        line = ": Content with &nbsp; and &lt;tag&gt;\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "Content with &nbsp; and &lt;tag&gt;\n"
        assert "&nbsp;" in result
        assert "&lt;" in result

    def test_windows_line_ending(self, fixer):
        """Test: Windows line endings."""
        line = ": content\r\n"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "content\r\n"

    def test_no_line_ending(self, fixer):
        """Test: Line without ending (last line in file)."""
        line = ": content"
        result, modified = fixer.fix_line(line)
        assert modified is True
        assert result == "content"
        assert not result.endswith("\n")


def run_manual_tests():
    """Run manual tests with output."""
    print("Running manual tests...\n")

    fixer = ColonFormattingFixer(dry_run=True, create_backup=False)

    test_cases = [
        ": htmlgen/base/templates/ using clean {{}} syntax",
        "  : htmlgen/[source]/templates/ for custom layouts",
        "Normal line: with colon in middle",
        "https://example.com:8080/path",
        "\t: Tab indented",
        ":",
        ":   ",
        "  :  ",
    ]

    for i, line in enumerate(test_cases, 1):
        result, modified = fixer.fix_line(line + "\n")
        status = "MODIFIED" if modified else "UNCHANGED"
        print(f"Test {i} [{status}]:")
        print(f"  Input:  {repr(line)}")
        print(f"  Output: {repr(result.rstrip())}")
        print()


if __name__ == '__main__':
    # Run manual tests
    run_manual_tests()

    # Run pytest if available
    if PYTEST_AVAILABLE:
        pytest.main([__file__, '-v'])
    else:
        print("pytest not available. Install with: pip install pytest")
        print("Manual tests completed successfully.")
