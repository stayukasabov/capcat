# core.source_system.questionary_ui

**File:** `Application/core/source_system/questionary_ui.py`

## Description

User interface implementation using questionary for interactive prompts.
Implements the UserInterface protocol for clean separation of concerns.

## Classes

### QuestionaryUserInterface

Interactive user interface using questionary library.
Handles all user interactions for the add-source command.

#### Methods

##### __init__

```python
def __init__(self, questionary_module = None)
```

Initialize with optional questionary module for dependency injection.

Args:
    questionary_module: Optional questionary module for testing

**Parameters:**

- `self`
- `questionary_module` *optional*

##### get_source_id

```python
def get_source_id(self, suggested: str) -> str
```

Get source ID from user with suggestion.

Args:
    suggested: Suggested source ID based on feed title

Returns:
    User-entered source ID

Raises:
    SystemExit: If user cancels or provides empty input

**Parameters:**

- `self`
- `suggested` (str)

**Returns:** str

##### select_category

```python
def select_category(self, categories: List[str]) -> str
```

Let user select a category from available options.

Args:
    categories: List of available categories

Returns:
    Selected category

Raises:
    SystemExit: If user cancels selection

**Parameters:**

- `self`
- `categories` (List[str])

**Returns:** str

##### confirm_bundle_addition

```python
def confirm_bundle_addition(self) -> bool
```

Ask user if they want to add source to a bundle.

Returns:
    True if user wants to add to bundle, False otherwise

**Parameters:**

- `self`

**Returns:** bool

##### select_bundle

```python
def select_bundle(self, bundles: List[str]) -> Optional[str]
```

Let user select a bundle from available options.

Args:
    bundles: List of available bundle names

Returns:
    Selected bundle name or None if cancelled

**Parameters:**

- `self`
- `bundles` (List[str])

**Returns:** Optional[str]

##### confirm_test_fetch

```python
def confirm_test_fetch(self) -> bool
```

Ask user if they want to run a test fetch.

Returns:
    True if user wants to test, False otherwise

**Parameters:**

- `self`

**Returns:** bool

##### show_success

```python
def show_success(self, message: str) -> None
```

Display success message to user.

Args:
    message: Success message to display

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_error

```python
def show_error(self, message: str) -> None
```

Display error message to user.

Args:
    message: Error message to display

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_info

```python
def show_info(self, message: str) -> None
```

Display informational message to user.

Args:
    message: Info message to display

**Parameters:**

- `self`
- `message` (str)

**Returns:** None


### MockUserInterface

Mock user interface for testing purposes.
Provides predictable responses for automated testing.

#### Methods

##### __init__

```python
def __init__(self, responses: dict)
```

Initialize with predefined responses.

Args:
    responses: Dictionary mapping method names to return values

**Parameters:**

- `self`
- `responses` (dict)

##### get_source_id

```python
def get_source_id(self, suggested: str) -> str
```

**Parameters:**

- `self`
- `suggested` (str)

**Returns:** str

##### select_category

```python
def select_category(self, categories: List[str]) -> str
```

**Parameters:**

- `self`
- `categories` (List[str])

**Returns:** str

##### confirm_bundle_addition

```python
def confirm_bundle_addition(self) -> bool
```

**Parameters:**

- `self`

**Returns:** bool

##### select_bundle

```python
def select_bundle(self, bundles: List[str]) -> Optional[str]
```

**Parameters:**

- `self`
- `bundles` (List[str])

**Returns:** Optional[str]

##### confirm_test_fetch

```python
def confirm_test_fetch(self) -> bool
```

**Parameters:**

- `self`

**Returns:** bool

##### show_success

```python
def show_success(self, message: str) -> None
```

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_error

```python
def show_error(self, message: str) -> None
```

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_info

```python
def show_info(self, message: str) -> None
```

**Parameters:**

- `self`
- `message` (str)

**Returns:** None


