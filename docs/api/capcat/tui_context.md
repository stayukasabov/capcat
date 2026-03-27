# capcat.core.tui_context

**File:** `Application/capcat/core/tui_context.py`

## Description

TUI context flag and per-fetch result accumulation.

Tracks whether the process is currently running inside the interactive TUI.
Used to suppress prompts and per-article warnings that would corrupt
questionary's terminal state when called via _dispatch inside the TUI.

## Functions

### set_tui_active

```python
def set_tui_active(active: bool) -> None
```

Set the TUI-active flag. Called by the TUI on entry and exit.

**Parameters:**

- `active` (bool)

**Returns:** None

### is_tui_active

```python
def is_tui_active() -> bool
```

Return True if the TUI is currently running.

**Returns:** bool

### reset_fetch_results

```python
def reset_fetch_results() -> None
```

Clear accumulated fetch results. Call before each fetch dispatch.

**Returns:** None

### record_fetch_result

```python
def record_fetch_result(success: bool, reason: str | None) -> None
```

Record one article outcome. Thread-safe.

**Parameters:**

- `success` (bool)
- `reason` (str | None)

**Returns:** None

### get_fetch_result

```python
def get_fetch_result() -> 'FetchResult'
```

Build and return a FetchResult from accumulated outcomes.

**Returns:** 'FetchResult'

