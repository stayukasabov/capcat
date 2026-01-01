# core.ethical_scraping

**File:** `Application/core/ethical_scraping.py`

## Description

Ethical scraping utilities for Capcat.

Implements best practices:
1. Robots.txt caching with 15-minute TTL
2. 429/503 error handling with exponential backoff
3. Rate limiting enforcement
4. Path validation against robots.txt

## Classes

### RobotsTxtCache

Cache entry for robots.txt.


### EthicalScrapingManager

Manages ethical scraping compliance.

Features:
- Robots.txt caching (15-minute TTL)
- Crawl delay enforcement
- 429/503 exponential backoff
- Path validation

#### Methods

##### __init__

```python
def __init__(self, user_agent: str = 'Capcat/2.0')
```

Initialize ethical scraping manager.

Args:
    user_agent: User agent string for requests

**Parameters:**

- `self`
- `user_agent` (str) *optional*

##### get_robots_txt

```python
def get_robots_txt(self, base_url: str, timeout: int = 10) -> Tuple[RobotFileParser, float]
```

Fetch and parse robots.txt with caching.

Args:
    base_url: Base URL of the site
    timeout: Request timeout in seconds

Returns:
    Tuple of (RobotFileParser, crawl_delay)

**Parameters:**

- `self`
- `base_url` (str)
- `timeout` (int) *optional*

**Returns:** Tuple[RobotFileParser, float]

##### _extract_crawl_delay

```python
def _extract_crawl_delay(self, parser: RobotFileParser) -> float
```

Extract crawl delay from robots.txt parser.

Args:
    parser: RobotFileParser instance

Returns:
    Crawl delay in seconds (0.0 if not specified)

**Parameters:**

- `self`
- `parser` (RobotFileParser)

**Returns:** float

##### can_fetch

```python
def can_fetch(self, url: str) -> Tuple[bool, str]
```

Check if URL can be fetched according to robots.txt.

Args:
    url: URL to check

Returns:
    Tuple of (allowed, reason)

**Parameters:**

- `self`
- `url` (str)

**Returns:** Tuple[bool, str]

##### enforce_rate_limit

```python
def enforce_rate_limit(self, domain: str, crawl_delay: float, min_delay: float = 1.0)
```

Enforce rate limiting with crawl delay.

Args:
    domain: Domain being accessed
    crawl_delay: Required crawl delay from robots.txt
    min_delay: Minimum delay even if robots.txt doesn't specify

**Parameters:**

- `self`
- `domain` (str)
- `crawl_delay` (float)
- `min_delay` (float) *optional*

##### request_with_backoff

```python
def request_with_backoff(self, session: requests.Session, url: str, method: str = 'GET', max_retries: int = 3, initial_delay: float = 1.0) -> requests.Response
```

Make HTTP request with exponential backoff for 429/503 errors.

Args:
    session: Requests session
    url: URL to fetch
    method: HTTP method (GET, POST, etc.)
    max_retries: Maximum number of retries
    initial_delay: Initial retry delay in seconds
    **kwargs: Additional arguments for requests

Returns:
    Response object

Raises:
    requests.RequestException: If all retries fail

**Parameters:**

- `self`
- `session` (requests.Session)
- `url` (str)
- `method` (str) *optional*
- `max_retries` (int) *optional*
- `initial_delay` (float) *optional*

**Returns:** requests.Response

⚠️ **High complexity:** 12

##### validate_source_config

```python
def validate_source_config(self, base_url: str, rate_limit: float) -> Tuple[bool, str]
```

Validate source configuration against robots.txt.

Args:
    base_url: Base URL of the source
    rate_limit: Configured rate limit in seconds

Returns:
    Tuple of (valid, message)

**Parameters:**

- `self`
- `base_url` (str)
- `rate_limit` (float)

**Returns:** Tuple[bool, str]

##### get_cache_stats

```python
def get_cache_stats(self) -> Dict[str, any]
```

Get statistics about robots.txt cache.

Returns:
    Dictionary with cache statistics

**Parameters:**

- `self`

**Returns:** Dict[str, any]

##### clear_stale_cache

```python
def clear_stale_cache(self)
```

Remove stale entries from robots.txt cache.

**Parameters:**

- `self`


## Functions

### get_ethical_manager

```python
def get_ethical_manager(user_agent: str = 'Capcat/2.0') -> EthicalScrapingManager
```

Get or create global ethical scraping manager.

Args:
    user_agent: User agent string

Returns:
    EthicalScrapingManager instance

**Parameters:**

- `user_agent` (str) *optional*

**Returns:** EthicalScrapingManager

