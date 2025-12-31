# core.network_resilience

**File:** `Application/core/network_resilience.py`

## Description

Network Resilience Patterns for Source Processing

Clean architecture implementation applying SOLID principles:
- Single Responsibility: Each class has one clear purpose
- Open/Closed: Extensible via strategy pattern
- Liskov Substitution: RetryStrategy implementations interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions not concretions

## Constants

### RETRY

**Value:** `'retry'`

### SKIP

**Value:** `'skip'`

### SUCCESS

**Value:** `'success'`

## Classes

### RetryDecision

**Inherits from:** Enum

Enum representing retry decisions.


### RetryAttempt

Data class representing a retry attempt.

#### Methods

##### is_first_attempt

```python
def is_first_attempt(self) -> bool
```

Check if this is the first attempt.

**Parameters:**

- `self`

**Returns:** bool

##### is_last_attempt

```python
def is_last_attempt(self) -> bool
```

Check if this is the last attempt.

**Parameters:**

- `self`

**Returns:** bool

##### attempts_remaining

```python
def attempts_remaining(self) -> int
```

Get number of attempts remaining.

**Parameters:**

- `self`

**Returns:** int


### RetryStrategy

**Inherits from:** ABC

Abstract base class for retry strategies.

Single Responsibility: Defines retry decision logic.
Open/Closed: New strategies can be added without modifying existing code.

#### Methods

##### should_retry

```python
def should_retry(self, attempt: RetryAttempt) -> RetryDecision
```

Determine if an operation should be retried.

Args:
    attempt: Information about the current attempt

Returns:
    RetryDecision indicating next action

**Parameters:**

- `self`
- `attempt` (RetryAttempt)

**Returns:** RetryDecision

##### get_delay

```python
def get_delay(self, attempt: RetryAttempt) -> float
```

Calculate delay before next retry.

Args:
    attempt: Information about the current attempt

Returns:
    Delay in seconds

**Parameters:**

- `self`
- `attempt` (RetryAttempt)

**Returns:** float


### ExponentialBackoffStrategy

**Inherits from:** RetryStrategy

Exponential backoff retry strategy.

Single Responsibility: Implements exponential backoff timing.

#### Methods

##### __init__

```python
def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0, exponential_base: float = 2.0, jitter: bool = True)
```

Initialize exponential backoff strategy.

Args:
    base_delay: Base delay in seconds
    max_delay: Maximum delay in seconds
    exponential_base: Base for exponential calculation
    jitter: Whether to add random jitter

**Parameters:**

- `self`
- `base_delay` (float) *optional*
- `max_delay` (float) *optional*
- `exponential_base` (float) *optional*
- `jitter` (bool) *optional*

##### should_retry

```python
def should_retry(self, attempt: RetryAttempt) -> RetryDecision
```

Determine if should retry based on attempt count.

Args:
    attempt: Current attempt information

Returns:
    RETRY if attempts remaining, SKIP otherwise

**Parameters:**

- `self`
- `attempt` (RetryAttempt)

**Returns:** RetryDecision

##### get_delay

```python
def get_delay(self, attempt: RetryAttempt) -> float
```

Calculate exponential backoff delay.

Args:
    attempt: Current attempt information

Returns:
    Delay in seconds with exponential backoff

**Parameters:**

- `self`
- `attempt` (RetryAttempt)

**Returns:** float


### ErrorClassifier

Classifies errors as retryable or non-retryable.

Single Responsibility: Error classification logic.

#### Methods

##### __init__

```python
def __init__(self, retryable_exceptions: Tuple[Type[Exception], ...] = None)
```

Initialize error classifier.

Args:
    retryable_exceptions: Tuple of exception types to retry

**Parameters:**

- `self`
- `retryable_exceptions` (Tuple[Type[Exception], ...]) *optional*

##### is_retryable

```python
def is_retryable(self, error: Exception) -> bool
```

Check if error is retryable.

Args:
    error: Exception to classify

Returns:
    True if retryable, False otherwise

**Parameters:**

- `self`
- `error` (Exception)

**Returns:** bool

##### get_error_type

```python
def get_error_type(self, error: Exception) -> str
```

Get human-readable error type.

Args:
    error: Exception to classify

Returns:
    Error type string

**Parameters:**

- `self`
- `error` (Exception)

**Returns:** str


### RetryLogger

Handles logging for retry operations.

Single Responsibility: Logging logic separation.

#### Methods

##### __init__

```python
def __init__(self, logger_name: str = __name__)
```

Initialize retry logger.

Args:
    logger_name: Name for logger instance

**Parameters:**

- `self`
- `logger_name` (str) *optional*

##### log_attempt

```python
def log_attempt(self, attempt: RetryAttempt)
```

Log retry attempt.

Args:
    attempt: Attempt information

**Parameters:**

