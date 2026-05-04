---
layout: default
render_with_liquid: false
---

# capcat.core.source_system.bundle_service

**File:** `Application/capcat/core/source_system/bundle_service.py`

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

⚠️ **High complexity:** 11

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


## Functions

### get_available_bundles

```python
def get_available_bundles(project_root: Path = None) -> dict
```

Load bundles from userspace (if mirrored) or builtin bundles.yml.

Args:
    project_root: Project root path. When provided and user bundles.yml
        exists there, reads from userspace. Falls back to builtin.

**Parameters:**

- `project_root` (Path) *optional*

**Returns:** dict

### get_available_sources

```python
def get_available_sources() -> dict
```

Get available sources from the source registry, excluding hidden sources.

**Returns:** dict

