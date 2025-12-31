# fix_colon_formatting

**File:** `Application/fix_colon_formatting.py`

## Description

fix_colon_formatting.py

Removes leading colons from HTML lines in website/docs/ directory.
Targets pattern: lines starting with `:` (optionally preceded by whitespace).

Pattern: `: content` → `content` (preserving indentation)

Usage:
    python3 fix_colon_formatting.py --dry-run  # Preview changes
    python3 fix_colon_formatting.py            # Apply changes
    python3 fix_colon_formatting.py --no-backup  # Apply without backup

## Constants

### PATTERN

**Value:** `re.compile('^(\\s*):\\s*(.*)$')`

## Classes

### ColonFormattingFixer

Removes leading colons from HTML lines while preserving structure.

#### Methods

##### __init__

```python
def __init__(self, dry_run: bool = True, create_backup: bool = True)
```

Initialize fixer.

Args:
    dry_run: Preview changes without modifying files
    create_backup: Create .bak files before modification

**Parameters:**

- `self`
- `dry_run` (bool) *optional*
- `create_backup` (bool) *optional*

##### fix_line

```python
def fix_line(self, line: str) -> Tuple[str, bool]
```

Fix a single line by removing leading colon.

Args:
    line: Input line

Returns:
    (fixed_line, was_modified)

**Parameters:**

- `self`
- `line` (str)

**Returns:** Tuple[str, bool]

##### fix_file

```python
def fix_file(self, filepath: Path) -> int
```

Fix all lines in a file.

Args:
    filepath: Path to HTML file

Returns:
    Number of lines modified

**Parameters:**

- `self`
- `filepath` (Path)

**Returns:** int

⚠️ **High complexity:** 11

##### process_directory

```python
def process_directory(self, directory: Path) -> None
```

Process all HTML files in directory recursively.

Args:
    directory: Root directory to scan

**Parameters:**

- `self`
- `directory` (Path)

**Returns:** None

##### print_summary

```python
def print_summary(self) -> None
```

Print statistics summary.

**Parameters:**

- `self`

**Returns:** None


## Functions

### main

```python
def main()
```

Main entry point.

