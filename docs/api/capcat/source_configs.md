# capcat.core.source_configs

**File:** `Application/capcat/core/source_configs.py`

## Description

Modular source configuration system with backward compatibility.
This replaces the monolithic configuration with the new modular system.

## Constants

### SOURCE_CONFIGURATIONS

**Value:** `SourceConfigDict()`

## Classes

### LegacyConfigAdapter

Adapter to provide backward compatibility with the old SOURCE_CONFIGURATIONS format.

#### Methods

##### __init__

```python
def __init__(self)
```

Initialize with source registry.

**Parameters:**

- `self`

##### _build_legacy_configs

```python
def _build_legacy_configs(self) -> Dict[str, Dict[str, Any]]
```

Build legacy configuration dictionary from modular sources.

**Parameters:**

- `self`

**Returns:** Dict[str, Dict[str, Any]]

##### get_legacy_configs

```python
def get_legacy_configs(self) -> Dict[str, Dict[str, Any]]
```

Get all configurations in legacy format.

**Parameters:**

- `self`

**Returns:** Dict[str, Dict[str, Any]]

##### reload

```python
def reload(self)
```

Reload configurations from modular system.

**Parameters:**

- `self`


### SourceConfigDict

**Inherits from:** dict

Dictionary subclass that dynamically loads from modular system.
Provides full backward compatibility with SOURCE_CONFIGURATIONS.

#### Methods

##### __init__

```python
def __init__(self)
```

Initialize with an empty dict; configs are loaded on first access.

**Parameters:**

- `self`

##### _ensure_loaded

```python
def _ensure_loaded(self)
```

Ensure configurations are loaded.

**Parameters:**

- `self`

##### __getitem__

```python
def __getitem__(self, key)
```

Load configs if needed, then return item for *key*.

Args:
    key: Source identifier string.

Returns:
    Source configuration dict for *key*.

Raises:
    KeyError: If *key* is not a registered source.

**Parameters:**

- `self`
- `key`

##### __setitem__

```python
def __setitem__(self, key, value)
```

Load configs if needed, then set *key* to *value*.

Args:
    key: Source identifier string.
    value: Configuration dict to store.

**Parameters:**

- `self`
- `key`
- `value`

##### __contains__

```python
def __contains__(self, key)
```

Load configs if needed, then test membership.

Args:
    key: Source identifier string.

Returns:
    ``True`` if *key* is a registered source.

**Parameters:**

- `self`
- `key`

##### get

```python
def get(self, key, default = None)
```

Load configs if needed, then return item or *default*.

Args:
    key: Source identifier string.
    default: Value to return when *key* is absent.

Returns:
    Config dict for *key*, or *default*.

**Parameters:**

- `self`
- `key`
- `default` *optional*

##### keys

```python
def keys(self)
```

Load configs if needed, then return all source IDs.

Returns:
    Dict keys view of all registered source identifiers.

**Parameters:**

- `self`

##### values

```python
def values(self)
```

Load configs if needed, then return all config dicts.

Returns:
    Dict values view of all source configuration dicts.

**Parameters:**

- `self`

##### items

```python
def items(self)
```

Load configs if needed, then return (source_id, config) pairs.

Returns:
    Dict items view of ``(source_id, config_dict)`` pairs.

**Parameters:**

- `self`

##### __len__

```python
def __len__(self)
```

Load configs if needed, then return the number of registered sources.

Returns:
    Count of registered source configurations.

**Parameters:**

- `self`

##### __iter__

```python
def __iter__(self)
```

Load configs if needed, then iterate over source IDs.

Returns:
    Iterator over all registered source identifier strings.

**Parameters:**

- `self`

##### reload

```python
def reload(self)
```

Reload configurations from modular system.

**Parameters:**

- `self`


## Functions

### get_source_config

```python
def get_source_config(source_name: str) -> Dict[str, Any]
```

Get configuration for a specific source.

**Parameters:**

- `source_name` (str)

**Returns:** Dict[str, Any]

### get_all_source_names

```python
def get_all_source_names() -> List[str]
```

Get list of all configured source names.

**Returns:** List[str]

### is_source_configured

```python
def is_source_configured(source_name: str) -> bool
```

Check if a source is configured.

**Parameters:**

- `source_name` (str)

**Returns:** bool

### reload_source_configs

```python
def reload_source_configs()
```

Reload source configurations from modular system.

