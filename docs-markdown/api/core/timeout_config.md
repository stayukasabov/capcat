# core.timeout_config

**File:** `Application/core/timeout_config.py`

## Description

Adaptive timeout configuration for Capcat.
Provides source-specific timeouts and adaptive learning from response times.

## Classes

### TimeoutConfig

Configuration for connection and read timeouts.

#### Methods

##### as_tuple

```python
def as_tuple(self) -> Tuple[int, int]
```

Get timeout as tuple for requests library.

Returns:
    Tuple of (connect_timeout, read_timeout)

**Parameters:**

- `self`

**Returns:** Tuple[int, int]

##### __post_init__

```python
def __post_init__(self)
```

Validate timeout values.

**Parameters:**

- `self`


### TimeoutTracker

Track actual response times to recommend timeout adjustments.

Collects response time data and uses statistical analysis to
suggest optimal timeout values.

#### Methods

##### __init__

```python
def __init__(self, history_size: int = 100)
```

Initialize timeout tracker.

Args:
    history_size: Maximum number of response times to track per source

**Parameters:**

- `self`
- `history_size` (int) *optional*

##### record_response_time

```python
def record_response_time(self, source_code: str, duration: float)
```

Record successful response time.

Args:
    source_code: Source identifier
    duration: Response time in seconds

**Parameters:**

- `self`
- `source_code` (str)
- `duration` (float)

##### get_recommended_timeout

```python
def get_recommended_timeout(self, source_code: str, min_samples: int = 10) -> Optional[TimeoutConfig]
```

Get recommended timeout based on historical data.

Uses percentile analysis to suggest timeout values that
will succeed for most requests while allowing margin for slower responses.

Args:
    source_code: Source identifier
    min_samples: Minimum number of samples required

Returns:
    Recommended TimeoutConfig or None if insufficient data

**Parameters:**

- `self`
- `source_code` (str)
- `min_samples` (int) *optional*

**Returns:** Optional[TimeoutConfig]

##### get_stats

```python
def get_stats(self, source_code: str) -> Dict[str, float]
```

Get statistics for a source.

Args:
    source_code: Source identifier

Returns:
    Dictionary with statistics (empty if no data)

**Parameters:**

- `self`
- `source_code` (str)

**Returns:** Dict[str, float]

##### get_all_stats

```python
def get_all_stats(self) -> Dict[str, Dict[str, float]]
```

Get statistics for all sources.

Returns:
    Dictionary mapping source codes to their statistics

**Parameters:**

- `self`

**Returns:** Dict[str, Dict[str, float]]


## Functions

### get_timeout_tracker

```python
def get_timeout_tracker() -> TimeoutTracker
```

Get the global timeout tracker instance (singleton).

Returns:
    Global TimeoutTracker instance

**Returns:** TimeoutTracker

### get_timeout_for_source

```python
def get_timeout_for_source(source_code: str, use_adaptive: bool = True) -> TimeoutConfig
```

Get timeout configuration for source.

Tries in order:
1. Configured source-specific timeout
2. Adaptive learned timeout (if enabled and sufficient data)
3. Default timeout

Args:
    source_code: Source identifier
    use_adaptive: Whether to use adaptive learned timeouts

Returns:
    TimeoutConfig for the source

**Parameters:**

- `source_code` (str)
- `use_adaptive` (bool) *optional*

**Returns:** TimeoutConfig

### record_response_time

```python
def record_response_time(source_code: str, duration: float)
```

Convenience function to record response time.

Args:
    source_code: Source identifier
    duration: Response time in seconds

**Parameters:**

- `source_code` (str)
- `duration` (float)

