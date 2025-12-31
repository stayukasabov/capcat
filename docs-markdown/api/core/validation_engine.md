# core.source_system.validation_engine

**File:** `Application/core/source_system/validation_engine.py`

## Description

Enhanced configuration validation engine for the source system.
Provides comprehensive validation rules and automated testing.

## Classes

### ValidationResult

Result of a validation check.

#### Methods

##### __init__

```python
def __init__(self, is_valid: bool, message: str, severity: str = 'error', category: str = 'general')
```

**Parameters:**

- `self`
- `is_valid` (bool)
- `message` (str)
- `severity` (str) *optional*
- `category` (str) *optional*

##### __str__

```python
def __str__(self)
```

**Parameters:**

- `self`


### ValidationEngine

Comprehensive validation engine for source configurations.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### validate_config

```python
def validate_config(self, config: SourceConfig, deep_validation: bool = False) -> List[ValidationResult]
```

Validate a source configuration.

Args:
    config: Source configuration to validate
    deep_validation: Whether to perform deep validation (network requests)

Returns:
    List of validation results

**Parameters:**

- `self`
- `config` (SourceConfig)
- `deep_validation` (bool) *optional*

**Returns:** List[ValidationResult]

##### _validate_basic_fields

```python
def _validate_basic_fields(self, config: SourceConfig) -> List[ValidationResult]
```

Validate basic required fields.

**Parameters:**

- `self`
- `config` (SourceConfig)

**Returns:** List[ValidationResult]

##### _validate_url_format

```python
def _validate_url_format(self, config: SourceConfig) -> List[ValidationResult]
```

Validate URL format and structure.

**Parameters:**

- `self`
- `config` (SourceConfig)

**Returns:** List[ValidationResult]

##### _validate_timing_settings

```python
def _validate_timing_settings(self, config: SourceConfig) -> List[ValidationResult]
```

Validate timeout and rate limiting settings.

**Parameters:**

- `self`
- `config` (SourceConfig)

**Returns:** List[ValidationResult]

##### _is_config_driven_source

```python
def _is_config_driven_source(self, config: SourceConfig) -> bool
```

Check if this is a config-driven source.

**Parameters:**

- `self`
- `config` (SourceConfig)

**Returns:** bool

##### _validate_config_driven_source

```python
def _validate_config_driven_source(self, config: SourceConfig) -> List[ValidationResult]
```

Validate config-driven source specific settings.

**Parameters:**

- `self`
- `config` (SourceConfig)

**Returns:** List[ValidationResult]

##### _validate_custom_source

```python
def _validate_custom_source(self, config: SourceConfig) -> List[ValidationResult]
```

Validate custom source configuration.

**Parameters:**

- `self`
- `config` (SourceConfig)

**Returns:** List[ValidationResult]

##### _validate_css_selectors

```python
def _validate_css_selectors(self, selectors: List[str], field_name: str) -> List[ValidationResult]
```

Validate CSS selector syntax.

**Parameters:**

- `self`
- `selectors` (List[str])
- `field_name` (str)

**Returns:** List[ValidationResult]

##### _validate_network_connectivity

```python
def _validate_network_connectivity(self, config: SourceConfig) -> List[ValidationResult]
```

Validate network connectivity to the source.

**Parameters:**

- `self`
- `config` (SourceConfig)

**Returns:** List[ValidationResult]

⚠️ **High complexity:** 11

##### _validate_selectors

```python
def _validate_selectors(self, config: SourceConfig) -> List[ValidationResult]
```

Validate selectors against actual page content.

**Parameters:**

- `self`
- `config` (SourceConfig)

**Returns:** List[ValidationResult]

⚠️ **High complexity:** 16

##### _validate_content_selectors_on_page

```python
def _validate_content_selectors_on_page(self, url: str, content_selectors: List[str]) -> List[ValidationResult]
```

Validate content selectors on a specific article page.

**Parameters:**

- `self`
- `url` (str)
- `content_selectors` (List[str])

**Returns:** List[ValidationResult]

##### validate_all_sources

```python
def validate_all_sources(self, source_configs: Dict[str, SourceConfig], deep_validation: bool = False) -> Dict[str, List[ValidationResult]]
```

Validate all source configurations.

Args:
    source_configs: Dictionary of source configurations
    deep_validation: Whether to perform deep validation

Returns:
    Dictionary mapping source names to validation results

**Parameters:**

- `self`
- `source_configs` (Dict[str, SourceConfig])
- `deep_validation` (bool) *optional*

**Returns:** Dict[str, List[ValidationResult]]

##### generate_validation_report

```python
def generate_validation_report(self, validation_results: Dict[str, List[ValidationResult]]) -> str
```

Generate a human-readable validation report.

**Parameters:**

- `self`
- `validation_results` (Dict[str, List[ValidationResult]])

**Returns:** str

⚠️ **High complexity:** 21


