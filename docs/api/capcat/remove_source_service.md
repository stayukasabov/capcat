# capcat.core.source_system.remove_source_service

**File:** `Application/capcat/core/source_system/remove_source_service.py`

## Description

Service layer for remove-source command.
Provides clean integration with CLI while maintaining separation of concerns.

## Classes

### RemoveSourceService

Service for removing existing sources.
Provides high-level interface for CLI integration.

#### Methods

##### __init__

```python
def __init__(self, base_path: Optional[Path] = None, project_root: Optional[Path] = None)
```

Initialize the remove-source service.

Args:
    base_path: Optional base path for the application
    project_root: Optional project root for userspace redirect

**Parameters:**

- `self`
- `base_path` (Optional[Path]) *optional*
- `project_root` (Optional[Path]) *optional*

##### remove_sources

```python
def remove_sources(self) -> None
```

Interactive removal of sources.

Raises:
    CapcatError: If removal fails

**Parameters:**

- `self`

**Returns:** None

##### _create_remove_source_command

```python
def _create_remove_source_command(self) -> RemoveSourceCommand
```

Create and configure RemoveSourceCommand with dependencies.

**Parameters:**

- `self`

**Returns:** RemoveSourceCommand

##### _remove_manifest_entry

```python
def _remove_manifest_entry(self, filename: str) -> None
```

Remove a manifest entry after successful source removal.

**Parameters:**

- `self`
- `filename` (str)

**Returns:** None

##### _remove_manifest_entry_after_remove

```python
def _remove_manifest_entry_after_remove(self) -> None
```

Remove manifest entries for config files that no longer exist on disk.

**Parameters:**

- `self`

**Returns:** None


## Functions

### create_remove_source_service

```python
def create_remove_source_service() -> RemoveSourceService
```

Factory: creates RemoveSourceService with project_root when inside a capcat project.

**Returns:** RemoveSourceService

