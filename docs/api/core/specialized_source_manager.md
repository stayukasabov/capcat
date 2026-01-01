# core.specialized_source_manager

**File:** `Application/core/specialized_source_manager.py`

## Description

Specialized Source Manager for automatic URL-based source activation.
Handles Medium, Substack, and other blog platforms with paywall detection.

## Classes

### SpecializedSourceManager

Manager for specialized sources that are automatically activated based on URL patterns.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### _load_specialized_configs

```python
def _load_specialized_configs(self)
```

Load configuration files for all specialized sources.

**Parameters:**

- `self`

##### can_handle_url

```python
def can_handle_url(self, url: str) -> bool
```

Check if any specialized source can handle the given URL.

Args:
    url: The URL to check

Returns:
    True if a specialized source can handle this URL

**Parameters:**

- `self`
- `url` (str)

**Returns:** bool

##### get_source_for_url

```python
def get_source_for_url(self, url: str) -> Optional[Tuple[object, str]]
```

Get the appropriate specialized source instance for a URL.

Args:
    url: The URL to process

Returns:
    Tuple of (source_instance, source_id) if available, None otherwise

**Parameters:**

- `self`
- `url` (str)

**Returns:** Optional[Tuple[object, str]]

##### _create_source_config

```python
def _create_source_config(self, source_id: str, config_data: Dict[str, Any], url: str) -> SourceConfig
```

Create a SourceConfig instance for a specialized source.

Args:
    source_id: The source identifier
    config_data: Configuration data from YAML
    url: The URL being processed

Returns:
    SourceConfig instance

**Parameters:**

- `self`
- `source_id` (str)
- `config_data` (Dict[str, Any])
- `url` (str)

**Returns:** SourceConfig

##### _extract_domain

```python
def _extract_domain(self, url: str) -> str
```

Extract domain from URL for dynamic configuration.

Args:
    url: The URL to extract domain from

Returns:
    Domain name

**Parameters:**

- `self`
- `url` (str)

**Returns:** str

##### get_paywall_info

```python
def get_paywall_info(self, source_id: str) -> Dict[str, Any]
```

Get paywall detection configuration for a specialized source.

Args:
    source_id: The source identifier

Returns:
    Paywall configuration dict

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** Dict[str, Any]

##### list_supported_platforms

```python
def list_supported_platforms(self) -> Dict[str, Dict[str, Any]]
```

Get information about all supported specialized platforms.

Returns:
    Dict with platform info

**Parameters:**

- `self`

**Returns:** Dict[str, Dict[str, Any]]

##### validate_specialized_sources

```python
def validate_specialized_sources(self) -> Dict[str, list]
```

Validate all specialized source configurations.

Returns:
    Dict with validation results

**Parameters:**

- `self`

**Returns:** Dict[str, list]


## Functions

### get_specialized_source_manager

```python
def get_specialized_source_manager() -> SpecializedSourceManager
```

Get the global specialized source manager instance.

**Returns:** SpecializedSourceManager

