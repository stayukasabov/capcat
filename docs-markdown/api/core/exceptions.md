# core.exceptions

**File:** `Application/core/exceptions.py`

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

**Parameters:**

- `self`
- `message` (str)
- `user_message` (str) *optional*
- `original_error` (Exception) *optional*
- `error_code` (int) *optional*

##### __str__

```python
def __str__(self)
```

**Parameters:**

- `self`

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

Raised when network operations fail.

#### Methods

##### __init__

```python
def __init__(self, url: str, original_error: Exception = None)
```

**Parameters:**

- `self`
- `url` (str)
- `original_error` (Exception) *optional*


### ContentFetchError

**Inherits from:** CapcatError

Raised when content fetching fails.

#### Methods

##### __init__

```python
def __init__(self, title: str, url: str, reason: str, original_error: Exception = None)
```

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

**Parameters:**

- `self`
- `config_issue` (str)
- `suggestion` (str) *optional*


### FileSystemError

**Inherits from:** CapcatError

Raised when file system operations fail.

#### Methods

##### __init__

```python
def __init__(self, operation: str, path: str, original_error: Exception = None)
```

**Parameters:**

- `self`
- `operation` (str)
- `path` (str)
- `original_error` (Exception) *optional*


### ParsingError

**Inherits from:** CapcatError

Raised when HTML/content parsing fails.

#### Methods

##### __init__

```python
def __init__(self, url: str, reason: str)
```

**Parameters:**

- `self`
- `url` (str)
- `reason` (str)


### ValidationError

**Inherits from:** CapcatError

Raised when input validation fails.

#### Methods

##### __init__

```python
def __init__(self, field: str, value: str, requirement: str)
```

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

**Parameters:**

- `self`
- `url` (str)
- `reason` (str) *optional*


