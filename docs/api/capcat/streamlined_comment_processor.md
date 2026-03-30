# capcat.core.streamlined_comment_processor

**File:** `Application/capcat/core/streamlined_comment_processor.py`

## Description

Streamlined comment processor for optimizing nested structure handling and reducing conversion time.
Designed to flatten complex comment hierarchies and provide inline comment display.

## Classes

### StreamlinedCommentProcessor

Comment processor that extracts comments with optional nesting depth preservation.

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
def process_comments_flattened(self, soup: BeautifulSoup, comment_selector: str, user_selector: str = '.hnuser', comment_text_selector: str = '.comment', depth_fn: Optional[Callable[[Any], int]] = None) -> List[Dict[str, Any]]
```

Process comments preserving nesting depth.

Args:
    soup: BeautifulSoup object of the comments page
    comment_selector: CSS selector for comment elements
    user_selector: CSS selector for user information
    comment_text_selector: CSS selector for comment text
    depth_fn: Optional callable(element) -> int returning nesting depth.
              If None, all comments get level=0.

Returns:
    List of comment dicts with 'level' field reflecting nesting depth.

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `comment_selector` (str)
- `user_selector` (str) *optional*
- `comment_text_selector` (str) *optional*
- `depth_fn` (Optional[Callable[[Any], int]]) *optional*

**Returns:** List[Dict[str, Any]]

##### _extract_comment_data_fast

```python
def _extract_comment_data_fast(self, comment_elem, user_selector: str, comment_text_selector: str, index: int, depth_fn: Optional[Callable[[Any], int]] = None) -> Optional[Dict[str, Any]]
```

Fast comment data extraction without deep processing.

**Parameters:**

- `self`
- `comment_elem`
- `user_selector` (str)
- `comment_text_selector` (str)
- `index` (int)
- `depth_fn` (Optional[Callable[[Any], int]]) *optional*

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
def generate_inline_comments_markdown(self, comments: List[Dict[str, Any]], article_title: str, comment_url: str, article_folder_path: str = None) -> str
```

Generate inline comments markdown with flattened structure.

If article_folder_path is provided, prepends and appends a
← [[article_stem|Article]] wikilink for Obsidian graph connectivity.

**Parameters:**

- `self`
- `comments` (List[Dict[str, Any]])
- `article_title` (str)
- `comment_url` (str)
- `article_folder_path` (str) *optional*

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

