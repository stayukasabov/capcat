# core.source_system.add_source_service

**File:** `Application/core/source_system/add_source_service.py`

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
def __init__(self, base_path: Optional[Path] = None)
```

Initialize the add-source service.

Args:
    base_path: Optional base path for the application (defaults to CLI's parent)

**Parameters:**

- `self`
- `base_path` (Optional[Path]) *optional*

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

Factory function to create an AddSourceService instance.

Returns:
    Configured AddSourceService instance

**Returns:** AddSourceService

