# core.html_generator

**File:** `Application/core/html_generator.py`

## Description

HTML Generator for Capcat - Static Site Generation
Creates self-contained HTML files from markdown content with embedded CSS and JavaScript.
Follows minimalist design principles with dark/light theme support using SVG icon toggle.

## Classes

### HTMLGenerator

Static HTML generator for Capcat archives.
Creates self-contained HTML files with embedded CSS and JavaScript.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### _setup_markdown_processor

```python
def _setup_markdown_processor(self)
```

Configure markdown processor with syntax highlighting and extensions.

**Parameters:**

- `self`

##### _get_embedded_css

```python
def _get_embedded_css(self, app_dir: Path) -> str
```

Read and embed CSS files into a single <style> tag with compiled design system.

Args:
    app_dir: Path to Application directory

Returns:
    HTML style tag with embedded CSS content including compiled design system

**Parameters:**

- `self`
- `app_dir` (Path)

**Returns:** str

##### _get_embedded_assets_for_template

```python
def _get_embedded_assets_for_template(self, app_dir: Path) -> dict
```

Read and embed CSS and JavaScript assets for template rendering with design system.

Args:
    app_dir: Path to Application directory

Returns:
    Dictionary containing embedded_styles and embedded_script

**Parameters:**

- `self`
- `app_dir` (Path)

**Returns:** dict

##### _get_base_template

```python
def _get_base_template(self, html_output_path: str = None, html_subfolder: bool = False) -> Template
```

Get the base HTML template with embedded CSS and JavaScript.
Returns a Template object that uses $variable syntax to avoid brace conflicts.

Args:
    html_output_path: Path where the HTML file will be saved
    html_subfolder: True if HTML is in html/ subfolder

**Parameters:**

- `self`
- `html_output_path` (str) *optional*
- `html_subfolder` (bool) *optional*

**Returns:** Template

##### generate_article_html

```python
def generate_article_html(self, markdown_path: str, article_title: str, breadcrumb_path: List[str], html_subfolder: bool = False, html_output_path: str = None) -> str
```

Generate HTML for an article from its markdown file.

Args:
    markdown_path: Path to the markdown file
    article_title: Title of the article
    breadcrumb_path: List of breadcrumb elements
    html_subfolder: True if HTML is in html/ subfolder (affects relative paths)
    html_output_path: Path where the HTML file will be saved (for dynamic CSS path calculation)

Returns:
    Generated HTML content

**Parameters:**

- `self`
- `markdown_path` (str)
- `article_title` (str)
- `breadcrumb_path` (List[str])
- `html_subfolder` (bool) *optional*
- `html_output_path` (str) *optional*

**Returns:** str

##### generate_article_html_from_template

```python
def generate_article_html_from_template(self, markdown_path: str, article_title: str, breadcrumb_path: List[str], source_config: Dict[str, Any], html_subfolder: bool = False, html_output_path: str = None, index_filename: str = 'news.html', is_single_article: bool = False) -> str
```

Generate HTML for an article using the template system.
This is the new, reliable template-based approach.

Args:
    markdown_path: Path to the markdown file
    article_title: Title of the article
    breadcrumb_path: List of breadcrumb elements
    source_config: Source configuration containing template metadata
    html_subfolder: True if HTML is in html/ subfolder

Returns:
    Generated HTML content

**Parameters:**

- `self`
- `markdown_path` (str)
- `article_title` (str)
- `breadcrumb_path` (List[str])
- `source_config` (Dict[str, Any])
- `html_subfolder` (bool) *optional*
- `html_output_path` (str) *optional*
- `index_filename` (str) *optional*
- `is_single_article` (bool) *optional*

**Returns:** str

##### _get_display_name_without_date

```python
def _get_display_name_without_date(self, name: str) -> str
```

Removes a date pattern (DD-MM-YYYY) from the end of a string.

**Parameters:**

- `self`
- `name` (str)

**Returns:** str

##### _get_article_title_from_markdown

```python
def _get_article_title_from_markdown(self, article_dir: Path) -> str
```

Extract article title from markdown file's H1 heading.
Falls back to folder name if extraction fails.

