# core.source_system.bundle_validator

**File:** `Application/core/source_system/bundle_validator.py`

## Description

Bundle validation logic.
Validates bundle IDs, descriptions, source IDs, and integrity.

## Constants

### BUNDLE_ID_PATTERN

**Value:** `re.compile('^[a-z0-9_]+$')`

### BUNDLE_ID_MAX_LENGTH

**Value:** `30`

### DESCRIPTION_MAX_LENGTH

**Value:** `200`

### DEFAULT_COUNT_MIN

**Value:** `1`

### DEFAULT_COUNT_MAX

**Value:** `100`

## Classes

### ValidationResult

Result of validation operation.

#### Methods

##### __post_init__

```python
def __post_init__(self)
```

**Parameters:**

- `self`


### BundleValidator

Validates bundle operations and data.

#### Methods

##### __init__

```python
def __init__(self, bundle_manager = None, source_registry = None)
```

Args:
    bundle_manager: BundleManager instance for existence checks
    source_registry: SourceRegistry instance for source validation

**Parameters:**

- `self`
- `bundle_manager` *optional*
- `source_registry` *optional*

##### validate_bundle_id

```python
def validate_bundle_id(self, bundle_id: str) -> ValidationResult
```

Validate bundle ID format.

Args:
    bundle_id: Bundle identifier to validate

Returns:
    ValidationResult with errors if invalid

**Parameters:**

- `self`
- `bundle_id` (str)

**Returns:** ValidationResult

##### validate_bundle_unique

```python
def validate_bundle_unique(self, bundle_id: str) -> ValidationResult
```

Check if bundle ID is unique.

Args:
    bundle_id: Bundle identifier to check

Returns:
    ValidationResult with error if duplicate

**Parameters:**

- `self`
- `bundle_id` (str)

**Returns:** ValidationResult

##### validate_description

```python
def validate_description(self, description: str) -> ValidationResult
```

Validate bundle description.

Args:
    description: Description text

Returns:
    ValidationResult with errors if invalid

**Parameters:**

- `self`
- `description` (str)

**Returns:** ValidationResult

##### validate_default_count

```python
def validate_default_count(self, count: int) -> ValidationResult
```

Validate default article count.

Args:
    count: Article count

Returns:
    ValidationResult with errors if invalid

**Parameters:**

- `self`
- `count` (int)

**Returns:** ValidationResult

##### validate_source_ids

```python
def validate_source_ids(self, source_ids: List[str]) -> Tuple[List[str], List[str]]
```

Validate source IDs against registry.

Args:
    source_ids: List of source IDs to validate

Returns:
    Tuple of (valid_ids, invalid_ids)

**Parameters:**

- `self`
- `source_ids` (List[str])

**Returns:** Tuple[List[str], List[str]]

##### validate_bundle_exists

```python
def validate_bundle_exists(self, bundle_id: str) -> ValidationResult
```

Check if bundle exists.

Args:
    bundle_id: Bundle identifier

Returns:
    ValidationResult with error if not found

**Parameters:**

- `self`
- `bundle_id` (str)

**Returns:** ValidationResult

##### validate_not_protected

```python
def validate_not_protected(self, bundle_id: str) -> ValidationResult
```

Check if bundle is protected from modification.

Args:
    bundle_id: Bundle identifier

Returns:
    ValidationResult with error if protected

**Parameters:**

- `self`
- `bundle_id` (str)

**Returns:** ValidationResult


