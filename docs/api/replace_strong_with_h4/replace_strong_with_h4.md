# replace_strong_with_h4

**File:** `Application/replace_strong_with_h4.py`

## Description

Strong to H4 Tag Replacement Script

Replaces all <strong> tags with <h4> tags in HTML files within website/docs/ directory.
When multiple <strong> tags appear on the same line, each replacement is placed on a new line.

Key Features:
- Replaces <strong> → <h4> and </strong> → </h4>
- Inserts newlines before subsequent <strong> tags on the same line
- Preserves indentation and spacing
- Handles nested content and attributes
- Dry-run mode for safe testing
- Automatic backups
- Comprehensive statistics and reporting

Usage:
    python replace_strong_with_h4.py                    # Dry run (no changes)
    python replace_strong_with_h4.py --execute          # Execute replacement
    python replace_strong_with_h4.py --backup-dir ./my-backups  # Custom backup location

## Constants

### STRONG_OPEN_PATTERN

**Value:** `re.compile('<strong\\b([^>]*)>', re.IGNORECASE)`

### STRONG_CLOSE_PATTERN

**Value:** `re.compile('</strong>', re.IGNORECASE)`

### MULTIPLE_STRONG_PATTERN

**Value:** `re.compile('(<strong\\b[^>]*>.*?</strong>).*(<strong\\b[^>]*>)', re.IGNORECASE | re.DOTALL)`

## Classes

### ReplacementStats

Statistics for replacement operations.

#### Methods

##### __post_init__

```python
def __post_init__(self)
```

**Parameters:**

- `self`


### StrongToH4Replacer

Handles replacement of <strong> tags with <h4> tags.

Special handling for multiple tags on the same line:
- Inserts newline before each subsequent <strong> tag (after the first)
- Preserves indentation and spacing
- Maintains exact content within tags

#### Methods

##### __init__

```python
def __init__(self, docs_dir: str = 'website/docs')
```

Initialize the replacer.

Args:
    docs_dir: Directory containing HTML files to process

**Parameters:**

- `self`
- `docs_dir` (str) *optional*

##### process_line

```python
def process_line(self, line: str) -> Tuple[str, int, bool]
```

Process a single line, replacing <strong> tags with <h4> tags.

If multiple <strong> tags exist on the line, insert newlines before
subsequent tags (but not the first).

Args:
    line: The line to process

Returns:
    Tuple of (modified_line, replacement_count, has_multiple_tags)

**Parameters:**

- `self`
- `line` (str)

**Returns:** Tuple[str, int, bool]

##### _handle_multiple_strong_tags

```python
def _handle_multiple_strong_tags(self, line: str) -> str
```

Handle lines with multiple <strong> tags by inserting newlines.

Strategy:
1. Find all <strong> tag positions
2. Starting from the second tag, insert a newline before it
3. Preserve indentation by extracting leading whitespace

Args:
    line: Line with multiple <strong> tags

Returns:
    Modified line with newlines inserted before subsequent tags

**Parameters:**

- `self`
- `line` (str)

**Returns:** str

##### process_file

```python
def process_file(self, file_path: Path) -> Tuple[str, int, int, int]
```

Process a single HTML file.

Args:
    file_path: Path to the HTML file

Returns:
    Tuple of (modified_content, total_replacements, modified_lines, multiple_tag_lines)

**Parameters:**

- `self`
- `file_path` (Path)

**Returns:** Tuple[str, int, int, int]

##### create_backup

```python
def create_backup(self, file_path: Path, backup_dir: Path) -> bool
```

Create a backup of the file before modification.

Args:
    file_path: Path to the file to backup
    backup_dir: Directory to store backups

Returns:
    True if backup successful, False otherwise

**Parameters:**

- `self`
- `file_path` (Path)
- `backup_dir` (Path)

**Returns:** bool

##### process_directory

```python
def process_directory(self, dry_run: bool = True, backup_dir: Path = None) -> ReplacementStats
```

Process all HTML files in the docs directory.

Args:
    dry_run: If True, only simulate changes without writing
    backup_dir: Directory for backups (if not dry run)

Returns:
    ReplacementStats object with processing statistics

**Parameters:**

- `self`
- `dry_run` (bool) *optional*
- `backup_dir` (Path) *optional*

**Returns:** ReplacementStats


## Functions

### print_statistics

```python
def print_statistics(stats: ReplacementStats, dry_run: bool)
```

Print formatted statistics.

**Parameters:**

- `stats` (ReplacementStats)
- `dry_run` (bool)

### main

```python
def main()
```

Main entry point.

