# core.source_system.feed_parser

**File:** `Application/core/source_system/feed_parser.py`

## Description

Feed parser abstraction for RSS and Atom feeds.
Provides clean separation of feed parsing logic.

## Constants

### ATOM_NS

**Value:** `{'atom': 'http://www.w3.org/2005/Atom'}`

## Classes

### FeedItem

Represents a single item from a feed.


### FeedParser

**Inherits from:** ABC

Base class for feed parsers.

#### Methods

##### parse

```python
def parse(self, content: bytes) -> List[FeedItem]
```

Parse feed content into FeedItem objects.

Args:
    content: Raw feed content as bytes

Returns:
    List of FeedItem objects

**Parameters:**

- `self`
- `content` (bytes)

**Returns:** List[FeedItem]


### RSSParser

**Inherits from:** FeedParser

Parser for RSS 2.0 feeds.

#### Methods

##### parse

```python
def parse(self, content: bytes) -> List[FeedItem]
```

Parse RSS feed content.

Args:
    content: Raw RSS content as bytes

Returns:
    List of FeedItem objects sorted by date (most recent first)

**Parameters:**

- `self`
- `content` (bytes)

**Returns:** List[FeedItem]

##### _get_text

```python
def _get_text(element) -> str
```

Extract and clean text from XML element.

**Parameters:**

- `element`

**Returns:** str

##### _parse_rss_date

```python
def _parse_rss_date(element) -> Optional[datetime]
```

Parse RSS pubDate to datetime.

RSS uses RFC 822/2822 format: "Mon, 08 Dec 2025 12:00:00 GMT"

Args:
    element: XML element containing date

Returns:
    datetime object or None if parsing fails

**Parameters:**

- `element`

**Returns:** Optional[datetime]


### AtomParser

**Inherits from:** FeedParser

Parser for Atom feeds.

#### Methods

##### parse

```python
def parse(self, content: bytes) -> List[FeedItem]
```

Parse Atom feed content.

Args:
    content: Raw Atom content as bytes

Returns:
    List of FeedItem objects sorted by date (most recent first)

**Parameters:**

- `self`
- `content` (bytes)

**Returns:** List[FeedItem]

##### _extract_title

```python
def _extract_title(self, entry) -> Optional[str]
```

Extract title from Atom entry.

**Parameters:**

- `self`
- `entry`

**Returns:** Optional[str]

##### _extract_link

```python
def _extract_link(self, entry) -> Optional[str]
```

Extract link from Atom entry.

**Parameters:**

- `self`
- `entry`

**Returns:** Optional[str]

##### _extract_description

```python
def _extract_description(self, entry) -> Optional[str]
```

Extract description/summary from Atom entry.

**Parameters:**

- `self`
- `entry`

**Returns:** Optional[str]

##### _extract_date

```python
def _extract_date(self, entry) -> Optional[datetime]
```

Extract publication date from Atom entry.

Atom uses <published> and <updated> tags in ISO 8601 format.

Args:
    entry: Atom entry element

Returns:
    datetime object or None if parsing fails

**Parameters:**

- `self`
- `entry`

**Returns:** Optional[datetime]

##### _get_text

```python
def _get_text(element) -> str
```

Extract and clean text from XML element.

**Parameters:**

- `element`

**Returns:** str


### FeedParserFactory

Factory for creating appropriate feed parsers.

#### Methods

##### detect_and_parse

```python
def detect_and_parse(content: bytes) -> List[FeedItem]
```

Auto-detect feed type and parse.

Args:
    content: Raw feed content as bytes

Returns:
    List of FeedItem objects

Raises:
    ValueError: If feed format is unrecognized or invalid

**Parameters:**

- `content` (bytes)

**Returns:** List[FeedItem]


