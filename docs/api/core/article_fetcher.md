# core.article_fetcher

**File:** `Application/core/article_fetcher.py`

## Description

Shared article fetching functionality for Capcat sources.

This module contains the base ArticleFetcher class that eliminates
code duplication between source-specific implementations.

## Constants

### _GLOBAL_UPDATE_MODE

**Value:** `False`

### LARGE_PDF_THRESHOLD_MB

**Value:** `5`

### SKIP_PROMPT_TIMEOUT_SECONDS

**Value:** `20`

### BYTES_TO_MB

**Value:** `1024 * 1024`

### _GLOBAL_UPDATE_MODE

**Value:** `update_mode`

## Classes

### ArticleFetcher

**Inherits from:** ABC

Base class for article fetching with shared functionality.

This eliminates code duplication between HN and Lobsters implementations
while allowing source-specific customizations.

#### Methods

##### __init__

```python
def __init__(self, session: requests.Session, download_files: bool = False, source_code: str = 'unknown', generate_html: bool = False)
```

Initialize with a requests session for connection pooling.

Args:
    session: Requests session for connection pooling
    download_files: Whether to download all media files
    source_code: Source identifier for rate limiting
        (e.g., 'hn', 'scientificamerican')
    generate_html: Whether to generate HTML output files

**Parameters:**

- `self`
- `session` (requests.Session)
- `download_files` (bool) *optional*
- `source_code` (str) *optional*
- `generate_html` (bool) *optional*

##### set_download_files

```python
def set_download_files(self, download_files: bool)
```

Dynamically set the download_files flag.

**Parameters:**

- `self`
- `download_files` (bool)

##### _create_markdown_link_replacement

```python
def _create_markdown_link_replacement(self, markdown_content: str, original_url: str, local_path: str, fallback_text: str, is_image: bool = False) -> str
```

Replace markdown link/image references with local paths.

Consolidates duplicate URL replacement logic that appears 4+ times
in the codebase. Handles both image and link syntax with proper
f-string formatting to prevent syntax errors.

Args:
    markdown_content: Markdown text to process
    original_url: URL to replace (will be escaped for regex)
    local_path: Local file path to use instead
    fallback_text: Text to use if link text is empty
    is_image: True for image syntax (![]()),
        False for link syntax ([])

Returns:
    Updated markdown content with replaced URLs

Example:
    >>> content = "![](http://example.com/img.jpg)"
    >>> result = self._create_markdown_link_replacement(
    ...     content, "http://example.com/img.jpg",
    ...     "images/img.jpg", "image", is_image=True
    ... )
    >>> print(result)
    ![image](images/img.jpg)

**Parameters:**

- `self`
- `markdown_content` (str)
- `original_url` (str)
- `local_path` (str)
- `fallback_text` (str)
- `is_image` (bool) *optional*

**Returns:** str

##### _fetch_url_with_retry

```python
def _fetch_url_with_retry(self, url: str, timeout: int = None) -> requests.Response
```

Fetch URL with automatic retry logic, rate limiting, and
adaptive timeouts.

This method provides:
- Adaptive timeouts based on source performance
- Rate limiting based on source-specific configuration
- Up to 3 retry attempts (via @network_retry decorator)
- Exponential backoff (1s, 2s, 4s)
- Automatic handling of connection errors and timeouts
- Response time tracking for adaptive learning

Args:
    url: URL to fetch
    timeout: Optional timeout override (uses adaptive if None)

Returns:
    Response object

Raises:
    requests.exceptions.RequestException: After all retries exhausted

**Parameters:**

- `self`
- `url` (str)
- `timeout` (int) *optional*

**Returns:** requests.Response

##### should_skip_url

```python
def should_skip_url(self, url: str, title: str) -> bool
```

Source-specific logic to determine if a URL should be skipped.

Args:
    url: The article URL to check
    title: The article title

Returns:
    True if the URL should be skipped, False otherwise

**Parameters:**

- `self`
- `url` (str)
- `title` (str)

**Returns:** bool

##### fetch_article_content

```python
def fetch_article_content(self, title: str, url: str, index: int, base_folder: str, progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, Optional[str], Optional[str]]
```

Fetch and save the content of an article in markdown format.

This method handles ONLY article content fetching. Comments should be
fetched separately using source-specific comment fetching methods.

