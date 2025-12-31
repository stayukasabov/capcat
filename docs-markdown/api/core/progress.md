# core.progress

**File:** `Application/core/progress.py`

## Description

Progress indicators and status reporting for Capcat.
Provides user-friendly feedback during long-running operations.

## Classes

### ProgressIndicator

Simple progress indicator for console output.
Shows a spinner or percentage-based progress bar.

#### Methods

##### __init__

```python
def __init__(self, message: str, total: Optional[int] = None, show_spinner: bool = True, spinner_style: str = 'dots', show_count: bool = True)
```

Initialize progress indicator.

Args:
    message: Message to display
    total: Total number of items (for percentage display)
    show_spinner: Whether to show animated spinner
    spinner_style: Style of spinner animation ('dots', 'wave', 'loading', 'pulse', 'bounce', 'modern')
    show_count: Whether to show current/total count (False shows only percentage)

**Parameters:**

- `self`
- `message` (str)
- `total` (Optional[int]) *optional*
- `show_spinner` (bool) *optional*
- `spinner_style` (str) *optional*
- `show_count` (bool) *optional*

##### __enter__

```python
def __enter__(self)
```

Context manager entry.

**Parameters:**

- `self`

##### __exit__

```python
def __exit__(self, exc_type, exc_val, exc_tb)
```

Context manager exit.

**Parameters:**

- `self`
- `exc_type`
- `exc_val`
- `exc_tb`

##### start

```python
def start(self)
```

Start the progress indicator.

**Parameters:**

- `self`

##### stop

```python
def stop(self, success_message: Optional[str] = None)
```

Stop the progress indicator.

**Parameters:**

- `self`
- `success_message` (Optional[str]) *optional*

##### update

```python
def update(self, increment: int = 1, status_message: Optional[str] = None)
```

Update progress counter and optionally change status message.

**Parameters:**

- `self`
- `increment` (int) *optional*
- `status_message` (Optional[str]) *optional*

##### error

```python
def error(self, error_message: str)
```

Stop with error message.

**Parameters:**

- `self`
- `error_message` (str)

##### _create_progress_bar

```python
def _create_progress_bar(self, percentage: float, width: int = 8) -> str
```

Create a visual progress bar with loading animation.

**Parameters:**

- `self`
- `percentage` (float)
- `width` (int) *optional*

**Returns:** str

##### _spin

```python
def _spin(self)
```

Internal spinner animation method with enhanced loading visualization.

**Parameters:**

- `self`

##### _clear_line

```python
def _clear_line(self)
```

Clear the current line.

**Parameters:**

- `self`

##### _hide_cursor

```python
def _hide_cursor(self)
```

Hide the cursor for clean progress display.

**Parameters:**

- `self`

##### _show_cursor

```python
def _show_cursor(self)
```

Show the cursor when progress is complete.

**Parameters:**

- `self`


### BatchProgress

Progress tracker for batch operations with detailed status reporting.

#### Methods

##### __init__

```python
def __init__(self, operation_name: str, total_items: int, quiet: bool = False, verbose: bool = False, spinner_style: str = 'activity')
```

Initialize batch progress tracker.

Args:
    operation_name: Name of the batch operation
    total_items: Total number of items to process
    quiet: Whether to suppress detailed output
    verbose: Whether to show detailed item-by-item progress
    spinner_style: Style of spinner animation ('activity', 'progress', 'pulse', 'wave', 'dots', 'scan')

**Parameters:**

- `self`
- `operation_name` (str)
- `total_items` (int)
- `quiet` (bool) *optional*
- `verbose` (bool) *optional*
- `spinner_style` (str) *optional*

##### __enter__

```python
def __enter__(self)
```

Context manager entry.

**Parameters:**

- `self`

##### __exit__

```python
def __exit__(self, exc_type, exc_val, exc_tb)
```

Context manager exit.

**Parameters:**

- `self`
- `exc_type`
- `exc_val`
- `exc_tb`

##### _create_progress_bar

```python
def _create_progress_bar(self, percentage: float, width: int = 6) -> str
```

Create a visual progress bar with loading animation for batch operations.

**Parameters:**

- `self`
- `percentage` (float)
- `width` (int) *optional*

**Returns:** str

##### _update_progress_display

```python
def _update_progress_display(self)
```

Update the progress display with current item sub-progress.

**Parameters:**

- `self`

⚠️ **High complexity:** 12

##### start

```python
def start(self)
```

Start the batch operation.

**Parameters:**

- `self`

##### _hide_cursor

```python
def _hide_cursor(self)
```

Hide the cursor for clean progress display.

**Parameters:**

- `self`

##### _show_cursor

```python
def _show_cursor(self)
```

Show the cursor when progress is complete.

**Parameters:**

- `self`

##### update_item_progress

```python
def update_item_progress(self, progress: float, stage: str = '')
```

Update progress for the current item being processed.

