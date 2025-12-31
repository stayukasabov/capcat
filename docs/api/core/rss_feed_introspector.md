# core.source_system.rss_feed_introspector

**File:** `Application/core/source_system/rss_feed_introspector.py`

## Classes

### RssFeedIntrospector

Fetches, parses, and validates an RSS feed to extract key metadata.

#### Methods

##### __init__

```python
def __init__(self, url: str)
```

Args:
    url: The URL of the RSS feed.

Raises:
    ValidationError: If the URL is invalid.
    NetworkError: If there's a problem fetching the feed.
    InvalidFeedError: If the content is not a valid feed.

**Parameters:**

- `self`
- `url` (str)

##### _validate_url

```python
def _validate_url(self, url: str) -> str
```

Validates the given URL.

**Parameters:**

- `self`
- `url` (str)

**Returns:** str

##### _fetch_feed

```python
def _fetch_feed(self) -> str
```

Fetches the raw content of the feed from the URL.

**Parameters:**

- `self`

**Returns:** str

##### _parse_feed

```python
def _parse_feed(self)
```

Parses the raw feed content.

**Parameters:**

- `self`

##### _extract_feed_title

```python
def _extract_feed_title(self) -> str
```

Extracts the title from the parsed feed.

**Parameters:**

- `self`

**Returns:** str

##### _extract_base_url

```python
def _extract_base_url(self) -> str
```

Extracts the base URL from the feed's link or the original URL.

**Parameters:**

- `self`

**Returns:** str


