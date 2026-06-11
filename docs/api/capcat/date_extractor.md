---
layout: default
render_with_liquid: false
---

# capcat.core.date_extractor

**File:** `Application/capcat/core/date_extractor.py`

## Description

Extract publication dates from HTML pages. No network calls.

## Functions

### extract_publish_date

```python
def extract_publish_date(soup: BeautifulSoup) -> Optional[str]
```

Extract publication date from parsed HTML.

Priority:
1. JSON-LD datePublished
2. <meta property="article:published_time">
3. First <time datetime="..."> element

Args:
    soup: Already-parsed BeautifulSoup object. No HTTP requests made.

Returns:
    ISO date string or None if no date found.

**Parameters:**

- `soup` (BeautifulSoup)

**Returns:** Optional[str]

### _extract_from_json_ld

```python
def _extract_from_json_ld(data) -> Optional[str]
```

Extract datePublished from JSON-LD data (dict or list).

**Parameters:**

- `data`

**Returns:** Optional[str]

