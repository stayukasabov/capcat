# fix_ethical_scraping_links

**File:** `Application/fix_ethical_scraping_links.py`

## Description

Fix ethical-scraping.html links to use correct relative paths based on file location.

## Constants

### WEBSITE_ROOT

**Value:** `Path('/Users/xpro/SynologyDrive/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application/website')`

## Functions

### calculate_relative_path

```python
def calculate_relative_path(file_path: str) -> str
```

Calculate the correct relative path to docs/ethical-scraping.html
based on the file's location.

Args:
    file_path: Relative path from website root (e.g., "docs/api/core/index.html")

Returns:
    Correct relative path to ethical-scraping.html

**Parameters:**

- `file_path` (str)

**Returns:** str

### update_file

```python
def update_file(file_path: Path, correct_path: str) -> tuple[bool, str, str]
```

Update ethical-scraping links in a file.

Returns:
    (changed, old_pattern, new_pattern)

**Parameters:**

- `file_path` (Path)
- `correct_path` (str)

**Returns:** tuple[bool, str, str]

### main

```python
def main()
```

Update all files with correct relative paths.

⚠️ **High complexity:** 15

