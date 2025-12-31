# core.circuit_breaker

**File:** `Application/core/circuit_breaker.py`

## Description

Circuit Breaker pattern implementation for Capcat.
Prevents repeated attempts to failing sources, providing fail-fast behavior
and automatic recovery testing.

## Constants

### CLOSED

**Value:** `'closed'`

### OPEN

**Value:** `'open'`

### HALF_OPEN

**Value:** `'half_open'`

## Classes

### CircuitState

**Inherits from:** Enum

States of the circuit breaker.


### CircuitBreakerConfig

Configuration for circuit breaker behavior.

#### Methods

##### __post_init__

```python
def __post_init__(self)
```

Validate configuration values.

**Parameters:**

- `self`


### CircuitBreakerOpenError

**Inherits from:** Exception

Exception raised when circuit breaker is open.

#### Methods

##### __init__

```python
def __init__(self, source_name: str, last_exception: Optional[Exception] = None)
```

**Parameters:**

- `self`
- `source_name` (str)
- `last_exception` (Optional[Exception]) *optional*


### CircuitBreaker

Circuit breaker implementation with state machine.

States:
- CLOSED: Normal operation, all calls go through
- OPEN: Blocking calls, failing fast
- HALF_OPEN: Testing recovery, limited calls allowed

Transitions:
- CLOSED -> OPEN: After failure_threshold failures
- OPEN -> HALF_OPEN: After timeout_seconds elapsed
- HALF_OPEN -> CLOSED: After success_threshold successes
- HALF_OPEN -> OPEN: On any failure

Example:
    breaker = CircuitBreaker("my_service", config)
    result = breaker.call(risky_function, arg1, arg2)

#### Methods

##### __init__

```python
def __init__(self, name: str, config: CircuitBreakerConfig)
```

Initialize circuit breaker.

Args:
    name: Name of the protected resource (e.g., source code)
    config: Circuit breaker configuration

**Parameters:**

- `self`
- `name` (str)
- `config` (CircuitBreakerConfig)

##### call

```python
def call(self, func: Callable) -> Any
```

Execute function through circuit breaker.

Args:
    func: Function to execute
    *args: Positional arguments for func
    **kwargs: Keyword arguments for func

Returns:
    Result of func execution

Raises:
    CircuitBreakerOpenError: If circuit is OPEN and timeout not expired
    Exception: Any exception raised by func

**Parameters:**

- `self`
- `func` (Callable)

**Returns:** Any

##### _on_success

```python
def _on_success(self)
```

Handle successful call.

**Parameters:**

- `self`

##### _on_failure

```python
def _on_failure(self, exception: Exception)
```

Handle failed call.

**Parameters:**

- `self`
- `exception` (Exception)

##### _should_attempt_reset

```python
def _should_attempt_reset(self) -> bool
```

Check if enough time has passed to attempt recovery.

**Parameters:**

- `self`

**Returns:** bool

##### _transition_to

```python
def _transition_to(self, new_state: CircuitState)
```

Transition to a new state.

**Parameters:**

- `self`
- `new_state` (CircuitState)

##### get_state

```python
def get_state(self) -> CircuitState
```

Get current circuit state (thread-safe).

**Parameters:**

- `self`

**Returns:** CircuitState

##### get_stats

```python
def get_stats(self) -> Dict[str, Any]
```

Get circuit breaker statistics.

Returns:
    Dictionary with statistics

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### reset

```python
def reset(self)
```

Reset circuit breaker to initial state.

**Parameters:**

- `self`


### CircuitBreakerPool

Pool of circuit breakers, one per source.

Manages circuit breakers for multiple sources, creating them on-demand
and applying source-specific configurations.

#### Methods

##### __init__

```python
def __init__(self, configs: Optional[Dict[str, CircuitBreakerConfig]] = None)
```

Initialize circuit breaker pool.

Args:
    configs: Optional custom circuit breaker configurations

**Parameters:**

- `self`
- `configs` (Optional[Dict[str, CircuitBreakerConfig]]) *optional*

##### get_breaker

```python
def get_breaker(self, source_code: str) -> CircuitBreaker
```

Get or create circuit breaker for a source.

Args:
    source_code: Source identifier (e.g., 'hn', 'scientificamerican')

Returns:
    CircuitBreaker instance for the source

**Parameters:**

- `self`
- `source_code` (str)

**Returns:** CircuitBreaker

##### call

```python
def call(self, source_code: str, func: Callable) -> Any
```

Execute function through circuit breaker for a source.

Args:
    source_code: Source identifier
    func: Function to execute
    *args: Positional arguments for func
    **kwargs: Keyword arguments for func

Returns:
    Result of func execution

Raises:
    CircuitBreakerOpenError: If circuit is open
    Exception: Any exception raised by func

**Parameters:**

- `self`
- `source_code` (str)
- `func` (Callable)

**Returns:** Any

##### get_all_states

```python
def get_all_states(self) -> Dict[str, str]
```

Get states of all circuit breakers.

Returns:
    Dictionary mapping source codes to their states

**Parameters:**

- `self`

**Returns:** Dict[str, str]

##### get_all_stats

```python
def get_all_stats(self) -> Dict[str, Dict[str, Any]]
```

Get statistics for all circuit breakers.

Returns:
    Dictionary mapping source codes to their statistics

**Parameters:**

- `self`

**Returns:** Dict[str, Dict[str, Any]]

##### reset_all

```python
def reset_all(self)
```

Reset all circuit breakers.

**Parameters:**

- `self`


## Functions

### get_circuit_breaker_pool

```python
def get_circuit_breaker_pool() -> CircuitBreakerPool
```

Get the global circuit breaker pool instance (singleton).

Returns:
    Global CircuitBreakerPool instance

**Returns:** CircuitBreakerPool

### call_with_circuit_breaker

```python
def call_with_circuit_breaker(source_code: str, func: Callable) -> Any
```

Convenience function to call function through global circuit breaker pool.

Args:
    source_code: Source identifier
    func: Function to execute
    *args: Positional arguments
    **kwargs: Keyword arguments

Returns:
    Result of function execution

Raises:
    CircuitBreakerOpenError: If circuit is open
    Exception: Any exception raised by func

**Parameters:**

- `source_code` (str)
- `func` (Callable)

**Returns:** Any

### get_circuit_state

```python
def get_circuit_state(source_code: str) -> CircuitState
```

Get circuit breaker state for a source.

Args:
    source_code: Source identifier

Returns:
    Current circuit state

**Parameters:**

- `source_code` (str)

**Returns:** CircuitState

