# core.utils

**File:** `Application/core/utils.py`

## Description

Core utilities for the Capcat application.
Handles file system operations, URL processing, and other shared functionalities.

## Functions

### get_source_folder_name

```python
def get_source_folder_name(source_code: str) -> str
```

Convert source code to proper folder name format using display_name from source configurations.

Args:
    source_code (str): Source code (e.g., 'hn', 'aljazeera', 'bbc')

Returns:
    str: Proper folder name (e.g., 'Hacker-News', 'Al-Jazeera', 'BBC-News')

**Parameters:**

- `source_code` (str)

**Returns:** str

### sanitize_filename

```python
def sanitize_filename(title: str, max_length: int = None, intelligent_truncation: bool = True) -> str
```

Sanitize a string to be used as a filename with intelligent title truncation.

Args:
    title (str): The title to sanitize.
    max_length (int): Maximum length for the filename.
    intelligent_truncation (bool): Whether to use intelligent truncation for long titles.

Returns:
    str: A sanitized filename string.

**Parameters:**

- `title` (str)
- `max_length` (int) *optional*
- `intelligent_truncation` (bool) *optional*

**Returns:** str

### truncate_title_intelligently

```python
def truncate_title_intelligently(title: str, max_length: int = 200) -> str
```

Intelligently truncate article titles to a reasonable length for folder names and display.

Preserves meaning by:
- Removing redundant prefixes (GitHub - user/repo: actual title)
- Truncating at word boundaries when possible
- Removing URL references and redundant information
- Keeping the most meaningful part of the title

Args:
    title (str): The original title to truncate
    max_length (int): Maximum desired length (default: 200 characters for HTML cards)

Returns:
    str: Intelligently truncated title

Examples:
    >>> truncate_title_intelligently("GitHub - xyflow/xyflow: React Flow | Svelte Flow - Powerful open source libraries for building node-based UIs with React (https://reactflow.dev) or Svelte (https://svelteflow.dev). Ready out-of-the-box and infinitely customizable.")
    "Powerful open source libraries for building node-based UIs with React"

    >>> truncate_title_intelligently("A" * 100)
    "AAAA..." (100 chars unchanged with 200 default)

    >>> truncate_title_intelligently("A" * 100, max_length=80)
    "AAAA..." (truncated to 80 chars)

**Parameters:**

- `title` (str)
- `max_length` (int) *optional*

**Returns:** str

⚠️ **High complexity:** 14

### create_output_directory

```python
def create_output_directory(base_path: str, source_prefix: str) -> str
```

Create the main output directory for a source with the current date (YYYY-MM-DD format).

Args:
    base_path (str): The base directory path.
    source_prefix (str): The prefix for the source (e.g., 'hn', 'lb').

Returns:
    str: The full path to the created directory.

**Parameters:**

- `base_path` (str)
- `source_prefix` (str)

**Returns:** str

### create_output_directory_capcat

```python
def create_output_directory_capcat(base_path: str, source_prefix: str) -> str
```

Create the main output directory for a source with the current date (DD-MM-YYYY format).

Args:
    base_path (str): The base directory path.
    source_prefix (str): The prefix for the source (e.g., 'hn', 'lb').

Returns:
    str: The full path to the created directory.

**Parameters:**

- `base_path` (str)
- `source_prefix` (str)

**Returns:** str

### create_batch_output_directory

```python
def create_batch_output_directory(source_prefix: str) -> str
```

Create the proper nested directory structure for batch processing (fetch/bundle commands).
Creates: ../News/news_DD-MM-YYYY/source_DD-MM-YYYY/

Args:
    source_prefix (str): The prefix for the source (e.g., 'hn', 'lb').

Returns:
    str: The full path to the created source directory.

**Parameters:**

- `source_prefix` (str)

**Returns:** str

### is_valid_url

```python
def is_valid_url(url: str) -> bool
```

Check if a string is a valid URL.

Args:
    url (str): The URL to check.

Returns:
    bool: True if valid, False otherwise.

**Parameters:**

- `url` (str)

**Returns:** bool

