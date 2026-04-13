"""Resolve direct PDF URLs to their HTML landing pages where possible.

Returns None for unknown domains so the caller can fall back to a stub article.
"""
import re
from typing import Optional
from urllib.parse import urlparse


def resolve_pdf_to_landing_page(url: str) -> Optional[str]:
    """Return an HTML landing-page URL for a known PDF URL pattern, or None."""
    parsed = urlparse(url)
    host = parsed.netloc.lower().lstrip("www.")
    path = parsed.path

    if not path.lower().endswith(".pdf") and "/pdf/" not in path.lower():
        # Quick reject: not obviously a PDF link
        if not _looks_like_pdf_path(path):
            return None

    # arxiv: /pdf/XXXX.XXXXXvN.pdf  →  /abs/XXXX.XXXXXvN
    if host == "arxiv.org":
        match = re.match(r"^/pdf/(.+?)(?:\.pdf)?$", path, re.IGNORECASE)
        if match:
            return f"https://arxiv.org/abs/{match.group(1)}"
        return None

    # biorxiv / medrxiv: /content/DOI.full.pdf  →  /content/DOI
    if host in ("biorxiv.org", "medrxiv.org"):
        clean = re.sub(r"(?:\.full)?\.pdf$", "", path, flags=re.IGNORECASE)
        if clean != path:
            return f"https://{parsed.netloc}{clean}"
        return None

    return None


def _looks_like_pdf_path(path: str) -> bool:
    return path.lower().endswith(".pdf")
