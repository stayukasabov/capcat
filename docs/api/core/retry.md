# core.retry

**File:** `Application/core/retry.py`

## Description

Retry mechanisms with exponential backoff for Capcat.
Provides robust error recovery for network and other transient failures.

## Classes

### RetryableOperation

Context manager for retryable operations with custom logic.

#### Methods

##### __init__

```python
def __init__(self, operation_name: str, max_retries: int = None)
```

**Parameters:**

- `self`
- `operation_name` (str)
- `max_retries` (int) *optional*

##### __enter__

```python
def __enter__(self)
```

**Parameters:**

- `self`

##### __exit__

```python
def __exit__(self, exc_type, exc_val, exc_tb)
```

**Parameters:**

- `self`
- `exc_type`
- `exc_val`
- `exc_tb`

##### should_retry

```python
def should_retry(self, exception: Exception) -> bool
```

Determine if an exception should trigger a retry.

Args:
    exception: The exception that occurred

Returns:
    True if the operation should be retried

**Parameters:**

- `self`
- `exception` (Exception)

**Returns:** bool


## Functions

### exponential_backoff_retry

```python
def exponential_backoff_retry(max_retries: int = None, base_delay: float = None, max_delay: float = 60.0, exponential_base: float = 2.0, jitter: bool = True, retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,), skip_after: int = None)
```

Decorator that implements exponential backoff retry logic.

Args:
    max_retries: Maximum number of retry attempts (uses config default if None)
    base_delay: Base delay in seconds (uses config default if None)
    max_delay: Maximum delay between retries in seconds
    exponential_base: Base for exponential backoff calculation
    jitter: Whether to add random jitter to delay
    retryable_exceptions: Tuple of exception types that should trigger retry
    skip_after: Number of attempts after which to skip instead of raising exception (None = never skip)

**Parameters:**

- `max_retries` (int) *optional*
- `base_delay` (float) *optional*
- `max_delay` (float) *optional*
- `exponential_base` (float) *optional*
- `jitter` (bool) *optional*
- `retryable_exceptions` (Tuple[Type[Exception], ...]) *optional*
- `skip_after` (int) *optional*

### network_retry

```python
def network_retry(func: Callable) -> Callable
```

Convenience decorator for network operations with appropriate retry settings.
Handles connection errors, timeouts, and transient HTTP errors.

**Parameters:**

- `func` (Callable)

**Returns:** Callable

### fast_media_retry

```python
def fast_media_retry(func: Callable) -> Callable
```

Fast retry decorator optimized for media downloads (images, audio, video).
Uses shorter delays and fewer retries for better performance with bulk downloads.

**Parameters:**

- `func` (Callable)

**Returns:** Callable

### decorator

```python
def decorator(func: Callable) -> Callable
```

**Parameters:**

- `func` (Callable)

**Returns:** Callable

### wrapper

```python
def wrapper() -> Any
```

**Returns:** Any