Args:
    title: Article title
    url: Article URL
    index: Article index number
    base_folder: Base directory to save to
    progress_callback: Optional callback function for progress
        updates (progress, stage)

Returns:
    Tuple[bool, Optional[str], Optional[str]]: (success,
        article_folder_path, article_title)

**Parameters:**

- `self`
- `title` (str)
- `url` (str)
- `index` (int)
- `base_folder` (str)
- `progress_callback` (Optional[Callable[[float, str], None]]) *optional*

**Returns:** Tuple[bool, Optional[str], Optional[str]]

⚠️ **High complexity:** 12

##### _is_pdf_url

```python
def _is_pdf_url(self, url: str) -> bool
```

Check if a URL points specifically to a PDF file.

**Parameters:**

- `self`
- `url` (str)

**Returns:** bool

##### _handle_media_file

```python
def _handle_media_file(self, title: str, url: str, index: int, base_folder: str, file_type: str) -> Tuple[bool, Optional[str], Optional[str]]
```

Handle direct media file downloads (documents, audio, video, PDF).

**Parameters:**

- `self`
- `title` (str)
- `url` (str)
- `index` (int)
- `base_folder` (str)
- `file_type` (str)

**Returns:** Tuple[bool, Optional[str], Optional[str]]

##### _create_skipped_pdf_placeholder

```python
def _create_skipped_pdf_placeholder(self, title: str, url: str, index: int, base_folder: str) -> Tuple[bool, str, str]
```

Create placeholder content for a skipped PDF download.

Args:
    title: Article title
    url: PDF URL that was skipped
    index: Article index
    base_folder: Base folder for article storage

Returns:
    Tuple of (success, title, content_path)

**Parameters:**

- `self`
- `title` (str)
- `url` (str)
- `index` (int)
- `base_folder` (str)

**Returns:** Tuple[bool, str, str]

##### _check_pdf_size_and_prompt

```python
def _check_pdf_size_and_prompt(self, url: str, title: str, is_direct_pdf: bool = False) -> bool
```

Check PDF file size and prompt user to skip if large.

Args:
    url: PDF file URL
    title: Article title
    is_direct_pdf: True if URL itself is a PDF (not discovered in content)

Returns:
    True if user wants to skip, False to proceed

**Parameters:**

- `self`
- `url` (str)
- `title` (str)
- `is_direct_pdf` (bool) *optional*

**Returns:** bool

##### _prompt_user_skip

```python
def _prompt_user_skip(self, title: str, size_mb: float, is_direct_pdf: bool = False) -> bool
```

Prompt user to skip large PDF download with ESC key.

Args:
    title: Article title
    size_mb: File size in megabytes
    is_direct_pdf: True if URL itself is a PDF (not discovered in content)

Returns:
    True if ESC pressed (skip), False on timeout (proceed)

**Parameters:**

- `self`
- `title` (str)
- `size_mb` (float)
- `is_direct_pdf` (bool) *optional*

**Returns:** bool

##### _fetch_web_content

```python
def _fetch_web_content(self, title: str, url: str, index: int, base_folder: str, progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, Optional[str], Optional[str]]
```

Fetch and process regular web page content.

**Parameters:**

- `self`
- `title` (str)
- `url` (str)
- `index` (int)
- `base_folder` (str)
- `progress_callback` (Optional[Callable[[float, str], None]]) *optional*

**Returns:** Tuple[bool, Optional[str], Optional[str]]

⚠️ **High complexity:** 65

##### _cleanup_empty_images_folder

```python
def _cleanup_empty_images_folder(self, article_folder_path: str) -> None
```

Remove images folder if it exists but is empty.

**Parameters:**

- `self`
- `article_folder_path` (str)

**Returns:** None

##### _parse_srcset

```python
def _parse_srcset(self, srcset: str) -> str
```

Parse srcset attribute and return the highest resolution image URL.

**Parameters:**

- `self`
- `srcset` (str)

**Returns:** str

##### _remove_image_from_markdown

```python
def _remove_image_from_markdown(self, markdown_content: str, image_src: str) -> str
```

Remove image references from markdown content when download fails.

**Parameters:**

- `self`
- `markdown_content` (str)
- `image_src` (str)

**Returns:** str

##### _process_document_links

```python
def _process_document_links(self, soup: BeautifulSoup, markdown_content: str, article_folder_path: str, base_url: str) -> str
```

