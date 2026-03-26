# capcat.core.source_system.base_source

**File:** `Application/capcat/core/source_system/base_source.py`

## Description

Abstract base class for all news sources.
Defines the contract that all source implementations must follow.

## Classes

### SourceConfig

Configuration data class for news sources.

Attributes:
    name: Machine-readable identifier (e.g. ``"hn"``).
    display_name: Human-readable name shown in menus (e.g. ``"Hacker News"``).
    base_url: Root URL of the source.
    timeout: HTTP request timeout in seconds.
    rate_limit: Minimum delay between requests in seconds.
    supports_comments: True if the source has comment threads.
    has_comments: True if the current fetch includes comments.
    category: Topic category (e.g. ``"tech"``, ``"science"``).
    custom_config: Source-specific extra config key/value pairs.

#### Methods

##### __post_init__

```python
def __post_init__(self) -> None
```

Ensure custom_config is never None after construction.

**Parameters:**

- `self`

**Returns:** None

##### to_dict

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary format for compatibility.

Returns:
    Dictionary representation of the source configuration

**Parameters:**

- `self`

**Returns:** Dict[str, Any]


### Article

Lightweight data transfer object for a single news article.

Attributes:
    title: Article headline.
    url: Canonical URL of the article.
    comment_url: URL of the comments page, if available.
    author: Byline, anonymized to ``"Anonymous"`` where applicable.
    published_date: Publication date string (format varies by source).
    summary: Short excerpt or lede, if provided by the feed.
    tags: List of topic tags associated with the article.

#### Methods

##### __post_init__

```python
def __post_init__(self) -> None
```

Ensure tags is never None after construction.

**Parameters:**

- `self`

**Returns:** None


### BaseSource

**Inherits from:** ABC

Abstract base class for all news sources.

This defines the contract that all source implementations must follow,
ensuring consistent behavior across different news sources.

#### Methods

##### __init__

```python
def __init__(self, config: SourceConfig, session: Optional[requests.Session] = None)
```

Initialize the source with configuration.

Args:
    config: Source configuration
    session: Optional HTTP session for connection pooling

**Parameters:**

- `self`
- `config` (SourceConfig)
- `session` (Optional[requests.Session]) *optional*

##### source_type

```python
def source_type(self) -> str
```

Return the source type ('config_driven' or 'custom').

**Parameters:**

- `self`

**Returns:** str

##### discover_articles

```python
def discover_articles(self, count: int) -> List[Article]
```

Discover articles from the source.

Args:
    count: Maximum number of articles to discover

Returns:
    List of Article objects

Raises:
    SourceError: If article discovery fails

**Parameters:**

- `self`
- `count` (int)

**Returns:** List[Article]

##### fetch_article_content

```python
def fetch_article_content(self, article: Article, output_dir: str, progress_callback = None, download_files: bool = False) -> Tuple[bool, Optional[str]]
```

Fetch and save article content.

Args:
    article: Article to fetch
    output_dir: Directory to save content
    progress_callback: Optional progress callback function
    download_files: Whether to download media files (--media flag)

Returns:
    Tuple of (success, article_path)

Raises:
    SourceError: If content fetching fails

**Parameters:**

- `self`
- `article` (Article)
- `output_dir` (str)
- `progress_callback` *optional*
- `download_files` (bool) *optional*

**Returns:** Tuple[bool, Optional[str]]

##### fetch_comments

```python
def fetch_comments(self, comment_url: str, article_title: str, article_folder_path: str) -> bool
```

Fetch and save article comments (if supported).

Override in sources that support comments. The default implementation
returns False (no comments fetched).

Args:
    comment_url: URL to the comments page for this article.
    article_title: Title of the article (used for logging and filenames).
    article_folder_path: Path to the article's output folder.

Returns:
    True if comments were saved, False otherwise.

**Parameters:**

- `self`
- `comment_url` (str)
- `article_title` (str)
- `article_folder_path` (str)

**Returns:** bool

##### validate_config

```python
def validate_config(self) -> List[str]
```

Validate the source configuration.

Returns:
    List of validation error messages (empty if valid)

**Parameters:**

- `self`

**Returns:** List[str]

##### _validate_custom_config

```python
def _validate_custom_config(self) -> List[str]
```

Validate custom configuration (override in subclasses).

Returns:
    List of validation error messages

**Parameters:**

