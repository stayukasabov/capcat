# core.rate_limiter

**File:** `Application/core/rate_limiter.py`

## Description

Rate limiting system for Capcat to prevent overwhelming source servers.
Implements token bucket algorithm for smooth request throttling.

## Classes

### RateLimitConfig

Configuration for rate limiting a specific source.

#### Methods

##### __post_init__

```python
def __post_init__(self)
```

Validate configuration values.

**Parameters:**

- `self`


### RateLimiter

Token bucket rate limiter for per-source request throttling.

Implements a smooth rate limiting algorithm that allows bursts
while maintaining an average rate limit over time.

Example:
    limiter = RateLimiter(RateLimitConfig(requests_per_second=2.0))
    limiter.acquire()  # Blocks until token is available
    make_request()  # Perform the rate-limited operation

#### Methods

##### __init__

```python
def __init__(self, config: RateLimitConfig)
```

Initialize rate limiter with configuration.

Args:
    config: Rate limit configuration

**Parameters:**

- `self`
- `config` (RateLimitConfig)

##### acquire

```python
def acquire(self, blocking: bool = True) -> bool
```

Acquire permission to make a request.

Args:
    blocking: If True, block until a token is available.
             If False, return immediately if no token available.

Returns:
    True if token acquired, False if non-blocking and no token available

**Parameters:**

- `self`
- `blocking` (bool) *optional*

**Returns:** bool

##### _refill_tokens

```python
def _refill_tokens(self)
```

Refill tokens based on elapsed time since last update.

**Parameters:**

- `self`

##### get_stats

```python
def get_stats(self) -> Dict[str, float]
```

Get rate limiter statistics.

Returns:
    Dictionary with wait statistics

**Parameters:**

- `self`

**Returns:** Dict[str, float]

##### reset_stats

```python
def reset_stats(self)
```

Reset statistics counters.

**Parameters:**

- `self`


### RateLimiterPool

Pool of rate limiters, one per source.

Manages rate limiters for multiple sources, creating them on-demand
and applying source-specific configurations.

#### Methods

##### __init__

```python
def __init__(self, rate_limits: Optional[Dict[str, RateLimitConfig]] = None)
```

Initialize rate limiter pool.

Args:
    rate_limits: Optional custom rate limit configurations

**Parameters:**

- `self`
- `rate_limits` (Optional[Dict[str, RateLimitConfig]]) *optional*

##### get_limiter

```python
def get_limiter(self, source_code: str) -> RateLimiter
```

Get or create rate limiter for a source.

Args:
    source_code: Source identifier (e.g., 'hn', 'scientificamerican')

Returns:
    RateLimiter instance for the source

**Parameters:**

- `self`
- `source_code` (str)

**Returns:** RateLimiter

##### acquire

```python
def acquire(self, source_code: str, blocking: bool = True) -> bool
```

Acquire rate limit permission for a source.

Args:
    source_code: Source identifier
    blocking: Whether to block until token available

Returns:
    True if acquired, False if non-blocking and unavailable

**Parameters:**

- `self`
- `source_code` (str)
- `blocking` (bool) *optional*

**Returns:** bool

##### get_all_stats

```python
def get_all_stats(self) -> Dict[str, Dict[str, float]]
```

Get statistics for all rate limiters.

Returns:
    Dictionary mapping source codes to their statistics

**Parameters:**

- `self`

**Returns:** Dict[str, Dict[str, float]]

##### reset_all_stats

```python
def reset_all_stats(self)
```

Reset statistics for all rate limiters.

**Parameters:**

- `self`


## Functions

### get_rate_limiter_pool

```python
def get_rate_limiter_pool() -> RateLimiterPool
```

Get the global rate limiter pool instance (singleton).

Returns:
    Global RateLimiterPool instance

**Returns:** RateLimiterPool

### acquire_rate_limit

```python
def acquire_rate_limit(source_code: str, blocking: bool = True) -> bool
```

Convenience function to acquire rate limit from global pool.

Args:
    source_code: Source identifier
    blocking: Whether to block until available

Returns:
    True if acquired, False if non-blocking and unavailable

**Parameters:**

- `source_code` (str)
- `blocking` (bool) *optional*

**Returns:** bool

