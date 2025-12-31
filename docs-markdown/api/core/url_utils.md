# core.url_utils

**File:** `Application/core/url_utils.py`

## Description

URL validation and normalization utilities for Capcat.

Provides safe URL handling for user inputs and media processing.
Prevents common URL-related errors and security issues.

## Constants

### ALLOWED_SCHEMES

**Value:** `('http', 'https')`

### BLOCKED_SCHEMES

**Value:** `('file', 'ftp', 'data', 'javascript', 'mailto')`

## Classes

### URLValidator

URL validation utilities for user input and media processing.

Validates URLs to ensure they use safe schemes and proper formatting.
Prevents file:// and other potentially dangerous URL schemes.

#### Methods

##### validate_article_url

```python
def validate_article_url(cls, url: str) -> bool
```

Validate user-provided article URLs.

Args:
    url: URL to validate

Returns:
    True if valid

Raises:
    ValidationError: If URL is invalid or unsafe

Example:
    >>> URLValidator.validate_article_url(
    ...     "https://example.com/article"
    ... )
    True
    >>> URLValidator.validate_article_url("file:///etc/passwd")
    Traceback (most recent call last):
    ...
    ValidationError: Only HTTP/HTTPS URLs supported

**Parameters:**

- `cls`
- `url` (str)

**Returns:** bool

##### normalize_url

```python
def normalize_url(cls, url: str, base_url: str) -> Optional[str]
```

Normalize relative/protocol-relative URLs to absolute.

Handles common URL patterns safely:
- Protocol-relative: //example.com/image.jpg
- Absolute path: /images/photo.jpg
- Relative path: images/photo.jpg
- Already absolute: https://example.com/img.jpg
- Blocked: data:, javascript:, mailto:, file:

Args:
    url: URL to normalize
    base_url: Base URL for resolution

Returns:
    Normalized absolute URL, or None if blocked/invalid

Example:
    >>> URLValidator.normalize_url(
    ...     "//cdn.com/img.jpg",
    ...     "https://example.com"
    ... )
    'https://cdn.com/img.jpg'
    >>> URLValidator.normalize_url(
    ...     "/images/photo.jpg",
    ...     "https://example.com"
    ... )
    'https://example.com/images/photo.jpg'

**Parameters:**

- `cls`
- `url` (str)
- `base_url` (str)

**Returns:** Optional[str]

⚠️ **High complexity:** 11


### URLProcessor

Centralized URL processing for media extraction.

Handles batch processing of image and media URLs with normalization
and deduplication.

#### Methods

##### __init__

```python
def __init__(self, base_url: str)
```

Initialize with base URL for relative resolution.

Args:
    base_url: Base URL for resolving relative URLs

**Parameters:**

- `self`
- `base_url` (str)

##### process_image_urls

```python
def process_image_urls(self, image_elements: list, existing_images: set) -> list
```

Process image elements into normalized URL tuples.

Args:
    image_elements: BeautifulSoup img elements
    existing_images: Set of already processed image URLs (modified)

Returns:
    List of (type, normalized_url, alt_text) tuples

Example:
    >>> processor = URLProcessor("https://example.com")
    >>> imgs = [{'src': '/photo.jpg', 'alt': 'Photo'}]
    >>> processor.process_image_urls(imgs, set())
    [('image', 'https://example.com/photo.jpg', 'Photo')]

**Parameters:**

- `self`
- `image_elements` (list)
- `existing_images` (set)

**Returns:** list

##### process_media_urls

```python
def process_media_urls(self, media_elements: list, existing_media: set) -> list
```

Process video/audio elements into normalized URL tuples.

Args:
    media_elements: BeautifulSoup video/audio/source elements
    existing_media: Set of already processed media URLs (modified)

Returns:
    List of (type, normalized_url, description) tuples

Example:
    >>> processor = URLProcessor("https://example.com")
    >>> videos = [{'src': '/video.mp4', 'type': 'video/mp4'}]
    >>> processor.process_media_urls(videos, set())
    [('video', 'https://example.com/video.mp4', 'video/mp4')]

**Parameters:**

- `self`
- `media_elements` (list)
- `existing_media` (set)

**Returns:** list


