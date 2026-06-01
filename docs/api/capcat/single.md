---
layout: default
render_with_liquid: false
---

# capcat.commands.single

**File:** `Application/capcat/commands/single.py`

## Description

Single article fetch command.

## Constants

### MIRROR_AVAILABLE

**Value:** `True`

### MIRROR_AVAILABLE

**Value:** `False`

## Classes

### GenericArticleFetcher

**Inherits from:** ArticleFetcher

ArticleFetcher subclass that never skips any URL.

Used as the generic fallback when no registered source
matches the requested URL.

#### Methods

##### should_skip_url

```python
def should_skip_url(self, url: str, title: str) -> bool
```

Always return False - no URL is skipped in generic mode.

Args:
    url: The article URL being evaluated.
    title: The article title being evaluated.

Returns:
    Always ``False``.

**Parameters:**

- `self`
- `url` (str)
- `title` (str)

**Returns:** bool


## Functions

### _rename_to_dated

```python
def _rename_to_dated(article_folder: str, date_str: str) -> str
```

Rename article_folder to '<date_str>-<name>' in its parent directory.

Idempotent: returns the original path unchanged if it already starts
with ``date_str + '-'``.

Args:
    article_folder: Absolute path to the article folder to rename.
    date_str: Date prefix in DD-MM-YYYY format.

Returns:
    Absolute path to the (possibly renamed) folder.

**Parameters:**

- `article_folder` (str)
- `date_str` (str)

**Returns:** str

### _scrape_with_specialized_source

```python
def _scrape_with_specialized_source(url: str, output_dir: str, verbose: bool = False, files: bool = False, generate_html: bool = False) -> Tuple[bool, Optional[str]]
```

Handle article scraping with specialized sources (Medium, Substack, etc.).

**Parameters:**

- `url` (str)
- `output_dir` (str)
- `verbose` (bool) *optional*
- `files` (bool) *optional*
- `generate_html` (bool) *optional*

**Returns:** Tuple[bool, Optional[str]]

### scrape_single_article

```python
def scrape_single_article(url: str, output_dir: str, verbose: bool = False, files: bool = False, pdfs: bool = False, generate_html: bool = False, update_mode: bool = False) -> Tuple[bool, Optional[str]]
```

Scrape a single article from any supported source.

Attempts specialized sources first (Medium, Substack), then falls back
to generic scraping. Auto-detects source and creates organized output.

Args:
    url: Article URL to scrape.
    output_dir: Base directory for output (uses project Capcats/ if ".").
    verbose: Enable verbose logging output.
    files: Download all media files (audio, video, documents).
    pdfs: Download PDF files (--pdfs flag).
    generate_html: Generate HTML version of article.
    update_mode: Update existing article instead of creating new.

Returns:
    Tuple of (success, output_directory_path).

**Parameters:**

- `url` (str)
- `output_dir` (str)
- `verbose` (bool) *optional*
- `files` (bool) *optional*
- `pdfs` (bool) *optional*
- `generate_html` (bool) *optional*
- `update_mode` (bool) *optional*

**Returns:** Tuple[bool, Optional[str]]

⚠️ **High complexity:** 18

