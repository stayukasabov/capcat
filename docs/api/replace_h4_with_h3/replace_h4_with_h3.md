# replace_h4_with_h3

**File:** `Application/replace_h4_with_h3.py`

## Description

H4 to H3 Tag Replacement Script
--------------------------------
Replaces all <h4> tags with <h3> tags in HTML files within website/docs/

Requirements Analysis:
1. Only replace h4 tags with h3 tags - no new content
2. Preserve all attributes (class, id, style, etc.)
3. Handle both opening and closing tags
4. Process all HTML files in website/docs/ recursively
5. Maintain exact formatting and content

Edge Cases Handled:
- Tags with attributes: <h4 class="foo" id="bar">
- Self-closing or malformed tags (though rare for h4)
- Tags spanning multiple lines
- Nested content within h4 tags
- Mixed case tags (HTML is case-insensitive)

Implementation Strategy:
- Use regex for precise tag replacement (faster than HTML parser for simple replacements)
- Process files in-place with backup option
- Track all changes for verification
- Dry-run mode for safety

Trade-offs:
1. Regex vs HTML Parser:
   - Regex: Faster, simpler, preserves exact formatting
   - Parser: More robust for malformed HTML, but may reformat
   - Choice: Regex (preserves formatting, sufficient for well-formed HTML)

2. In-place vs New Files:
   - In-place: Simpler, saves space
   - New files: Safer, allows comparison
   - Choice: In-place with backup option

## Constants

### OPENING_TAG_PATTERN

**Value:** `re.compile('<h4((?:\\s+[^>]*)?)>', re.IGNORECASE)`

### CLOSING_TAG_PATTERN

**Value:** `re.compile('</h4>', re.IGNORECASE)`

## Classes

### H4ToH3Replacer

Handles replacement of h4 tags with h3 tags in HTML files.

#### Methods

##### __init__

```python
def __init__(self, base_dir: str, dry_run: bool = False, backup: bool = True)
```

Initialize the replacer.

Args:
    base_dir: Base directory to search for HTML files
    dry_run: If True, only report changes without modifying files
    backup: If True, create backup files before modification

**Parameters:**

- `self`
- `base_dir` (str)
- `dry_run` (bool) *optional*
- `backup` (bool) *optional*

##### find_html_files

```python
def find_html_files(self) -> List[Path]
```

Recursively find all HTML files in the base directory.

Returns:
    List of Path objects for HTML files

**Parameters:**

- `self`

**Returns:** List[Path]

##### replace_tags_in_content

```python
def replace_tags_in_content(self, content: str) -> Tuple[str, int, int]
```

Replace h4 tags with h3 tags in the given content.

Args:
    content: HTML content as string

Returns:
    Tuple of (modified_content, opening_tags_count, closing_tags_count)

**Parameters:**

- `self`
- `content` (str)

**Returns:** Tuple[str, int, int]

##### process_file

```python
def process_file(self, file_path: Path) -> bool
```

Process a single HTML file.

Args:
    file_path: Path to the HTML file

Returns:
    True if file was modified, False otherwise

**Parameters:**

- `self`
- `file_path` (Path)

**Returns:** bool

##### run

```python
def run(self) -> Dict
```

Run the replacement process on all HTML files.

Returns:
    Dictionary containing processing statistics

**Parameters:**

- `self`

**Returns:** Dict

##### print_summary

```python
def print_summary(self)
```

Print summary of the replacement process.

**Parameters:**

- `self`


## Functions

### main

```python
def main()
```

Main entry point for the script.

