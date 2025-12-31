# htmlgen.lesswrong.generator

**File:** `Application/htmlgen/lesswrong/generator.py`

## Description

LessWrong specific HTML generator implementation.

This module implements the source-specific HTML generation logic for LessWrong,
inheriting from BaseHTMLGenerator and providing LessWrong-specific customizations.

Key Features:
- LessWrong-specific comment pattern recognition (HTML format)
- Conditional comment display (only show when comments exist)
- Academic breadcrumb navigation style
- AI/rationality-focused CSS styling
- Enhanced content cleaning for LessWrong UI elements

## Classes

### LessWrongGenerator

**Inherits from:** BaseHTMLGenerator

LessWrong specific HTML generator.

Implements LessWrong-specific behavior:
- Comment pattern: **username** (<a href="...">profile</a>)
- Conditional comment links (only when comments exist)
- Academic navigation style for rationality content
- AI/rationality-focused styling
- Enhanced content cleaning

#### Methods

##### count_comments

```python
def count_comments(self, comments_file: Path) -> int
```

Count LessWrong comments using HTML profile pattern.

LessWrong comments follow this pattern in HTML:
**username** (<a href="https://www.lesswrong.com/users/username">profile</a>)

Args:
    comments_file: Path to comments markdown file

Returns:
    Number of LessWrong comments found

**Parameters:**

- `self`
- `comments_file` (Path)

**Returns:** int

##### should_show_comment_link

```python
def should_show_comment_link(self, comment_count: int) -> bool
```

LessWrong only shows comment links when comments exist.

Args:
    comment_count: Number of comments

Returns:
    True if comment link should be shown (LessWrong: only when count > 0)

**Parameters:**

- `self`
- `comment_count` (int)

**Returns:** bool

##### matches_directory_pattern

```python
def matches_directory_pattern(self, directory_name: str) -> bool
```

Check if directory matches LessWrong patterns.

LessWrong supports these naming conventions:
- lesswrong (lowercase)
- LessWrong (camelCase)

Args:
    directory_name: Directory name to check

Returns:
    True if directory belongs to LessWrong

**Parameters:**

- `self`
- `directory_name` (str)

**Returns:** bool

##### generate_breadcrumb

```python
def generate_breadcrumb(self, breadcrumb_path: List[str]) -> str
```

Generate LessWrong-specific breadcrumb navigation.

LessWrong uses academic breadcrumb style with:
- Simplified navigation for comments pages
- Academic styling appropriate for rationality content
- Enhanced readability for long-form content

Args:
    breadcrumb_path: List of breadcrumb elements
    **kwargs: Additional context

Returns:
    LessWrong-styled breadcrumb HTML

**Parameters:**

- `self`
- `breadcrumb_path` (List[str])

**Returns:** str

##### _generate_breadcrumb_link

```python
def _generate_breadcrumb_link(self, breadcrumb_path: List[str], index: int, html_subfolder: bool, is_comments_page: bool) -> str
```

Generate appropriate breadcrumb link for LessWrong academic navigation.

Args:
    breadcrumb_path: Full breadcrumb path
    index: Current item index
    html_subfolder: Whether HTML is in subfolder
    is_comments_page: Whether current page is comments

Returns:
    Appropriate href for the breadcrumb item

**Parameters:**

- `self`
- `breadcrumb_path` (List[str])
- `index` (int)
- `html_subfolder` (bool)
- `is_comments_page` (bool)

**Returns:** str

⚠️ **High complexity:** 12

##### clean_lesswrong_content

```python
def clean_lesswrong_content(self, content: str) -> str
```

Enhanced content cleaning for LessWrong-specific UI elements.

LessWrong articles often contain UI elements that need cleaning:
- User interaction elements (voting, timestamps)
- Navigation elements
- Site-specific formatting

Args:
    content: Raw content to clean

Returns:
    Cleaned content suitable for archival display

**Parameters:**

- `self`
- `content` (str)

**Returns:** str

##### generate_article_page

```python
def generate_article_page(self, markdown_path: str, article_title: str, breadcrumb_path: List[str], html_subfolder: bool = False) -> str
```

Generate LessWrong-style article page with academic formatting.

Args:
    markdown_path: Path to article markdown
    article_title: Article title
    breadcrumb_path: Breadcrumb path
    html_subfolder: Whether HTML is in subfolder

Returns:
    Generated HTML for LessWrong article page

**Parameters:**

- `self`
- `markdown_path` (str)
- `article_title` (str)
- `breadcrumb_path` (List[str])
- `html_subfolder` (bool) *optional*

**Returns:** str

##### _generate_lesswrong_navigation

```python
def _generate_lesswrong_navigation(self, current_path: str, html_subfolder: bool) -> dict
```

Generate LessWrong-specific navigation with academic styling.

Args:
    current_path: Current file path
    html_subfolder: Whether in HTML subfolder

Returns:
    Navigation context dictionary

**Parameters:**

- `self`
- `current_path` (str)
- `html_subfolder` (bool)

**Returns:** dict

##### _generate_index_navigation

```python
def _generate_index_navigation(self, current_path: str, html_subfolder: bool) -> str
```

Generate back to news navigation for LessWrong with academic styling.

**Parameters:**

- `self`
- `current_path` (str)
- `html_subfolder` (bool)

**Returns:** str

##### _generate_comments_navigation

```python
def _generate_comments_navigation(self, current_path: str, html_subfolder: bool) -> str
```

Generate comments navigation for LessWrong with conditional display.

**Parameters:**

- `self`
- `current_path` (str)
- `html_subfolder` (bool)

**Returns:** str

##### generate_comments_page

```python
def generate_comments_page(self, comments_path: str, article_title: str, breadcrumb_path: List[str], html_subfolder: bool = False) -> str
```

Generate LessWrong-style comments page with enhanced comment display.

Args:
    comments_path: Path to comments markdown
    article_title: Article title
    breadcrumb_path: Breadcrumb path
    html_subfolder: Whether HTML is in subfolder

Returns:
    Generated HTML for LessWrong comments page

**Parameters:**

- `self`
- `comments_path` (str)
- `article_title` (str)
- `breadcrumb_path` (List[str])
- `html_subfolder` (bool) *optional*

**Returns:** str


