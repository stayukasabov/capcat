# remove_hr_tags

**File:** `Application/remove_hr_tags.py`

## Description

Script to remove all <hr> tags from HTML files in website/docs/ directory.
This script follows clean code principles with proper error handling and logging.

## Classes

### HRTagRemover

Clean, focused class responsible for removing HR tags from HTML files.

#### Methods

##### __init__

```python
def __init__(self, docs_directory: str = 'website/docs')
```

Initialize the HR tag remover.

Args:
    docs_directory: Path to the docs directory to process

**Parameters:**

- `self`
- `docs_directory` (str) *optional*

##### find_html_files

```python
def find_html_files(self) -> List[Path]
```

Find all HTML files in the docs directory recursively.

Returns:
    List of Path objects for HTML files

**Parameters:**

- `self`

**Returns:** List[Path]

##### remove_hr_tags_from_content

```python
def remove_hr_tags_from_content(self, content: str) -> Tuple[str, int]
```

Remove all <hr> tags from HTML content.

Args:
    content: HTML content as string

Returns:
    Tuple of (cleaned_content, number_of_tags_removed)

**Parameters:**

- `self`
- `content` (str)

**Returns:** Tuple[str, int]

##### process_file

```python
def process_file(self, file_path: Path) -> bool
```

Process a single HTML file to remove HR tags.

Args:
    file_path: Path to the HTML file

Returns:
    True if file was successfully processed, False otherwise

**Parameters:**

- `self`
- `file_path` (Path)

**Returns:** bool

##### run

```python
def run(self) -> None
```

Main method to execute the HR tag removal process.

**Parameters:**

- `self`

**Returns:** None

##### report_results

```python
def report_results(self, total_files: int, successful_files: int) -> None
```

Report the final results of the HR tag removal process.

Args:
    total_files: Total number of files found
    successful_files: Number of files successfully processed

**Parameters:**

- `self`
- `total_files` (int)
- `successful_files` (int)

**Returns:** None


## Functions

### main

```python
def main()
```

Main entry point for the script.

