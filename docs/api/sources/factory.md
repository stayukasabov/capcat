# sources.base.factory

**File:** `Application/sources/base/factory.py`

## Description

Clean factory pattern for creating news source adapters.
Uses the new modular configuration system.

## Classes

### ModularNewsSource

**Inherits from:** NewsSourceAdapter

A modular news source that adapts to any news site
based on its individual configuration file.

#### Methods

##### __init__

```python
def __init__(self, config: SourceConfig)
```

Initialize with source config.

**Parameters:**

- `self`
- `config` (SourceConfig)


### ModularSourceFactory

Factory for creating news source instances using modular configs.

#### Methods

##### __init__

```python
def __init__(self)
```

Initialize factory with source registry.

**Parameters:**

- `self`

##### create_source

```python
def create_source(self, source_name: str) -> Optional[ModularNewsSource]
```

Create a news source adapter for the given source name.

Args:
    source_name: The source identifier

Returns:
    ModularNewsSource instance or None if source not found

**Parameters:**

- `self`
- `source_name` (str)

**Returns:** Optional[ModularNewsSource]

##### create_multiple_sources

```python
def create_multiple_sources(self, source_names: list) -> Dict[str, ModularNewsSource]
```

Create multiple news source adapters.

Args:
    source_names: List of source identifiers

Returns:
    Dictionary mapping source names to source instances

**Parameters:**

- `self`
- `source_names` (list)

**Returns:** Dict[str, ModularNewsSource]

##### get_available_sources

```python
def get_available_sources(self) -> list
```

Get list of all available source names.

**Parameters:**

- `self`

**Returns:** list

##### is_source_available

```python
def is_source_available(self, source_name: str) -> bool
```

Check if a source is available.

**Parameters:**

- `self`
- `source_name` (str)

**Returns:** bool


## Functions

### get_modular_source_factory

```python
def get_modular_source_factory() -> ModularSourceFactory
```

Get the global modular source factory instance.

**Returns:** ModularSourceFactory

### create_source

```python
def create_source(source_name: str) -> Optional[ModularNewsSource]
```

Create a source using the modular factory.

**Parameters:**

- `source_name` (str)

**Returns:** Optional[ModularNewsSource]

### create_multiple_sources

```python
def create_multiple_sources(source_names: list) -> Dict[str, ModularNewsSource]
```

Create multiple sources using the modular factory.

**Parameters:**

- `source_names` (list)

**Returns:** Dict[str, ModularNewsSource]

