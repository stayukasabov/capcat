# core.html_post_processor

**File:** `Application/core/html_post_processor.py`

## Description

HTML Post-Processor for Capcat Archives
Handles post-processing HTML generation after article scraping is complete.
Creates directory indices, article pages, and manages the complete web view system.

## Classes

### HTMLPostProcessor

Post-processing HTML generation system.
Handles directory traversal, index generation, and browser launching.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### process_directory_tree

```python
def process_directory_tree(self, root_path: str, incremental: bool = True, is_single_article: bool = False) -> str
```

Process an entire directory tree and generate HTML files.

Args:
    root_path: Root directory path to process
    incremental: If True, only process changed/missing articles
    is_single_article: If True, skip directory index creation (for single command)

Returns:
    URL of the main index page or article.html for single articles

**Parameters:**

- `self`
- `root_path` (str)
- `incremental` (bool) *optional*
- `is_single_article` (bool) *optional*

**Returns:** str

##### _process_article_files

```python
def _process_article_files(self, root_path: Path, incremental: bool = True) -> None
```

Process article.md and comments.md files with intelligent caching.

**Parameters:**

- `self`
- `root_path` (Path)
- `incremental` (bool) *optional*

**Returns:** None

##### _should_process_article

```python
def _should_process_article(self, article_dir: Path) -> bool
```

Determine if article should be processed based on intelligent caching.

Returns True if:
- HTML files don't exist, OR
- Source files are newer than HTML files

**Parameters:**

- `self`
- `article_dir` (Path)

**Returns:** bool

##### _is_article_directory

```python
def _is_article_directory(self, directory: Path) -> bool
```

Check if directory contains article content.

**Parameters:**

- `self`
- `directory` (Path)

**Returns:** bool

##### _get_source_config

```python
def _get_source_config(self, article_dir: Path) -> Optional[Dict]
```

Get source configuration if it has template metadata.

**Parameters:**

- `self`
- `article_dir` (Path)

**Returns:** Optional[Dict]

##### _process_article_directory

```python
def _process_article_directory(self, article_dir: Path, progress = None) -> None
```

Process a single article directory to generate HTML files.

**Parameters:**

- `self`
- `article_dir` (Path)
- `progress` *optional*

**Returns:** None

##### _generate_directory_indices

```python
def _generate_directory_indices(self, root_path: Path) -> None
```

Generate index.html files for all directories.

**Parameters:**

- `self`
- `root_path` (Path)

**Returns:** None

##### _should_have_index

```python
def _should_have_index(self, directory: Path) -> bool
```

Determine if directory should have an index.html file.

**Parameters:**

- `self`
- `directory` (Path)

**Returns:** bool

##### _create_directory_index

```python
def _create_directory_index(self, directory: Path) -> None
```

Create news.html for a specific directory.

Skip news.html for Capcats single article directories since they only
contain one article and index.html is sufficient.

**Parameters:**

- `self`
- `directory` (Path)

**Returns:** None

##### _is_capcats_single_article

```python
def _is_capcats_single_article(self, directory: Path) -> bool
```

Check if directory is a Capcats single article capture.

Returns True if:
- Parent directory is named "Capcats"
- This indicates a single article capture, not a News archive

Examples:
    Capcats/Sam-Altman-Article/ -> True (skip news.html)
    Capcats/InfoQ_26-10-2025/ -> True (skip news.html)
    News_26-10-2025/BBC_26-10-2025/ -> False (keep news.html)

**Parameters:**

- `self`
- `directory` (Path)

**Returns:** bool

##### _create_main_index

```python
def _create_main_index(self, root_path: Path, index_path: Path) -> None
```

Create the main index.html at the root level.

**Parameters:**

- `self`
- `root_path` (Path)
- `index_path` (Path)

**Returns:** None

##### _build_breadcrumb_path

```python
def _build_breadcrumb_path(self, current_path: Path) -> List[str]
```

Build breadcrumb navigation path for a given directory.

**Parameters:**

- `self`
- `current_path` (Path)

**Returns:** List[str]

##### _is_archive_root

```python
def _is_archive_root(self, path: Path) -> bool
```

Check if path is an archive root directory.

**Parameters:**

- `self`
- `path` (Path)

**Returns:** bool

##### _detect_output_mode

```python
def _detect_output_mode(self, path: Path) -> str
```

Detect output mode based on directory structure.

Args:
    path: Path to check (article directory or any path in the tree)

Returns:
    'batch' for standard news archive structure
    'custom' for custom --output directories

**Parameters:**

- `self`
- `path` (Path)

**Returns:** str

##### _get_index_filename

```python
def _get_index_filename(self, output_mode: str) -> str
```

Get the appropriate index filename based on output mode.

Args:
    output_mode: Either 'batch' or 'custom'

Returns:
    'news.html' for batch mode
    'index.html' for custom mode or unknown modes

**Parameters:**

- `self`
- `output_mode` (str)

**Returns:** str

##### _extract_title_from_markdown

```python
def _extract_title_from_markdown(self, markdown_path: Path) -> str
```

Extract the article title from the markdown file's H1 heading.
Falls back to using the folder name if no H1 is found.

Args:
    markdown_path: Path to the markdown file

Returns:
    The article title string

**Parameters:**

- `self`
- `markdown_path` (Path)

**Returns:** str

##### _write_html_file

```python
def _write_html_file(self, file_path: Path, content: str) -> None
```

Write HTML content to file.

**Parameters:**

- `self`
- `file_path` (Path)
- `content` (str)

**Returns:** None

##### launch_browser

```python
def launch_browser(self, index_url: str) -> bool
```

Display URL for browser opening (platform-agnostic approach).

Args:
    index_url: File URL to the main index

Returns:
    True if URL was displayed successfully

**Parameters:**

- `self`
- `index_url` (str)

**Returns:** bool


## Functions

### process_html_generation

```python
def process_html_generation(directory_path: str, incremental: bool = True, is_single_article: bool = False) -> Optional[str]
```

Convenience function to process HTML generation for a directory.

Args:
    directory_path: Path to the directory to process
    incremental: If True, only process recently modified files (default: True)
    is_single_article: If True, skip directory index creation (for single command)

Returns:
    URL of the generated index page or article.html, or None if failed

**Parameters:**

- `directory_path` (str)
- `incremental` (bool) *optional*
- `is_single_article` (bool) *optional*

**Returns:** Optional[str]

### launch_web_view

```python
def launch_web_view(directory_path: str, incremental: bool = True, is_single_article: bool = False) -> bool
```

Generate HTML files and display browser URL for a directory.

Args:
    directory_path: Path to the directory to process
    incremental: If True, only process recently modified files (default: True)
    is_single_article: If True, skip directory index creation (for single command)

Returns:
    True if successful, False otherwise

**Parameters:**

- `directory_path` (str)
- `incremental` (bool) *optional*
- `is_single_article` (bool) *optional*

**Returns:** bool

