---
layout: default
render_with_liquid: false
---

# capcat.sources.builtin.custom.hn.source

**File:** `Application/capcat/sources/builtin/custom/hn/source.py`

## Description

Hacker News source implementation using the official Firebase API.
Uses hacker-news.firebaseio.com/v0/ for article discovery and comment fetching.

## Constants

### _HN_API_BASE

**Value:** `'https://hacker-news.firebaseio.com/v0'`

### _MAX_LINKS_PER_COMMENT

**Value:** `5`

### _MAX_COMMENTS_PER_ARTICLE

**Value:** `200`

### _MAX_COMMENT_DEPTH

**Value:** `4`

### _CONCURRENT_WORKERS

**Value:** `5`

## Classes

### HnSource

**Inherits from:** BaseSource

Hacker News source implementation using the official Firebase API.

All article discovery and comment fetching uses the HN Firebase API
at hacker-news.firebaseio.com/v0/. No HTML is scraped from
news.ycombinator.com for discovery or comments.

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

Discover articles from Hacker News via the official Firebase API.

Fetches /v0/topstories.json for story IDs, then fetches metadata
for each story sequentially with rate limiting.

**Parameters:**

- `self`
- `count` (int)

**Returns:** List[Article]

⚠️ **High complexity:** 14

##### fetch_article_content

```python
def fetch_article_content(self, article: Article, output_dir: str, progress_callback = None, download_files: bool = False, download_pdfs: bool = False) -> Tuple[bool, Optional[str]]
```

Fetch article content from Hacker News.
Optimized to prevent conversion hangs.

**Parameters:**

- `self`
- `article` (Article)
- `output_dir` (str)
- `progress_callback` *optional*
- `download_files` (bool) *optional*
- `download_pdfs` (bool) *optional*

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
def fetch_comments(self, comment_url: str, article_title: str, article_folder_path: str, html_mode: bool = False, comment_ids: Optional[List[int]] = None) -> bool
```

Fetch and save HN comments via the official Firebase API.

Recursively fetches each comment item from /v0/item/{id}.json,
building a flat list with depth tracking. Passes the result to
StreamlinedCommentProcessor for rendering.

Args:
    comment_url: URL of the comments page (used in output header)
    article_title: Title of the article for logging
    article_folder_path: Folder path for saving the output file
    html_mode: If True, generate HTML; if False, generate markdown
    comment_ids: List of top-level comment IDs from the story item

Returns:
    True if comments were successfully saved, False otherwise

**Parameters:**

- `self`
- `comment_url` (str)
- `article_title` (str)
- `article_folder_path` (str)
- `html_mode` (bool) *optional*
- `comment_ids` (Optional[List[int]]) *optional*

**Returns:** bool

##### _fetch_comment_tree

```python
def _fetch_comment_tree(self, manager, comment_ids: List[int], depth: int) -> List[dict]
```

Fetch comments from the HN Firebase API using concurrent workers.

Top-level comments are fetched in parallel using a thread pool.
Children are fetched recursively within each worker thread.
Display order is preserved by processing results in submission order.

Args:
    manager: EthicalScrapingManager instance
    comment_ids: List of comment IDs to fetch
    depth: Current nesting depth (0 = top-level)

Returns:
    Flat list of comment dicts in display order

**Parameters:**

- `self`
- `manager`
- `comment_ids` (List[int])
- `depth` (int)

**Returns:** List[dict]

⚠️ **High complexity:** 14

##### _clean_api_comment_html

```python
def _clean_api_comment_html(self, html: str) -> str
```

Convert HN API comment HTML to clean text with markdown links.

The Firebase API returns comment text as HTML-encoded content
(e.g. <p>tags, <a> links, <code> blocks). This method converts
it to plain text with markdown-style links, matching the output
format of the former HTML scraper.

Args:
    html: HTML string from the API's text field

Returns:
    Cleaned text with markdown links

**Parameters:**

- `self`
- `html` (str)

**Returns:** str

⚠️ **High complexity:** 12


## Functions

### _fetch_single

```python
def _fetch_single(cid, d)
```

Fetch one comment and its children. Thread-safe.

**Parameters:**

- `cid`
- `d`

