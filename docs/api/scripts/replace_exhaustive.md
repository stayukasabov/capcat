# scripts.replace_exhaustive

**File:** `Application/scripts/replace_exhaustive.py`

## Description

Replace "Exhaustive" with "Comprehensive" in all website files.

## Functions

### replace_exhaustive

```python
def replace_exhaustive(content: str) -> tuple[str, int]
```

Replace "Exhaustive" with "Comprehensive" in content.

Args:
    content: File content string

Returns:
    Tuple of (updated_content, number_of_replacements)

**Parameters:**

- `content` (str)

**Returns:** tuple[str, int]

### process_file

```python
def process_file(file_path: Path) -> bool
```

Process a single file to replace text.

Args:
    file_path: Path to file

Returns:
    True if file was modified, False otherwise

**Parameters:**

- `file_path` (Path)

**Returns:** bool

### main

```python
def main()
```

Process all files in website/ directory.

