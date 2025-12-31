# sources.base.config_schema

**File:** `Application/sources/base/config_schema.py`

## Description

Base configuration schema for news sources.
Provides standardized structure for source configuration.

## Classes

### SourceConfig

Standardized configuration schema for news sources.

#### Methods

##### to_dict

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary format for compatibility.

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

⚠️ **High complexity:** 15

##### from_dict

```python
def from_dict(cls, data: Dict[str, Any], source_id: str) -> 'SourceConfig'
```

Create SourceConfig from dictionary (for legacy compatibility).

**Parameters:**

- `cls`
- `data` (Dict[str, Any])
- `source_id` (str)

**Returns:** 'SourceConfig'

##### validate

```python
def validate(self) -> List[str]
```

Validate configuration and return list of errors.

**Parameters:**

- `self`

**Returns:** List[str]

⚠️ **High complexity:** 11


