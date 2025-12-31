# core.news_source_adapter

**File:** `Application/core/news_source_adapter.py`

## Description

Base NewsSourceAdapter class to eliminate code duplication across source modules.
Provides a configuration-driven approach for news source scraping.

## Classes

### NewsSourceAdapter

**Inherits from:** ABC

Base class for news source adapters.
Eliminates code duplication by providing common functionality.

#### Methods

##### __init__

```python
def __init__(self, source_config: Dict[str, Any])
```

Initialize with source-specific configuration.

**Parameters:**

- `self`
- `source_config` (Dict[str, Any])

##### _create_article_fetcher

```python
def _create_article_fetcher(self) -> 'NewsSourceArticleFetcher'
```

Create source-specific article fetcher.

**Parameters:**

- `self`

**Returns:** 'NewsSourceArticleFetcher'

##### scrape_articles

```python
def scrape_articles(self, count: int = 30) -> List[Tuple[str, str, Optional[str]]]
```

Scrape articles from the news source with comprehensive error handling.

Args:
    count: Number of articles to scrape

Returns:
    List of tuples containing (title, url, comment_url) for each article

Error Handling:
    - Network timeouts and connection errors
    - HTTP status errors (403, 404, 500, etc.)
    - HTML parsing errors
    - Graceful degradation for missing elements

**Parameters:**

- `self`
- `count` (int) *optional*

**Returns:** List[Tuple[str, str, Optional[str]]]

⚠️ **High complexity:** 19

##### _extract_article_from_element

```python
def _extract_article_from_element(self, element, processed_urls: set) -> Optional[Tuple[str, str, Optional[str]]]
```

Extract article information from HTML element.

**Parameters:**

- `self`
- `element`
- `processed_urls` (set)

**Returns:** Optional[Tuple[str, str, Optional[str]]]

##### _extract_title

```python
def _extract_title(self, element, link_elem) -> str
```

Extract article title from element.

**Parameters:**

- `self`
- `element`
- `link_elem`

**Returns:** str

##### _extract_comment_url

```python
def _extract_comment_url(self, element) -> Optional[str]
```

Extract comment URL from the article element for sources with comments.

**Parameters:**

- `self`
- `element`

**Returns:** Optional[str]

⚠️ **High complexity:** 25

##### _should_skip_url

```python
def _should_skip_url(self, url: str) -> bool
```

Check if URL should be skipped based on configuration.

**Parameters:**

- `self`
- `url` (str)

**Returns:** bool

##### fetch_article_content

```python
def fetch_article_content(self, title: str, url: str, index: int, base_folder: str, progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, str, str]
```

Fetch article content using the article fetcher.

**Parameters:**

- `self`
- `title` (str)
- `url` (str)
- `index` (int)
- `base_folder` (str)
- `progress_callback` (Optional[Callable[[float, str], None]]) *optional*

**Returns:** Tuple[bool, str, str]

##### process_article

```python
def process_article(self, title: str, url: str, index: int, base_folder: str, comment_url: str = None, download_files: bool = False, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool
```

Process a single article - unified interface for the optimized system.

Args:
    title: Article title
    url: Article URL
    index: Article index number
    base_folder: Base directory to save article
    comment_url: Optional comment URL for sources with comments
    download_files: Whether to download media files
    progress_callback: Optional callback for progress updates (progress, stage_description)

Returns:
    bool: True if article was processed successfully

**Parameters:**

- `self`
- `title` (str)
- `url` (str)
- `index` (int)
- `base_folder` (str)
- `comment_url` (str) *optional*
- `download_files` (bool) *optional*
- `progress_callback` (Optional[Callable[[float, str], None]]) *optional*

**Returns:** bool

##### _process_comments

```python
def _process_comments(self, comment_url: str, title: str, index: int, base_folder: str, article_folder_path: str) -> bool
```

Process comments for an article by delegating to source-specific implementation.

Args:
    comment_url: URL to fetch comments from
    title: Article title
    index: Article index number
    base_folder: Base directory
    article_folder_path: Path to the article folder

Returns:
    bool: True if comments were processed successfully

**Parameters:**

- `self`
- `comment_url` (str)
- `title` (str)
- `index` (int)
- `base_folder` (str)
- `article_folder_path` (str)

**Returns:** bool

##### _create_comment_placeholder

```python
def _create_comment_placeholder(self, title: str, article_folder_path: str) -> None
```

Create a placeholder comments.md file for sources without comment support.

**Parameters:**

- `self`
- `title` (str)
- `article_folder_path` (str)

**Returns:** None


### NewsSourceArticleFetcher

**Inherits from:** ArticleFetcher

Configurable article fetcher that works with any news source.

#### Methods

##### __init__

```python
def __init__(self, source_config: Dict[str, Any], session: requests.Session)
```

**Parameters:**

- `self`
- `source_config` (Dict[str, Any])
- `session` (requests.Session)

##### should_skip_url

```python
def should_skip_url(self, url: str, title: str) -> bool
```

Skip URLs based on source configuration.

**Parameters:**

- `self`
- `url` (str)
- `title` (str)

**Returns:** bool

##### _fetch_web_content

```python
def _fetch_web_content(self, title: str, url: str, index: int, base_folder: str, progress_callback = None)
```

Override to extract content using configured selectors.

**Parameters:**

- `self`
- `title` (str)
- `url` (str)
- `index` (int)
- `base_folder` (str)
- `progress_callback` *optional*

⚠️ **High complexity:** 67

##### _cleanup_empty_images_folder

```python
def _cleanup_empty_images_folder(self, article_folder_path: str) -> None
```

Remove images folder if it exists but is empty.

**Parameters:**

- `self`
- `article_folder_path` (str)

**Returns:** None

##### _fallback_image_detection

```python
def _fallback_image_detection(self, full_page_html: str, existing_images: set, article_folder_path: str, base_url: str)
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