Process and download document files linked in the content.

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `markdown_content` (str)
- `article_folder_path` (str)
- `base_url` (str)

**Returns:** str

⚠️ **High complexity:** 14

##### _process_embedded_media_efficiently

```python
def _process_embedded_media_efficiently(self, soup: BeautifulSoup, markdown_content: str, article_folder_path: str, base_url: str) -> str
```

Process and download embedded media files efficiently with batch
processing.

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `markdown_content` (str)
- `article_folder_path` (str)
- `base_url` (str)

**Returns:** str

⚠️ **High complexity:** 90

##### _fallback_image_detection

```python
def _fallback_image_detection(self, full_page_html: str, existing_images: set, article_folder_path: str, base_url: str) -> List[str]
```

Fallback image detection system that scans the entire page for images
when the primary extraction method finds few images.

Args:
    full_page_html: Original full page HTML before article extraction
    existing_images: Set of image URLs already found by primary method
    article_folder_path: Path to save downloaded images
    base_url: Base URL for resolving relative image paths

Returns:
    List of additional image URLs found and downloaded

**Parameters:**

- `self`
- `full_page_html` (str)
- `existing_images` (set)
- `article_folder_path` (str)
- `base_url` (str)

**Returns:** List[str]

⚠️ **High complexity:** 19

##### _should_skip_image

```python
def _should_skip_image(self, img_tag, img_src: str, ui_patterns: dict) -> bool
```

Determine if an image should be skipped based on UI element patterns.

Args:
    img_tag: BeautifulSoup img tag
    img_src: Image source URL
    ui_patterns: Dictionary of patterns to match against

Returns:
    True if image should be skipped (is likely a UI element)

**Parameters:**

- `self`
- `img_tag`
- `img_src` (str)
- `ui_patterns` (dict)

**Returns:** bool

⚠️ **High complexity:** 11

##### _cleanup_failed_media_reference

```python
def _cleanup_failed_media_reference(self, markdown_content: str, url: str, link_type: str, alt_text: str) -> str
```

Clean up broken media references when download fails.

**Parameters:**

- `self`
- `markdown_content` (str)
- `url` (str)
- `link_type` (str)
- `alt_text` (str)

**Returns:** str

##### _get_next_available_index

```python
def _get_next_available_index(self, base_folder: str, suggested_index: int) -> int
```

Get the next available index to avoid duplicate folder numbering.

**Parameters:**

- `self`
- `base_folder` (str)
- `suggested_index` (int)

**Returns:** int

##### _get_unique_folder_name

```python
def _get_unique_folder_name(self, base_folder: str, base_title: str) -> str
```

Get folder name - always returns base_title to allow overwrite.
When user runs repeatedly, content is replaced instead of
creating duplicates.

**Parameters:**

- `self`
- `base_folder` (str)
- `base_title` (str)

**Returns:** str

##### _discover_rss_feed

```python
def _discover_rss_feed(self, base_url: str) -> Optional[str]
```

Attempt to discover RSS/Atom feed for a website.

Args:
    base_url: Base URL of the website

Returns:
    Feed URL if found, None otherwise

**Parameters:**

- `self`
- `base_url` (str)

**Returns:** Optional[str]

##### _download_pdf_with_progress

```python
def _download_pdf_with_progress(self, url: str, progress_callback: Optional[Callable[[float, str], None]] = None) -> bytes
```

Download PDF with streaming and progress reporting.

Args:
    url: PDF URL to download
    progress_callback: Optional callback for progress updates

Returns:
    PDF content as bytes

**Parameters:**

- `self`
- `url` (str)
- `progress_callback` (Optional[Callable[[float, str], None]]) *optional*

**Returns:** bytes

⚠️ **High complexity:** 11

##### _handle_pdf_article

```python
def _handle_pdf_article(self, title: str, url: str, base_folder: str, progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, Optional[str], Optional[str]]
```

Handle article URLs that are PDF files.

Downloads the PDF file with streaming progress and extracts text content.

Args:
    title: Article title
    url: PDF URL
    base_folder: Base folder for output
    progress_callback: Optional progress callback

Returns:
    Tuple of (success, title, folder_path)

**Parameters:**

- `self`
- `title` (str)
- `url` (str)
- `base_folder` (str)
- `progress_callback` (Optional[Callable[[float, str], None]]) *optional*

