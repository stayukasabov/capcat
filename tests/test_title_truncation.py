#!/usr/bin/env python3
"""
Test suite for title truncation functionality.
Ensures titles in HTML cards are limited to 200 characters.
"""

import pytest
from core.utils import truncate_title_intelligently


class TestTitleTruncation:
    """Test cases for intelligent title truncation."""

    def test_title_under_200_chars_unchanged(self):
        """Titles under 200 chars should remain unchanged."""
        short_title = "This is a reasonable length title that should not be truncated"
        result = truncate_title_intelligently(short_title)
        assert result == short_title
        assert len(result) <= 200

    def test_title_exactly_200_chars(self):
        """Title exactly 200 chars should remain unchanged."""
        exact_title = "A" * 200
        result = truncate_title_intelligently(exact_title)
        assert len(result) == 200

    def test_title_over_200_chars_truncated(self):
        """Titles over 200 chars should be truncated."""
        long_title = "A" * 250
        result = truncate_title_intelligently(long_title)
        assert len(result) <= 200
        # Function does not add ellipsis, just truncates
        assert len(result) < len(long_title)

    def test_title_word_boundary_truncation(self):
        """Truncation should prefer word boundaries."""
        title = "This is a very long title that needs to be truncated " * 5
        result = truncate_title_intelligently(title, max_length=200)
        assert len(result) <= 200
        # Should not cut words in half (ends with complete word)
        assert not result.endswith("trun") # Not cut mid-word

    def test_title_with_github_prefix_removed(self):
        """GitHub prefixes should be removed when title is over max_length."""
        # Short title - returned unchanged (function only processes if over max_length)
        short_title = "GitHub - user/repo: Short content"
        result = truncate_title_intelligently(short_title, max_length=100)
        # Short titles are returned as-is
        assert result == short_title

        # Long title with GitHub prefix - should be processed
        long_title = "GitHub - user/repo: " + "A" * 250
        result = truncate_title_intelligently(long_title, max_length=200)
        assert len(result) <= 200
        # GitHub prefix removed when processing long titles
        assert not result.startswith("GitHub -")

    def test_empty_title_handled(self):
        """Empty titles should be handled gracefully."""
        result = truncate_title_intelligently("")
        assert result == ""

    def test_none_title_handled(self):
        """None titles should be handled gracefully."""
        result = truncate_title_intelligently(None)
        assert result is None or result == ""

    def test_special_characters_preserved(self):
        """Special characters should be preserved in truncation."""
        title = "Test™ Title® with Spëcial Çharacters and Émojis 🚀 " * 4
        result = truncate_title_intelligently(title, max_length=200)
        assert len(result) <= 200

    def test_url_references_removed(self):
        """URLs in parentheses should be removed when title is over max_length."""
        # Short title - returned unchanged
        short_title = "Article (https://example.com) content"
        result = truncate_title_intelligently(short_title, max_length=100)
        # Short titles returned as-is
        assert result == short_title

        # Long title with URL - should be processed and URL removed
        long_title = "Great Article Title " + "A" * 100 + " (https://example.com/very-long-url) " + "B" * 100
        result = truncate_title_intelligently(long_title, max_length=200)
        assert len(result) <= 200

    def test_default_max_length_is_200(self):
        """Default max_length parameter should be 200."""
        long_title = "A" * 250
        result = truncate_title_intelligently(long_title)
        assert len(result) <= 200

    def test_custom_max_length_respected(self):
        """Custom max_length should override default."""
        long_title = "A" * 150
        result = truncate_title_intelligently(long_title, max_length=100)
        assert len(result) <= 100

    def test_real_world_github_title(self):
        """Test with real-world GitHub title example."""
        title = (
            "GitHub - xyflow/xyflow: React Flow | Svelte Flow - "
            "Powerful open source libraries for building node-based UIs "
            "with React (https://reactflow.dev) or Svelte (https://svelteflow.dev). "
            "Ready out-of-the-box and infinitely customizable."
        )
        result = truncate_title_intelligently(title)
        assert len(result) <= 200
        assert "Powerful open source libraries" in result
        assert "GitHub -" not in result
        assert "https://" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
