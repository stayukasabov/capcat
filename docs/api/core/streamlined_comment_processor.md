# core.streamlined_comment_processor

**File:** `Application/core/streamlined_comment_processor.py`

## Description

Streamlined comment processor for optimizing nested structure handling and reducing conversion time.
Designed to flatten complex comment hierarchies and provide inline comment display.

## Classes

### StreamlinedCommentProcessor

High-performance comment processor that flattens nested structures
and optimizes conversion time by eliminating complex tree traversal.

#### Methods

##### __init__

```python
def __init__(self, max_comments: int = 100, max_links_per_comment: int = 5)
```

**Parameters:**

- `self`
- `max_comments` (int) *optional*
- `max_links_per_comment` (int) *optional*

##### process_comments_flattened

```python
def process_comments_flattened(self, soup: BeautifulSoup, comment_selector: str, user_selector: str = '.hnuser', comment_text_selector: str = '.comment') -> List[Dict[str, Any]]
```

Process comments with flattened structure - no nested hierarchy processing.

Args:
    soup: BeautifulSoup object of the comments page
    comment_selector: CSS selector for comment elements
    user_selector: CSS selector for user information
    comment_text_selector: CSS selector for comment text

Returns:
    List of flattened comment dictionaries

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `comment_selector` (str)
- `user_selector` (str) *optional*
- `comment_text_selector` (str) *optional*

**Returns:** List[Dict[str, Any]]

##### _extract_comment_data_fast

```python
def _extract_comment_data_fast(self, comment_elem, user_selector: str, comment_text_selector: str, index: int) -> Optional[Dict[str, Any]]
```

Fast comment data extraction without deep processing.

**Parameters:**

- `self`
- `comment_elem`
- `user_selector` (str)
- `comment_text_selector` (str)
- `index` (int)

**Returns:** Optional[Dict[str, Any]]

##### _process_comment_text_streamlined

```python
def _process_comment_text_streamlined(self, comment_elem) -> str
```

Streamlined comment text processing with minimal link handling.

**Parameters:**

- `self`
- `comment_elem`

**Returns:** str

##### generate_inline_comments_markdown

```python
def generate_inline_comments_markdown(self, comments: List[Dict[str, Any]], article_title: str, comment_url: str) -> str
```

Generate inline comments markdown with flattened structure.

**Parameters:**

- `self`
- `comments` (List[Dict[str, Any]])
- `article_title` (str)
- `comment_url` (str)

**Returns:** str

##### generate_inline_comments_html

```python
def generate_inline_comments_html(self, comments: List[Dict[str, Any]], article_title: str, comment_url: str) -> str
```

Generate inline comments HTML directly, skipping markdown conversion.
Optimized for HTML post-processor performance.

**Parameters:**

- `self`
- `comments` (List[Dict[str, Any]])
- `article_title` (str)
- `comment_url` (str)

**Returns:** str

##### process_hacker_news_comments_optimized

```python
def process_hacker_news_comments_optimized(self, soup: BeautifulSoup, article_title: str, comment_url: str) -> str
```

Optimized HN comment processing with flattened structure.

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `article_title` (str)
- `comment_url` (str)

**Returns:** str

##### process_lobsters_comments_optimized

```python
def process_lobsters_comments_optimized(self, soup: BeautifulSoup, article_title: str, comment_url: str) -> str
```

Optimized Lobsters comment processing with flattened structure.

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `article_title` (str)
- `comment_url` (str)

**Returns:** str

##### process_lesswrong_comments_optimized

```python
def process_lesswrong_comments_optimized(self, soup: BeautifulSoup, article_title: str, comment_url: str) -> str
```

Optimized LessWrong comment processing with flattened structure.

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `article_title` (str)
- `comment_url` (str)

**Returns:** str

##### process_hacker_news_comments_html_optimized

```python
def process_hacker_news_comments_html_optimized(self, soup: BeautifulSoup, article_title: str, comment_url: str) -> str
```

Optimized HN comment processing with direct HTML generation.
Skips markdown conversion for HTML output.

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `article_title` (str)
- `comment_url` (str)

**Returns:** str

##### process_lobsters_comments_html_optimized

```python
def process_lobsters_comments_html_optimized(self, soup: BeautifulSoup, article_title: str, comment_url: str) -> str
```

Optimized Lobsters comment processing with direct HTML generation.
Skips markdown conversion for HTML output.

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `article_title` (str)
- `comment_url` (str)

**Returns:** str

##### get_performance_metrics

```python
def get_performance_metrics(self) -> Dict[str, Any]
```

Get performance metrics for monitoring.

**Parameters:**

- `self`

**Returns:** Dict[str, Any]


## Functions

### create_optimized_comment_processor

```python
def create_optimized_comment_processor(max_comments: int = 100) -> StreamlinedCommentProcessor
```

Factory function to create optimized comment processor.

Args:
    max_comments: Maximum number of comments to process

Returns:
    Configured StreamlinedCommentProcessor instance

**Parameters:**

- `max_comments` (int) *optional*

**Returns:** StreamlinedCommentProcessor

