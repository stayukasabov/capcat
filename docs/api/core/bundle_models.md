# core.source_system.bundle_models

**File:** `Application/core/source_system/bundle_models.py`

## Description

Data models for bundle management.

## Classes

### BundleInfo

Complete information about a bundle.


### BundleData

Data for creating/updating a bundle.


### ValidationResult

Result of a validation operation.


### BackupMetadata

Metadata for bundle backup.

#### Methods

##### formatted_timestamp

```python
def formatted_timestamp(self) -> str
```

Human-readable timestamp.

**Parameters:**

- `self`

**Returns:** str


### BundleOperation

Record of bundle operation for undo/audit.


