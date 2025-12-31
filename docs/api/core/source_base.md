# core.config.source_base

**File:** `Application/core/config/source_base.py`

## Description

Base configuration classes for news sources.
Provides the foundation for source-specific configuration management.

## Classes

### SourceConfig

Base configuration for news sources.

#### Methods

##### __post_init__

```python
def __post_init__(self)
```

Initialize default values after creation.

**Parameters:**

- `self`

##### to_dict

```python
def to_dict(self) -> Dict[str, Any]
```

Convert configuration to dictionary format.

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### from_dict

```python
def from_dict(cls, data: Dict[str, Any]) -> 'SourceConfig'
```

Create SourceConfig from dictionary data.

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Returns:** 'SourceConfig'

##### merge_with

```python
def merge_with(self, other: 'SourceConfig') -> 'SourceConfig'
```

Merge this configuration with another, with other taking precedence.

**Parameters:**

- `self`
- `other` ('SourceConfig')

**Returns:** 'SourceConfig'


### BundleConfig

Configuration for source bundles.

#### Methods

##### __post_init__

```python
def __post_init__(self)
```

Initialize default values after creation.

**Parameters:**

- `self`

##### to_dict

```python
def to_dict(self) -> Dict[str, Any]
```

Convert bundle configuration to dictionary format.

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### from_dict

```python
def from_dict(cls, data: Dict[str, Any]) -> 'BundleConfig'
```

Create BundleConfig from dictionary data.

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Returns:** 'BundleConfig'


### SourceConfigLoader

Loads source configurations from various file formats.

#### Methods

##### __init__

```python
def __init__(self)
```

Initialize the configuration loader.

**Parameters:**

- `self`

##### load_from_file

```python
def load_from_file(self, file_path: Path) -> Dict[str, Any]
```

Load configuration from a file (YAML or JSON).

Args:
    file_path: Path to the configuration file

Returns:
    Dictionary containing the configuration data

Raises:
    ValueError: If file format is not supported
    FileNotFoundError: If file does not exist

**Parameters:**

- `self`
- `file_path` (Path)

**Returns:** Dict[str, Any]

##### save_to_file

```python
def save_to_file(self, data: Dict[str, Any], file_path: Path, format_type: str = 'yaml')
```

Save configuration to a file.

Args:
    data: Configuration data to save
    file_path: Path where to save the file
    format_type: File format ('yaml' or 'json')

**Parameters:**

- `self`
- `data` (Dict[str, Any])
- `file_path` (Path)
- `format_type` (str) *optional*

##### load_source_config

```python
def load_source_config(self, file_path: Path, source_id: str) -> Optional[SourceConfig]
```

Load a specific source configuration from a file.

Args:
    file_path: Path to the configuration file
    source_id: ID of the source to load

Returns:
    SourceConfig instance or None if not found

**Parameters:**

- `self`
- `file_path` (Path)
- `source_id` (str)

**Returns:** Optional[SourceConfig]

##### load_bundle_config

```python
def load_bundle_config(self, file_path: Path, bundle_id: str) -> Optional[BundleConfig]
```

Load a specific bundle configuration from a file.

Args:
    file_path: Path to the configuration file
    bundle_id: ID of the bundle to load

Returns:
    BundleConfig instance or None if not found

**Parameters:**

- `self`
- `file_path` (Path)
- `bundle_id` (str)

**Returns:** Optional[BundleConfig]


