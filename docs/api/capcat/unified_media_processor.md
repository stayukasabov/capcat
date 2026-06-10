---
layout: default
render_with_liquid: false
---

# capcat.core.unified_media_processor

**File:** `Application/capcat/core/unified_media_processor.py`

## Description

Unified Media Processor Integration Layer.
Clean, DRY interface using modular ImageProcessor.

## Classes

### UnifiedMediaProcessor

Clean, DRY integration layer using modular ImageProcessor.

#### Methods

##### process_article_media

```python
def process_article_media(content: str, html_content: str, url: str, article_folder: str, source_name: str, session: requests.Session, media_enabled: bool = False, page_title: str = '') -> str
```

Process images using clean, modular architecture.

Args:
    content: Markdown content of the article
    html_content: Original HTML content
    url: Source URL of the article
    article_folder: Path to article folder
    source_name: Name of the news source
    session: HTTP session for downloading

Returns:
    Updated markdown content with local image references

**Parameters:**

- `content` (str)
- `html_content` (str)
- `url` (str)
- `article_folder` (str)
- `source_name` (str)
- `session` (requests.Session)
- `media_enabled` (bool) *optional*
- `page_title` (str) *optional*

**Returns:** str

##### _download_inline_images

```python
def _download_inline_images(content: str, article_folder: str, session: requests.Session, img_cfg: dict, max_image_bytes: int) -> str
```

Download images already referenced inline in markdown content.

Scans for ![alt](url) patterns, downloads each remote image, and
replaces the URL with a local path. This ensures images captured by
content selectors (e.g. Guardian, BBC) are downloaded even when
image_processing selectors find different URLs on the full page.

**Parameters:**

- `content` (str)
- `article_folder` (str)
- `session` (requests.Session)
- `img_cfg` (dict)
- `max_image_bytes` (int)

**Returns:** str

##### _replace_linked_image_urls

```python
def _replace_linked_image_urls(content: str) -> str
```

Replace web URLs in linked-image markdown with local image paths.

Pattern: [![alt](images/file.png)](https://web-url)
Becomes: [![alt](images/file.png)](images/file.png)

**Parameters:**

- `content` (str)

**Returns:** str

##### _insert_images_into_markdown

```python
def _insert_images_into_markdown(content: str, url_mapping: dict) -> str
```

Insert images into markdown content for config-driven sources.
Adds images at the end of content in a dedicated section.

**Parameters:**

- `content` (str)
- `url_mapping` (dict)

**Returns:** str

##### _load_source_config

```python
def _load_source_config(source_name: str) -> dict
```

Load source configuration from YAML file.

**Parameters:**

- `source_name` (str)

**Returns:** dict


## Functions

### replace_link

```python
def replace_link(match)
```

**Parameters:**

- `match`

### _resolve

```python
def _resolve(relative: str) -> str
```

**Parameters:**

- `relative` (str)

**Returns:** str

