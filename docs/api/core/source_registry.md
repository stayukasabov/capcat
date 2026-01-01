# core.source_system.source_registry

**File:** `Application/core/source_system/source_registry.py`

## Description

Source registry for automatic discovery and management of news sources.
Handles both config-driven and custom source types.

## Classes

### SourceRegistry

Registry for managing and discovering news sources.

Supports both config-driven sources (YAML/JSON) and custom source implementations.
Provides auto-discovery and validation of sources.

#### Methods

##### __init__

```python
def __init__(self, sources_dir: str = None)
```

Initialize the source registry.

Args:
    sources_dir: Path to sources directory (defaults to sources/ relative to app root)

**Parameters:**

- `self`
- `sources_dir` (str) *optional*

##### discover_sources

```python
def discover_sources(self) -> Dict[str, SourceConfig]
```

Discover all available sources (both config-driven and custom).

Returns:
    Dictionary mapping source names to their configurations

Raises:
    SourceError: If source discovery fails

**Parameters:**

- `self`

**Returns:** Dict[str, SourceConfig]

##### _discover_config_driven_sources

```python
def _discover_config_driven_sources(self)
```

Discover sources defined by configuration files.

**Parameters:**

- `self`

##### _discover_custom_sources

```python
def _discover_custom_sources(self)
```

Discover custom source implementations.

**Parameters:**

- `self`

##### _load_custom_source

```python
def _load_custom_source(self, source_dir: Path)
```

Load a custom source implementation.

**Parameters:**

- `self`
- `source_dir` (Path)

⚠️ **High complexity:** 12

##### _load_config_file

```python
def _load_config_file(self, config_file: Path) -> Dict
```

Load a configuration file (YAML or JSON).

**Parameters:**

- `self`
- `config_file` (Path)

**Returns:** Dict

##### _validate_config_driven_config

```python
def _validate_config_driven_config(self, config: SourceConfig) -> List[str]
```

Validate configuration for config-driven sources.

**Parameters:**

- `self`
- `config` (SourceConfig)

**Returns:** List[str]

##### get_source

```python
def get_source(self, source_name: str, session = None) -> BaseSource
```

Get a source instance by name.

Args:
    source_name: Name of the source
    session: Optional HTTP session

Returns:
    BaseSource instance

Raises:
    SourceError: If source is not found or cannot be instantiated

**Parameters:**

- `self`
- `source_name` (str)
- `session` *optional*

**Returns:** BaseSource

##### get_available_sources

```python
def get_available_sources(self) -> List[str]
```

Get list of available source names.

**Parameters:**

- `self`

**Returns:** List[str]

##### get_sources_by_category

```python
def get_sources_by_category(self, category: str) -> List[str]
```

Get sources by category.

**Parameters:**

- `self`
- `category` (str)

**Returns:** List[str]

##### get_source_config

```python
def get_source_config(self, source_name: str) -> Optional[SourceConfig]
```

Get source configuration by name.

**Parameters:**

- `self`
- `source_name` (str)

**Returns:** Optional[SourceConfig]

##### validate_all_sources

```python
def validate_all_sources(self, deep_validation: bool = False) -> Dict[str, List[str]]
```

Validate all registered sources using enhanced validation engine.

Args:
    deep_validation: Whether to perform deep validation (network tests)

Returns:
    Dictionary mapping source names to validation errors (empty list if valid)

**Parameters:**

- `self`
- `deep_validation` (bool) *optional*

**Returns:** Dict[str, List[str]]

##### enhanced_validate_all_sources

```python
def enhanced_validate_all_sources(self, deep_validation: bool = False)
```

Enhanced validation with detailed results.

Args:
    deep_validation: Whether to perform deep validation

Returns:
    Dictionary mapping source names to ValidationResult objects

**Parameters:**

- `self`
- `deep_validation` (bool) *optional*

##### generate_validation_report

```python
def generate_validation_report(self, deep_validation: bool = False) -> str
```

Generate a comprehensive validation report.

Args:
    deep_validation: Whether to perform deep validation

Returns:
    Human-readable validation report

**Parameters:**

- `self`
- `deep_validation` (bool) *optional*

**Returns:** str

##### get_registry_stats

```python
def get_registry_stats(self) -> Dict[str, int]
```

Get registry statistics.

**Parameters:**

- `self`

**Returns:** Dict[str, int]

##### clear_cache

```python
def clear_cache(self)
```

Clear cached source instances.

**Parameters:**

- `self`

##### reload_sources

```python
def reload_sources(self)
```

Reload all sources (useful for development).

**Parameters:**

- `self`


## Functions

### get_source_registry

```python
def get_source_registry() -> SourceRegistry
```

Get the global source registry instance.

**Returns:** SourceRegistry

### reset_source_registry

```python
def reset_source_registry()
```

Reset the global source registry (useful for testing).

