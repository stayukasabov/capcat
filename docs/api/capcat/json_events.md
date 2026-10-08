---
layout: default
render_with_liquid: false
---

# capcat.core.json_events

**File:** `Application/capcat/core/json_events.py`

## Description

JSON event emission for the hidden --capcatmac-ipc CLI output mode.

Module-level state, mirroring the existing capcat.core.tui_context pattern
(set_tui_active/is_tui_active) - enabled once per command invocation rather
than threaded as a parameter through the whole fetch pipeline.

## Functions

### enable

```python
def enable(stream: TextIO) -> None
```

Turn on JSON event emission, writing to *stream*.

**Parameters:**

- `stream` (TextIO)

**Returns:** None

### disable

```python
def disable() -> None
```

Turn off JSON event emission.

**Returns:** None

### is_enabled

```python
def is_enabled() -> bool
```

Return whether JSON event emission is currently active.

**Returns:** bool

### emit

```python
def emit(event: str) -> None
```

Print one NDJSON line ({"event": event, **fields}) if enabled.

**Parameters:**

- `event` (str)

**Returns:** None

### emit_raw

```python
def emit_raw(payload: dict) -> None
```

Print *payload* as a single JSON object, no "event" wrapper.

Used for one-shot structured output (list --capcatmac-ipc) as opposed to the
NDJSON event stream emit() produces for fetch/bundle/single.

**Parameters:**

- `payload` (dict)

**Returns:** None

### record_article_fetched

```python
def record_article_fetched() -> None
```

Emit article_fetched and bump the running fetched counter.

**Returns:** None

### record_article_error

```python
def record_article_error() -> None
```

Emit article_error and bump the running error counter.

**Returns:** None

### pop_article_counts

```python
def pop_article_counts() -> tuple[int, int]
```

Return (fetched, errors) accumulated since the last call, then reset.

**Returns:** tuple[int, int]

### set_html_path

```python
def set_html_path(path: str | None) -> None
```

Record the generated HTML index path/URL for the next run_complete event.

**Parameters:**

- `path` (str | None)

**Returns:** None

### pop_html_path

```python
def pop_html_path() -> str | None
```

Return the recorded HTML path, then reset it to None.

**Returns:** str | None

