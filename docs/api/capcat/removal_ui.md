---
layout: default
render_with_liquid: false
---

# capcat.core.source_system.removal_ui

**File:** `Application/capcat/core/source_system/removal_ui.py`

## Description

User interface implementation for remove-source command.
Follows the same clean styling as add-source with orange theme.

## Classes

### QuestionaryRemovalUI

Interactive UI for remove-source using questionary.
Matches the styling of add-source and catch menu.

#### Methods

##### __init__

```python
def __init__(self, questionary_module = None)
```

Initialize with optional questionary module.

Args:
    questionary_module: Optional questionary for testing

**Parameters:**

- `self`
- `questionary_module` *optional*

##### select_sources_to_remove

```python
def select_sources_to_remove(self, sources: List[tuple[str, str]]) -> List[str]
```

Let user select sources to remove using checkbox.

Args:
    sources: List of (source_id, display_name) tuples

Returns:
    List of selected source IDs

**Parameters:**

- `self`
- `sources` (List[tuple[str, str]])

**Returns:** List[str]

##### show_removal_summary

```python
def show_removal_summary(self, sources_info: List[SourceRemovalInfo]) -> None
```

Display summary of what will be removed.

Args:
    sources_info: Information about sources to be removed

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** None

##### confirm_removal

```python
def confirm_removal(self, sources_info: List[SourceRemovalInfo]) -> bool
```

Confirm removal with user.

Args:
    sources_info: Sources to be removed

Returns:
    True if confirmed, False otherwise

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** bool

##### show_success

```python
def show_success(self, message: str) -> None
```

Display success message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_error

```python
def show_error(self, message: str) -> None
```

Display error message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_info

```python
def show_info(self, message: str) -> None
```

Display informational message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None


### MockRemovalUI

Mock UI for testing remove-source.

#### Methods

##### __init__

```python
def __init__(self, responses: dict)
```

Initialize with predefined responses.

Args:
    responses: Dictionary with test responses

**Parameters:**

- `self`
- `responses` (dict)

##### select_sources_to_remove

```python
def select_sources_to_remove(self, sources: List[tuple[str, str]]) -> List[str]
```

Record call and return the configured selected_sources response.

Args:
    sources: List of ``(source_id, display_name)`` tuples.

Returns:
    ``responses['selected_sources']`` if set, otherwise ``[]``.

**Parameters:**

- `self`
- `sources` (List[tuple[str, str]])

**Returns:** List[str]

##### show_removal_summary

```python
def show_removal_summary(self, sources_info: List[SourceRemovalInfo]) -> None
```

Record call without printing the summary.

Args:
    sources_info: Source removal info objects passed by the workflow.

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** None

##### confirm_removal

```python
def confirm_removal(self, sources_info: List[SourceRemovalInfo]) -> bool
```

Record call and return the configured confirm_removal response.

Args:
    sources_info: Source removal info objects passed by the workflow.

Returns:
    ``responses['confirm_removal']`` if set, otherwise ``False``.

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** bool

##### show_success

```python
def show_success(self, message: str) -> None
```

Record success message call without producing output.

Args:
    message: Success message passed by the workflow.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_error

```python
def show_error(self, message: str) -> None
```

Record error message call without producing output.

Args:
    message: Error message passed by the workflow.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_info

```python
def show_info(self, message: str) -> None
```

Record info message call without producing output.

Args:
    message: Informational message passed by the workflow.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None


