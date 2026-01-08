# scripts.update_svg_color

**File:** `Application/scripts/update_svg_color.py`

## Description

Update SVG fill color in all documentation HTML files.
Changes fill:rgb(234,94,52) to fill:rgb(255,83,31) in SVG elements.

## Functions

### update_svg_color

```python
def update_svg_color(content: str) -> tuple[str, int]
```

Update SVG fill color in HTML content.

Args:
    content: HTML content string

Returns:
    Tuple of (updated_content, number_of_replacements)

**Parameters:**

- `content` (str)

**Returns:** tuple[str, int]

### process_html_file

```python
def process_html_file(file_path: Path) -> bool
```

Process a single HTML file to update SVG colors.

Args:
    file_path: Path to HTML file

Returns:
    True if file was modified, False otherwise

**Parameters:**

- `file_path` (Path)

**Returns:** bool

### main

```python
def main()
```

Process all HTML files in website/docs directory.

