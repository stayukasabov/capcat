"""Extract publication dates from HTML pages. No network calls."""

import json
from typing import Optional

from bs4 import BeautifulSoup


def extract_publish_date(soup: BeautifulSoup) -> Optional[str]:
    """Extract publication date from parsed HTML.

    Priority:
    1. JSON-LD datePublished
    2. <meta property="article:published_time">
    3. First <time datetime="..."> element

    Args:
        soup: Already-parsed BeautifulSoup object. No HTTP requests made.

    Returns:
        ISO date string or None if no date found.
    """
    # 1. JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
            date = _extract_from_json_ld(data)
            if date:
                return date
        except (json.JSONDecodeError, TypeError):
            continue

    # 2. Meta tag
    meta = soup.find("meta", property="article:published_time")
    if meta and meta.get("content"):
        return meta["content"]

    # 3. <time> element
    time_el = soup.find("time", attrs={"datetime": True})
    if time_el and time_el["datetime"].strip():
        return time_el["datetime"].strip()

    return None


def _extract_from_json_ld(data) -> Optional[str]:
    """Extract datePublished from JSON-LD data (dict or list)."""
    if isinstance(data, dict):
        if "datePublished" in data:
            return data["datePublished"]
        if "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                result = _extract_from_json_ld(item)
                if result:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = _extract_from_json_ld(item)
            if result:
                return result
    return None