**Returns:** Tuple[bool, Optional[str], Optional[str]]

##### _create_error_article

```python
def _create_error_article(self, title: str, url: str, error_type: str, error_details: str, base_folder: str, rss_feed_url: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]
```

Create a clean error article when fetching fails.

Args:
    title: Article title
    url: Original article URL
    error_type: Type of error (e.g., "403 Forbidden",
        "Connection Timeout")
    error_details: Detailed error message
    base_folder: Base directory to save to
    rss_feed_url: Optional RSS feed URL if discovered

Returns:
    Tuple[bool, Optional[str], Optional[str]]: (success,
        article_title, article_folder_path)

**Parameters:**

- `self`
- `title` (str)
- `url` (str)
- `error_type` (str)
- `error_details` (str)
- `base_folder` (str)
- `rss_feed_url` (Optional[str]) *optional*

**Returns:** Tuple[bool, Optional[str], Optional[str]]


### HackerNewsArticleFetcher

**Inherits from:** ArticleFetcher

Hacker News specific article fetcher.

#### Methods

##### __init__

```python
def __init__(self, session, download_files: bool = False)
```

**Parameters:**

- `self`
- `session`
- `download_files` (bool) *optional*

##### should_skip_url

```python
def should_skip_url(self, url: str, title: str) -> bool
```

Skip Hacker News internal links.

**Parameters:**

- `self`
- `url` (str)
- `title` (str)

**Returns:** bool


### LobstersArticleFetcher

**Inherits from:** ArticleFetcher

Lobsters specific article fetcher.

#### Methods

##### __init__

```python
def __init__(self, session, download_files: bool = False)
```

**Parameters:**

- `self`
- `session`
- `download_files` (bool) *optional*

##### should_skip_url

```python
def should_skip_url(self, url: str, title: str) -> bool
```

Skip Lobste.rs internal links that don't point to external content.

**Parameters:**

- `self`
- `url` (str)
- `title` (str)

**Returns:** bool


## Functions

### _suppress_stderr

```python
def _suppress_stderr()
```

Context manager to temporarily suppress stderr output at OS level.

Used to suppress pynput's misleading accessibility warning on macOS.
The warning says "Input event monitoring will not be possible" but
keyboard detection actually works correctly. Uses os.dup2() for
OS-level redirection to catch warnings from subprocesses/threads.

Falls back to Python-level redirection in test environments where
stderr is replaced with StringIO.

### set_global_update_mode

```python
def set_global_update_mode(update_mode: bool)
```

Set the global update mode flag.

**Parameters:**

- `update_mode` (bool)

### get_global_update_mode

```python
def get_global_update_mode() -> bool
```

Get the global update mode flag.

**Returns:** bool

### convert_html_with_timeout

```python
def convert_html_with_timeout(html_content: str, url: str, timeout: int = CONVERSION_TIMEOUT_SECONDS) -> str
```

Convert HTML to markdown with thread-safe timeout protection.

Uses concurrent.futures for thread-safe timeout handling, replacing
signal-based approach which caused race conditions in parallel processing.

Args:
    html_content: Raw HTML content to convert
    url: Source URL for logging context
    timeout: Maximum seconds to allow conversion (default: 30)

Returns:
    Converted markdown content, empty string if timeout or error

Raises:
    None - All exceptions are caught and logged

Example:
    >>> html = "<html><body><h1>Test</h1></body></html>"
    >>> markdown = convert_html_with_timeout(html, "https://example.com")
    >>> print(markdown)
    # Test

Thread Safety:
    This function is thread-safe and can be called concurrently
    from multiple threads without race conditions.

**Parameters:**

- `html_content` (str)
- `url` (str)
- `timeout` (int) *optional*

**Returns:** str

### replacement_func

```python
def replacement_func(match)
```

Create replacement text with fallback for empty groups.

**Parameters:**

- `match`

### on_press

```python
def on_press(key)
```

Handle key press events.

**Parameters:**

- `key`

### replace_if_image_link

```python
def replace_if_image_link(match)
```

**Parameters:**

- `match`

### process_single_media

```python
def process_single_media(link_info)
```

**Parameters:**

- `link_info`

### download_progress

```python
def download_progress(progress, status)
```

**Parameters:**

- `progress`
- `status`

