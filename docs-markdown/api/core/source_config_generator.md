# core.source_system.source_config_generator

**File:** `Application/core/source_system/source_config_generator.py`

## Classes

### SourceConfigGenerator

Generates and saves YAML configuration files for new config-driven sources.

#### Methods

##### __init__

```python
def __init__(self, source_metadata: dict)
```

Args:
    source_metadata: A dictionary containing the required data:
        - source_id (str): The unique identifier for the source.
        - display_name (str): The user-facing name.
        - base_url (str): The base URL of the source website.
        - rss_url (str): The URL of the RSS feed.
        - category (str): The category the source belongs to.

**Parameters:**

- `self`
- `source_metadata` (dict)

##### generate_yaml_content

```python
def generate_yaml_content(self) -> str
```

Generates the YAML configuration as a string.

Returns:
    A string containing the YAML configuration.

**Parameters:**

- `self`

**Returns:** str

##### generate_and_save

```python
def generate_and_save(self, base_path: str) -> str
```

Generates the YAML content and saves it to the specified path.

Args:
    base_path: The directory where the config file should be saved.

Returns:
    The full path to the newly created file.

**Parameters:**

- `self`
- `base_path` (str)

**Returns:** str


