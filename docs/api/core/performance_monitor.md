# core.source_system.performance_monitor

**File:** `Application/core/source_system/performance_monitor.py`

## Description

Source performance monitoring system for the hybrid architecture.
Tracks source performance, success rates, and health metrics.

## Classes

### SourceMetrics

Performance metrics for a source.

#### Methods

##### __post_init__

```python
def __post_init__(self)
```

**Parameters:**

- `self`

##### success_rate

```python
def success_rate(self) -> float
```

Calculate success rate percentage.

**Parameters:**

- `self`

**Returns:** float

##### content_success_rate

```python
def content_success_rate(self) -> float
```

Calculate content fetching success rate.

**Parameters:**

- `self`

**Returns:** float


### PerformanceMonitor

Performance monitoring system for sources.

#### Methods

##### __init__

```python
def __init__(self, metrics_file: Optional[str] = None)
```

Initialize performance monitor.

Args:
    metrics_file: Path to store metrics data

**Parameters:**

- `self`
- `metrics_file` (Optional[str]) *optional*

##### start_request

```python
def start_request(self, source_name: str, source_type: str) -> float
```

Start timing a request for a source.

Args:
    source_name: Name of the source
    source_type: Type of source ('config_driven' or 'custom')

Returns:
    Start timestamp

**Parameters:**

- `self`
- `source_name` (str)
- `source_type` (str)

**Returns:** float

##### end_request

```python
def end_request(self, source_name: str, start_time: float, success: bool, error_type: Optional[str] = None)
```

End timing a request and update metrics.

Args:
    source_name: Name of the source
    start_time: Start timestamp from start_request
    success: Whether the request was successful
    error_type: Type of error if request failed

**Parameters:**

- `self`
- `source_name` (str)
- `start_time` (float)
- `success` (bool)
- `error_type` (Optional[str]) *optional*

##### record_article_discovery

```python
def record_article_discovery(self, source_name: str, count: int)
```

Record successful article discovery.

Args:
    source_name: Name of the source
    count: Number of articles discovered

**Parameters:**

- `self`
- `source_name` (str)
- `count` (int)

##### record_content_fetch

```python
def record_content_fetch(self, source_name: str, success: bool)
```

Record content fetching result.

Args:
    source_name: Name of the source
    success: Whether content fetch was successful

**Parameters:**

- `self`
- `source_name` (str)
- `success` (bool)

##### get_source_metrics

```python
def get_source_metrics(self, source_name: str) -> Optional[SourceMetrics]
```

Get metrics for a specific source.

**Parameters:**

- `self`
- `source_name` (str)

**Returns:** Optional[SourceMetrics]

##### get_all_metrics

```python
def get_all_metrics(self) -> Dict[str, SourceMetrics]
```

Get metrics for all sources.

**Parameters:**

- `self`

**Returns:** Dict[str, SourceMetrics]

##### get_performance_summary

```python
def get_performance_summary(self) -> Dict[str, Any]
```

Get performance summary across all sources.

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### health_check_source

```python
def health_check_source(self, source_name: str) -> bool
```

Perform health check on a specific source.

Args:
    source_name: Name of the source to check

Returns:
    True if source is healthy

**Parameters:**

- `self`
- `source_name` (str)

**Returns:** bool

##### cleanup_old_metrics

```python
def cleanup_old_metrics(self, days: int = 30)
```

Clean up old metrics data.

Args:
    days: Number of days to keep metrics

**Parameters:**

- `self`
- `days` (int) *optional*

##### save_metrics

```python
def save_metrics(self)
```

Save metrics to file.

**Parameters:**

- `self`

##### load_metrics

```python
def load_metrics(self)
```

Load metrics from file.

**Parameters:**

- `self`

##### generate_report

```python
def generate_report(self) -> str
```

Generate a human-readable performance report.

**Parameters:**

- `self`

**Returns:** str


## Functions

### get_performance_monitor

```python
def get_performance_monitor() -> PerformanceMonitor
```

Get the global performance monitor instance.

**Returns:** PerformanceMonitor

### reset_performance_monitor

```python
def reset_performance_monitor()
```

Reset the global performance monitor (useful for testing).

