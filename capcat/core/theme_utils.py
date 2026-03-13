#!/usr/bin/env python3
"""
Theme utilities for hash-based theme persistence.

Provides functions for injecting theme hashes into HTML links
and parsing theme from URL hashes.
"""

import re
from typing import Optional


def inject_theme_hash(html: str, theme: str) -> str:
    """
    Inject theme hash into HTML links.

    Args:
        html: HTML content with links
        theme: Current theme ('light' or 'dark')

    Returns:
        HTML with theme hash appended to internal links
    """

    def replace_link(match):
        full_match = match.group(0)
        href = match.group(1)

        # Skip external links (http://, https://, //)
        if re.match(r'^(https?:|//)', href, re.IGNORECASE):
            return full_match

        # Skip special protocols
        if re.match(r'^(mailto:|javascript:|tel:|ftp:)', href, re.IGNORECASE):
            return full_match

        # Handle existing hash
        if '#' in href:
            # Preserve existing anchor, append theme with &
            return f'href="{href}&theme={theme}"'

        # Handle query params
        if '?' in href:
            return f'href="{href}#theme={theme}"'

        # Simple relative link
        return f'href="{href}#theme={theme}"'

    # Replace all href attributes
    pattern = r'href="([^"]+)"'
    result = re.sub(pattern, replace_link, html)

    return result


def parse_theme_from_hash(hash_value: str) -> Optional[str]:
    """
    Parse theme from URL hash.

    Args:
        hash_value: URL hash string (e.g., '#theme=light')

    Returns:
        Theme value or None if not found
    """
    if not hash_value:
        return None

    # Remove leading #
    hash_value = hash_value.lstrip('#')

    # Match theme=light or theme=dark
    match = re.search(r'theme=(light|dark)', hash_value)

    if match:
        return match.group(1)

    return None
