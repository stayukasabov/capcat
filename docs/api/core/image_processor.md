# core.image_processor

**File:** `Application/core/image_processor.py`

## Description

Global Image Processor for Capcat.
Modular, DRY architecture with source-specific configurations.

## Classes

### ImageProcessor

Global image processing coordinator.
Uses source-specific configurations for clean, modular processing.

#### Methods

##### __init__

```python
def __init__(self, session: Optional[requests.Session] = None)
```

**Parameters:**

- `self`
- `session` (Optional[requests.Session]) *optional*

##### process_article_images

```python
def process_article_images(self, html_content: str, source_config: dict, base_url: str, output_folder: str, page_title: str = '', media_enabled: bool = False) -> Dict[str, str]
```

Process images for an article using source-specific configuration.
Includes intelligent protection against aggregator sites.

Args:
    html_content: Raw HTML content
    source_config: Source configuration with image processing rules
    base_url: Base URL for resolving relative links
    output_folder: Article output folder path
    page_title: Page title for classification
    media_enabled: Whether --media flag is enabled (affects limits)

Returns:
    Dict mapping original URLs to local filenames

**Parameters:**

- `self`
- `html_content` (str)
- `source_config` (dict)
- `base_url` (str)
- `output_folder` (str)
- `page_title` (str) *optional*
- `media_enabled` (bool) *optional*

**Returns:** Dict[str, str]

##### _extract_image_urls

```python
def _extract_image_urls(self, html_content: str, img_config: dict, base_url: str) -> List[str]
```

Extract image URLs using source-specific selectors.

**Parameters:**

- `self`
- `html_content` (str)
- `img_config` (dict)
- `base_url` (str)

**Returns:** List[str]

⚠️ **High complexity:** 13

##### _should_skip_image

```python
def _should_skip_image(self, img_element, skip_selectors: List[str]) -> bool
```

Check if image should be skipped based on skip selectors.

**Parameters:**

- `self`
- `img_element`
- `skip_selectors` (List[str])

**Returns:** bool

##### _matches_url_patterns

```python
def _matches_url_patterns(self, url: str, patterns: List[str]) -> bool
```

Check if URL matches any of the specified patterns.

**Parameters:**

- `self`
- `url` (str)
- `patterns` (List[str])

**Returns:** bool

##### _is_valid_image_url

```python
def _is_valid_image_url(self, url: str, allow_extensionless: bool = False) -> bool
```

Validate image URL.

**Parameters:**

- `self`
- `url` (str)
- `allow_extensionless` (bool) *optional*

**Returns:** bool

##### _download_images

```python
def _download_images(self, image_urls: List[str], output_folder: str, max_total_size_mb: int = 20, allow_large_files: bool = False) -> Dict[str, str]
```

Download images with size limits and return URL to filename mapping.

**Parameters:**

- `self`
- `image_urls` (List[str])
- `output_folder` (str)
- `max_total_size_mb` (int) *optional*
- `allow_large_files` (bool) *optional*

**Returns:** Dict[str, str]

##### _download_images_with_checking

```python
def _download_images_with_checking(self, image_urls: List[str], output_folder: str, media_enabled: bool = False, min_image_size: int = 0) -> Dict[str, str]
```

Download images with simple per-image checking and optional size filtering.

**Parameters:**

- `self`
- `image_urls` (List[str])
- `output_folder` (str)
- `media_enabled` (bool) *optional*
- `min_image_size` (int) *optional*

**Returns:** Dict[str, str]

##### _has_explicit_source_config

```python
def _has_explicit_source_config(self, source_config: Dict) -> bool
```

Check if source has explicit configuration (not a generic/discovered source).

**Parameters:**

- `self`
- `source_config` (Dict)

**Returns:** bool

##### _download_single_image_simple

```python
def _download_single_image_simple(self, url: str, images_dir: str, counter: int) -> Optional[str]
```

Download single image with simple error handling.

**Parameters:**

- `self`
- `url` (str)
- `images_dir` (str)
- `counter` (int)

**Returns:** Optional[str]

##### _download_single_image_with_min_size

```python
def _download_single_image_with_min_size(self, url: str, images_dir: str, counter: int, min_size: int) -> Optional[str]
```

Download single image with minimum size filtering.

**Parameters:**

- `self`
- `url` (str)
- `images_dir` (str)
- `counter` (int)
- `min_size` (int)

**Returns:** Optional[str]

##### _download_single_image_with_size_check

```python
def _download_single_image_with_size_check(self, url: str, images_dir: str, counter: int, remaining_bytes: int, allow_large_files: bool = False) -> Tuple[Optional[str], int]
```

Download single image with size checking and return (filename, size).

**Parameters:**

- `self`
- `url` (str)
- `images_dir` (str)
- `counter` (int)
- `remaining_bytes` (int)
- `allow_large_files` (bool) *optional*

**Returns:** Tuple[Optional[str], int]

##### _download_single_image

```python
def _download_single_image(self, url: str, images_dir: str, counter: int) -> Optional[str]
```

Download single image and return filename (legacy method).

**Parameters:**

- `self`
- `url` (str)
- `images_dir` (str)
- `counter` (int)

**Returns:** Optional[str]

##### _generate_filename

```python
def _generate_filename(self, url: str, content_type: Optional[str] = None) -> str
```

Generate clean filename from URL.

**Parameters:**

- `self`
- `url` (str)
- `content_type` (Optional[str]) *optional*

**Returns:** str

##### _get_extension_from_content_type

```python
def _get_extension_from_content_type(self, content_type: str) -> Optional[str]
```

Get file extension from content type.

**Parameters:**

- `self`
- `content_type` (str)

**Returns:** Optional[str]

##### _get_extension_from_url_or_content

```python
def _get_extension_from_url_or_content(self, url: str, content_type: Optional[str] = None) -> str
```

Get file extension from URL or content type, defaulting to .jpg.

**Parameters:**

- `self`
- `url` (str)
- `content_type` (Optional[str]) *optional*

**Returns:** str

##### replace_image_urls

```python
def replace_image_urls(markdown_content: str, url_mapping: Dict[str, str]) -> str
```

Clean URL replacement in markdown content.
DRY approach with systematic pattern matching.

**Parameters:**

- `markdown_content` (str)
- `url_mapping` (Dict[str, str])

**Returns:** str

##### _apply_url_patterns

```python
def _apply_url_patterns(content: str, original_url: str, local_path: str) -> str
```

Apply systematic URL replacement patterns.

**Parameters:**

- `content` (str)
- `original_url` (str)
- `local_path` (str)

**Returns:** str


## Functions

### get_image_processor

```python
def get_image_processor(session: Optional[requests.Session] = None) -> ImageProcessor
```

Get ImageProcessor instance.

**Parameters:**

- `session` (Optional[requests.Session]) *optional*

**Returns:** ImageProcessor

