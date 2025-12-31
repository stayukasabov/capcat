# core.unified_source_processor

**File:** `Application/core/unified_source_processor.py`

## Description

Unified Source Processor for Capcat.
This eliminates the 46+ duplicate process_*_articles functions by providing
a single, configurable processor that works with all sources.

Follows DRY principle while maintaining source-specific optimizations.

## Constants

### NEW_SOURCE_SYSTEM_AVAILABLE

**Value:** `True`

### NEW_SOURCE_SYSTEM_AVAILABLE

**Value:** `False`

## Classes

### UnifiedSourceProcessor

Unified processor for all news sources.
Eliminates code duplication while preserving source-specific functionality.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### clear_url_cache

```python
def clear_url_cache(cls)
```

Clear the URL cache for a new processing session.

**Parameters:**

- `cls`

##### is_url_processed

```python
def is_url_processed(cls, url: str) -> bool
```

Check if a URL has already been processed.

**Parameters:**

- `cls`
- `url` (str)

**Returns:** bool

##### mark_url_processed

```python
def mark_url_processed(cls, url: str)
```

Mark a URL as processed.

**Parameters:**

- `cls`
- `url` (str)

##### _is_source_in_new_system

```python
def _is_source_in_new_system(self, source_name: str) -> bool
```

Check if source is available in the new source system.

**Parameters:**

- `self`
- `source_name` (str)

**Returns:** bool

##### process_source_articles

```python
def process_source_articles(self, source_name: str, count: int, output_dir: str, quiet: bool = False, verbose: bool = False, download_files: bool = False, batch_mode: bool = False) -> None
```

Universal article processing function that replaces all 46+ process_*_articles functions.

Args:
    source_name: The source identifier (e.g., 'hn', 'bbc', 'cnn')
    count: Number of articles to fetch
    quiet: Suppress progress output
    verbose: Enable verbose logging
    download_files: Enable media file downloads
    batch_mode: Whether processing multiple sources (affects retry messages)

**Parameters:**

- `self`
- `source_name` (str)
- `count` (int)
- `output_dir` (str)
- `quiet` (bool) *optional*
- `verbose` (bool) *optional*
- `download_files` (bool) *optional*
- `batch_mode` (bool) *optional*

**Returns:** None

##### _get_articles

```python
def _get_articles(self, source_name: str, source_config: dict, count: int) -> List[Tuple[str, str, Optional[str]]]
```

Get articles using either custom scraping function or generic adapter.

Returns:
    List of (title, url, comment_url) tuples

**Parameters:**

- `self`
- `source_name` (str)
- `source_config` (dict)
- `count` (int)

**Returns:** List[Tuple[str, str, Optional[str]]]

##### _get_articles_custom

```python
def _get_articles_custom(self, source_name: str, source_config: dict, count: int) -> List[Tuple[str, str, Optional[str]]]
```

Get articles using custom scraping function.

**Parameters:**

- `self`
- `source_name` (str)
- `source_config` (dict)
- `count` (int)

**Returns:** List[Tuple[str, str, Optional[str]]]

##### _get_articles_generic

```python
def _get_articles_generic(self, source_name: str, source_config: dict, count: int) -> List[Tuple[str, str, Optional[str]]]
```

Get articles using generic configuration-driven adapter.

**Parameters:**

- `self`
- `source_name` (str)
- `source_config` (dict)
- `count` (int)

**Returns:** List[Tuple[str, str, Optional[str]]]

##### _process_articles_parallel

```python
def _process_articles_parallel(self, source_name: str, source_config: dict, articles: List[Tuple], base_dir: str, download_files: bool, quiet: bool, verbose: bool) -> None
```

Process articles in parallel using ThreadPoolExecutor.

**Parameters:**

- `self`
- `source_name` (str)
- `source_config` (dict)
- `articles` (List[Tuple])
- `base_dir` (str)
- `download_files` (bool)
- `quiet` (bool)
- `verbose` (bool)

**Returns:** None

⚠️ **High complexity:** 16

##### _process_single_article

