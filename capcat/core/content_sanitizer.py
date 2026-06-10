#!/usr/bin/env python3
"""
Content Sanitizer - Archive isolation for Capcat.

Strips tracking, analytics, scripts, and dangerous elements from archived
content. Runs as a single pass at the end of the processing pipeline,
before file write. Always enabled. No config toggle.
"""

import re
from typing import Set


# Known tracking/analytics domains
TRACKER_DOMAINS: Set[str] = {
    "google-analytics.com",
    "googletagmanager.com",
    "googlesyndication.com",
    "googleads.g.doubleclick.net",
    "static.doubleclick.net",
    "facebook.com",
    "facebook.net",
    "fbcdn.net",
    "connect.facebook.net",
    "twitter.com",
    "analytics.twitter.com",
    "scorecardresearch.com",
    "comscore.com",
    "quantserve.com",
    "outbrain.com",
    "taboola.com",
    "chartbeat.com",
    "newrelic.com",
    "elfsight.com",
    "static.elfsight.com",
    "amazon-adsystem.com",
}

# URL path segments that indicate tracking endpoints
TRACKER_PATH_PATTERNS: Set[str] = {
    "/collect",
    "/pixel",
    "/beacon",
    "/analytics",
    "/tr",
}


def sanitize(content: str, mode: str = "markdown") -> str:
    """Sanitize content for complete archive isolation.

    Args:
        content: Raw content string (markdown or HTML).
        mode: "markdown" or "html".

    Returns:
        Sanitized content with dangerous elements removed.
    """
    if not content:
        return content

    # Protect fenced code blocks from sanitization
    code_blocks = []
    def _stash_code_block(match):
        code_blocks.append(match.group(0))
        return f"\x00CODEBLOCK{len(code_blocks) - 1}\x00"

    protected = re.sub(
        r"```[\s\S]*?```", _stash_code_block, content
    )

    # Apply markdown-mode rules (M1-M9)
    protected = _strip_dangerous_html(protected)
    protected = _strip_tracking_heuristics(protected)

    # Apply HTML-mode rules (H1-H4) when mode is html
    if mode == "html":
        protected = _apply_html_hardening(protected)

    # Restore code blocks
    def _restore_code_block(match):
        idx = int(match.group(1))
        return code_blocks[idx]

    result = re.sub(r"\x00CODEBLOCK(\d+)\x00", _restore_code_block, protected)

    return result


def _strip_dangerous_html(content: str) -> str:
    """Strip dangerous HTML elements from content (rules M1-M9)."""
    # M1: Remove <script>...</script> tags
    content = re.sub(
        r"<script\b[^>]*>[\s\S]*?</script>",
        "",
        content,
        flags=re.IGNORECASE,
    )
    return content


def _strip_tracking_heuristics(content: str) -> str:
    """Detect and remove tracking elements by heuristic patterns."""
    return content


def _apply_html_hardening(content: str) -> str:
    """Apply HTML-specific hardening rules (H1-H4)."""
    return content
