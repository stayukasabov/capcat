# core.config

**File:** `Application/core/config.py`

## Description

Configuration management for Capcat.
Handles settings from config files, environment variables, and CLI overrides.

## Classes

### NetworkConfig

Network-related configuration settings.


### ProcessingConfig

Processing-related configuration settings.


### UIConfig

User interface and experience configuration settings.


### LoggingConfig

Logging-related configuration settings.


### FetchNewsConfig

Main configuration class containing all settings.

#### Methods

##### __post_init__

```python
def __post_init__(self)
```

Initialize sub-configs if not provided.

Creates default instances for network, processing, logging, and UI
configurations when not explicitly specified.

**Parameters:**

- `self`

##### to_dict

```python
def to_dict(self) -> Dict[str, Any]
```

Convert configuration to dictionary.

Returns:
    Dictionary representation of full configuration

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### from_dict

```python
def from_dict(cls, data: Dict[str, Any]) -> 'FetchNewsConfig'
```

Create configuration from dictionary.

Args:
    data: Dictionary with network, processing, logging sections

Returns:
    New FetchNewsConfig instance

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Returns:** 'FetchNewsConfig'


### ConfigManager

Manages configuration loading and merging from multiple sources.

#### Methods

##### __init__

```python
def __init__(self)
```

Initialize the configuration manager.

Creates default configuration and sets load status to false.

**Parameters:**

- `self`

##### load_config

```python
def load_config(self, config_file: Optional[str] = None, load_env: bool = True) -> FetchNewsConfig
```

Load configuration from files and environment variables.

Searches default locations if no file specified. Caches loaded config.

Args:
    config_file: Path to config file (JSON or YAML)
    load_env: Whether to load environment variables

Returns:
    Loaded configuration instance

**Parameters:**

- `self`
- `config_file` (Optional[str]) *optional*
- `load_env` (bool) *optional*

**Returns:** FetchNewsConfig

##### _load_default_config_files

```python
def _load_default_config_files(self)
```

Load from default config file locations.

Searches in order: local dir, ~/.config/capcat/, /etc/capcat/.
Stops at first found file.

**Parameters:**

- `self`

##### _load_from_file

```python
def _load_from_file(self, config_file: str)
```

Load configuration from a file.

Supports JSON and YAML formats. Merges into existing config.

Args:
    config_file: Path to configuration file

**Parameters:**

- `self`
- `config_file` (str)

##### _load_from_env

```python
def _load_from_env(self)
```

Load configuration from environment variables.

Maps CAPCAT_* environment variables to configuration settings.
Handles type conversion for int, float, bool, and str types.

**Parameters:**

- `self`

##### _merge_config_data

```python
def _merge_config_data(self, data: Dict[str, Any])
```

Merge configuration data into current config.

Updates existing config object with values from data dict.
Warns about unknown sections or keys.

Args:
    data: Dictionary with section.key structure

**Parameters:**

- `self`
- `data` (Dict[str, Any])

##### get_config

```python
def get_config(self) -> FetchNewsConfig
```

Get the current configuration.

Returns:
    Current configuration instance

**Parameters:**

- `self`

**Returns:** FetchNewsConfig

##### save_config

```python
def save_config(self, config_file: str, format: str = 'yaml')
```

Save current configuration to a file.

Creates parent directories if needed. Supports YAML and JSON formats.

Args:
    config_file: Path to save configuration
    format: Output format - 'yaml', 'yml', or 'json'

Returns:
    True if saved successfully, False otherwise

**Parameters:**

- `self`
- `config_file` (str)
- `format` (str) *optional*


## Functions

### get_config

```python
def get_config() -> FetchNewsConfig
```

Get the global configuration instance.

Returns:
    Global configuration object (singleton)

**Returns:** FetchNewsConfig

### load_config

```python
def load_config(config_file: Optional[str] = None, load_env: bool = True) -> FetchNewsConfig
```

Load configuration from file and/or environment variables.

Module-level convenience function for global config manager.

Args:
    config_file: Path to config file (JSON or YAML)
    load_env: Whether to load environment variables

Returns:
    Loaded configuration instance

**Parameters:**

- `config_file` (Optional[str]) *optional*
- `load_env` (bool) *optional*

**Returns:** FetchNewsConfig

### save_config

```python
def save_config(config_file: str, format: str = 'yaml') -> bool
```

Save current configuration to a file.

Module-level convenience function for global config manager.

Args:
    config_file: Path to save configuration
    format: Output format - 'yaml', 'yml', or 'json'

Returns:
    True if saved successfully, False otherwise

**Parameters:**

- `config_file` (str)
- `format` (str) *optional*

**Returns:** bool