Args:
    progress: Progress from 0.0 to 1.0 for current item
    stage: Description of current processing stage

**Parameters:**

- `self`
- `progress` (float)
- `stage` (str) *optional*

##### item_completed

```python
def item_completed(self, success: bool = True, item_name: Optional[str] = None)
```

Mark an item as completed.

Args:
    success: Whether the item completed successfully
    item_name: Optional name of the completed item

**Parameters:**

- `self`
- `success` (bool) *optional*
- `item_name` (Optional[str]) *optional*

⚠️ **High complexity:** 11

##### get_summary

```python
def get_summary(self) -> str
```

Get a summary of the batch operation.

**Parameters:**

- `self`

**Returns:** str

##### finish

```python
def finish(self)
```

Finish the batch operation and display summary.

**Parameters:**

- `self`

##### _start_animation_thread

```python
def _start_animation_thread(self)
```

Start the continuous animation thread for smooth spinner rotation.

**Parameters:**

- `self`

##### _stop_animation_thread

```python
def _stop_animation_thread(self)
```

Stop the continuous animation thread.

**Parameters:**

- `self`

##### _continuous_animation

```python
def _continuous_animation(self)
```

Continuous animation loop that keeps the spinner rotating.

**Parameters:**

- `self`

##### _force_display_update

```python
def _force_display_update(self)
```

Force an immediate display update with current progress.

**Parameters:**

- `self`

⚠️ **High complexity:** 12


### QuietProgress

No-op progress indicator for quiet mode.
Maintains the same interface but produces no output.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### __enter__

```python
def __enter__(self)
```

**Parameters:**

- `self`

##### __exit__

```python
def __exit__(self, exc_type, exc_val, exc_tb)
```

**Parameters:**

- `self`
- `exc_type`
- `exc_val`
- `exc_tb`

##### start

```python
def start(self)
```

**Parameters:**

- `self`

##### stop

```python
def stop(self, success_message: Optional[str] = None)
```

**Parameters:**

- `self`
- `success_message` (Optional[str]) *optional*

##### update

```python
def update(self, increment: int = 1, status_message: Optional[str] = None)
```

**Parameters:**

- `self`
- `increment` (int) *optional*
- `status_message` (Optional[str]) *optional*

##### update_item_progress

```python
def update_item_progress(self, progress: float, stage: str = '')
```

No-op implementation of update_item_progress for interface compatibility.

**Parameters:**

- `self`
- `progress` (float)
- `stage` (str) *optional*

##### error

```python
def error(self, error_message: str)
```

**Parameters:**

- `self`
- `error_message` (str)

##### item_completed

```python
def item_completed(self, success: bool = True, item_name: Optional[str] = None)
```

**Parameters:**

- `self`
- `success` (bool) *optional*
- `item_name` (Optional[str]) *optional*

##### get_summary

```python
def get_summary(self) -> str
```

**Parameters:**

- `self`

**Returns:** str

##### finish

```python
def finish(self)
```

**Parameters:**

- `self`


## Functions

### _restore_cursor

```python
def _restore_cursor()
```

Global function to ensure cursor is always restored on exit.

### _signal_handler

```python
def _signal_handler(signum, frame)
```

Handle interruption signals and restore cursor.

**Parameters:**

- `signum`
- `frame`

### with_progress

```python
def with_progress(message: str, show_spinner: bool = True)
```

Decorator to add progress indication to functions.

Args:
    message: Message to display during operation
    show_spinner: Whether to show animated spinner

**Parameters:**

- `message` (str)
- `show_spinner` (bool) *optional*

### get_progress_indicator

```python
def get_progress_indicator(message: str, total: Optional[int] = None, quiet: bool = False) -> ProgressIndicator
```

Factory function to get appropriate progress indicator based on quiet mode and config.

Args:
    message: Progress message
    total: Total number of items (optional)
    quiet: Whether to use quiet mode

Returns:
    Progress indicator instance

**Parameters:**

- `message` (str)
- `total` (Optional[int]) *optional*
- `quiet` (bool) *optional*

**Returns:** ProgressIndicator

### get_batch_progress

```python
def get_batch_progress(operation_name: str, total_items: int, quiet: bool = False, verbose: bool = False) -> BatchProgress
```

Factory function to get appropriate batch progress tracker based on quiet mode.

Args:
    operation_name: Name of the batch operation
    total_items: Total number of items
    quiet: Whether to use quiet mode
    verbose: Whether to show detailed item-by-item progress

Returns:
    Batch progress tracker instance

**Parameters:**

- `operation_name` (str)
- `total_items` (int)
- `quiet` (bool) *optional*
- `verbose` (bool) *optional*

**Returns:** BatchProgress

### decorator

```python
def decorator(func: Callable) -> Callable
```

**Parameters:**

- `func` (Callable)

**Returns:** Callable

### wrapper

```python
def wrapper() -> Any
```

**Returns:** Any

