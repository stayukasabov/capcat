# core.shutdown

**File:** `Application/core/shutdown.py`

## Description

Graceful shutdown handling for Capcat.
Handles signal interrupts and cleanup operations.

## Classes

### GracefulShutdown

Context manager for handling graceful shutdown on signals.

#### Methods

##### __init__

```python
def __init__(self, cleanup_func: Optional[Callable] = None)
```

Initialize graceful shutdown handler.

Args:
    cleanup_func: Optional cleanup function to call on shutdown

**Parameters:**

- `self`
- `cleanup_func` (Optional[Callable]) *optional*

##### __enter__

```python
def __enter__(self)
```

Set up signal handlers.

**Parameters:**

- `self`

##### __exit__

```python
def __exit__(self, exc_type, exc_val, exc_tb)
```

Restore original signal handlers.

**Parameters:**

- `self`
- `exc_type`
- `exc_val`
- `exc_tb`

##### _signal_handler

```python
def _signal_handler(self, signum: int, frame)
```

Handle shutdown signals.

**Parameters:**

- `self`
- `signum` (int)
- `frame`

##### should_shutdown

```python
def should_shutdown(self) -> bool
```

Check if shutdown has been requested.

**Parameters:**

- `self`

**Returns:** bool

##### wait_for_shutdown

```python
def wait_for_shutdown(self, timeout: Optional[float] = None) -> bool
```

Wait for shutdown signal.

Args:
    timeout: Maximum time to wait in seconds

Returns:
    True if shutdown was requested, False if timeout occurred

**Parameters:**

- `self`
- `timeout` (Optional[float]) *optional*

**Returns:** bool


### InterruptibleOperation

Context manager for operations that can be interrupted gracefully.

#### Methods

##### __init__

```python
def __init__(self, operation_name: str, shutdown_handler: Optional[GracefulShutdown] = None)
```

Initialize interruptible operation.

Args:
    operation_name: Name of the operation for logging
    shutdown_handler: Optional existing shutdown handler to use

**Parameters:**

- `self`
- `operation_name` (str)
- `shutdown_handler` (Optional[GracefulShutdown]) *optional*

##### __enter__

```python
def __enter__(self)
```

Start the interruptible operation.

**Parameters:**

- `self`

##### __exit__

```python
def __exit__(self, exc_type, exc_val, exc_tb)
```

Clean up the interruptible operation.

**Parameters:**

- `self`
- `exc_type`
- `exc_val`
- `exc_tb`

##### check_shutdown

```python
def check_shutdown(self)
```

Check if shutdown has been requested and raise KeyboardInterrupt if so.
Call this periodically during long-running operations.

**Parameters:**

- `self`

##### should_continue

```python
def should_continue(self) -> bool
```

Check if the operation should continue.

Returns:
    False if shutdown has been requested, True otherwise

**Parameters:**

- `self`

**Returns:** bool


## Functions

### setup_signal_handlers

```python
def setup_signal_handlers()
```

Set up basic signal handlers for the application.
This is a simple version that just logs and exits.

### with_graceful_shutdown

```python
def with_graceful_shutdown(cleanup_func: Optional[Callable] = None)
```

Decorator to add graceful shutdown handling to functions.

Args:
    cleanup_func: Optional cleanup function to call on shutdown

**Parameters:**

- `cleanup_func` (Optional[Callable]) *optional*

### signal_handler

```python
def signal_handler(signum: int, frame)
```

**Parameters:**

- `signum` (int)
- `frame`

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

