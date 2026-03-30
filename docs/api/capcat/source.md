# capcat.sources.builtin.custom.hn.source

**File:** `Application/capcat/sources/builtin/custom/hn/source.py`

## Description

Hacker News source implementation for the new source system.
Enhanced with comment functionality from V1 implementation.

## Constants

### _HN_SELECTORS

**Value:** `{'comment_selector': '.comment-tree .athing', 'user_selector': '.hnuser', 'comment_text_selector': '.comment', 'depth_fn': _hn_depth}`

## Classes

### HnSource

**Inherits from:** BaseSource

Hacker News source implementation with comment support.

#### Methods

##### source_type

```python
def source_type(self) -> str
```

**Parameters:**

- `self`

**Returns:** str

##### discover_articles

```python
def discover_articles(self, count: int) -> List[Article]
```

Discover articles from Hacker News with comment URLs.
Supports pagination for fetching >30 articles.

**Parameters:**

- `self`
- `count` (int)

**Returns:** List[Article]

⚠️ **High complexity:** 21

##### fetch_article_content

```python
def fetch_article_content(self, article: Article, output_dir: str, progress_callback = None, download_files: bool = False) -> Tuple[bool, Optional[str]]
```

Fetch article content from Hacker News.
Optimized to prevent conversion hangs.

**Parameters:**

- `self`
- `article` (Article)
- `output_dir` (str)
- `progress_callback` *optional*
- `download_files` (bool) *optional*

**Returns:** Tuple[bool, Optional[str]]

##### _validate_custom_config

```python
def _validate_custom_config(self) -> List[str]
```

Validate Hacker News-specific configuration.

**Parameters:**

- `self`

**Returns:** List[str]

##### _should_skip_custom

```python
def _should_skip_custom(self, url: str, title: str = '') -> bool
```

Custom skip logic for Hacker News.

**Parameters:**

- `self`
- `url` (str)
- `title` (str) *optional*

**Returns:** bool

##### fetch_comments

```python
def fetch_comments(self, comment_url: str, article_title: str, article_folder_path: str, html_mode: bool = False) -> bool
```

Fetch and save Hacker News comments using optimized streamlined processor.

Args:
    comment_url: URL to the HN comments page
    article_title: Title of the article for logging
    article_folder_path: Specific folder path for this article
    html_mode: If True, generate HTML directly; if False, generate markdown

Returns:
    bool: True if comments were successfully saved, False otherwise

**Parameters:**

- `self`
- `comment_url` (str)
- `article_title` (str)
- `article_folder_path` (str)
- `html_mode` (bool) *optional*

**Returns:** bool

⚠️ **High complexity:** 15


## Functions

### _hn_depth

```python
def _hn_depth(elem) -> int
```

Extract comment depth from HN's td.ind img width attribute (40px per level).

**Parameters:**

- `elem`

**Returns:** int

