# core.media_config

**File:** `Application/core/media_config.py`

## Description

Media Configuration Manager for different news sources.
Provides source-specific configurations for media processing.

## Classes

### MediaConfigManager

Manages media processing configurations for different news sources.

#### Methods

##### get_source_config

```python
def get_source_config(source_name: str) -> Dict[str, Any]
```

Get media processing configuration for a specific source.

Args:
    source_name: Name of the news source

Returns:
    Dictionary with media processing configuration

**Parameters:**

- `source_name` (str)

**Returns:** Dict[str, Any]

##### _get_default_config

```python
def _get_default_config() -> Dict[str, Any]
```

Get default media processing configuration.

**Returns:** Dict[str, Any]

##### get_all_source_names

```python
def get_all_source_names() -> list
```

Get list of all configured source names.

**Returns:** list


