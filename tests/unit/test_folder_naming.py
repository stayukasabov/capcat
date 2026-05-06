"""
Tests for get_source_folder_name canonical folder name format.

Canonical format: Source-Name_DD-MM-YYYY
Word separator: hyphen (-)
Date separator: underscore (_)
"""
from __future__ import annotations


def test_hn_folder_name_uses_hyphens():
    """'Hacker News' display_name must produce 'Hacker-News', not 'Hacker_News'."""
    from capcat.core.utils import get_source_folder_name
    result = get_source_folder_name("hn")
    assert result == "Hacker-News", f"Expected 'Hacker-News', got '{result}'"


def test_folder_name_contains_no_underscores_as_word_separators():
    """Word separators must be hyphens - no underscores allowed in the source name."""
    from capcat.core.utils import get_source_folder_name
    result = get_source_folder_name("hn")
    assert "_" not in result, f"Underscore found in folder name: '{result}'"
