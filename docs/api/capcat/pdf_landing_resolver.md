---
layout: default
---

# capcat.core.pdf_landing_resolver

**File:** `Application/capcat/core/pdf_landing_resolver.py`

## Description

Resolve direct PDF URLs to their HTML landing pages where possible.

Returns None for unknown domains so the caller can fall back to a stub article.

## Functions

### resolve_pdf_to_landing_page

```python
def resolve_pdf_to_landing_page(url: str) -> Optional[str]
```

Return an HTML landing-page URL for a known PDF URL pattern, or None.

**Parameters:**

- `url` (str)

**Returns:** Optional[str]

### _looks_like_pdf_path

```python
def _looks_like_pdf_path(path: str) -> bool
```

**Parameters:**

- `path` (str)

**Returns:** bool

