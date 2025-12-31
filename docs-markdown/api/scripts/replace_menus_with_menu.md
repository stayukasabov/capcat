# scripts.replace_menus_with_menu

**File:** `Application/scripts/replace_menus_with_menu.py`

## Description

Replace 'menus' with 'menu' in text under Mermaid diagrams in diagrams/*.html files.

## Functions

### replace_menus_after_diagram

```python
def replace_menus_after_diagram(content: str) -> tuple[str, int]
```

Replace 'menus' with 'menu' in content after Mermaid diagrams.

Args:
    content: HTML file content

Returns:
    Tuple of (updated_content, number_of_replacements)

**Parameters:**

- `content` (str)

**Returns:** tuple[str, int]

### process_diagram_file

```python
def process_diagram_file(file_path: Path) -> bool
```

Process a single diagram HTML file.

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

Process all diagram HTML files.

