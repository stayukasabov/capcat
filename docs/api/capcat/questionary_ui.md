# capcat.core.source_system.questionary_ui

**File:** `Application/capcat/core/source_system/questionary_ui.py`

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

##### get_display_name

```python
def get_display_name(self, suggested: str) -> str
```

Get display name from user with feed title as suggestion.

Args:
    suggested: Feed title from RSS feed

Returns:
    User-entered display name

**Parameters:**

- `self`
- `suggested` (str)

**Returns:** str

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

##### get_article_count

```python
def get_article_count(self) -> int
```

Ask how many articles to fetch per run.

**Parameters:**

- `self`

**Returns:** int

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
def __init__(self, responses: dict = None)
```

Initialize with predefined responses.

Args:
    responses: Dictionary mapping method names to return values

**Parameters:**

- `self`
- `responses` (dict) *optional*

##### get_display_name

```python
def get_display_name(self, suggested: str) -> str
```

Record call and return the configured display_name response.

Args:
    suggested: Feed title passed by the workflow.

Returns:
    ``responses['display_name']`` if set, otherwise *suggested*.

**Parameters:**

- `self`
- `suggested` (str)

**Returns:** str

##### get_source_id

```python
def get_source_id(self, suggested: str) -> str
```

Record call and return the configured source_id response.

Args:
    suggested: Suggested source ID passed by the workflow.

Returns:
    ``responses['source_id']`` if set, otherwise *suggested*.

**Parameters:**

- `self`
- `suggested` (str)

**Returns:** str

##### select_category

```python
def select_category(self, categories: List[str]) -> str
```

Record call and return the configured category response.

Args:
    categories: Available category names.

Returns:
    ``responses['category']`` if set, otherwise the first category or
    ``'tech'`` when the list is empty.

**Parameters:**

- `self`
- `categories` (List[str])

**Returns:** str

##### get_article_count

```python
def get_article_count(self) -> int
```

**Parameters:**

- `self`

**Returns:** int

##### confirm_bundle_addition

```python
def confirm_bundle_addition(self) -> bool
```

Record call and return the configured confirm_bundle response.

Returns:
    ``responses['confirm_bundle']`` if set, otherwise ``False``.

**Parameters:**

- `self`

**Returns:** bool

##### select_bundle

```python
def select_bundle(self, bundles: List[str]) -> Optional[str]
```

Record call and return the configured bundle response.

Args:
    bundles: Available bundle names.

Returns:
    ``responses['bundle']`` if set, otherwise the first bundle or
    ``None`` when the list is empty.

**Parameters:**

- `self`
- `bundles` (List[str])

**Returns:** Optional[str]

##### confirm_test_fetch

```python
def confirm_test_fetch(self) -> bool
```

Record call and return the configured confirm_test response.

Returns:
    ``responses['confirm_test']`` if set, otherwise ``False``.

**Parameters:**

- `self`

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


