# core.source_system.source_analytics

**File:** `Application/core/source_system/source_analytics.py`

## Description

Source usage analytics and statistics.
Tracks source usage patterns for informed removal decisions.

## Classes

### SourceUsageStats

Statistics about source usage.


### SourceAnalytics

Tracks and analyzes source usage patterns.
Helps users make informed decisions about source removal.

#### Methods

##### __init__

```python
def __init__(self, analytics_file: Optional[Path] = None)
```

Initialize source analytics.

Args:
    analytics_file: Path to analytics data file

**Parameters:**

- `self`
- `analytics_file` (Optional[Path]) *optional*

##### record_fetch

```python
def record_fetch(self, source_id: str, success: bool, articles_count: int = 0) -> None
```

Record a fetch operation for analytics.

Args:
    source_id: Source identifier
    success: Whether fetch was successful
    articles_count: Number of articles fetched

**Parameters:**

- `self`
- `source_id` (str)
- `success` (bool)
- `articles_count` (int) *optional*

**Returns:** None

##### get_source_stats

```python
def get_source_stats(self, source_id: str, display_name: str = None) -> SourceUsageStats
```

Get usage statistics for a source.

Args:
    source_id: Source identifier
    display_name: Display name (optional)

Returns:
    SourceUsageStats object

**Parameters:**

- `self`
- `source_id` (str)
- `display_name` (str) *optional*

**Returns:** SourceUsageStats

##### get_all_stats

```python
def get_all_stats(self, source_names: Dict[str, str]) -> List[SourceUsageStats]
```

Get statistics for all tracked sources.

Args:
    source_names: Mapping of source_id to display_name

Returns:
    List of SourceUsageStats objects

**Parameters:**

- `self`
- `source_names` (Dict[str, str])

**Returns:** List[SourceUsageStats]

##### get_unused_sources

```python
def get_unused_sources(self, all_source_ids: List[str], days_threshold: int = 30) -> List[str]
```

Get sources that haven't been used recently.

Args:
    all_source_ids: List of all available source IDs
    days_threshold: Days without use to consider unused

Returns:
    List of unused source IDs

**Parameters:**

- `self`
- `all_source_ids` (List[str])
- `days_threshold` (int) *optional*

**Returns:** List[str]

##### get_low_performing_sources

```python
def get_low_performing_sources(self, all_source_ids: List[str], min_success_rate: float = 0.5) -> List[tuple[str, float]]
```

Get sources with low success rates.

Args:
    all_source_ids: List of all available source IDs
    min_success_rate: Minimum acceptable success rate (0.0-1.0)

Returns:
    List of tuples (source_id, success_rate)

**Parameters:**

- `self`
- `all_source_ids` (List[str])
- `min_success_rate` (float) *optional*

**Returns:** List[tuple[str, float]]

##### _calculate_frequency

```python
def _calculate_frequency(self, source_id: str, days_since_last: Optional[int]) -> str
```

Calculate fetch frequency category.

**Parameters:**

- `self`
- `source_id` (str)
- `days_since_last` (Optional[int])

**Returns:** str

##### _load_data

```python
def _load_data(self) -> Dict[str, Any]
```

Load analytics data from file.

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### _save_data

```python
def _save_data(self) -> None
```

Save analytics data to file.

**Parameters:**

- `self`

**Returns:** None


### AnalyticsReporter

Generates human-readable analytics reports.

#### Methods

##### format_stats

```python
def format_stats(stats: SourceUsageStats) -> str
```

Format source stats as readable text.

**Parameters:**

- `stats` (SourceUsageStats)

**Returns:** str

##### format_removal_recommendation

```python
def format_removal_recommendation(stats: SourceUsageStats) -> str
```

Generate removal recommendation based on stats.

**Parameters:**

- `stats` (SourceUsageStats)

**Returns:** str


