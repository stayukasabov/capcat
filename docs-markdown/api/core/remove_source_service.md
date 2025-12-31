# core.source_system.remove_source_service

**File:** `Application/core/source_system/remove_source_service.py`

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
def __init__(self, base_path: Optional[Path] = None)
```

Initialize the remove-source service.

Args:
    base_path: Optional base path for the application

**Parameters:**

- `self`
- `base_path` (Optional[Path]) *optional*

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


## Functions

### create_remove_source_service

```python
def create_remove_source_service() -> RemoveSourceService
```

Factory function to create RemoveSourceService.

Returns:
    Configured RemoveSourceService instance

**Returns:** RemoveSourceService

