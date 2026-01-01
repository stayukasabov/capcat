# core.command_logging

**File:** `Application/core/command_logging.py`

## Description

Enhanced command logging for CLI debugging and audit trail.

## Classes

### CommandLogger

Logger for CLI command execution and debugging.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### log_command_start

```python
def log_command_start(self, command: str, args: Dict[str, Any], raw_args: List[str])
```

Log command execution start with full context.

Args:
    command: Command name (e.g., 'fetch', 'bundle')
    args: Parsed arguments dictionary
    raw_args: Raw command line arguments

**Parameters:**

- `self`
- `command` (str)
- `args` (Dict[str, Any])
- `raw_args` (List[str])

##### log_command_end

```python
def log_command_end(self, command: str, success: bool, duration: float, error: Optional[str] = None)
```

Log command execution completion.

Args:
    command: Command name
    success: Whether command succeeded
    duration: Execution duration in seconds
    error: Error message if failed

**Parameters:**

- `self`
- `command` (str)
- `success` (bool)
- `duration` (float)
- `error` (Optional[str]) *optional*

##### log_argument_error

```python
def log_argument_error(self, command: str, error_type: str, error_message: str, raw_args: List[str], suggestions: Optional[List[str]] = None)
```

Log argument parsing errors with suggestions.

Args:
    command: Command name
    error_type: Type of error (e.g., 'flag_syntax', 'invalid_argument')
    error_message: Error description
    raw_args: Raw command line arguments
    suggestions: Suggested corrections

**Parameters:**

- `self`
- `command` (str)
- `error_type` (str)
- `error_message` (str)
- `raw_args` (List[str])
- `suggestions` (Optional[List[str]]) *optional*

##### log_help_displayed

```python
def log_help_displayed(self, command: Optional[str], trigger_reason: str)
```

Log when help is displayed and why.

Args:
    command: Command name (None for main help)
    trigger_reason: Why help was shown (e.g., 'help_flag', 'invalid_syntax')

**Parameters:**

- `self`
- `command` (Optional[str])
- `trigger_reason` (str)


## Functions

### get_command_logger

```python
def get_command_logger() -> CommandLogger
```

Get the global command logger instance.

**Returns:** CommandLogger

### log_command_start

```python
def log_command_start(command: str, args: Dict[str, Any], raw_args: List[str])
```

Log command execution start.

**Parameters:**

- `command` (str)
- `args` (Dict[str, Any])
- `raw_args` (List[str])

### log_command_end

```python
def log_command_end(command: str, success: bool, duration: float, error: Optional[str] = None)
```

Log command execution end.

**Parameters:**

- `command` (str)
- `success` (bool)
- `duration` (float)
- `error` (Optional[str]) *optional*

### log_argument_error

```python
def log_argument_error(command: str, error_type: str, error_message: str, raw_args: List[str], suggestions: Optional[List[str]] = None)
```

Log argument parsing error.

**Parameters:**

- `command` (str)
- `error_type` (str)
- `error_message` (str)
- `raw_args` (List[str])
- `suggestions` (Optional[List[str]]) *optional*

### log_help_displayed

```python
def log_help_displayed(command: Optional[str], trigger_reason: str)
```

Log help display event.

**Parameters:**

- `command` (Optional[str])
- `trigger_reason` (str)