- `self`

**Returns:** List[str]

##### should_skip_url

```python
def should_skip_url(self, url: str, title: str = '') -> bool
```

Check if a URL should be skipped during processing.

Args:
    url: URL to check
    title: Optional article title

Returns:
    True if URL should be skipped

**Parameters:**

- `self`
- `url` (str)
- `title` (str) *optional*

**Returns:** bool

##### _should_skip_custom

```python
def _should_skip_custom(self, url: str, title: str = '') -> bool
```

Custom skip logic (override in subclasses).

Args:
    url: URL to check
    title: Optional article title

Returns:
    True if URL should be skipped

**Parameters:**

- `self`
- `url` (str)
- `title` (str) *optional*

**Returns:** bool

##### get_rate_limit

```python
def get_rate_limit(self) -> float
```

Get the rate limit for this source.

**Parameters:**

- `self`

**Returns:** float

##### get_timeout

```python
def get_timeout(self) -> float
```

Get the timeout for this source.

**Parameters:**

- `self`

**Returns:** float

##### _get_logger

```python
def _get_logger(self)
```

Get a logger instance for this source.

**Parameters:**

- `self`

##### _setup_performance_monitoring

```python
def _setup_performance_monitoring(self)
```

Setup performance monitoring for this source.

**Parameters:**

- `self`

##### _start_performance_timing

```python
def _start_performance_timing(self) -> float
```

Start performance timing for an operation.

**Parameters:**

- `self`

**Returns:** float

##### _end_performance_timing

```python
def _end_performance_timing(self, start_time: float, success: bool, error_type: Optional[str] = None)
```

End performance timing for an operation.

**Parameters:**

- `self`
- `start_time` (float)
- `success` (bool)
- `error_type` (Optional[str]) *optional*

##### _record_article_discovery

```python
def _record_article_discovery(self, count: int)
```

Record successful article discovery.

**Parameters:**

- `self`
- `count` (int)

##### _record_content_fetch

```python
def _record_content_fetch(self, success: bool)
```

Record content fetching result.

**Parameters:**

- `self`
- `success` (bool)

##### discover_articles_with_retry_skip

```python
def discover_articles_with_retry_skip(self, count: int, max_retries: int = 2, batch_mode: bool = False) -> Optional[List[Article]]
```

Discover articles with retry-and-skip logic for network resilience.

Attempts to discover articles up to max_retries times. If all attempts
fail due to timeout or connection errors, returns None (skip source).

Args:
    count: Maximum number of articles to discover
    max_retries: Maximum number of retry attempts (default: 2)
    batch_mode: Whether processing multiple sources (affects user messages)

Returns:
    List of Article objects if successful, None if skipped

Example:
    >>> source = MySource(config)
    >>> articles = source.discover_articles_with_retry_skip(
    ...     count=10, max_retries=2
    ... )
    >>> if articles is None:
    ...     print("Source skipped after failures")

**Parameters:**

- `self`
- `count` (int)
- `max_retries` (int) *optional*
- `batch_mode` (bool) *optional*

**Returns:** Optional[List[Article]]

##### __str__

```python
def __str__(self) -> str
```

String representation of the source.

**Parameters:**

- `self`

**Returns:** str

##### __repr__

```python
def __repr__(self) -> str
```

Detailed string representation of the source.

**Parameters:**

- `self`

**Returns:** str


### SourceError

**Inherits from:** Exception

Base exception for source-related errors.

#### Methods

##### __init__

```python
def __init__(self, message: str, source_name: str = None)
```

Create a SourceError with an optional source name prefix.

Args:
    message: Human-readable description of the error.
    source_name: Source identifier prepended to the message in
        ``__str__`` (e.g. ``"hn"``). Defaults to ``None``.

**Parameters:**

- `self`
- `message` (str)
- `source_name` (str) *optional*

##### __str__

```python
def __str__(self)
```

Return message prefixed with ``[source_name]`` when set.

Returns:
    ``"[source_name] message"`` if *source_name* is set, otherwise
    the plain *message* string.

**Parameters:**

- `self`


### ArticleDiscoveryError

**Inherits from:** SourceError

Exception raised when article discovery fails.


### ContentFetchError

**Inherits from:** SourceError

Exception raised when content fetching fails.


### ConfigurationError

**Inherits from:** SourceError

Exception raised when source configuration is invalid.


