# core.source_system.feed_discovery

**File:** `Application/core/source_system/feed_discovery.py`

## Description

RSS/Atom feed discovery utilities.
Automatically discovers feed URLs from websites when configured feeds fail.

## Functions

### discover_feed_urls

```python
def discover_feed_urls(base_url: str, timeout: int = 10) -> List[str]
```

Attempt to discover RSS/Atom feed URLs from a website.

Looks for:
- <link rel="alternate" type="application/rss+xml"> in HTML
- <link rel="alternate" type="application/atom+xml"> in HTML
- Common feed paths: /feed, /rss, /atom, /feed.xml, /rss.xml

Args:
    base_url: Base URL of the website
    timeout: Request timeout in seconds

Returns:
    List of discovered feed URLs (may be empty)

**Parameters:**

- `base_url` (str)
- `timeout` (int) *optional*

**Returns:** List[str]

### validate_feed

```python
def validate_feed(content: bytes) -> bool
```

Quick validation that content is a valid RSS/Atom feed.

Args:
    content: Raw feed content as bytes

Returns:
    True if content appears to be a valid feed

**Parameters:**

- `content` (bytes)

**Returns:** bool

### test_feed_url

```python
def test_feed_url(url: str, timeout: int = 10) -> bool
```

Test if a URL returns a valid feed.

Args:
    url: URL to test
    timeout: Request timeout in seconds

Returns:
    True if URL returns a valid feed

**Parameters:**

- `url` (str)
- `timeout` (int) *optional*

**Returns:** bool

### find_working_feed_url

```python
def find_working_feed_url(base_url: str, timeout: int = 10) -> str
```

Discover and return first working feed URL for a website.

Args:
    base_url: Base URL of the website
    timeout: Request timeout in seconds

Returns:
    First working feed URL found

Raises:
    ValueError: If no working feed URL is found

**Parameters:**

- `base_url` (str)
- `timeout` (int) *optional*

**Returns:** str

