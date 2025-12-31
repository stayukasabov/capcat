# website.apply_full_layout

**File:** `Application/website/apply_full_layout.py`

## Description

Apply full layout (header, footer, back-to-top button, container wrapper) to all docs HTML files.

## Functions

### calculate_relative_path

```python
def calculate_relative_path(html_file_path, website_root)
```

Calculate relative path from HTML file to website root

**Parameters:**

- `html_file_path`
- `website_root`

### get_header_html

```python
def get_header_html(rel_path)
```

Generate header HTML with correct relative paths

**Parameters:**

- `rel_path`

### get_footer_html

```python
def get_footer_html(rel_path)
```

Generate footer HTML with correct relative paths

**Parameters:**

- `rel_path`

### process_html_file

```python
def process_html_file(file_path, website_root)
```

Process a single HTML file to add header, footer, layout, and back-to-top button

**Parameters:**

- `file_path`
- `website_root`

### main

```python
def main()
```

