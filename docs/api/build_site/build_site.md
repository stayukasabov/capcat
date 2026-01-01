# build_site

**File:** `Application/build_site.py`

## Description

Build script: Replace Jekyll includes with actual HTML content.
This creates a static site without needing Jekyll processing.

## Functions

### get_favicon_path

```python
def get_favicon_path(html_file, docs_root)
```

Calculate relative path to favicon based on file location.

**Parameters:**

- `html_file`
- `docs_root`

### inject_favicon

```python
def inject_favicon(content, favicon_path)
```

Inject favicon link into <head> if not already present.

**Parameters:**

- `content`
- `favicon_path`

### build_site

```python
def build_site()
```

Replace {% include %} directives and old HTML with actual content.

