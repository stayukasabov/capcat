# core.cli_recovery

**File:** `Application/core/cli_recovery.py`

## Description

CLI error recovery and user guidance system.

## Classes

### CLIRecovery

System for recovering from CLI errors and guiding users.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### handle_help_triggered_by_error

```python
def handle_help_triggered_by_error(self, args: List[str]) -> bool
```

Handle cases where help was triggered by a syntax error.

Args:
    args: Command line arguments

Returns:
    True if error was detected and handled, False otherwise

**Parameters:**

- `self`
- `args` (List[str])

**Returns:** bool

##### _is_suspicious_flag

```python
def _is_suspicious_flag(self, arg: str) -> bool
```

Check if argument looks like a common flag mistake.

**Parameters:**

- `self`
- `arg` (str)

**Returns:** bool

##### _get_flag_suggestion

```python
def _get_flag_suggestion(self, flag: str) -> Optional[str]
```

Get suggested correction for a flag.

**Parameters:**

- `self`
- `flag` (str)

**Returns:** Optional[str]

##### _show_recovery_options

```python
def _show_recovery_options(self, args: List[str])
```

Show recovery options to the user.

**Parameters:**

- `self`
- `args` (List[str])

##### _auto_correct_command

```python
def _auto_correct_command(self, command: str) -> str
```

Automatically correct common command mistakes.

**Parameters:**

- `self`
- `command` (str)

**Returns:** str

##### suggest_alternative_commands

```python
def suggest_alternative_commands(self, failed_command: str, command_type: str) -> List[str]
```

Suggest alternative commands when the current one fails.

Args:
    failed_command: The command that failed
    command_type: Type of command ('fetch', 'bundle', etc.)

Returns:
    List of suggested alternative commands

**Parameters:**

- `self`
- `failed_command` (str)
- `command_type` (str)

**Returns:** List[str]

##### provide_contextual_help

```python
def provide_contextual_help(self, command_type: str, error_context: Dict)
```

Provide contextual help based on the specific error and command type.

Args:
    command_type: Type of command that failed
    error_context: Context about what went wrong

**Parameters:**

- `self`
- `command_type` (str)
- `error_context` (Dict)


## Functions

### handle_cli_error_recovery

```python
def handle_cli_error_recovery(args: List[str], command_type: Optional[str] = None) -> bool
```

Handle CLI error recovery and provide user guidance.

Args:
    args: Command line arguments that caused error
    command_type: Type of command if known

Returns:
    True if recovery guidance was provided

**Parameters:**

- `args` (List[str])
- `command_type` (Optional[str]) *optional*

**Returns:** bool

