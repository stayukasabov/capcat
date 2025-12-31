# core.source_system.discovery_strategies

**File:** `Application/core/source_system/discovery_strategies.py`

## Description

Discovery strategy implementations for article discovery.
Implements Strategy pattern for clean separation of discovery methods.

## Classes

### DiscoveryStrategy

**Inherits from:** ABC

Base class for article discovery strategies.

#### Methods

##### discover

```python
def discover(self, count: int, config: dict, session: requests.Session, base_url: str, timeout: int, logger, should_skip_callback) -> List[Article]
```

Discover articles using this strategy.

Args:
    count: Maximum number of articles to discover
    config: Configuration dictionary
    session: HTTP session for requests
    base_url: Base URL for the source
    timeout: Request timeout in seconds
    logger: Logger instance
    should_skip_callback: Callback to check if URL should be skipped

Returns:
    List of Article objects

Raises:
    ArticleDiscoveryError: If discovery fails

**Parameters:**

- `self`
- `count` (int)
- `config` (dict)
- `session` (requests.Session)
- `base_url` (str)
- `timeout` (int)
- `logger`
- `should_skip_callback`

**Returns:** List[Article]


### RSSDiscoveryStrategy

**Inherits from:** DiscoveryStrategy

Discovery strategy using RSS/Atom feeds.

#### Methods

##### discover

```python
def discover(self, count: int, config: dict, session: requests.Session, base_url: str, timeout: int, logger, should_skip_callback) -> List[Article]
```

Discover articles via RSS/Atom feed.

Args:
    count: Maximum number of articles to discover
    config: Configuration dictionary with 'discovery' section
    session: HTTP session for requests
    base_url: Base URL for the source
    timeout: Request timeout in seconds
    logger: Logger instance
    should_skip_callback: Callback(url, title) -> bool

Returns:
    List of Article objects

Raises:
    ArticleDiscoveryError: If RSS discovery fails

**Parameters:**

- `self`
- `count` (int)
- `config` (dict)
- `session` (requests.Session)
- `base_url` (str)
- `timeout` (int)
- `logger`
- `should_skip_callback`

**Returns:** List[Article]

⚠️ **High complexity:** 24

##### _should_skip_patterns

```python
def _should_skip_patterns(url: str, patterns: List[str]) -> bool
```

Check if URL matches any skip pattern.

**Parameters:**

- `url` (str)
- `patterns` (List[str])

**Returns:** bool


### HTMLDiscoveryStrategy

**Inherits from:** DiscoveryStrategy

Discovery strategy using HTML scraping.

#### Methods

##### discover

```python
def discover(self, count: int, config: dict, session: requests.Session, base_url: str, timeout: int, logger, should_skip_callback) -> List[Article]
```

Discover articles via HTML scraping.

Args:
    count: Maximum number of articles to discover
    config: Configuration dictionary with 'article_selectors'
    session: HTTP session for requests
    base_url: Base URL to scrape
    timeout: Request timeout in seconds
    logger: Logger instance
    should_skip_callback: Callback(url, title) -> bool

Returns:
    List of Article objects

Raises:
    ArticleDiscoveryError: If HTML discovery fails

**Parameters:**

- `self`
- `count` (int)
- `config` (dict)
- `session` (requests.Session)
- `base_url` (str)
- `timeout` (int)
- `logger`
- `should_skip_callback`

**Returns:** List[Article]

##### _extract_article_from_link

```python
def _extract_article_from_link(self, link, base_url: str, skip_patterns: List[str], processed_urls: set, should_skip_callback, logger) -> Optional[Article]
```

Extract article information from a link element.

Returns:
    Article object if valid, None if should be skipped

**Parameters:**

- `self`
- `link`
- `base_url` (str)
- `skip_patterns` (List[str])
- `processed_urls` (set)
- `should_skip_callback`
- `logger`

**Returns:** Optional[Article]

##### _make_absolute_url

```python
def _make_absolute_url(href: str, base_url: str) -> str
```

Convert relative URL to absolute URL.

**Parameters:**

- `href` (str)
- `base_url` (str)

**Returns:** str


### DiscoveryStrategyFactory

Factory for creating discovery strategies.

#### Methods

##### create

```python
def create(discovery_config: dict, legacy_config: dict = None) -> DiscoveryStrategy
```

Create appropriate discovery strategy based on configuration.

Supports both new schema (discovery.method) and legacy schema
(top-level rss_url).

Args:
    discovery_config: Discovery configuration dictionary
    legacy_config: Full config for backward compatibility (optional)

Returns:
    DiscoveryStrategy instance

Raises:
    ValueError: If discovery method is unsupported

**Parameters:**

- `discovery_config` (dict)
- `legacy_config` (dict) *optional*

**Returns:** DiscoveryStrategy


## Functions

### _fetch_url_with_retry

```python
def _fetch_url_with_retry(session: requests.Session, url: str, timeout: int, headers: dict = None, source_code: str = 'unknown') -> requests.Response
```

Fetch URL with automatic retry logic and rate limiting.

This function provides:
- Rate limiting based on source-specific configuration
- Up to 3 retry attempts (via @network_retry decorator)
- Exponential backoff (1s, 2s, 4s)
- Automatic handling of connection errors and timeouts

Args:
    session: Requests session to use
    url: URL to fetch
    timeout: Request timeout in seconds
    headers: Optional request headers
    source_code: Source identifier for rate limiting

Returns:
    Response object

Raises:
    requests.exceptions.RequestException: After all retries exhausted

**Parameters:**

- `session` (requests.Session)
- `url` (str)
- `timeout` (int)
- `headers` (dict) *optional*
- `source_code` (str) *optional*

**Returns:** requests.Response

