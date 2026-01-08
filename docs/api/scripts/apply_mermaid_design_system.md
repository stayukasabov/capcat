# scripts.apply_mermaid_design_system

**File:** `Application/scripts/apply_mermaid_design_system.py`

## Description

Apply design system CSS variables to Mermaid diagram styling in diagrams/*.html files.
Uses Capcat design system colors, fonts, and spacing.

## Functions

### get_mermaid_styling

```python
def get_mermaid_styling() -> str
```

Generate Mermaid styling using design system hex colors.

**Returns:** str

### update_mermaid_initialization

```python
def update_mermaid_initialization(content: str) -> tuple[str, bool]
```

Replace mermaid.initialize with design system version.

Args:
    content: HTML file content

Returns:
    Tuple of (updated_content, was_modified)

**Parameters:**

- `content` (str)

**Returns:** tuple[str, bool]

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

