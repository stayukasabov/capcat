---
layout: default
render_with_liquid: false
---

# capcat.core.exceptions

**File:** `Application/capcat/core/exceptions.py`

## Description

Custom exceptions for Capcat application.
Provides structured error handling with user-friendly messages.

## Classes

### CapcatError

**Inherits from:** Exception

Base exception for all Capcat related errors.

#### Methods

##### __init__

```python
def __init__(self, message: str, user_message: str = None, original_error: Exception = None, error_code: int = None)
```

Create a CapcatError with separate technical and user-facing messages.

Args:
    message: Technical error message (logged, not shown to user).
    user_message: Human-readable message shown in the CLI. Defaults
        to *message* if not provided.
    original_error: The underlying exception that triggered this one,
        preserved for logging and ``to_dict()``.
    error_code: Numeric code from ``ErrorCode``. Defaults to
        ``ErrorCode.UNKNOWN_ERROR``.

**Parameters:**

- `self`
- `message` (str)
- `user_message` (str) *optional*
- `original_error` (Exception) *optional*
- `error_code` (int) *optional*

##### __str__

```python
def __str__(self) -> str
```

Return the user-facing message string.

**Parameters:**

- `self`

**Returns:** str

##### to_dict

```python
def to_dict(self) -> dict
```

Convert exception to dictionary for logging/API responses.

Returns:
    Dictionary with error details including code and messages

Example:
    >>> try:
    ...     raise NetworkError("https://example.com")
    ... except NetworkError as e:
    ...     print(e.to_dict())
    {'error_code': 1001, 'message': 'Could not access...',
     'technical_message': 'Network error...', ...}

**Parameters:**

- `self`

**Returns:** dict


### NetworkError

**Inherits from:** CapcatError

Raised when network operations fail (DNS, timeout, HTTP errors).

#### Methods

##### __init__

```python
def __init__(self, url: str, original_error: Exception = None)
```

Create a NetworkError for a failed URL request.

Args:
    url: The URL that could not be reached.
    original_error: The underlying ``requests`` exception.

**Parameters:**

- `self`
- `url` (str)
- `original_error` (Exception) *optional*


### ContentFetchError

**Inherits from:** CapcatError

Raised when an article's content cannot be extracted after a successful request.

#### Methods

##### __init__

```python
def __init__(self, title: str, url: str, reason: str, original_error: Exception = None)
```

Create a ContentFetchError.

Args:
    title: Article title (for the error message).
    url: Article URL that failed content extraction.
    reason: Human-readable explanation of why extraction failed.
    original_error: The underlying exception, if any.

**Parameters:**

- `self`
- `title` (str)
- `url` (str)
- `reason` (str)
- `original_error` (Exception) *optional*


### ConfigurationError

**Inherits from:** CapcatError

Raised when configuration is invalid or missing.

#### Methods

##### __init__

```python
def __init__(self, config_issue: str, suggestion: str = None)
```

Create a ConfigurationError.

Args:
    config_issue: Description of what is wrong with the config.
    suggestion: Optional fix suggestion appended to the user message.

**Parameters:**

- `self`
- `config_issue` (str)
- `suggestion` (str) *optional*


### FileSystemError

**Inherits from:** CapcatError

Raised when file system operations fail (read, write, mkdir, unlink).

#### Methods

##### __init__

```python
def __init__(self, operation: str, path: str, original_error: Exception = None)
```

Create a FileSystemError.

Args:
    operation: Verb describing the failed operation (e.g. ``"write"``).
    path: Filesystem path where the operation failed.
    original_error: The underlying ``OSError`` or ``IOError``.

**Parameters:**

- `self`
- `operation` (str)
- `path` (str)
- `original_error` (Exception) *optional*


### ParsingError

**Inherits from:** CapcatError

Raised when HTML or feed content cannot be parsed (structure changed, truncated, etc.).

#### Methods

##### __init__

```python
def __init__(self, url: str, reason: str)
```

Create a ParsingError.

Args:
    url: The URL whose content failed to parse.
    reason: Technical description of the parse failure.

**Parameters:**

- `self`
- `url` (str)
- `reason` (str)


### ValidationError

**Inherits from:** CapcatError

Raised when input validation fails (invalid URL, bad config value, etc.).

#### Methods

##### __init__

```python
def __init__(self, field: str, value: str, requirement: str)
```

Create a ValidationError.

Args:
    field: Name of the field that failed validation (e.g. ``"url"``).
    value: The invalid value that was provided.
    requirement: Description of what the value should satisfy.

**Parameters:**

- `self`
- `field` (str)
- `value` (str)
- `requirement` (str)


### InvalidFeedError

**Inherits from:** CapcatError

Raised when a URL does not point to a valid RSS/Atom feed.

#### Methods

##### __init__

```python
def __init__(self, url: str, reason: str = 'Not a valid RSS/Atom feed.')
```

Create an InvalidFeedError.

Args:
    url: The URL that was tested as a feed.
    reason: Optional description of why it is not a valid feed.

**Parameters:**

- `self`
- `url` (str)
- `reason` (str) *optional*


