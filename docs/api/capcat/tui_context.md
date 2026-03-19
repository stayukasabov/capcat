# capcat.core.tui_context

**File:** `Application/capcat/core/tui_context.py`

## Description

TUI context flag.

Tracks whether the process is currently running inside the interactive TUI.
Used to suppress prompts (e.g. theme upgrade dialogue) that would corrupt
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

