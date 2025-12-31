#!/usr/bin/env python3
"""
Test suite for h4 to h3 tag replacement
Validates that the replacement preserves all attributes and content
"""

import re
from replace_h4_with_h3 import H4ToH3Replacer


def test_basic_replacement():
    """Test basic h4 to h3 replacement."""
    replacer = H4ToH3Replacer('.')

    content = '<h4>Test Header</h4>'
    result, opening, closing = replacer.replace_tags_in_content(content)

    assert result == '<h3>Test Header</h3>', f"Expected '<h3>Test Header</h3>', got '{result}'"
    assert opening == 1, f"Expected 1 opening tag, got {opening}"
    assert closing == 1, f"Expected 1 closing tag, got {closing}"
    print("✓ Basic replacement test passed")


def test_attributes_preserved():
    """Test that attributes are preserved during replacement."""
    replacer = H4ToH3Replacer('.')

    test_cases = [
        ('<h4 class="header">Test</h4>', '<h3 class="header">Test</h3>'),
        ('<h4 id="test-id">Test</h4>', '<h3 id="test-id">Test</h3>'),
        ('<h4 class="foo" id="bar">Test</h4>', '<h3 class="foo" id="bar">Test</h3>'),
        ('<h4 style="color: red;">Test</h4>', '<h3 style="color: red;">Test</h3>'),
        ('<h4 class="header" data-test="value">Test</h4>', '<h3 class="header" data-test="value">Test</h3>'),
    ]

    for input_html, expected in test_cases:
        result, _, _ = replacer.replace_tags_in_content(input_html)
        assert result == expected, f"Expected '{expected}', got '{result}'"

    print("✓ Attributes preserved test passed")


def test_multiple_tags():
    """Test multiple h4 tags in same content."""
    replacer = H4ToH3Replacer('.')

    content = '''
    <h4>First Header</h4>
    <p>Some content</p>
    <h4 class="second">Second Header</h4>
    <h4 id="third">Third Header</h4>
    '''

    expected = '''
    <h3>First Header</h3>
    <p>Some content</p>
    <h3 class="second">Second Header</h3>
    <h3 id="third">Third Header</h3>
    '''

    result, opening, closing = replacer.replace_tags_in_content(content)

    assert result == expected, f"Multiple tags replacement failed"
    assert opening == 3, f"Expected 3 opening tags, got {opening}"
    assert closing == 3, f"Expected 3 closing tags, got {closing}"
    print("✓ Multiple tags test passed")


def test_nested_content():
    """Test h4 tags with nested content."""
    replacer = H4ToH3Replacer('.')

    content = '<h4>Header with <strong>bold</strong> text</h4>'
    expected = '<h3>Header with <strong>bold</strong> text</h3>'

    result, _, _ = replacer.replace_tags_in_content(content)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ Nested content test passed")


def test_case_insensitivity():
    """Test that replacement works for different case variations."""
    replacer = H4ToH3Replacer('.')

    test_cases = [
        '<h4>Test</h4>',
        '<H4>Test</H4>',
        '<H4>Test</h4>',  # Mixed case
        '<h4>Test</H4>',  # Mixed case
    ]

    for content in test_cases:
        result, opening, closing = replacer.replace_tags_in_content(content)
        # Should have lowercase h3 tags
        assert '<h3>Test</h3>' in result or '<h3>Test</h3>' == result, \
            f"Case insensitive replacement failed for '{content}', got '{result}'"

    print("✓ Case insensitivity test passed")


def test_no_replacement_needed():
    """Test content without h4 tags."""
    replacer = H4ToH3Replacer('.')

    content = '''
    <h1>Main Header</h1>
    <h2>Subheader</h2>
    <h3>Already h3</h3>
    <p>Regular content</p>
    '''

    result, opening, closing = replacer.replace_tags_in_content(content)

    assert result == content, "Content should remain unchanged"
    assert opening == 0, f"Expected 0 opening tags, got {opening}"
    assert closing == 0, f"Expected 0 closing tags, got {closing}"
    print("✓ No replacement needed test passed")


def test_whitespace_preservation():
    """Test that whitespace is preserved."""
    replacer = H4ToH3Replacer('.')

    content = '<h4  class="test"  id="foo"  >Content</h4>'
    expected = '<h3  class="test"  id="foo"  >Content</h3>'

    result, _, _ = replacer.replace_tags_in_content(content)
    assert result == expected, f"Whitespace not preserved: '{result}'"
    print("✓ Whitespace preservation test passed")


def test_multiline_content():
    """Test h4 tags with content spanning multiple lines."""
    replacer = H4ToH3Replacer('.')

    content = '''<h4 class="header"
         id="test"
         data-value="123">
    Multi-line header content
</h4>'''

    expected = '''<h3 class="header"
         id="test"
         data-value="123">
    Multi-line header content
</h3>'''

    result, _, _ = replacer.replace_tags_in_content(content)
    assert result == expected, "Multiline content replacement failed"
    print("✓ Multiline content test passed")


def test_real_world_example():
    """Test with real HTML from the docs."""
    replacer = H4ToH3Replacer('.')

    content = '''
                        <h4>Documentation</h4>
                        <ul>
                            <li><a href="docs/index.html">Documentation Home</a></li>
                        </ul>
    '''

    expected = '''
                        <h3>Documentation</h3>
                        <ul>
                            <li><a href="docs/index.html">Documentation Home</a></li>
                        </ul>
    '''

    result, _, _ = replacer.replace_tags_in_content(content)
    assert result == expected, "Real world example failed"
    print("✓ Real world example test passed")


def test_no_new_symbols():
    """Verify that no new symbols are added, only replacement occurs."""
    replacer = H4ToH3Replacer('.')

    content = '<div><h4 class="test">Header</h4><p>Text</p></div>'
    result, _, _ = replacer.replace_tags_in_content(content)

    # Count all characters except for the h3/h4 difference
    content_without_h4 = content.replace('<h4', '').replace('</h4>', '')
    result_without_h3 = result.replace('<h3', '').replace('</h3>', '')

    assert content_without_h4 == result_without_h3, "New symbols were added"
    print("✓ No new symbols test passed")


def run_all_tests():
    """Run all test cases."""
    print("\nRunning H4 to H3 Replacement Tests")
    print("=" * 60)

    tests = [
        test_basic_replacement,
        test_attributes_preserved,
        test_multiple_tags,
        test_nested_content,
        test_case_insensitivity,
        test_no_replacement_needed,
        test_whitespace_preservation,
        test_multiline_content,
        test_real_world_example,
        test_no_new_symbols,
    ]

    failed = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed.append((test.__name__, str(e)))
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed.append((test.__name__, str(e)))

    print("=" * 60)
    if failed:
        print(f"\n{len(failed)} test(s) failed:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        return False
    else:
        print(f"\nAll {len(tests)} tests passed!")
        return True


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
