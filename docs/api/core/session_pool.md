# core.session_pool

**File:** `Application/core/session_pool.py`

## Description

Global session pooling for optimal network performance across all sources.
Eliminates memory waste from individual session instances and provides
centralized connection management.

## Constants

### USER_AGENTS

**Value:** `['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0']`

## Classes

### SessionPool

Global session pool manager for optimal network performance.
Provides shared, configured sessions with connection pooling.

#### Methods

##### __new__

```python
def __new__(cls)
```

Singleton pattern to ensure only one session pool.

**Parameters:**

- `cls`

##### __init__

```python
def __init__(self)
```

Initialize the session pool if not already done.

**Parameters:**

- `self`

##### get_session

```python
def get_session(self, source_name: str = 'default') -> requests.Session
```

Get or create a configured session for a source.

Args:
    source_name: Name of the source (for logging and potential customization)

Returns:
    Configured requests.Session instance

**Parameters:**

- `self`
- `source_name` (str) *optional*

**Returns:** requests.Session

##### _create_session

```python
def _create_session(self, source_name: str) -> requests.Session
```

Create a properly configured session with realistic browser headers.

Uses rotating User-Agent strings and comprehensive browser headers
to avoid anti-bot detection while maintaining ethical scraping practices.

**Parameters:**

- `self`
- `source_name` (str)

**Returns:** requests.Session

##### close_all_sessions

```python
def close_all_sessions(self)
```

Close all sessions in the pool.

**Parameters:**

- `self`

##### get_session_stats

```python
def get_session_stats(self) -> Dict[str, int]
```

Get statistics about session pool usage.

**Parameters:**

- `self`

**Returns:** Dict[str, int]


## Functions

### get_global_session

```python
def get_global_session(source_name: str = 'default') -> requests.Session
```

Get a global session instance for the given source.

This function provides the main interface for getting optimized,
pooled session instances throughout the application.

Args:
    source_name: Name of the source requesting the session

Returns:
    Configured requests.Session instance from the global pool

**Parameters:**

- `source_name` (str) *optional*

**Returns:** requests.Session

### close_all_sessions

```python
def close_all_sessions()
```

Close all sessions in the global pool.

### get_session_stats

```python
def get_session_stats() -> Dict[str, int]
```

Get statistics about global session pool usage.

**Returns:** Dict[str, int]

