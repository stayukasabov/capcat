---
layout: default
---

# capcat.core.source_system.feed_parser

**File:** `Application/capcat/core/source_system/feed_parser.py`

## Description

Feed parser abstraction for RSS and Atom feeds.
Provides clean separation of feed parsing logic.

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

Raises:
    ValueError: If the content cannot be parsed as RSS

**Parameters:**

- `self`
- `content` (bytes)

**Returns:** List[FeedItem]


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

Raises:
    ValueError: If the content cannot be parsed as Atom

**Parameters:**

- `self`
- `content` (bytes)

**Returns:** List[FeedItem]


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


## Functions

### _parse_feedparser_date

```python
def _parse_feedparser_date(time_struct) -> Optional[datetime]
```

Convert a feedparser time_struct to datetime.

Args:
    time_struct: A time.struct_time returned by feedparser

Returns:
    datetime object or None

**Parameters:**

- `time_struct`

**Returns:** Optional[datetime]

### _entries_to_feed_items

```python
def _entries_to_feed_items(entries) -> List[FeedItem]
```

Convert feedparser entries to FeedItem objects sorted by date.

Args:
    entries: Sequence of feedparser entry objects

Returns:
    List of FeedItem objects sorted by date (most recent first)

**Parameters:**

- `entries`

**Returns:** List[FeedItem]