Args:
    article_dir: Path to article directory

Returns:
    Article title string

**Parameters:**

- `self`
- `article_dir` (Path)

**Returns:** str

⚠️ **High complexity:** 11

##### generate_directory_index

```python
def generate_directory_index(self, directory_path: str, title: str, breadcrumb_path: List[str]) -> str
```

Generate HTML index for a directory listing using template system.

Args:
    directory_path: Path to the directory
    title: Page title
    breadcrumb_path: List of breadcrumb elements

Returns:
    Generated HTML content

**Parameters:**

- `self`
- `directory_path` (str)
- `title` (str)
- `breadcrumb_path` (List[str])

**Returns:** str

##### _get_index_filename

```python
def _get_index_filename(self, levels_up: int, total_levels: int) -> str
```

Determine whether to use index.html (root) or news.html (directory).

**Parameters:**

- `self`
- `levels_up` (int)
- `total_levels` (int)

**Returns:** str

##### _generate_breadcrumb

```python
def _generate_breadcrumb(self, breadcrumb_path: List[str], html_subfolder: bool = False, current_file_path: str = None) -> str
```

Generate breadcrumb navigation HTML with proper directory-aware links.

**Parameters:**

- `self`
- `breadcrumb_path` (List[str])
- `html_subfolder` (bool) *optional*
- `current_file_path` (str) *optional*

**Returns:** str

⚠️ **High complexity:** 22

##### _generate_directory_listing

```python
def _generate_directory_listing(self, directory_path: str, is_root_level: bool = False) -> str
```

Generate HTML listing for directory contents with intelligent content detection.
Auto-discovers categories from source configurations.

**Parameters:**

- `self`
- `directory_path` (str)
- `is_root_level` (bool) *optional*

**Returns:** str

⚠️ **High complexity:** 48

##### _generate_index_navigation

```python
def _generate_index_navigation(self, current_path: str, show: bool = True, html_subfolder: bool = False) -> str
```

Generate index navigation HTML.

**Parameters:**

- `self`
- `current_path` (str)
- `show` (bool) *optional*
- `html_subfolder` (bool) *optional*

**Returns:** str

⚠️ **High complexity:** 22

##### _generate_global_index_navigation

```python
def _generate_global_index_navigation(self) -> str
```

Generate global index navigation HTML.

**Parameters:**

- `self`

**Returns:** str

##### _generate_comments_navigation

```python
def _generate_comments_navigation(self, current_article_path: str, html_subfolder: bool = False) -> str
```

Generate comments navigation HTML if comments exist.

**Parameters:**

- `self`
- `current_article_path` (str)
- `html_subfolder` (bool) *optional*

**Returns:** str

##### _create_navigation_container

```python
def _create_navigation_container(self, index_nav: str, comments_nav: str) -> str
```

Create a navigation container with both index and comments navigation.

**Parameters:**

- `self`
- `index_nav` (str)
- `comments_nav` (str)

**Returns:** str

##### _generate_article_navigation

```python
def _generate_article_navigation(self, markdown_path: str, html_subfolder: bool = False) -> Dict[str, str]
```

Generate navigation content for articles, including Back to News button.

Args:
    markdown_path: Path to the markdown file
    html_subfolder: True if HTML is in html/ subfolder

Returns:
    Dictionary with 'top' and 'bottom' navigation HTML

**Parameters:**

- `self`
- `markdown_path` (str)
- `html_subfolder` (bool) *optional*

**Returns:** Dict[str, str]

##### _clean_markdown_content

```python
def _clean_markdown_content(self, content: str) -> str
```

Clean up problematic content in markdown that could interfere with templates.

**Parameters:**

- `self`
- `content` (str)

**Returns:** str

##### _remove_grey_placeholder_images

```python
def _remove_grey_placeholder_images(self, html_content: str) -> str
```

Remove grey-placeholder images from HTML content.

**Parameters:**

- `self`
- `html_content` (str)

**Returns:** str

##### _remove_headerlink_anchors

```python
def _remove_headerlink_anchors(self, html_content: str) -> str
```

Remove headerlink anchor tags from HTML content.

**Parameters:**

