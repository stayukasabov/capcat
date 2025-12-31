# core.media_executor

**File:** `Application/core/media_executor.py`

## Description

Shared executor pool for media processing to prevent nested ThreadPoolExecutor deadlock.

This module provides a global executor that can be safely used by multiple article
processing threads without creating nested executors that exhaust thread resources.

## Classes

### MediaExecutorPool

Singleton executor pool for media downloads across all articles.

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

### get_media_executor

```python
def get_media_executor() -> ThreadPoolExecutor
```

Get the shared media processing executor.

Returns:
    ThreadPoolExecutor: Shared executor for media downloads

**Returns:** ThreadPoolExecutor

### shutdown_media_executor

```python
def shutdown_media_executor(wait = True)
```

Shutdown the shared media executor.

Args:
    wait: If True, wait for all tasks to complete

**Parameters:**

- `wait` *optional*

