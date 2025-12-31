# core.media_processor

**File:** `Application/core/media_processor.py`

## Description

Media processing component for Capcat.

Separates media discovery, download, and embedding operations from the
ArticleFetcher class to improve maintainability and testability.

## Classes

### MediaProcessor

Handles all media processing responsibilities: discovery, download, and embedding.

#### Methods

##### __init__

```python
def __init__(self, session: requests.Session, download_files: bool = False)
```

Initialize the media processor.

Args:
    session: HTTP session for making requests
    download_files: Whether to download all media types (not just images)

**Parameters:**

- `self`
- `session` (requests.Session)
- `download_files` (bool) *optional*

##### process_media

```python
def process_media(self, soup: BeautifulSoup, base_url: str, article_folder_path: str) -> str
```

Process all media in the content and return updated markdown content.

Args:
    soup: Parsed HTML soup object
    base_url: Base URL for resolving relative links
    article_folder_path: Path to save downloaded media files
    
Returns:
    Updated markdown content with media references

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `base_url` (str)
- `article_folder_path` (str)

**Returns:** str

##### _extract_media_links

```python
def _extract_media_links(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str, str]]
```

Extract all media links from the soup object.

Returns:
    List of tuples (link_type, url, alt_text)

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `base_url` (str)

**Returns:** List[Tuple[str, str, str]]

⚠️ **High complexity:** 43

##### _filter_media_links

```python
def _filter_media_links(self, all_links: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]
```

Filter media links based on type and extension.

Args:
    all_links: List of (link_type, url, alt_text) tuples
    
Returns:
    Filtered list of media links

**Parameters:**

- `self`
- `all_links` (List[Tuple[str, str, str]])

**Returns:** List[Tuple[str, str, str]]

⚠️ **High complexity:** 21

##### _process_media_links

```python
def _process_media_links(self, media_links: List[Tuple[str, str, str]], article_folder_path: str) -> Dict[str, str]
```

Process media links with concurrent downloading.

Args:
    media_links: List of (link_type, url, alt_text) tuples
    article_folder_path: Path to save downloaded files
    
Returns:
    Dictionary mapping original URLs to local file paths

**Parameters:**

- `self`
- `media_links` (List[Tuple[str, str, str]])
- `article_folder_path` (str)

**Returns:** Dict[str, str]

##### create_markdown_link_replacement

```python
def create_markdown_link_replacement(self, markdown_content: str, original_url: str, local_path: str, fallback_text: str, is_image: bool = False) -> str
```

Replace markdown link/image references with local paths.

Consolidates URL replacement logic. Handles both image and link
syntax with proper escaping to prevent f-string syntax errors.

Args:
    markdown_content: Markdown text to process
    original_url: URL to replace (will be escaped for regex)
    local_path: Local file path to use instead
    fallback_text: Text to use if link text is empty
    is_image: True for image syntax (!![]()), False for link syntax ([])

Returns:
    Updated markdown content with replaced URLs

Example:
    >>> content = "![](http://example.com/img.jpg)"
    >>> result = processor.create_markdown_link_replacement(
    ...     content, "http://example.com/img.jpg",
    ...     "images/img.jpg", "image", is_image=True
    ... )
    >>> print(result)
    ![image](images/img.jpg)

**Parameters:**

- `self`
- `markdown_content` (str)
- `original_url` (str)
- `local_path` (str)
- `fallback_text` (str)
- `is_image` (bool) *optional*

**Returns:** str

##### _replace_media_reference

```python
def _replace_media_reference(self, markdown_content: str, original_url: str, local_path: str) -> str
```

Replace a media reference in markdown content.

Args:
    markdown_content: Original markdown content
    original_url: The original media URL
    local_path: Path to the downloaded local file

Returns:
    Updated markdown content

**Parameters:**

- `self`
- `markdown_content` (str)
- `original_url` (str)
- `local_path` (str)

**Returns:** str

##### is_pdf_url

```python
def is_pdf_url(self, url: str) -> bool
```

Check if a URL points specifically to a PDF file.

Args:
    url: URL to check

Returns:
    True if URL points to a PDF file, False otherwise

Example:
    >>> processor.is_pdf_url("https://example.com/doc.pdf")
    True
    >>> processor.is_pdf_url("https://example.com/page.html")
    False

**Parameters:**

- `self`
- `url` (str)

**Returns:** bool

##### cleanup_empty_images_folder

```python
def cleanup_empty_images_folder(self, article_folder_path: str) -> None
```

Remove empty images folder if no images were downloaded.

Args:
    article_folder_path: Path to article folder

Example:
    >>> processor.cleanup_empty_images_folder("/path/to/article")
    # Removes /path/to/article/images if empty