- `self`
- `html_content` (str)

**Returns:** str

##### _remove_duplicate_h1_title

```python
def _remove_duplicate_h1_title(self, html_content: str, article_title: str) -> str
```

Remove duplicate H1 title from article content if it matches header title.

**Parameters:**

- `self`
- `html_content` (str)
- `article_title` (str)

**Returns:** str

##### _wrap_source_url_in_div

```python
def _wrap_source_url_in_div(self, html_content: str) -> str
```

Transform source/comments URL paragraphs into semantic div elements for better styling.

This function converts markdown-generated paragraph tags containing source URLs
and comments URLs into div elements with CSS class 'source-url' for consistent
styling across the application.

Args:
    html_content: HTML string from markdown conversion

Returns:
    HTML string with URL paragraphs converted to divs

Regex Pattern Explanation:
    - (<p[^>]*>): Captures opening <p> tag with any attributes
    - \s*: Matches optional whitespace
    - (<strong>(?:Source URL|Comments URL):</strong>\s*<a\s+href="[^"]*"[^>]*>[^<]*</a>):
      Captures the strong tag + link structure for both source and comments URLs
    - \s*: Matches optional whitespace
    - (</p>): Captures closing </p> tag

Transform: <p><strong>Source URL:</strong> <a href="...">...</a></p>
        → <div class="source-url"><strong>Source URL:</strong> <a href="...">...</a></div>

**Parameters:**

- `self`
- `html_content` (str)

**Returns:** str

##### _adjust_paths_for_subfolder

```python
def _adjust_paths_for_subfolder(self, html_content: str) -> str
```

Adjust relative paths in HTML content when HTML files are in html/ subfolder.

**Parameters:**

- `self`
- `html_content` (str)

**Returns:** str

##### _is_main_news_index

```python
def _is_main_news_index(self, directory_path: str) -> bool
```

Check if current directory is the main news index (news_DD-MM-YYYY or News_DD-MM-YYYY level).

**Parameters:**

- `self`
- `directory_path` (str)

**Returns:** bool

##### _is_news_source_directory

```python
def _is_news_source_directory(self, directory_name: str) -> bool
```

Check if directory is a news source directory (e.g., Hacker-News_DD-MM-YYYY, BBC-News_DD-MM-YYYY).

**Parameters:**

- `self`
- `directory_name` (str)

**Returns:** bool

##### _clean_title_for_display

```python
def _clean_title_for_display(self, title: str) -> str
```

Clean title for display by removing date stamps and replacing underscores.
Converts folder names like "IEEE_Spectrum_25-09-2025" to "IEEE Spectrum".

**Parameters:**

- `self`
- `title` (str)

**Returns:** str

##### _count_comments

```python
def _count_comments(self, comments_file_path: Path) -> int
```

Count the number of comments in a comments.md file.

**Parameters:**

- `self`
- `comments_file_path` (Path)

**Returns:** int

##### _format_date_for_h1_header

```python
def _format_date_for_h1_header(self, title: str) -> str
```

Format dates in titles specifically for h1 headers only.
Converts "InfoQ 11-09-2025" to "InfoQ 11 September 2025"
Only affects the date portion, leaves source names unchanged.

**Parameters:**

- `self`
- `title` (str)

**Returns:** str

##### _generate_error_page

```python
def _generate_error_page(self, error_message: str) -> str
```

Generate error page HTML.

**Parameters:**

- `self`
- `error_message` (str)

**Returns:** str


## Functions

### extract_source_id

```python
def extract_source_id(name)
```

Extract source ID from folder name.
Folder names use display_name (e.g., 'Hacker_News_19-10-2025')
Need to map back to source_id (e.g., 'hn')

**Parameters:**

- `name`

### find_category

```python
def find_category(source_id)
```

**Parameters:**

- `source_id`

### sort_items

```python
def sort_items(item)
```

**Parameters:**

- `item`

### extract_content

```python
def extract_content(html_content: str, div_class: str) -> str
```

**Parameters:**

- `html_content` (str)
- `div_class` (str)

**Returns:** str

### replace_source_url

```python
def replace_source_url(match)
```

**Parameters:**

- `match`

