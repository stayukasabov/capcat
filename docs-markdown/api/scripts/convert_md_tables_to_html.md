# scripts.convert_md_tables_to_html

**File:** `Application/scripts/convert_md_tables_to_html.py`

## Description

Convert Markdown Tables to Centered HTML Tables

Scans all markdown files in website/docs/ directory and converts
markdown tables to centered HTML tables with proper styling.

Usage:
    python scripts/convert_md_tables_to_html.py [--dry-run]

## Classes

### MarkdownTableConverter

Convert markdown tables to centered HTML tables.

#### Methods

##### __init__

```python
def __init__(self, docs_dir: str = 'docs')
```

**Parameters:**

- `self`
- `docs_dir` (str) *optional*

##### find_markdown_files

```python
def find_markdown_files(self) -> List[Path]
```

Find all markdown files in docs directory.

**Parameters:**

- `self`

**Returns:** List[Path]

##### detect_markdown_table

```python
def detect_markdown_table(self, content: str) -> List[Tuple[int, int, str]]
```

Detect markdown tables in content.

Returns:
    List of tuples (start_line, end_line, table_text)

**Parameters:**

- `self`
- `content` (str)

**Returns:** List[Tuple[int, int, str]]

##### parse_markdown_table

```python
def parse_markdown_table(self, table_text: str) -> Tuple[List[str], List[List[str]]]
```

Parse markdown table into headers and rows.

Args:
    table_text: Raw markdown table text

Returns:
    Tuple of (headers, rows)

**Parameters:**

- `self`
- `table_text` (str)

**Returns:** Tuple[List[str], List[List[str]]]

##### convert_to_html_table

```python
def convert_to_html_table(self, headers: List[str], rows: List[List[str]]) -> str
```

Convert parsed table to centered HTML table.

Args:
    headers: List of header cells
    rows: List of row data (each row is a list of cells)

Returns:
    HTML table string with center alignment

**Parameters:**

- `self`
- `headers` (List[str])
- `rows` (List[List[str]])

**Returns:** str

##### _escape_html

```python
def _escape_html(self, text: str) -> str
```

Escape HTML special characters but preserve code formatting.

**Parameters:**

- `self`
- `text` (str)

**Returns:** str

##### convert_file

```python
def convert_file(self, file_path: Path, dry_run: bool = False) -> int
```

Convert markdown tables in a single file.

Args:
    file_path: Path to markdown file
    dry_run: If True, only report changes without modifying

Returns:
    Number of tables converted

**Parameters:**

- `self`
- `file_path` (Path)
- `dry_run` (bool) *optional*

**Returns:** int

##### convert_all

```python
def convert_all(self, dry_run: bool = False) -> None
```

Convert all markdown tables in docs directory.

Args:
    dry_run: If True, only report changes without modifying

**Parameters:**

- `self`
- `dry_run` (bool) *optional*

**Returns:** None

##### print_summary

```python
def print_summary(self, dry_run: bool = False) -> None
```

Print conversion summary.

**Parameters:**

- `self`
- `dry_run` (bool) *optional*

**Returns:** None


## Functions

### add_css_styles

```python
def add_css_styles() -> None
```

Add centered table styles to main.css if not already present.

**Returns:** None

### main

```python
def main()
```

Main execution function.

