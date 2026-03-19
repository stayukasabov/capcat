"""
Test for image anchor wrapper removal in HTML generation.

Red-Green-Refactor TDD:
1. RED: Write failing test showing images wrapped in anchor tags
2. GREEN: Implement _remove_image_anchor_wrappers() method
3. REFACTOR: Ensure clean integration and no regressions
"""

import pytest
import re
from pathlib import Path
from core.html_generator import HTMLGenerator


class TestImageAnchorRemoval:
    """Test suite for removing anchor wrappers around downloaded images."""

    def setup_method(self):
        """Setup HTMLGenerator instance for tests."""
        self.html_gen = HTMLGenerator()

    def test_remove_single_image_anchor_wrapper(self):
        """Test removal of anchor tag wrapping a single image."""
        html_input = '<a href="https://example.com/image.jpg"><img src="local/path/image.jpg" alt="Test"></a>'
        expected_output = '<img src="local/path/image.jpg" alt="Test">'

        result = self.html_gen._remove_image_anchor_wrappers(html_input)
        assert result == expected_output, "Single image anchor wrapper should be removed"

    def test_remove_multiple_image_anchor_wrappers(self):
        """Test removal of multiple anchor tags wrapping images."""
        html_input = '''
        <a href="https://example.com/image1.jpg"><img src="local/image1.jpg" alt="First"></a>
        <p>Some text</p>
        <a href="https://example.com/image2.png"><img src="local/image2.png" alt="Second"></a>
        '''

        result = self.html_gen._remove_image_anchor_wrappers(html_input)

        # Images should remain but without anchor wrappers
        assert '<img src="local/image1.jpg" alt="First">' in result
        assert '<img src="local/image2.png" alt="Second">' in result

        # Anchor tags around images should be gone
        assert '<a href="https://example.com/image1.jpg">' not in result
        assert '<a href="https://example.com/image2.png">' not in result

    def test_preserve_regular_links(self):
        """Test that regular text links are preserved."""
        html_input = '''
        <a href="https://example.com/article">Read more</a>
        <a href="https://example.com/image.jpg"><img src="local/image.jpg" alt="Test"></a>
        <a href="https://example.com">Another link</a>
        '''

        result = self.html_gen._remove_image_anchor_wrappers(html_input)

        # Regular links should remain
        assert '<a href="https://example.com/article">Read more</a>' in result
        assert '<a href="https://example.com">Another link</a>' in result

        # Image anchor wrapper should be removed
        assert '<img src="local/image.jpg" alt="Test">' in result
        assert '<a href="https://example.com/image.jpg">' not in result

    def test_preserve_image_attributes(self):
        """Test that all image attributes are preserved during anchor removal."""
        html_input = '<a href="https://example.com/img.jpg"><img src="local/img.jpg" alt="Test Image" class="centered" width="500" height="300"></a>'

        result = self.html_gen._remove_image_anchor_wrappers(html_input)

        # All image attributes should be preserved
        assert 'src="local/img.jpg"' in result
        assert 'alt="Test Image"' in result
        assert 'class="centered"' in result
        assert 'width="500"' in result
        assert 'height="300"' in result

        # Anchor should be gone
        assert '<a href=' not in result

    def test_handle_whitespace_around_image(self):
        """Test anchor removal with whitespace around img tag."""
        html_input = '<a href="https://example.com/image.jpg">\n  <img src="local/image.jpg" alt="Test">\n</a>'

        result = self.html_gen._remove_image_anchor_wrappers(html_input)

        # Image should remain (whitespace handling may vary)
        assert 'src="local/image.jpg"' in result
        assert 'alt="Test"' in result

        # Anchor should be gone
        assert '<a href="https://example.com/image.jpg">' not in result

    def test_handle_anchor_with_additional_attributes(self):
        """Test anchor removal when anchor has multiple attributes."""
        html_input = '<a href="https://example.com/image.jpg" class="image-link" target="_blank"><img src="local/image.jpg" alt="Test"></a>'

        result = self.html_gen._remove_image_anchor_wrappers(html_input)

        # Image should remain
        assert '<img src="local/image.jpg" alt="Test">' in result

        # Anchor should be gone
        assert '<a href=' not in result

    def test_complex_html_structure(self):
        """Test anchor removal in complex HTML with mixed content."""
        html_input = '''
        <div class="article">
            <h2>Article Title</h2>
            <p>Some text with <a href="https://example.com">a link</a> in it.</p>
            <a href="https://example.com/image1.jpg"><img src="local/image1.jpg" alt="Figure 1"></a>
            <p>More text</p>
            <a href="https://example.com/image2.png">
                <img src="local/image2.png" alt="Figure 2">
            </a>
            <p>Final paragraph with <a href="https://example.com/doc">another link</a>.</p>
        </div>
        '''

        result = self.html_gen._remove_image_anchor_wrappers(html_input)

        # Images should remain
        assert '<img src="local/image1.jpg" alt="Figure 1">' in result
        assert '<img src="local/image2.png" alt="Figure 2">' in result

        # Regular links should remain
        assert '<a href="https://example.com">a link</a>' in result
        assert '<a href="https://example.com/doc">another link</a>' in result

        # Image anchor wrappers should be gone
        assert re.search(r'<a[^>]*href="[^"]*image1\.jpg"', result) is None
        assert re.search(r'<a[^>]*href="[^"]*image2\.png"', result) is None

    def test_self_closing_img_tags(self):
        """Test anchor removal with self-closing img tags."""
        html_input = '<a href="https://example.com/image.jpg"><img src="local/image.jpg" alt="Test" /></a>'

        result = self.html_gen._remove_image_anchor_wrappers(html_input)

        # Image should remain
        assert 'src="local/image.jpg"' in result
        assert 'alt="Test"' in result

        # Anchor should be gone
        assert '<a href="https://example.com/image.jpg">' not in result

    def test_no_modification_when_no_image_anchors(self):
        """Test that HTML without image anchors remains unchanged."""
        html_input = '''
        <div>
            <p>Text with <a href="https://example.com">a link</a>.</p>
            <img src="local/standalone.jpg" alt="Standalone image">
            <a href="https://example.com/page">Another link</a>
        </div>
        '''

        result = self.html_gen._remove_image_anchor_wrappers(html_input)

        # Content should be identical
        assert result == html_input


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
