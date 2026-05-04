---
layout: default
render_with_liquid: false
---

# capcat.htmlgen.generator

**File:** `Application/capcat/htmlgen/generator.py`

## Description

HTML Generator for Capcat - Static Site Generation
Creates self-contained HTML files from markdown content with embedded CSS and JavaScript.
Follows minimalist design principles with dark/light theme support using SVG icon toggle.

## Constants

### _MAX_URL_DISPLAY

**Value:** `80`

## Classes

### ArticleHTMLGenerator

Static HTML generator for Capcat archives.
Creates self-contained HTML files with embedded CSS and JavaScript.

#### Methods

##### __init__

```python
def __init__(self)
```

Initialize the HTML generator with config, markdown, and template dependencies.

**Parameters:**

- `self`

##### _resolve_user_themes_dir

```python
def _resolve_user_themes_dir(self) -> 'Path | None'
```

Return Config/themes/ path if it exists in the project root, else None.

**Parameters:**

- `self`

**Returns:** 'Path | None'

##### _resolve_base_css_path

```python
def _resolve_base_css_path(self, app_dir: 'Path') -> 'Path'
```

Return the base.css path, preferring Config/themes/ over the package copy.

**Parameters:**

- `self`
- `app_dir` ('Path')

**Returns:** 'Path'

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

⚠️ **High complexity:** 14

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

Generate breadcrumb navigation HTML.

Renders 1–3 links depending on page type:
  news.html  (source dir)      → date only (1 link)
  article.html                 → date + source (2 links)
  html/article.html            → date + source (2 links)
  html/comments.html           → date + source + article (3 links)

Display format:
  Level 0 (date):    "News 15 March 2026"
  Level 1 (source):  "Hacker News"
  Level 2 (article): article title as-is

Depths are fixed by physical directory structure, not breadcrumb length.

**Parameters:**

- `self`
- `breadcrumb_path` (List[str])
- `html_subfolder` (bool) *optional*
- `current_file_path` (str) *optional*

**Returns:** str

⚠️ **High complexity:** 16

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

⚠️ **High complexity:** 49

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

##### _remove_image_anchor_wrappers

```python
def _remove_image_anchor_wrappers(self, html_content: str) -> str
```

Remove anchor tags that wrap image tags.

Substack and other sources download images locally but markdown-to-HTML
conversion wraps them in <a href> linking to original URL. This removes
those anchor wrappers while preserving the image tags and their attributes.

Args:
    html_content: HTML content to process

Returns:
    HTML with image anchor wrappers removed

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

##### _extract_viewbox

```python
def _extract_viewbox(self, el) -> 'tuple[float, float] | None'
```

Extract (width, height) from a BeautifulSoup SVG/img element, or None.

**Parameters:**

- `self`
- `el`

**Returns:** 'tuple[float, float] | None'

⚠️ **High complexity:** 15

##### _score_svg_element

```python
def _score_svg_element(self, el, soup) -> 'tuple[int, int]'
```

Return (icon_score, illustration_score) for a BeautifulSoup element.

**Parameters:**

- `self`
- `el`
- `soup`

**Returns:** 'tuple[int, int]'

⚠️ **High complexity:** 23

##### _classify_svg_elements

```python
def _classify_svg_elements(self, html_content: str) -> str
```

Classify <img src="*.svg"> and inline <svg> elements as icons or
illustrations using weighted heuristics. Appends class 'capcat-icon'
to elements classified as icons. Uses html.parser (no extra deps).

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
Folder names use display_name (e.g., 'Hacker-News_19-10-2025')
Need to map back to source_id (e.g., 'hn')

**Parameters:**

- `name`

### find_category

```python
def find_category(source_id)
```

Return the category name for a source ID, or None if unknown.

Args:
    source_id: Source identifier string to look up.

Returns:
    Category string (e.g. ``"tech"``), or ``None`` if not found.

**Parameters:**

- `source_id`

### sort_items

```python
def sort_items(item)
```

Return a sort key for a directory entry based on category order.

Args:
    item: A ``pathlib.Path``-like directory entry with a ``name``
        attribute.

Returns:
    Tuple used as a sort key: ``(category_index, source_order, name)``.

**Parameters:**

- `item`

### extract_content

```python
def extract_content(html_content: str, div_class: str) -> str
```

Extract the inner HTML from a known div wrapper, if present.

Args:
    html_content: HTML string that may contain a ``<div class="…">``
        wrapper.
    div_class: CSS class name of the wrapper div to strip.

Returns:
    Inner content string with the outer div removed, or the original
    *html_content* if the wrapper is not found.

**Parameters:**

- `html_content` (str)
- `div_class` (str)

**Returns:** str

### _truncate_anchor_text

```python
def _truncate_anchor_text(anchor_match)
```

Shorten anchor display text to ``_MAX_URL_DISPLAY`` characters.

Args:
    anchor_match: Regex match with groups ``(href, text)``.

Returns:
    Replacement ``<a>`` tag with truncated display text.

**Parameters:**

- `anchor_match`

### replace_source_url

```python
def replace_source_url(match)
```

Replace a ``<p>`` containing a source URL with a semantic div.

Args:
    match: Regex match with groups ``(p_open, content, p_close)``.

Returns:
    ``<div class="source-url">`` wrapping the (possibly truncated)
    anchor content.

**Parameters:**

- `match`