```python
def _process_single_article(self, source_name: str, source_config: dict, article_info: tuple, base_dir: str, download_files: bool, progress_tracker = None) -> bool
```

Process a single article with progress reporting.

**Parameters:**

- `self`
- `source_name` (str)
- `source_config` (dict)
- `article_info` (tuple)
- `base_dir` (str)
- `download_files` (bool)
- `progress_tracker` *optional*

**Returns:** bool

##### _process_article_custom

```python
def _process_article_custom(self, source_name: str, source_config: dict, article_info: tuple, base_dir: str, download_files: bool, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool
```

Process article using source-specific functions.

**Parameters:**

- `self`
- `source_name` (str)
- `source_config` (dict)
- `article_info` (tuple)
- `base_dir` (str)
- `download_files` (bool)
- `progress_callback` (Optional[Callable[[float, str], None]]) *optional*

**Returns:** bool

##### _process_with_new_system

```python
def _process_with_new_system(self, source_name: str, count: int, output_dir: str, quiet: bool = False, verbose: bool = False, download_files: bool = False, batch_mode: bool = False) -> None
```

Process articles using the new source system.

**Parameters:**

- `self`
- `source_name` (str)
- `count` (int)
- `output_dir` (str)
- `quiet` (bool) *optional*
- `verbose` (bool) *optional*
- `download_files` (bool) *optional*
- `batch_mode` (bool) *optional*

**Returns:** None

##### _process_articles_with_new_system

```python
def _process_articles_with_new_system(self, source, articles, base_dir: str, download_files: bool, quiet: bool, verbose: bool)
```

Process articles using the new source system with parallel execution.

**Parameters:**

- `self`
- `source`
- `articles`
- `base_dir` (str)
- `download_files` (bool)
- `quiet` (bool)
- `verbose` (bool)

⚠️ **High complexity:** 14

##### _process_single_article_new_system

```python
def _process_single_article_new_system(self, source, article, base_dir: str, download_files: bool, progress_tracker = None, index: int = 1) -> bool
```

Process a single article using the new source system.

**Parameters:**

- `self`
- `source`
- `article`
- `base_dir` (str)
- `download_files` (bool)
- `progress_tracker` *optional*
- `index` (int) *optional*

**Returns:** bool

⚠️ **High complexity:** 14

##### _process_article_generic

```python
def _process_article_generic(self, source_name: str, source_config: dict, article_info: tuple, base_dir: str, download_files: bool, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool
```

Process article using generic configuration-driven approach.

**Parameters:**

- `self`
- `source_name` (str)
- `source_config` (dict)
- `article_info` (tuple)
- `base_dir` (str)
- `download_files` (bool)
- `progress_callback` (Optional[Callable[[float, str], None]]) *optional*

**Returns:** bool


## Functions

### get_unified_processor

```python
def get_unified_processor() -> UnifiedSourceProcessor
```

Get global unified processor instance.

**Returns:** UnifiedSourceProcessor

### process_source_articles

```python
def process_source_articles(source_name: str, count: int, output_dir: str, quiet: bool = False, verbose: bool = False, download_files: bool = False, batch_mode: bool = False) -> None
```

Convenience function to process articles from any source.
This replaces all 46+ individual process_*_articles functions.

Args:
    source_name: The source identifier (e.g., 'hn', 'bbc', 'cnn')
    count: Number of articles to fetch
    quiet: Suppress progress output
    verbose: Enable verbose logging
    download_files: Enable media file downloads
    batch_mode: Whether processing multiple sources (affects retry messages)

**Parameters:**

- `source_name` (str)
- `count` (int)
- `output_dir` (str)
- `quiet` (bool) *optional*
- `verbose` (bool) *optional*
- `download_files` (bool) *optional*
- `batch_mode` (bool) *optional*

**Returns:** None

### progress_callback

```python
def progress_callback(progress: float, stage: str)
```

**Parameters:**

- `progress` (float)
- `stage` (str)

### progress_callback

```python
def progress_callback(progress: float, stage: str)
```

**Parameters:**

- `progress` (float)
- `stage` (str)

