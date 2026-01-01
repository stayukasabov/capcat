# core.source_system.bundle_ui

**File:** `Application/core/source_system/bundle_ui.py`

## Description

User interface components for bundle management.
Uses questionary for consistent menu design.

## Classes

### BundleUI

Interactive UI for bundle management.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### show_bundle_menu

```python
def show_bundle_menu(self) -> Optional[str]
```

Show main bundle management menu.

Returns:
    Selected action or None if cancelled

**Parameters:**

- `self`

**Returns:** Optional[str]

##### prompt_create_bundle

```python
def prompt_create_bundle(self) -> Optional[BundleData]
```

Prompt user for new bundle information.

Returns:
    BundleData or None if cancelled

**Parameters:**

- `self`

**Returns:** Optional[BundleData]

##### prompt_edit_bundle_metadata

```python
def prompt_edit_bundle_metadata(self, current_description: str, current_default_count: int) -> Optional[Dict[str, any]]
```

Prompt user to edit bundle metadata.

Args:
    current_description: Current description
    current_default_count: Current default count

Returns:
    Dictionary with updated values or None if cancelled

**Parameters:**

- `self`
- `current_description` (str)
- `current_default_count` (int)

**Returns:** Optional[Dict[str, any]]

##### prompt_select_bundle

```python
def prompt_select_bundle(self, bundles: List[Dict[str, any]], message: str = '  Select a bundle:', show_cancel: bool = True) -> Optional[str]
```

Prompt user to select a bundle from list.

Args:
    bundles: List of bundle dictionaries
    message: Prompt message
    show_cancel: Whether to show cancel option

Returns:
    Selected bundle_id or None if cancelled

**Parameters:**

- `self`
- `bundles` (List[Dict[str, any]])
- `message` (str) *optional*
- `show_cancel` (bool) *optional*

**Returns:** Optional[str]

##### prompt_select_sources

```python
def prompt_select_sources(self, sources: Dict[str, str], current_selections: List[str] = None, message: str = '  Select sources:', group_by_category: bool = True) -> Optional[List[str]]
```

Prompt user to multi-select sources.

Args:
    sources: Dict of source_id -> display_name
    current_selections: Pre-selected source IDs
    message: Prompt message
    group_by_category: Whether to group sources by category

Returns:
    List of selected source IDs or None if cancelled

**Parameters:**

- `self`
- `sources` (Dict[str, str])
- `current_selections` (List[str]) *optional*
- `message` (str) *optional*
- `group_by_category` (bool) *optional*

**Returns:** Optional[List[str]]

##### prompt_copy_or_move

```python
def prompt_copy_or_move(self) -> Optional[str]
```

Prompt user to choose between copy and move mode.

Returns:
    'copy' or 'move' or None if cancelled

**Parameters:**

- `self`

**Returns:** Optional[str]

##### show_bundle_details

```python
def show_bundle_details(self, bundle_info: Dict[str, any]) -> None
```

Display detailed bundle information.

Args:
    bundle_info: Bundle information dictionary

**Parameters:**

- `self`
- `bundle_info` (Dict[str, any])

**Returns:** None

##### show_all_bundles

```python
def show_all_bundles(self, bundles: List[Dict[str, any]]) -> None
```

Display all bundles in a formatted list.

Args:
    bundles: List of bundle dictionaries

**Parameters:**

- `self`
- `bundles` (List[Dict[str, any]])

**Returns:** None

##### prompt_confirm

```python
def prompt_confirm(self, message: str, details: List[str] = None, default: bool = False) -> bool
```

Prompt user for confirmation.

Args:
    message: Confirmation question
    details: Optional list of detail lines to show
    default: Default response

Returns:
    True if confirmed, False otherwise

**Parameters:**

- `self`
- `message` (str)
- `details` (List[str]) *optional*
- `default` (bool) *optional*

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

##### show_warning

```python
def show_warning(self, message: str) -> None
```

Display warning message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None


