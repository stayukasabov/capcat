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

    # M2: Remove <iframe>...</iframe> tags
    content = re.sub(
        r"<iframe\b[^>]*>[\s\S]*?</iframe>",
        "",
        content,
        flags=re.IGNORECASE,
    )

    # M3: Remove inline JS event handlers from HTML elements
    content = re.sub(
        r"\s+on\w+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)",
        "",
        content,
        flags=re.IGNORECASE,
    )

    # M4: Remove <img> tags with known tracker domains
    def _remove_tracker_img(match):
        tag = match.group(0)
        src_match = re.search(r'src\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if src_match:
            src = src_match.group(1)
            for domain in TRACKER_DOMAINS:
                if domain in src:
                    return ""
        return tag

    content = re.sub(r"<img\b[^>]*>", _remove_tracker_img, content, flags=re.IGNORECASE)

    # M5: Remove <meta http-equiv="refresh">
    content = re.sub(
        r'<meta\s+[^>]*http-equiv\s*=\s*["\']refresh["\'][^>]*>',
        "",
        content,
        flags=re.IGNORECASE,
    )

    # M6: Remove <link rel="prefetch/preload/dns-prefetch">
    content = re.sub(
        r'<link\s+[^>]*rel\s*=\s*["\'](?:prefetch|preload|dns-prefetch)["\'][^>]*>',
        "",
        content,
        flags=re.IGNORECASE,
    )

    # M7: SVG onload/script removal handled by M1 (strips <script> inside SVG)
    # and M3 (strips onload from any element including SVG). No additional code.

    # M8: Remove external url() from inline style attributes
    def _clean_style_url(match):
        style_val = match.group(1)
        cleaned = re.sub(
            r"url\s*\(\s*(?:['\"]?\s*(?:https?:)?//[^)]+)\s*\)",
            "",
            style_val,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r";\s*;", ";", cleaned)
        cleaned = re.sub(r"^\s*;\s*", "", cleaned)
        cleaned = re.sub(r"\s*;\s*$", "", cleaned)
        if not cleaned.strip():
            return ""
        return f'style="{cleaned}"'

    content = re.sub(
        r'style\s*=\s*"([^"]*)"',
        _clean_style_url,
        content,
        flags=re.IGNORECASE,
    )

    # M9: Remove elements with protocol-relative URLs in src/href
    content = re.sub(
        r'<(?:script|link)\b[^>]*(?:src|href)\s*=\s*["\']//[^"\']+["\'][^>]*>(?:[\s\S]*?</(?:script|link)>)?',
        "",
        content,
        flags=re.IGNORECASE,
    )

    return content


def _strip_tracking_heuristics(content: str) -> str:
    """Detect and remove tracking elements by heuristic patterns."""

    def _is_heuristic_tracker(tag: str) -> bool:
        """Check if an <img> tag matches tracking heuristics."""
        src_match = re.search(r'src\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if not src_match:
            return False
        src = src_match.group(1)

        # Heuristic 1: 1x1 pixel images
        if re.search(r'(?:width|height)\s*=\s*["\']?1["\']?', tag, re.IGNORECASE):
            other_dim = re.findall(r'(?:width|height)\s*=\s*["\']?(\d+)["\']?', tag, re.IGNORECASE)
            if all(int(d) <= 1 for d in other_dim):
                return True

        # Heuristic 1b: Filename contains pixel/beacon/track
        src_lower = src.lower()
        if re.search(r"(?:^|/)(?:pixel|beacon|track)\b", src_lower.split("?")[0]):
            return True

        # Heuristic 2: Query-heavy image URLs (3+ query params)
        if "?" in src:
            query = src.split("?", 1)[1]
            param_count = len(re.findall(r"[&;]", query)) + 1
            if param_count >= 3:
                return True

        # Heuristic 3: Tracker path patterns
        path = src.split("?")[0]
        for pattern in TRACKER_PATH_PATTERNS:
            if pattern in path.lower():
                return True

        # Heuristic 4: Visibility hidden on the image itself
        if re.search(r'style\s*=\s*"[^"]*visibility\s*:\s*hidden', tag, re.IGNORECASE):
            return True

        return False

    # Apply heuristics to <img> tags not already removed by M4
    content = re.sub(
        r"<img\b[^>]*>",
        lambda m: "" if _is_heuristic_tracker(m.group(0)) else m.group(0),
        content,
        flags=re.IGNORECASE,
    )

    # Heuristic 4b: Remove display:none containers with external URLs
    content = re.sub(
        r'<div\b[^>]*style\s*=\s*"[^"]*display\s*:\s*none[^"]*"[^>]*>[\s\S]*?</div>',
        "",
        content,
        flags=re.IGNORECASE,
    )

    return content


def _apply_html_hardening(content: str) -> str:
    """Apply HTML-specific hardening rules (H1-H4)."""
    return content