- `self`
- `attempt` (RetryAttempt)

##### log_skip

```python
def log_skip(self, operation_name: str, attempts: int, error_type: str)
```

Log skip decision.

Args:
    operation_name: Name of operation being skipped
    attempts: Number of attempts made
    error_type: Type of error that caused skip

**Parameters:**

- `self`
- `operation_name` (str)
- `attempts` (int)
- `error_type` (str)

##### log_success

```python
def log_success(self, operation_name: str, attempt_number: int)
```

Log successful retry.

Args:
    operation_name: Name of operation that succeeded
    attempt_number: Attempt number that succeeded

**Parameters:**

- `self`
- `operation_name` (str)
- `attempt_number` (int)


### SkipRecord

Record of a skipped operation.


### SkipTracker

Tracks skipped operations for reporting.

Single Responsibility: Skip tracking and reporting.

#### Methods

##### __init__

```python
def __init__(self)
```

Initialize skip tracker.

**Parameters:**

- `self`

##### record_skip

```python
def record_skip(self, source_name: str, operation_name: str, reason: str, attempts: int, error_type: str)
```

Record a skipped operation.

Args:
    source_name: Source identifier
    operation_name: Operation name
    reason: Reason for skip
    attempts: Number of attempts made
    error_type: Type of error

**Parameters:**

- `self`
- `source_name` (str)
- `operation_name` (str)
- `reason` (str)
- `attempts` (int)
- `error_type` (str)

##### get_summary

```python
def get_summary(self) -> Dict[str, Any]
```

Get summary of skipped operations.

Returns:
    Dictionary with skip summary

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### reset

```python
def reset(self)
```

Reset skip tracking.

**Parameters:**

- `self`


### RetryExecutor

Executes operations with retry logic.

Single Responsibility: Orchestrates retry execution.
Dependency Inversion: Depends on abstractions (RetryStrategy, etc.)

#### Methods

##### __init__

```python
def __init__(self, strategy: RetryStrategy, error_classifier: ErrorClassifier, logger: RetryLogger, skip_tracker: SkipTracker)
```

Initialize retry executor.

Args:
    strategy: Retry strategy to use
    error_classifier: Error classifier
    logger: Retry logger
    skip_tracker: Skip tracker

**Parameters:**

- `self`
- `strategy` (RetryStrategy)
- `error_classifier` (ErrorClassifier)
- `logger` (RetryLogger)
- `skip_tracker` (SkipTracker)

##### execute

```python
def execute(self, operation: Callable[[], Any], operation_name: str, source_name: str, max_attempts: int = 2) -> Optional[Any]
```

Execute operation with retry logic.

Args:
    operation: Callable to execute
    operation_name: Name for logging
    source_name: Source identifier
    max_attempts: Maximum retry attempts

Returns:
    Operation result or None if skipped

**Parameters:**

- `self`
- `operation` (Callable[[], Any])
- `operation_name` (str)
- `source_name` (str)
- `max_attempts` (int) *optional*

**Returns:** Optional[Any]


### URLFallbackExecutor

Executes operations with URL fallback logic.

Single Responsibility: URL fallback orchestration.

#### Methods

##### __init__

```python
def __init__(self, retry_executor: RetryExecutor)
```

Initialize URL fallback executor.

Args:
    retry_executor: Retry executor to use

**Parameters:**

- `self`
- `retry_executor` (RetryExecutor)

##### execute_with_fallbacks

```python
def execute_with_fallbacks(self, urls: List[str], fetch_function: Callable[[str], Any], source_name: str, max_retries_per_url: int = 2) -> Optional[Any]
```

Try multiple URLs with retry logic.

Args:
    urls: List of URLs to try
    fetch_function: Function to fetch from URL
    source_name: Source identifier
    max_retries_per_url: Retries per URL

Returns:
    Fetch result or None if all URLs exhausted

**Parameters:**

- `self`
- `urls` (List[str])
- `fetch_function` (Callable[[str], Any])
- `source_name` (str)
- `max_retries_per_url` (int) *optional*

**Returns:** Optional[Any]


## Functions

### create_retry_executor

```python
def create_retry_executor(max_retries: int = 2) -> RetryExecutor
```

Create a retry executor with default configuration.

Factory pattern for clean object creation.

Args:
    max_retries: Maximum retry attempts

Returns:
    Configured RetryExecutor instance

**Parameters:**

- `max_retries` (int) *optional*

**Returns:** RetryExecutor

### get_retry_executor

```python
def get_retry_executor() -> RetryExecutor
```

Get global retry executor instance.

**Returns:** RetryExecutor

### get_skip_tracker

```python
def get_skip_tracker() -> SkipTracker
```

Get global skip tracker instance.

**Returns:** SkipTracker

### reset_retry_state

```python
def reset_retry_state()
```

Reset global retry state.

### operation

```python
def operation()
```

