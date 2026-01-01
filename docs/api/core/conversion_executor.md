# core.conversion_executor

**File:** `Application/core/conversion_executor.py`

## Description

Shared executor pool for HTML-to-Markdown conversion to prevent nested ThreadPoolExecutor deadlock.

This module provides a global executor that can be safely used by multiple article
processing threads without creating nested executors that exhaust thread resources.

## Classes

### ConversionExecutorPool

Singleton executor pool for HTML-to-Markdown conversions across all articles.

#### Methods

##### __new__

```python
def __new__(cls)
```

**Parameters:**

- `cls`

##### __init__

```python
def __init__(self)
```

Initialize the shared executor pool.

**Parameters:**

- `self`

##### executor

```python
def executor(self) -> ThreadPoolExecutor
```

Get the shared executor instance.

**Parameters:**

- `self`

**Returns:** ThreadPoolExecutor

##### shutdown

```python
def shutdown(self, wait = True)
```

Shutdown the executor pool.

**Parameters:**

- `self`
- `wait` *optional*


## Functions

### get_conversion_executor

```python
def get_conversion_executor() -> ThreadPoolExecutor
```

Get the shared HTML-to-Markdown conversion executor.

Returns:
    ThreadPoolExecutor: Shared executor for conversions

**Returns:** ThreadPoolExecutor

### shutdown_conversion_executor

```python
def shutdown_conversion_executor(wait = True)
```

Shutdown the shared conversion executor.

Args:
    wait: If True, wait for all tasks to complete

**Parameters:**

- `wait` *optional*

