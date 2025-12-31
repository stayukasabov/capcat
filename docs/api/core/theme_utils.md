# core.theme_utils

**File:** `Application/core/theme_utils.py`

## Description

Theme utilities for hash-based theme persistence.

Provides functions for injecting theme hashes into HTML links
and parsing theme from URL hashes.

## Functions

### inject_theme_hash

```python
def inject_theme_hash(html: str, theme: str) -> str
```

Inject theme hash into HTML links.

Args:
    html: HTML content with links
    theme: Current theme ('light' or 'dark')

Returns:
    HTML with theme hash appended to internal links

**Parameters:**

- `html` (str)
- `theme` (str)

**Returns:** str

### parse_theme_from_hash

```python
def parse_theme_from_hash(hash_value: str) -> Optional[str]
```

Parse theme from URL hash.

Args:
    hash_value: URL hash string (e.g., '#theme=light')

Returns:
    Theme value or None if not found

**Parameters:**

- `hash_value` (str)

**Returns:** Optional[str]

### replace_link

```python
def replace_link(match)
```

**Parameters:**

- `match`

