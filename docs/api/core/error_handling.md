# core.error_handling

**File:** `Application/core/error_handling.py`

## Description

Comprehensive error handling and recovery system for Capcat.

This module provides:
- Custom exception classes for different error types
- Dependency validation and auto-recovery
- Retry mechanisms with exponential backoff
- Error correlation and monitoring
- Graceful degradation strategies

## Constants

### HAS_REQUESTS

**Value:** `True`

### HAS_YAML

**Value:** `True`

### HAS_BS4

**Value:** `True`

### LOW

**Value:** `'low'`

### MEDIUM

**Value:** `'medium'`

### HIGH

**Value:** `'high'`

### CRITICAL

**Value:** `'critical'`

### DEPENDENCY

**Value:** `'dependency'`

### NETWORK

**Value:** `'network'`

### FILE_SYSTEM

**Value:** `'file_system'`

### CONFIGURATION

**Value:** `'configuration'`

### SOURCE_PROCESSING

**Value:** `'source_processing'`

### MEDIA_DOWNLOAD

**Value:** `'media_download'`

### VALIDATION

**Value:** `'validation'`

### RUNTIME

**Value:** `'runtime'`

### REQUIRED_PACKAGES

**Value:** `{'requests': '2.25.0', 'beautifulsoup4': '4.9.0', 'PyYAML': '5.4.0', 'markdownify': '0.11.0', 'markdown': '3.5.0', 'pygments': '2.16.0', 'charset_normalizer': '3.0.0'}`

### HAS_REQUESTS

**Value:** `False`

### HAS_YAML

**Value:** `False`

### HAS_BS4

**Value:** `False`

## Classes

### ErrorSeverity

**Inherits from:** Enum

Error severity levels for categorization and handling.


### ErrorCategory

**Inherits from:** Enum

Error categories for classification and handling strategies.


### ErrorContext

Context information for error analysis and correlation.


### CapcatError

**Inherits from:** Exception

Base exception for all Capcat-specific errors.

#### Methods

##### __init__

```python
def __init__(self, message: str, category: ErrorCategory = ErrorCategory.RUNTIME, severity: ErrorSeverity = ErrorSeverity.MEDIUM, context: Optional[ErrorContext] = None, recoverable: bool = True, original_error: Optional[Exception] = None)
```

**Parameters:**

- `self`
- `message` (str)
- `category` (ErrorCategory) *optional*
- `severity` (ErrorSeverity) *optional*
- `context` (Optional[ErrorContext]) *optional*
- `recoverable` (bool) *optional*
- `original_error` (Optional[Exception]) *optional*

##### to_dict

```python
def to_dict(self) -> Dict[str, Any]
```

Convert error to dictionary for logging/monitoring.

**Parameters:**

- `self`

**Returns:** Dict[str, Any]


### DependencyError

**Inherits from:** CapcatError

Raised when required dependencies are missing or corrupted.

#### Methods

##### __init__

```python
def __init__(self, message: str, dependency_name: str)
```

**Parameters:**

- `self`
- `message` (str)
- `dependency_name` (str)


### NetworkError

**Inherits from:** CapcatError

Raised for network-related issues.

#### Methods

##### __init__

```python
def __init__(self, message: str, status_code: Optional[int] = None)
```

**Parameters:**

- `self`
- `message` (str)
- `status_code` (Optional[int]) *optional*


### SourceProcessingError

**Inherits from:** CapcatError

Raised during source-specific processing errors.

#### Methods

##### __init__

```python
def __init__(self, message: str, source_id: str)
```

**Parameters:**

- `self`
- `message` (str)
- `source_id` (str)


### ConfigurationError

**Inherits from:** CapcatError

Raised for configuration-related errors.

#### Methods

##### __init__

```python
def __init__(self, message: str, config_file: Optional[str] = None)
```

**Parameters:**

- `self`
- `message` (str)
- `config_file` (Optional[str]) *optional*


### MediaDownloadError

**Inherits from:** CapcatError

Raised during media download failures.

#### Methods

##### __init__

```python
def __init__(self, message: str, media_url: str)
```

**Parameters:**

- `self`
- `message` (str)
- `media_url` (str)


### DependencyValidator

Validates and manages application dependencies.

