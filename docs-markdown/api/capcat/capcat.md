# capcat

**File:** `Application/capcat.py`

## Description

Capcat - News Article Archiving System

A free and open-source tool to make people's lives easier.

Author: Stayu Kasabov (https://stayux.com)
License: MIT-Style Non-Commercial
Copyright (c) 2025 Stayu Kasabov

## Classes

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


### Args

#### Methods

##### __init__

```python
def __init__(self, config_dict)
```

**Parameters:**

- `self`
- `config_dict`


### Args

#### Methods

##### __init__

```python
def __init__(self, config_dict)
```

**Parameters:**

- `self`
- `config_dict`


## Functions

### process_sources

```python
def process_sources(sources: List[str], args: argparse.Namespace, config, logger, generate_html: bool = False, output_dir: str = '.') -> Dict[str, any]
```

Process multiple sources using the unified processor.

Args:
    sources: List of source identifiers to process (e.g., 'hn', 'bbc')
    args: Parsed command-line arguments containing count, quiet, verbose
    config: Configuration object with system settings
    logger: Logger instance for output
    generate_html: Whether to generate HTML output after processing
    output_dir: Output directory path for saved articles

Returns:
    Dictionary with keys:
        - 'successful': List of successfully processed sources
        - 'failed': List of tuples (source, error_message)
        - 'total': Total number of sources attempted

Raises:
    SourceError: If source cannot be loaded from registry

**Parameters:**

- `sources` (List[str])
- `args` (argparse.Namespace)
- `config`
- `logger`
- `generate_html` (bool) *optional*
- `output_dir` (str) *optional*

**Returns:** Dict[str, any]

### _scrape_with_specialized_source

```python
def _scrape_with_specialized_source(url: str, output_dir: str, verbose: bool = False, files: bool = False, generate_html: bool = False) -> Tuple[bool, Optional[str]]
```

Handle article scraping with specialized sources.

Supports Medium, Substack, and similar platforms with paywall detection.

Args:
    url: Article URL to scrape
    output_dir: Directory to save article content
    verbose: Enable verbose logging output
    files: Download all media files (PDFs, audio, video)
    generate_html: Generate HTML version of article

Returns:
    Tuple of (success status, output directory path). Returns
    (True, path) on success, (False, path) or (False, None) on failure.

Raises:
    SpecializedSourceError: If source detection or scraping fails

**Parameters:**

- `url` (str)
- `output_dir` (str)
- `verbose` (bool) *optional*
- `files` (bool) *optional*
- `generate_html` (bool) *optional*

**Returns:** Tuple[bool, Optional[str]]

### scrape_single_article

```python
def scrape_single_article(url: str, output_dir: str, verbose: bool = False, files: bool = False, generate_html: bool = False, update_mode: bool = False) -> Tuple[bool, Optional[str]]
```

Scrape a single article from any supported source.

Attempts specialized sources first (Medium, Substack), then falls back
to generic scraping. Auto-detects source and creates organized output.

Args:
    url: Article URL to scrape
    output_dir: Base directory for output (uses ../Capcats/ if ".")
    verbose: Enable verbose logging output
    files: Download all media files (PDFs, audio, video)
    generate_html: Generate HTML version of article
    update_mode: Update existing article instead of creating new

Returns:
    Tuple of (success status, output directory path). Returns
    (True, path) on success, (False, path) or (False, None) on failure.

Raises:
    SourceError: If source detection fails
    IOError: If output directory cannot be created

**Parameters:**

- `url` (str)
- `output_dir` (str)
- `verbose` (bool) *optional*
- `files` (bool) *optional*
- `generate_html` (bool) *optional*
- `update_mode` (bool) *optional*

**Returns:** Tuple[bool, Optional[str]]

⚠️ **High complexity:** 16

### run_app

```python
def run_app(argv: Optional[List[str]] = None)
```

Main application logic.

**Parameters:**

- `argv` (Optional[List[str]]) *optional*

⚠️ **High complexity:** 51

### main

```python
def main() -> None
```

Main entry point for the optimized Capcat application.

Parses command-line arguments and delegates to run_app for execution.
Handles single article scraping, batch processing, and interactive mode.

**Returns:** None

