# scripts.update_footer_text

**File:** `Application/scripts/update_footer_text.py`

## Description

Update footer text in website HTML files.

Changes: "Design and context engineering by"
To: "Design, illustration and context engineering by"

## Functions

### should_skip_directory

```python
def should_skip_directory(dir_name: str) -> bool
```

Check if directory should be skipped.

**Parameters:**

- `dir_name` (str)

**Returns:** bool

### should_skip_file

```python
def should_skip_file(file_name: str) -> bool
```

Check if file should be skipped.

**Parameters:**

- `file_name` (str)

**Returns:** bool

### update_footer_in_file

```python
def update_footer_in_file(file_path: Path) -> Tuple[bool, int]
```

Update footer text in a single HTML file.

Returns:
    Tuple of (changed: bool, count: int) - whether file was modified and number of replacements

**Parameters:**

- `file_path` (Path)

**Returns:** Tuple[bool, int]

### find_and_update_html_files

```python
def find_and_update_html_files(root_dir: Path) -> List[Tuple[Path, int]]
```

Find all HTML files in directory tree and update footer text.

Returns:
    List of (file_path, replacement_count) tuples for modified files

**Parameters:**

- `root_dir` (Path)

**Returns:** List[Tuple[Path, int]]

### main

```python
def main()
```

Main execution function.

