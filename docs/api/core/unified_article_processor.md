# core.unified_article_processor

**File:** `Application/core/unified_article_processor.py`

## Description

Unified Article Processor - Universal entry point for all article processing.

All commands (single, fetch, bundle) route through this processor to ensure
consistent behavior across the application.

## Classes

### UnifiedArticleProcessor

Universal article processing entry point.

Provides consistent article fetching logic across all commands:
- Single article mode
- Fetch mode (multiple sources)
- Bundle mode (predefined source groups)

Processing Order:
1. Check specialized sources (Twitter, YouTube, Medium, Substack)
2. Check source-specific handlers (HN, BBC, etc.)
3. Fall back to generic ArticleFetcher

#### Methods

##### __init__

```python
def __init__(self)
```

Initialize processor with specialized source manager.

**Parameters:**

- `self`

##### process_article

```python
def process_article(self, url: str, title: str, index: int, base_folder: str, download_files: bool = False, progress_callback: Optional[Callable[[float, str], None]] = None, update_mode: bool = False) -> Tuple[bool, Optional[str], Optional[str]]
```

Universal article processing with specialized source detection.

Args:
    url: Article URL to process
    title: Article title (may be placeholder)
    index: Article index for folder numbering
    base_folder: Output directory path
    download_files: Whether to download media files
    progress_callback: Optional progress reporting callback
    update_mode: Re-check URL validity and update timestamp

Returns:
    Tuple[bool, Optional[str], Optional[str]]:
    (success, article_title, article_folder_path)

**Parameters:**

- `self`
- `url` (str)
- `title` (str)
- `index` (int)
- `base_folder` (str)
- `download_files` (bool) *optional*
- `progress_callback` (Optional[Callable[[float, str], None]]) *optional*
- `update_mode` (bool) *optional*

**Returns:** Tuple[bool, Optional[str], Optional[str]]

##### _process_with_specialized_source

```python
def _process_with_specialized_source(self, url: str, title: str, base_folder: str, update_mode: bool) -> Tuple[bool, Optional[str], Optional[str]]
```

Handle specialized sources (Twitter, YouTube, Medium, Substack).

Args:
    url: Article URL
    title: Article title
    base_folder: Output directory
    update_mode: Whether to re-check URL and update timestamp

Returns:
    Tuple of (success, article_title, article_folder_path)

**Parameters:**

- `self`
- `url` (str)
- `title` (str)
- `base_folder` (str)
- `update_mode` (bool)

**Returns:** Tuple[bool, Optional[str], Optional[str]]

##### _process_with_source_handler

```python
def _process_with_source_handler(self, url: str, title: str, index: int, base_folder: str, download_files: bool, progress_callback: Optional[Callable], source: str) -> Tuple[bool, Optional[str], Optional[str]]
```

Handle source-specific processing (HN, BBC, etc.).

Delegates to existing source-specific implementations.

Args:
    url: Article URL
    title: Article title
    index: Article index
    base_folder: Output directory
    download_files: Whether to download media
    progress_callback: Progress callback
    source: Source identifier (e.g., 'hn', 'bbc')

Returns:
    Tuple of (success, article_title, article_folder_path)

**Parameters:**

- `self`
- `url` (str)
- `title` (str)
- `index` (int)
- `base_folder` (str)
- `download_files` (bool)
- `progress_callback` (Optional[Callable])
- `source` (str)

**Returns:** Tuple[bool, Optional[str], Optional[str]]

##### _process_with_generic_handler

```python
def _process_with_generic_handler(self, url: str, title: str, index: int, base_folder: str, download_files: bool, progress_callback: Optional[Callable]) -> Tuple[bool, Optional[str], Optional[str]]
```

Handle generic article processing.

Uses ArticleFetcher for unknown sources.

Args:
    url: Article URL
    title: Article title
    index: Article index
    base_folder: Output directory
    download_files: Whether to download media
    progress_callback: Progress callback

Returns:
    Tuple of (success, article_title, article_folder_path)

**Parameters:**

- `self`
- `url` (str)
- `title` (str)
- `index` (int)
- `base_folder` (str)
- `download_files` (bool)
- `progress_callback` (Optional[Callable])

**Returns:** Tuple[bool, Optional[str], Optional[str]]

##### _check_url_validity

```python
def _check_url_validity(self, url: str) -> bool
```

Check if URL is still valid (HEAD request).

Args:
    url: URL to check

Returns:
    True if URL valid (status 200-399), False otherwise

**Parameters:**

- `self`
- `url` (str)

**Returns:** bool

##### _update_timestamp

```python
def _update_timestamp(self, article_folder: str)
```

Update timestamp in article metadata.

Args:
    article_folder: Path to article folder containing article.md

**Parameters:**

- `self`
- `article_folder` (str)

##### _add_url_warning

```python
def _add_url_warning(self, article_folder: str, url: str)
```

Add warning about invalid URL to article.

Args:
    article_folder: Path to article folder
    url: Invalid URL

**Parameters:**

- `self`
- `article_folder` (str)
- `url` (str)


### GenericArticleFetcher

**Inherits from:** ArticleFetcher

#### Methods

##### should_skip_url

```python
def should_skip_url(self, url: str, title: str) -> bool
```

Never skip URLs for generic fetching.

**Parameters:**

- `self`
- `url` (str)
- `title` (str)

**Returns:** bool


## Functions

### get_unified_processor

```python
def get_unified_processor() -> UnifiedArticleProcessor
```

Get the global unified article processor instance.

**Returns:** UnifiedArticleProcessor

