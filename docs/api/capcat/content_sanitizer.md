---
layout: default
render_with_liquid: false
---

# capcat.core.content_sanitizer

**File:** `Application/capcat/core/content_sanitizer.py`

## Description

Content Sanitizer - Archive isolation for Capcat.

Strips tracking, analytics, scripts, and dangerous elements from archived
content. Runs as a single pass at the end of the processing pipeline,
before file write. Always enabled. No config toggle.

## Functions

### sanitize

```python
def sanitize(content: str, mode: str = 'markdown') -> str
```

Sanitize content for complete archive isolation.

Args:
    content: Raw content string (markdown or HTML).
    mode: "markdown" or "html".

Returns:
    Sanitized content with dangerous elements removed.

**Parameters:**

- `content` (str)
- `mode` (str) *optional*

**Returns:** str

### _strip_dangerous_html

```python
def _strip_dangerous_html(content: str) -> str
```

Strip dangerous HTML elements from content (rules M1-M9).

**Parameters:**

- `content` (str)

**Returns:** str

### _strip_tracking_heuristics

```python
def _strip_tracking_heuristics(content: str) -> str
```

Detect and remove tracking elements by heuristic patterns.

**Parameters:**

- `content` (str)

**Returns:** str

### _apply_html_hardening

```python
def _apply_html_hardening(content: str) -> str
```

Apply HTML-specific hardening rules (H1-H4).

**Parameters:**

- `content` (str)

**Returns:** str

### _stash_code_block

```python
def _stash_code_block(match)
```

**Parameters:**

- `match`

### _restore_code_block

```python
def _restore_code_block(match)
```

**Parameters:**

- `match`

### _remove_tracker_img

```python
def _remove_tracker_img(match)
```

**Parameters:**

- `match`

### _clean_style_url

```python
def _clean_style_url(match)
```

**Parameters:**

- `match`

### _is_heuristic_tracker

```python
def _is_heuristic_tracker(tag: str) -> bool
```

Check if an <img> tag matches tracking heuristics.

**Parameters:**

- `tag` (str)

**Returns:** bool

### _remove_external_stylesheet

```python
def _remove_external_stylesheet(match)
```

**Parameters:**

- `match`

