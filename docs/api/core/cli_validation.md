# core.cli_validation

**File:** `Application/core/cli_validation.py`

## Description

Enhanced CLI validation and error handling for better user experience.

## Classes

### CLIValidationError

**Inherits from:** Exception

Custom exception for CLI validation errors.


### CLIValidator

Enhanced CLI validation with helpful error messages.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### validate_unknown_args

```python
def validate_unknown_args(self, unknown_args: List[str], valid_flags: List[str]) -> None
```

Validate unknown arguments and provide helpful suggestions.

Args:
    unknown_args: List of unrecognized arguments
    valid_flags: List of valid flag names

Raises:
    CLIValidationError: If invalid flags are found with suggestions

**Parameters:**

- `self`
- `unknown_args` (List[str])
- `valid_flags` (List[str])

**Returns:** None

##### detect_flag_typos

```python
def detect_flag_typos(self, args_string: str) -> List[str]
```

Detect common flag typing mistakes in command string.

Args:
    args_string: Full command line arguments as string

Returns:
    List of detected issues with suggestions

**Parameters:**

- `self`
- `args_string` (str)

**Returns:** List[str]

##### suggest_correct_command

```python
def suggest_correct_command(self, original_command: str) -> Optional[str]
```

Suggest corrected command based on common mistakes.

Args:
    original_command: Original command with errors

Returns:
    Suggested corrected command or None

**Parameters:**

- `self`
- `original_command` (str)

**Returns:** Optional[str]


## Functions

### validate_cli_args

```python
def validate_cli_args(args: Any, command_line: str) -> None
```

Validate CLI arguments and provide helpful error messages.

Args:
    args: Parsed arguments object
    command_line: Original command line string

Raises:
    CLIValidationError: If validation fails

**Parameters:**

- `args` (Any)
- `command_line` (str)

**Returns:** None

### with_cli_validation

```python
def with_cli_validation(func)
```

Decorator to add CLI validation to command functions.

**Parameters:**

- `func`

### wrapper

```python
def wrapper()
```