**Parameters:**

- `self`
- `article_folder_path` (str)

**Returns:** None

##### should_skip_image

```python
def should_skip_image(self, img_tag, img_src: str, ui_patterns: dict) -> bool
```

Determine if an image should be skipped based on UI element patterns.

Filters out:
- UI icons (logos, avatars, buttons)
- Tracking pixels (1x1, analytics)
- Social media badges
- Advertisement placeholders

Args:
    img_tag: BeautifulSoup img tag
    img_src: Image source URL
    ui_patterns: Dictionary of patterns to match against
        - class_patterns: CSS class names to skip
        - id_patterns: Element ID patterns to skip
        - alt_patterns: Alt text patterns to skip
        - src_patterns: URL patterns to skip

Returns:
    True if image should be skipped (is likely a UI element)

Example:
    >>> ui_patterns = {
    ...     "class_patterns": ["icon", "logo"],
    ...     "id_patterns": ["avatar"],
    ...     "alt_patterns": ["badge"],
    ...     "src_patterns": ["pixel"]
    ... }
    >>> processor.should_skip_image(img_tag, "logo.png", ui_patterns)
    True

**Parameters:**

- `self`
- `img_tag`
- `img_src` (str)
- `ui_patterns` (dict)

**Returns:** bool

⚠️ **High complexity:** 11

##### cleanup_failed_media_reference

```python
def cleanup_failed_media_reference(self, markdown_content: str, url: str, link_type: str, alt_text: str) -> str
```

Clean up markdown references to failed media downloads.

Replaces failed media links with informative text indicating
the media is unavailable.

Args:
    markdown_content: Markdown text to clean
    url: Failed media URL
    link_type: Type of media (image, document, audio, video)
    alt_text: Alternative text for the media

Returns:
    Cleaned markdown with unavailable notice

Example:
    >>> content = "![Image](http://fail.com/img.jpg)"
    >>> result = processor.cleanup_failed_media_reference(
    ...     content, "http://fail.com/img.jpg", "image", "Photo"
    ... )
    >>> print(result)
    [Photo](http://fail.com/img.jpg) *(image unavailable)*

**Parameters:**

- `self`
- `markdown_content` (str)
- `url` (str)
- `link_type` (str)
- `alt_text` (str)

**Returns:** str

##### parse_srcset

```python
def parse_srcset(self, srcset: str) -> str
```

Parse srcset attribute and return the highest resolution image URL.

Args:
    srcset: HTML srcset attribute value

Returns:
    URL of highest resolution image

Example:
    >>> srcset = "img.jpg 1x, img@2x.jpg 2x, img@3x.jpg 3x"
    >>> processor.parse_srcset(srcset)
    'img@3x.jpg'

**Parameters:**

- `self`
- `srcset` (str)

**Returns:** str

##### remove_image_from_markdown

```python
def remove_image_from_markdown(self, markdown_content: str, image_src: str) -> str
```

Remove image references from markdown content when download fails.

Args:
    markdown_content: Markdown text to process
    image_src: Image source URL to remove

Returns:
    Markdown with image references removed

Example:
    >>> content = "Text\n![Image](http://example.com/img.jpg)\nMore"
    >>> result = processor.remove_image_from_markdown(
    ...     content, "http://example.com/img.jpg"
    ... )
    >>> "![Image]" not in result
    True

**Parameters:**

- `self`
- `markdown_content` (str)
- `image_src` (str)

**Returns:** str

##### process_document_links

```python
def process_document_links(self, soup: BeautifulSoup, markdown_content: str, article_folder_path: str, base_url: str) -> str
```

Process and download document files linked in the content.

Args:
    soup: BeautifulSoup parsed HTML
    markdown_content: Markdown content to update
    article_folder_path: Path to save downloaded documents
    base_url: Base URL for resolving relative links

Returns:
    Updated markdown content with local document paths

Example:
    >>> # Downloads PDFs and updates markdown links
    >>> updated_md = processor.process_document_links(
    ...     soup, markdown, "/path/to/article", "https://example.com"
    ... )

**Parameters:**

- `self`
- `soup` (BeautifulSoup)
- `markdown_content` (str)
- `article_folder_path` (str)
- `base_url` (str)

**Returns:** str

⚠️ **High complexity:** 14


## Functions

### process_single_media

```python
def process_single_media(link_info)
```

**Parameters:**

- `link_info`

### replacement_func

```python
def replacement_func(match)
```

Create replacement text with fallback for empty groups.

**Parameters:**

- `match`

### replace_if_image_link

```python
def replace_if_image_link(match)
```

**Parameters:**

- `match`

