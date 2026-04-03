# capcat.core.unified_source_processor

**File:** `Application/capcat/core/unified_source_processor.py`

## Description

Unified Source Processor for Capcat.
This eliminates the 46+ duplicate process_*_articles functions by providing
a single, configurable processor that works with all sources.

Follows DRY principle while maintaining source-specific optimizations.

## Constants

### NEW_SOURCE_SYSTEM_AVAILABLE

**Value:** `True`

### MIRROR_AVAILABLE

**Value:** `True`

### NEW_SOURCE_SYSTEM_AVAILABLE

**Value:** `False`

### MIRROR_AVAILABLE

**Value:** `False`

## Classes

### FetchResult


### UnifiedSourceProcessor

Unified processor for all news sources.
Eliminates code duplication while preserving source-specific functionality.

#### Methods

##### __init__

```python
def __init__(self, project_root: Optional[Path] = None)
```

**Parameters:**

- `self`
- `project_root` (Optional[Path]) *optional*

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

##### _assert_all_sources_in_new_system

```python
def _assert_all_sources_in_new_system(self) -> None
```

Assert that every source in the legacy config is also registered in the new system.
Raises ValueError listing any sources that would fall through to the deleted legacy path.

**Parameters:**

- `self`

**Returns:** None

##### process_source_articles

```python
def process_source_articles(self, source_name: str, count: Optional[int], output_dir: str, quiet: bool = False, verbose: bool = False, download_files: bool = False, batch_mode: bool = False, generate_html: bool = False) -> None
```

Universal article processing function. All sources route through the new system.

Args:
    source_name: The source identifier (e.g., 'hn', 'bbc', 'cnn')
    count: Number of articles to fetch
    quiet: Suppress progress output
    verbose: Enable verbose logging
    download_files: Enable media file downloads
    batch_mode: Whether processing multiple sources (affects retry messages)
    generate_html: Generate HTML version after fetching

**Parameters:**

- `self`
- `source_name` (str)
- `count` (Optional[int])
- `output_dir` (str)
- `quiet` (bool) *optional*
- `verbose` (bool) *optional*
- `download_files` (bool) *optional*
- `batch_mode` (bool) *optional*
- `generate_html` (bool) *optional*

**Returns:** None

##### _process_with_new_system

```python
def _process_with_new_system(self, source_name: str, count: Optional[int], output_dir: str, quiet: bool = False, verbose: bool = False, download_files: bool = False, batch_mode: bool = False, generate_html: bool = False) -> None
```

Process articles using the new source system.

**Parameters:**

- `self`
- `source_name` (str)
- `count` (Optional[int])
- `output_dir` (str)
- `quiet` (bool) *optional*
- `verbose` (bool) *optional*
- `download_files` (bool) *optional*
- `batch_mode` (bool) *optional*
- `generate_html` (bool) *optional*

**Returns:** None

⚠️ **High complexity:** 19

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

⚠️ **High complexity:** 16

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

⚠️ **High complexity:** 20


## Functions

### _resolve_count

```python
def _resolve_count(cli_count: Optional[int], source_config: 'SourceConfig', config = None) -> int
```

Resolve article count: CLI flag > capcat.yml sources list > source YAML > global config default.

Args:
    cli_count: Value from --count flag, or None if not provided.
    source_config: The source's SourceConfig (has article_count field).
    config: FetchNewsConfig instance (used for vault overrides and global fallback).

Returns:
    Number of articles to fetch.

**Parameters:**

- `cli_count` (Optional[int])
- `source_config` ('SourceConfig')
- `config` *optional*

**Returns:** int

### _build_article_metadata

```python
def _build_article_metadata(article, source) -> dict
```

Build frontmatter metadata dict for an article.

**Parameters:**

- `article`
- `source`

**Returns:** dict

### _build_comments_metadata

```python
def _build_comments_metadata(article, source) -> dict
```

Build frontmatter metadata dict for a comments file.

**Parameters:**

- `article`
- `source`

**Returns:** dict

### get_unified_processor

```python
def get_unified_processor(project_root: Optional[Path] = None) -> UnifiedSourceProcessor
```

Get global unified processor instance.

**Parameters:**

- `project_root` (Optional[Path]) *optional*

**Returns:** UnifiedSourceProcessor

### process_source_articles

```python
def process_source_articles(source_name: str, count: Optional[int], output_dir: str, quiet: bool = False, verbose: bool = False, download_files: bool = False, batch_mode: bool = False, generate_html: bool = False, project_root: Optional[Path] = None) -> None
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
    project_root: Optional project root override

**Parameters:**

- `source_name` (str)
- `count` (Optional[int])
- `output_dir` (str)
- `quiet` (bool) *optional*
- `verbose` (bool) *optional*
- `download_files` (bool) *optional*
- `batch_mode` (bool) *optional*
- `generate_html` (bool) *optional*
- `project_root` (Optional[Path]) *optional*

**Returns:** None

### progress_callback

```python
def progress_callback(progress: float, stage: str)
```

**Parameters:**

- `progress` (float)
- `stage` (str)

