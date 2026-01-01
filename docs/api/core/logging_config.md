# core.logging_config

**File:** `Application/core/logging_config.py`

## Description

Logging configuration for Capcat.
Provides centralized logging setup with configurable levels and optional file output.

## Constants

### COLORS

**Value:** `{'DEBUG': '\x1b[36m', 'INFO': '\x1b[38;5;230m', 'WARNING': '\x1b[33m', 'ERROR': '\x1b[31m', 'CRITICAL': '\x1b[35m', 'RESET': '\x1b[0m'}`

### EMOJIS

**Value:** `{'DEBUG': '\x1b[36m⚚\x1b[0m', 'INFO': '\x1b[32m Catching→\x1b[0m', 'WARNING': '\x1b[33m☢\x1b[0m', 'ERROR': '\x1b[31m☒\x1b[0m', 'CRITICAL': '\x1b[35m Catching→\x1b[0m'}`

## Classes

### ProgressFilter

**Inherits from:** logging.Filter

Filter to suppress INFO/DEBUG logs during progress animation.

#### Methods

##### filter

```python
def filter(self, record)
```

**Parameters:**

- `self`
- `record`


### ColoredFormatter

**Inherits from:** logging.Formatter

Custom formatter with colors for different log levels.

#### Methods

##### format

```python
def format(self, record)
```

**Parameters:**

- `self`
- `record`


## Functions

### set_progress_active

```python
def set_progress_active(active: bool)
```

Set whether progress animation is active (to suppress console logging).

**Parameters:**

- `active` (bool)

### is_progress_active

```python
def is_progress_active() -> bool
```

Check if progress animation is currently active.

**Returns:** bool

### setup_logging

```python
def setup_logging(level: str = 'INFO', log_file: Optional[str] = None, quiet: bool = False, verbose: bool = False) -> logging.Logger
```

Setup logging configuration for Capcat.

Args:
    level: Base logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    log_file: Optional file path to write logs to
    quiet: If True, only show warnings and errors
    verbose: If True, show debug messages

Returns:
    Configured logger instance

**Parameters:**

- `level` (str) *optional*
- `log_file` (Optional[str]) *optional*
- `quiet` (bool) *optional*
- `verbose` (bool) *optional*

**Returns:** logging.Logger

### get_logger

```python
def get_logger(name: str = '') -> logging.Logger
```

Get a logger instance for a specific module.

Args:
    name: Logger name (usually __name__ from the calling module)

Returns:
    Logger instance

**Parameters:**

- `name` (str) *optional*

**Returns:** logging.Logger

### set_verbosity

```python
def set_verbosity(verbose: bool = False, quiet: bool = False)
```

Dynamically change the verbosity of the console handler.

Args:
    verbose: Show debug messages
    quiet: Show only warnings and errors

**Parameters:**

- `verbose` (bool) *optional*
- `quiet` (bool) *optional*

