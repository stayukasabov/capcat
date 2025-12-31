# core.formatter

**File:** `Application/core/formatter.py`

## Description

HTML to Markdown converter for Capcat.
This module provides functionality to convert HTML content to clean Markdown format.

## Functions

### _normalize_url

```python
def _normalize_url(url: str) -> str
```

Normalize URL by properly handling encoding/decoding issues.

**Parameters:**

- `url` (str)

**Returns:** str

### _create_smart_link

```python
def _create_smart_link(text: str, url: str) -> str
```

Create a smart link that keeps functionality but has readable display text.

**Parameters:**

- `text` (str)
- `url` (str)

**Returns:** str

### format_comment_paragraphs

```python
def format_comment_paragraphs(comment_text: str) -> str
```

Format comment text with proper paragraph breaks and improved readability.
This is a global utility function for all news sources to improve comment formatting.

Args:
    comment_text: Raw comment text

Returns:
    Formatted comment text with proper paragraphs

**Parameters:**

- `comment_text` (str)

**Returns:** str

### html_to_markdown

```python
def html_to_markdown(html_content: str, base_url: str = None) -> str
```

Convert HTML content to clean markdown format.

**Parameters:**

- `html_content` (str)
- `base_url` (str) *optional*

**Returns:** str

### _parse_srcset

```python
def _parse_srcset(srcset: str) -> str
```

Parse srcset attribute and return the highest resolution image URL.

**Parameters:**

- `srcset` (str)

**Returns:** str

⚠️ **High complexity:** 13

### _process_images

```python
def _process_images(soup)
```

Process img tags to ensure proper Markdown syntax, filtering out broken images.

**Parameters:**

- `soup`

⚠️ **High complexity:** 13

### _is_broken_image_url

```python
def _is_broken_image_url(url: str) -> bool
```

Check if an image URL is likely to be broken or undownloadable.

**Parameters:**

- `url` (str)

**Returns:** bool

### _process_links

```python
def _process_links(soup)
```

Process a tags to ensure proper Markdown syntax.

**Parameters:**

- `soup`

⚠️ **High complexity:** 15

### _process_code_blocks

```python
def _process_code_blocks(soup)
```

Process pre and code tags to ensure proper Markdown code block formatting.

**Parameters:**

- `soup`

⚠️ **High complexity:** 17

### _process_media_elements

```python
def _process_media_elements(soup)
```

Process audio and video elements to preserve them in the output.

**Parameters:**

- `soup`

⚠️ **High complexity:** 42

### _convert_element

```python
def _convert_element(element, depth = 0, max_depth = 50) -> str
```

Recursively convert an HTML element to Markdown with improved formatting preservation.

**Parameters:**

- `element`
- `depth` *optional*
- `max_depth` *optional*

**Returns:** str

⚠️ **High complexity:** 44

### _process_list_items

```python
def _process_list_items(list_element, marker_type, depth, start_num = 1)
```

Process list items with improved formatting and nesting support.

**Parameters:**

- `list_element`
- `marker_type`
- `depth`
- `start_num` *optional*

⚠️ **High complexity:** 20

### _format_blockquote

```python
def _format_blockquote(content)
```

Format blockquote content with proper markdown quoting.

**Parameters:**

- `content`

### _convert_table_element

```python
def _convert_table_element(element, children_content)
```

Convert table elements to markdown table format.

**Parameters:**

- `element`
- `children_content`

### _enhanced_cleanup

```python
def _enhanced_cleanup(soup)
```

Enhanced cleanup for InfoQ and other sources.

**Parameters:**

- `soup`

⚠️ **High complexity:** 90

