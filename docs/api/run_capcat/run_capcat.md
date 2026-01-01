# run_capcat

**File:** `Application/run_capcat.py`

## Description

Capcat - News Article Archiving System (Enhanced Python Wrapper)

Refactored wrapper with robust dependency management, intelligent error
handling, and comprehensive validation. Integrates with the automated
dependency setup system.

Author: Stayu Kasabov (https://stayux.com)
License: MIT-Style Non-Commercial
Copyright (c) 2025 Stayu Kasabov

## Classes

### CapcatExecutionError

**Inherits from:** Exception

Custom exception for Capcat execution failures.


### DependencyError

**Inherits from:** Exception

Custom exception for dependency-related failures.


### CapcatWrapperRefactored

Enhanced wrapper with robust dependency management and error handling.

Provides intelligent dependency validation, automatic repair, comprehensive
error handling, and fallback mechanisms for reliability.

Attributes:
    script_dir: Application root directory path
    capcat_py: Path to main capcat.py script
    dependency_script: Path to automated dependency setup script

#### Methods

##### __init__

```python
def __init__(self) -> None
```

Initialize the wrapper with path validation.

Sets up script directory paths and validates that essential files exist.
Falls back to basic dependency management if enhanced script missing.

Raises:
    CapcatExecutionError: If capcat.py not found in script directory

**Parameters:**

- `self`

**Returns:** None

##### _validate_installation

```python
def _validate_installation(self) -> None
```

Validate that essential files exist.

Checks for capcat.py and dependency setup script. Sets dependency_script
to None if enhanced script missing (triggers basic fallback).

Raises:
    CapcatExecutionError: If capcat.py not found

**Parameters:**

- `self`

**Returns:** None

##### _log_message

```python
def _log_message(self, message: str, level: str = 'INFO', color: str = '\x1b[38;5;157m') -> None
```

Log formatted message with color.

Args:
    message: Text to log
    level: Log level string (INFO, ERROR, WARNING, SUCCESS)
    color: ANSI color code for formatting

**Parameters:**

- `self`
- `message` (str)
- `level` (str) *optional*
- `color` (str) *optional*

**Returns:** None

##### _log_error

```python
def _log_error(self, message: str) -> None
```

Log error message.

Args:
    message: Error message to display

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### _log_warning

```python
def _log_warning(self, message: str) -> None
```

Log warning message.

Args:
    message: Warning message to display

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### _log_success

```python
def _log_success(self, message: str) -> None
```

Log success message.

Args:
    message: Success message to display

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### _run_dependency_setup

```python
def _run_dependency_setup(self, force_rebuild: bool = False) -> bool
```

Run the automated dependency setup script.

Falls back to basic setup if enhanced script unavailable.

Args:
    force_rebuild: Force complete venv rebuild

Returns:
    True if setup successful, False otherwise

Raises:
    subprocess.CalledProcessError: If dependency setup command fails

**Parameters:**

- `self`
- `force_rebuild` (bool) *optional*

**Returns:** bool

##### _basic_dependency_setup

```python
def _basic_dependency_setup(self) -> bool
```

Basic fallback dependency setup when enhanced script unavailable.

Creates venv if missing and installs requirements.txt dependencies.

Returns:
    True if basic setup successful, False otherwise

Raises:
    subprocess.CalledProcessError: If venv creation or pip install fails

**Parameters:**

- `self`

**Returns:** bool

##### _get_python_executable

```python
def _get_python_executable(self) -> str
```

Get the best available Python executable.

Tries venv Python first, tests if it works, then falls back to
system Python if necessary.

Returns:
    Path to Python executable

Raises:
    DependencyError: If no suitable Python found

**Parameters:**

- `self`

**Returns:** str

##### _validate_dependencies

```python
def _validate_dependencies(self, python_exe: str) -> bool
```

Quick validation of critical dependencies.

Tests imports of requests, yaml, and bs4 (BeautifulSoup).

Args:
    python_exe: Python executable to test

Returns:
    True if basic dependencies available, False otherwise

**Parameters:**

- `self`
- `python_exe` (str)

**Returns:** bool

##### _handle_dependency_failure

```python
def _handle_dependency_failure(self, python_exe: str) -> bool
```

Handle dependency validation failure with repair attempts.

Tries automated setup first, then force rebuild as last resort.

Args:
    python_exe: Python executable that failed validation

Returns:
    True if repair successful, False otherwise

**Parameters:**

- `self`
- `python_exe` (str)

**Returns:** bool

##### _should_show_success_message

```python
def _should_show_success_message(self, args: List[str]) -> bool
```

Determine if success message should be shown.

Suppresses success message for help/version/list commands and
detects when help was triggered by flag syntax errors.

Args:
    args: Command line arguments

Returns:
    True if success message appropriate, False otherwise

**Parameters:**

- `self`
- `args` (List[str])

**Returns:** bool

##### _show_intelligent_help

```python
def _show_intelligent_help(self, args: List[str], detected_issues: List[str])
```

Show intelligent help when flag syntax errors are detected.

Args:
    args: Original command line arguments
    detected_issues: List of problematic flags detected

**Parameters:**

- `self`
- `args` (List[str])
- `detected_issues` (List[str])

##### execute_capcat

```python
def execute_capcat(self, args: List[str]) -> int
```

Execute capcat.py with comprehensive error handling.

Validates dependencies, attempts repair if needed, and executes capcat
with proper subprocess management and error handling.

Args:
    args: Command line arguments to pass to capcat.py

Returns:
    Exit code from capcat execution

Raises:
    CapcatExecutionError: If execution fails
    DependencyError: If dependencies cannot be resolved

**Parameters:**

- `self`
- `args` (List[str])

**Returns:** int

##### run

```python
def run(self) -> None
```

Main execution method with comprehensive error handling.

Handles all exceptions and exits with appropriate codes. Provides
manual recovery instructions on failure.

Exit Codes:
    0: Success
    1: Unexpected error
    2: Dependency error
    3: Execution error
    130: User interrupt (Ctrl+C)

**Parameters:**

- `self`

**Returns:** None


## Functions

### main

```python
def main() -> None
```

Entry point for the enhanced wrapper.

Instantiates CapcatWrapperRefactored and runs the application with
comprehensive dependency management and error handling.

**Returns:** None

