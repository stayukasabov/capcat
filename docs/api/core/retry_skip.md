# core.retry_skip

**File:** `Application/core/retry_skip.py`

## Description

Retry-and-Skip Logic for Network Resilience

Implements intelligent retry-and-skip mechanism for sources that timeout
or refuse connection. After N failed attempts, sources are skipped
(not endlessly retried) to maintain batch processing momentum.

GREEN PHASE - Minimal Implementation
This is the minimal code needed to pass all TDD tests.
Refactoring will be applied in the REFACTOR phase.

## Classes

### RetrySkipManager

Manages retry-and-skip logic for source processing.

GREEN PHASE: Minimal implementation to pass tests.

#### Methods

##### __init__

```python
def __init__(self, max_retries: int = 2)
```

Initialize retry-skip manager.

Args:
    max_retries: Maximum retry attempts before skipping

**Parameters:**

- `self`
- `max_retries` (int) *optional*

##### execute_with_retry_skip

```python
def execute_with_retry_skip(self, operation: Callable, operation_name: str, source_name: str = 'unknown', retryable_exceptions: Tuple = None) -> Optional[Any]
```

Execute operation with retry-skip logic.

Args:
    operation: Callable to execute
    operation_name: Name for logging
    source_name: Source identifier
    retryable_exceptions: Exceptions that trigger retry

Returns:
    Operation result or None if skipped

**Parameters:**

- `self`
- `operation` (Callable)
- `operation_name` (str)
- `source_name` (str) *optional*
- `retryable_exceptions` (Tuple) *optional*

**Returns:** Optional[Any]

##### execute_with_url_fallbacks

```python
def execute_with_url_fallbacks(self, urls: List[str], fetch_function: Callable[[str], Any], source_name: str = 'unknown', max_retries_per_url: int = 2) -> Optional[Any]
```

Try multiple URLs with retry logic before skipping.

Args:
    urls: List of URLs to try
    fetch_function: Function to fetch from URL
    source_name: Source identifier
    max_retries_per_url: Retries per URL

Returns:
    Fetch result or None if all URLs exhausted

**Parameters:**

- `self`
- `urls` (List[str])
- `fetch_function` (Callable[[str], Any])
- `source_name` (str) *optional*
- `max_retries_per_url` (int) *optional*

**Returns:** Optional[Any]

##### get_skip_summary

```python
def get_skip_summary(self) -> Dict[str, Any]
```

Get summary of skipped sources.

Returns:
    Dictionary with skip information

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### reset

```python
def reset(self)
```

Reset skip tracking.

**Parameters:**

- `self`


## Functions

### get_retry_skip_manager

```python
def get_retry_skip_manager(max_retries: int = 2) -> RetrySkipManager
```

Get global retry-skip manager instance.

**Parameters:**

- `max_retries` (int) *optional*

**Returns:** RetrySkipManager

### reset_retry_skip_manager

```python
def reset_retry_skip_manager()
```

Reset global retry-skip manager.

### operation

```python
def operation()
```

