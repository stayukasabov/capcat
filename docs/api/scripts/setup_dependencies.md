# scripts.setup_dependencies

**File:** `Application/scripts/setup_dependencies.py`

## Description

Automated Dependency Setup and Repair Script for Capcat

This script provides robust virtual environment management with:
- Intelligent venv validation and repair
- Dependency verification and installation
- Path corruption detection and fixing
- Fallback mechanisms for common issues
- Comprehensive logging and diagnostics

Usage:
    python3 scripts/setup_dependencies.py [options]

Options:
    --force-rebuild    Force complete venv rebuild
    --check-only       Only validate, don't install/repair
    --verbose         Enable detailed logging
    --requirements     Custom requirements file path

## Constants

### RED

**Value:** `'\x1b[0;31m'`

### GREEN

**Value:** `'\x1b[38;5;157m'`

### YELLOW

**Value:** `'\x1b[38;5;166m'`

### BLUE

**Value:** `'\x1b[0;34m'`

### CYAN

**Value:** `'\x1b[0;36m'`

### NC

**Value:** `'\x1b[0m'`

## Classes

### Colors

ANSI color codes for terminal output.


### DependencyManager

Comprehensive dependency management system for Capcat.

Handles virtual environment creation, validation, repair,
and dependency installation with robust error handling.

#### Methods

##### __init__

```python
def __init__(self, base_path: Optional[Path] = None, verbose: bool = False)
```

Initialize dependency manager.

Args:
    base_path: Application base directory (auto-detected if None)
    verbose: Enable detailed logging

**Parameters:**

- `self`
- `base_path` (Optional[Path]) *optional*
- `verbose` (bool) *optional*

##### log

```python
def log(self, message: str, color: str = Colors.GREEN, prefix: str = 'INFO') -> None
```

Print colored log message.

**Parameters:**

- `self`
- `message` (str)
- `color` (str) *optional*
- `prefix` (str) *optional*

**Returns:** None

##### log_verbose

```python
def log_verbose(self, message: str) -> None
```

Print verbose log message if verbose mode enabled.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### log_error

```python
def log_error(self, message: str) -> None
```

Print error message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### log_warning

```python
def log_warning(self, message: str) -> None
```

Print warning message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### log_success

```python
def log_success(self, message: str) -> None
```

Print success message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### check_python_version

```python
def check_python_version(self) -> bool
```

Verify Python version meets requirements.

Returns:
    True if Python version is acceptable

**Parameters:**

- `self`

**Returns:** bool

##### detect_venv_corruption

```python
def detect_venv_corruption(self) -> Tuple[bool, List[str]]
```

Detect various types of virtual environment corruption.

Returns:
    Tuple of (is_corrupted, list_of_issues)

**Parameters:**

- `self`

**Returns:** Tuple[bool, List[str]]

⚠️ **High complexity:** 13

##### rebuild_venv

```python
def rebuild_venv(self) -> bool
```

Completely rebuild the virtual environment.

Returns:
    True if rebuild successful

**Parameters:**

- `self`

**Returns:** bool

##### get_required_packages

```python
def get_required_packages(self) -> List[str]
```

Parse requirements.txt and return list of required packages.

Returns:
    List of package names (without version specifiers)

**Parameters:**

- `self`

**Returns:** List[str]

##### validate_dependencies

```python
def validate_dependencies(self, python_exe: str) -> Tuple[bool, List[str]]
```

Validate that all required dependencies are installed and importable.

Args:
    python_exe: Path to Python executable to test

Returns:
    Tuple of (all_valid, list_of_missing_packages)

**Parameters:**

- `self`
- `python_exe` (str)

**Returns:** Tuple[bool, List[str]]

##### upgrade_pip

```python
def upgrade_pip(self, python_exe: str) -> bool
```

Upgrade pip to latest version silently.

Args:
    python_exe: Path to Python executable

Returns:
    True if upgrade successful or already latest

**Parameters:**

- `self`
- `python_exe` (str)

**Returns:** bool

##### install_dependencies

```python
def install_dependencies(self, python_exe: str, force: bool = False) -> bool
```

Install dependencies using pip.

Args:
    python_exe: Path to Python executable
    force: Force reinstallation even if packages exist

Returns:
    True if installation successful

**Parameters:**

- `self`
- `python_exe` (str)
- `force` (bool) *optional*

**Returns:** bool

##### _update_dependency_cache

```python
def _update_dependency_cache(self, python_exe: str) -> None
```

Update dependency validation cache.

**Parameters:**

- `self`
- `python_exe` (str)

**Returns:** None

##### get_python_executable

```python
def get_python_executable(self) -> str
```

Get the best available Python executable.

Returns:
    Path to Python executable (venv or system fallback)

**Parameters:**

- `self`

**Returns:** str

##### setup_dependencies

```python
def setup_dependencies(self, force_rebuild: bool = False, check_only: bool = False) -> bool
```

Main method to setup and validate dependencies.

Args:
    force_rebuild: Force complete venv rebuild
    check_only: Only validate, don't install/repair

Returns:
    True if dependencies are ready

**Parameters:**

- `self`
- `force_rebuild` (bool) *optional*
- `check_only` (bool) *optional*

**Returns:** bool


## Functions

### main

```python
def main()
```

CLI entry point for dependency setup script.

