# website.apply_design_system

**File:** `Application/website/apply_design_system.py`

## Description

Apply design system CSS and JS to all HTML files in the docs folder.
Removes inline <style> tags and adds links to design-system.css, main.css, and main.js

## Functions

### calculate_relative_path

```python
def calculate_relative_path(html_file_path, website_root)
```

Calculate relative path from HTML file to website root

**Parameters:**

- `html_file_path`
- `website_root`

### process_html_file

```python
def process_html_file(file_path, website_root)
```

Process a single HTML file to add design system links

**Parameters:**

- `file_path`
- `website_root`

### main

```python
def main()
```

