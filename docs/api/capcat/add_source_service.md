---
layout: default
---

# capcat.core.source_system.add_source_service

**File:** `Application/capcat/core/source_system/add_source_service.py`

## Description

Service layer for the add-source command.
Provides a clean interface for CLI integration while maintaining separation of concerns.

## Classes

### AddSourceService

Service for adding new RSS sources.
Provides a clean, high-level interface for CLI integration.

#### Methods

##### __init__

```python
def __init__(self, base_path: Optional[Path] = None, project_root: Optional[Path] = None)
```

Args:
    project_root: Project root (preferred). When provided, writes to
        Config/sources/active/config_driven/configs/.
    base_path: Legacy fallback (package root). Ignored when project_root is set.

**Parameters:**

- `self`
- `base_path` (Optional[Path]) *optional*
- `project_root` (Optional[Path]) *optional*

##### add_source

```python
def add_source(self, url: str) -> None
```

Add a new RSS source using the provided URL.

Args:
    url: URL of the RSS feed to add

Raises:
    CapcatError: If the source cannot be added

**Parameters:**

- `self`
- `url` (str)

**Returns:** None

##### _write_manifest_entry

```python
def _write_manifest_entry(self, filename: str) -> None
```

Write a manifest entry with builtin_hash='' for a user-added source.

**Parameters:**

- `self`
- `filename` (str)

**Returns:** None

##### _create_add_source_command

```python
def _create_add_source_command(self) -> AddSourceCommand
```

Create and configure the AddSourceCommand with all dependencies.

**Parameters:**

- `self`

**Returns:** AddSourceCommand


## Functions

### create_add_source_service

```python
def create_add_source_service() -> AddSourceService
```

Factory: creates AddSourceService with project_root when inside a capcat project.

**Returns:** AddSourceService