#### Methods

##### __init__

```python
def __init__(self, venv_path: Optional[Path] = None)
```

**Parameters:**

- `self`
- `venv_path` (Optional[Path]) *optional*

##### validate_environment

```python
def validate_environment(self) -> Dict[str, bool]
```

Validate the virtual environment and dependencies.

**Parameters:**

- `self`

**Returns:** Dict[str, bool]

##### _check_venv_exists

```python
def _check_venv_exists(self) -> bool
```

Check if virtual environment exists.

**Parameters:**

- `self`

**Returns:** bool

##### _check_venv_activated

```python
def _check_venv_activated(self) -> bool
```

Check if virtual environment is activated.

**Parameters:**

- `self`

**Returns:** bool

##### _check_dependencies

```python
def _check_dependencies(self) -> bool
```

Check if all required dependencies are available.

**Parameters:**

- `self`

**Returns:** bool

##### auto_repair

```python
def auto_repair(self) -> bool
```

Attempt to automatically repair dependency issues.

**Parameters:**

- `self`

**Returns:** bool

##### _recreate_venv

```python
def _recreate_venv(self)
```

Recreate the virtual environment.

**Parameters:**

- `self`

##### _reinstall_dependencies

```python
def _reinstall_dependencies(self)
```

Reinstall all dependencies.

**Parameters:**

- `self`


### RetryStrategy

Implements retry logic with exponential backoff and circuit breaker.

#### Methods

##### __init__

```python
def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, exponential_base: float = 2.0, jitter: bool = True)
```

**Parameters:**

- `self`
- `max_retries` (int) *optional*
- `base_delay` (float) *optional*
- `max_delay` (float) *optional*
- `exponential_base` (float) *optional*
- `jitter` (bool) *optional*

##### get_delay

```python
def get_delay(self, attempt: int) -> float
```

Calculate delay for the given attempt.

**Parameters:**

- `self`
- `attempt` (int)

**Returns:** float


### ErrorMonitor

Monitors and correlates errors for analysis and alerting.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### record_error

```python
def record_error(self, error: CapcatError)
```

Record an error for monitoring and analysis.

**Parameters:**

- `self`
- `error` (CapcatError)

##### get_error_summary

```python
def get_error_summary(self) -> Dict[str, Any]
```

Get a summary of recorded errors.

**Parameters:**

- `self`

**Returns:** Dict[str, Any]


### ErrorHandler

Main error handling orchestrator.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### handle_startup_error

```python
def handle_startup_error(self, error: Exception) -> bool
```

Handle errors during application startup.

**Parameters:**

- `self`
- `error` (Exception)

**Returns:** bool

##### handle_runtime_error

```python
def handle_runtime_error(self, error: Exception, context: Optional[ErrorContext] = None) -> bool
```

Handle runtime errors with appropriate recovery strategies.

**Parameters:**

- `self`
- `error` (Exception)
- `context` (Optional[ErrorContext]) *optional*

**Returns:** bool


## Functions

### with_retry

```python
def with_retry(max_retries: int = 3, retry_on: Union[Type[Exception], tuple] = Exception, strategy: Optional[RetryStrategy] = None)
```

Decorator that adds retry logic to functions.

**Parameters:**

- `max_retries` (int) *optional*
- `retry_on` (Union[Type[Exception], tuple]) *optional*
- `strategy` (Optional[RetryStrategy]) *optional*

### handle_error

```python
def handle_error(error: Exception, context: Optional[ErrorContext] = None) -> bool
```

Global error handling function.

**Parameters:**

- `error` (Exception)
- `context` (Optional[ErrorContext]) *optional*

**Returns:** bool

### get_error_monitor

```python
def get_error_monitor() -> ErrorMonitor
```

Get the global error monitor instance.

**Returns:** ErrorMonitor

### validate_dependencies

```python
def validate_dependencies() -> bool
```

Validate application dependencies.

**Returns:** bool

### startup_check

```python
def startup_check() -> bool
```

Perform startup validation and auto-repair if needed.

**Returns:** bool

### decorator

```python
def decorator(func: Callable) -> Callable
```

**Parameters:**

- `func` (Callable)

**Returns:** Callable

### wrapper

```python
def wrapper()
```

