# core.source_system.bundle_service

**File:** `Application/core/source_system/bundle_service.py`

## Description

Service layer for bundle management.
Orchestrates BundleManager, BundleValidator, and BundleUI.

## Classes

### BundleService

Service for bundle management operations.
Coordinates validation, UI, and persistence.

#### Methods

##### __init__

```python
def __init__(self, bundles_path: Path, ui: BundleUI = None, logger = None)
```

Args:
    bundles_path: Path to bundles.yml
    ui: BundleUI instance (creates if None)
    logger: Logger instance (creates if None)

**Parameters:**

- `self`
- `bundles_path` (Path)
- `ui` (BundleUI) *optional*
- `logger` *optional*

##### execute_create_bundle

```python
def execute_create_bundle(self) -> None
```

Execute bundle creation workflow.

**Parameters:**

- `self`

**Returns:** None

⚠️ **High complexity:** 11

##### execute_delete_bundle

```python
def execute_delete_bundle(self) -> None
```

Execute bundle deletion workflow.

**Parameters:**

- `self`

**Returns:** None

##### execute_edit_bundle

```python
def execute_edit_bundle(self) -> None
```

Execute bundle editing workflow.

**Parameters:**

- `self`

**Returns:** None

⚠️ **High complexity:** 15

##### execute_add_sources

```python
def execute_add_sources(self) -> None
```

Execute add sources to bundle workflow.

**Parameters:**

- `self`

**Returns:** None

##### execute_remove_sources

```python
def execute_remove_sources(self) -> None
```

Execute remove sources from bundle workflow.

**Parameters:**

- `self`

**Returns:** None

##### execute_move_source

```python
def execute_move_source(self) -> None
```

Execute move source between bundles workflow.

**Parameters:**

- `self`

**Returns:** None

##### execute_list_bundles

```python
def execute_list_bundles(self) -> None
```

Execute list bundles workflow.

**Parameters:**

- `self`

**Returns:** None


