# scripts.rename_ink_to_imprint

**File:** `Application/scripts/rename_ink_to_imprint.py`

## Description

Rename all instances of --cream to --paper in website/css/ files.

## Functions

### replace_cream_with_paper

```python
def replace_cream_with_paper(content: str) -> tuple[str, int]
```

Replace --cream with --paper in CSS content.

Args:
    content: CSS file content

Returns:
    Tuple of (updated_content, number_of_replacements)

**Parameters:**

- `content` (str)

**Returns:** tuple[str, int]

### process_css_file

```python
def process_css_file(file_path: Path) -> bool
```

Process a single CSS file.

Args:
    file_path: Path to CSS file

Returns:
    True if file was modified, False otherwise

**Parameters:**

- `file_path` (Path)

**Returns:** bool

### main

```python
def main()
```

Process all CSS files in website/css/ directory.

