# core.source_system.source_config

**File:** `Application/core/source_system/source_config.py`

## Description

Source configuration system for specialized sources.
Provides configuration management for automated source activation.

## Classes

### SourceConfig

Configuration container for specialized sources.
Stores source metadata, selectors, and processing rules.

#### Methods

##### __init__

```python
def __init__(self, source_id: str, name: str, display_name: str, base_url: str, timeout: int = 30, headers: Optional[Dict[str, str]] = None, source_type: str = 'specialized')
```

Initialize source configuration.

Args:
    source_id: Unique identifier for the source
    name: Source name
    display_name: Human-readable display name
    base_url: Base URL for the source
    timeout: Request timeout in seconds
    headers: Custom headers for requests
    source_type: Type of source (specialized, standard, etc.)

**Parameters:**

- `self`
- `source_id` (str)
- `name` (str)
- `display_name` (str)
- `base_url` (str)
- `timeout` (int) *optional*
- `headers` (Optional[Dict[str, str]]) *optional*
- `source_type` (str) *optional*

##### get_headers

```python
def get_headers(self) -> Dict[str, str]
```

Get request headers for this source.

Returns:
    Dictionary of headers to use in requests

**Parameters:**

- `self`

**Returns:** Dict[str, str]

##### to_dict

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary format for compatibility.

Returns:
    Dictionary representation of the source configuration

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### __repr__

```python
def __repr__(self) -> str
```

String representation of the config.

**Parameters:**

- `self`

**Returns:** str


