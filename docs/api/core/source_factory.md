# core.source_system.source_factory

**File:** `Application/core/source_system/source_factory.py`

## Description

Source factory for creating and managing news source instances.
Provides a high-level interface for source instantiation and management.

## Classes

### SourceFactory

Factory for creating and managing news source instances.

Provides high-level interface for source instantiation, batch operations,
and source lifecycle management.

#### Methods

##### __init__

```python
def __init__(self, registry: Optional[SourceRegistry] = None)
```

Initialize the source factory.

Args:
    registry: Optional source registry (uses global registry if not provided)

**Parameters:**

- `self`
- `registry` (Optional[SourceRegistry]) *optional*

##### create_source

```python
def create_source(self, source_name: str, use_session_pool: bool = True) -> BaseSource
```

Create a source instance.

Args:
    source_name: Name of the source to create
    use_session_pool: Whether to use session pooling

Returns:
    BaseSource instance

Raises:
    SourceError: If source creation fails

**Parameters:**

- `self`
- `source_name` (str)
- `use_session_pool` (bool) *optional*

**Returns:** BaseSource

##### create_sources

```python
def create_sources(self, source_names: List[str], use_session_pool: bool = True) -> Dict[str, BaseSource]
```

Create multiple source instances.

Args:
    source_names: List of source names to create
    use_session_pool: Whether to use session pooling

Returns:
    Dictionary mapping source names to BaseSource instances

Raises:
    SourceError: If any source creation fails

**Parameters:**

- `self`
- `source_names` (List[str])
- `use_session_pool` (bool) *optional*

**Returns:** Dict[str, BaseSource]

##### get_cached_source

```python
def get_cached_source(self, source_name: str) -> Optional[BaseSource]
```

Get a cached source instance.

Args:
    source_name: Name of the source

Returns:
    Cached BaseSource instance or None if not cached

**Parameters:**

- `self`
- `source_name` (str)

**Returns:** Optional[BaseSource]

##### cache_source

```python
def cache_source(self, source_name: str, source: BaseSource)
```

Cache a source instance.

Args:
    source_name: Name of the source
    source: Source instance to cache

**Parameters:**

- `self`
- `source_name` (str)
- `source` (BaseSource)

##### clear_cache

```python
def clear_cache(self)
```

Clear the source instance cache.

**Parameters:**

- `self`

##### validate_sources

```python
def validate_sources(self, source_names: List[str]) -> Dict[str, List[str]]
```

Validate multiple sources.

Args:
    source_names: List of source names to validate

Returns:
    Dictionary mapping source names to validation errors

**Parameters:**

- `self`
- `source_names` (List[str])

**Returns:** Dict[str, List[str]]

##### get_sources_by_category

```python
def get_sources_by_category(self, category: str) -> List[str]
```

Get source names by category.

Args:
    category: Category name

Returns:
    List of source names in the category

**Parameters:**

- `self`
- `category` (str)

**Returns:** List[str]

##### get_available_sources

```python
def get_available_sources(self) -> List[str]
```

Get all available source names.

**Parameters:**

- `self`

**Returns:** List[str]

##### get_source_config

```python
def get_source_config(self, source_name: str) -> Optional[SourceConfig]
```

Get source configuration.

Args:
    source_name: Name of the source

Returns:
    SourceConfig or None if source not found

**Parameters:**

- `self`
- `source_name` (str)

**Returns:** Optional[SourceConfig]

##### batch_discover_articles

```python
def batch_discover_articles(self, source_names: List[str], count_per_source: int, max_workers: int = 4) -> Dict[str, List]
```

Discover articles from multiple sources in parallel.

Args:
    source_names: List of source names
    count_per_source: Number of articles to discover per source
    max_workers: Maximum number of worker threads

Returns:
    Dictionary mapping source names to article lists

**Parameters:**

- `self`
- `source_names` (List[str])
- `count_per_source` (int)
- `max_workers` (int) *optional*

**Returns:** Dict[str, List]

##### test_source_connectivity

```python
def test_source_connectivity(self, source_name: str, timeout: float = 10.0) -> bool
```

Test if a source is reachable.

Args:
    source_name: Name of the source to test
    timeout: Connection timeout in seconds

Returns:
    True if source is reachable, False otherwise

**Parameters:**

- `self`
- `source_name` (str)
- `timeout` (float) *optional*

**Returns:** bool

##### get_source_stats

```python
def get_source_stats(self) -> Dict[str, Dict]
```

Get statistics for all sources.

Returns:
    Dictionary with source statistics

**Parameters:**

- `self`

**Returns:** Dict[str, Dict]

##### health_check

```python
def health_check(self, source_names: Optional[List[str]] = None, timeout: float = 5.0) -> Dict[str, bool]
```

Perform health check on sources.

Args:
    source_names: List of sources to check (all if None)
    timeout: Timeout per source check

Returns:
    Dictionary mapping source names to health status

**Parameters:**

- `self`
- `source_names` (Optional[List[str]]) *optional*
- `timeout` (float) *optional*

**Returns:** Dict[str, bool]

##### reload_sources

```python
def reload_sources(self)
```

Reload all sources from the registry.

**Parameters:**

- `self`

##### get_performance_summary

```python
def get_performance_summary(self) -> Dict[str, Any]
```

Get performance summary for all sources.

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### get_source_performance

```python
def get_source_performance(self, source_name: str) -> Optional[Dict[str, Any]]
```

Get performance metrics for a specific source.

**Parameters:**

- `self`
- `source_name` (str)

**Returns:** Optional[Dict[str, Any]]

##### generate_performance_report

```python
def generate_performance_report(self) -> str
```

Generate a human-readable performance report.

**Parameters:**

- `self`

**Returns:** str

##### save_performance_metrics

```python
def save_performance_metrics(self)
```

Save performance metrics to disk.

**Parameters:**

- `self`

##### __str__

```python
def __str__(self) -> str
```

String representation of the factory.

**Parameters:**

- `self`

**Returns:** str


## Functions

### get_source_factory

```python
def get_source_factory() -> SourceFactory
```

Get the global source factory instance.

**Returns:** SourceFactory

### reset_source_factory

```python
def reset_source_factory()
```

Reset the global source factory (useful for testing).

### discover_for_source

```python
def discover_for_source(source_name: str)
```

**Parameters:**

- `source_name` (str)

