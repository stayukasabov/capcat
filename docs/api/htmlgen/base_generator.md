# htmlgen.base.base_generator

**File:** `Application/htmlgen/base/base_generator.py`

## Description

Base HTML Generator for Compartmentalized HTML Generation System.

This module provides the abstract base class and common functionality for all
source-specific HTML generators. It replaces the monolithic html_generator.py
with a modular, configuration-driven approach.

Architecture:
- BaseHTMLGenerator: Abstract base class with common functionality
- Source-specific generators inherit from this base
- Configuration-driven behavior via YAML files
- Template system with override capability
- Factory pattern for generator instantiation

## Constants

### JINJA2_AVAILABLE

**Value:** `True`

### JINJA2_AVAILABLE

**Value:** `False`

## Classes

### HTMLGeneratorError

**Inherits from:** Exception

Base exception for HTML generation errors.


### ConfigurationError

**Inherits from:** HTMLGeneratorError

Raised when configuration validation fails.


### TemplateError

**Inherits from:** HTMLGeneratorError

Raised when template processing fails.


### BaseHTMLGenerator

**Inherits from:** ABC

Abstract base class for source-specific HTML generators.

Provides common functionality and enforces the interface that all
source-specific generators must implement. This replaces the monolithic
html_generator.py with a modular, maintainable architecture.

Key Features:
- Configuration-driven behavior via YAML files
- Template system with source-specific overrides
- Common HTML processing utilities
- Abstract methods for source-specific logic
- Comprehensive error handling and logging

Design Patterns:
- Template Method: Base methods call abstract methods for customization
- Strategy: Different comment parsing strategies per source
- Factory: Dynamic generator instantiation based on source
- Configuration: YAML-driven behavior modification

#### Methods

##### __init__

```python
def __init__(self, source_id: str)
```

Initialize base HTML generator with source-specific configuration.

Args:
    source_id: Unique identifier for the source (e.g., 'hn', 'lesswrong')

Raises:
    ConfigurationError: If source configuration is invalid
    FileNotFoundError: If configuration files are missing

**Parameters:**

- `self`
- `source_id` (str)

##### _load_source_config

```python
def _load_source_config(self) -> Dict[str, Any]
```

Load source-specific configuration from YAML file.

Returns:
    Parsed configuration dictionary

Raises:
    FileNotFoundError: If config file doesn't exist
    yaml.YAMLError: If config file is invalid YAML
    ConfigurationError: If required fields are missing

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### _validate_configuration

```python
def _validate_configuration(self) -> None
```

Validate source configuration against schema.

Raises:
    ConfigurationError: If configuration is invalid

**Parameters:**

- `self`

**Returns:** None

##### _setup_markdown_processor

```python
def _setup_markdown_processor(self) -> markdown.Markdown
```

Configure markdown processor with source-specific extensions.

Returns:
    Configured markdown processor instance

**Parameters:**

- `self`

**Returns:** markdown.Markdown

##### _get_app_directory

```python
def _get_app_directory(self) -> Path
```

Get absolute path to Application directory for assets.

**Parameters:**

- `self`

**Returns:** Path

##### _load_template

```python
def _load_template(self, template_name: str) -> Template
```

Load and cache template with source-specific override support.

Args:
    template_name: Name of template (e.g., 'article.html', 'comments.html')

Returns:
    Compiled template object

Raises:
    TemplateError: If template file is not found or invalid

**Parameters:**

- `self`
- `template_name` (str)

**Returns:** Template

##### _resolve_template_path

```python
def _resolve_template_path(self, template_name: str) -> Path
```

Resolve template path with source-specific override support.

Template resolution order:
1. Source-specific template (htmlgen/source_id/templates/template_name)
2. Base template (htmlgen/base/templates/template_name)

Args:
    template_name: Name of template file

Returns:
    Path to template file

Raises:
    TemplateError: If template is not found

**Parameters:**

- `self`
- `template_name` (str)

**Returns:** Path

##### _get_template_context

```python
def _get_template_context(self) -> Dict[str, Any]
```

Build template context with common variables and source-specific data.

Args:
    **kwargs: Additional context variables

Returns:
    Complete template context dictionary

**Parameters:**

- `self`

**Returns:** Dict[str, Any]

##### count_comments

```python
def count_comments(self, comments_file: Path) -> int
```

Count comments using source-specific pattern.

Args:
    comments_file: Path to comments markdown file

Returns:
    Number of comments found

**Parameters:**

- `self`
- `comments_file` (Path)

**Returns:** int

##### should_show_comment_link

```python
def should_show_comment_link(self, comment_count: int) -> bool
```

Determine whether to show comment link based on source-specific rules.

Args:
    comment_count: Number of comments

Returns:
    True if comment link should be shown

**Parameters:**

- `self`
- `comment_count` (int)

**Returns:** bool

##### matches_directory_pattern

```python
def matches_directory_pattern(self, directory_name: str) -> bool
```

Check if directory name matches this source's patterns.

Args:
    directory_name: Name of directory to check

Returns:
    True if directory belongs to this source

**Parameters:**

- `self`
- `directory_name` (str)

**Returns:** bool

##### generate_breadcrumb

```python
def generate_breadcrumb(self, breadcrumb_path: List[str]) -> str
```

Generate breadcrumb navigation HTML with source-specific logic.

Args:
    breadcrumb_path: List of breadcrumb elements
    **kwargs: Additional context (html_subfolder, current_file_path, etc.)

Returns:
    Breadcrumb HTML string

**Parameters:**

- `self`
- `breadcrumb_path` (List[str])

**Returns:** str

##### clean_markdown_content

```python
def clean_markdown_content(self, content: str) -> str
```

Clean up problematic content in markdown that could interfere with templates.

**Parameters:**

- `self`
- `content` (str)

**Returns:** str

##### remove_grey_placeholder_images

```python
def remove_grey_placeholder_images(self, html_content: str) -> str
```

Remove grey-placeholder images from HTML content.

**Parameters:**

- `self`
- `html_content` (str)

**Returns:** str

##### remove_headerlink_anchors

```python
def remove_headerlink_anchors(self, html_content: str) -> str
```

Remove headerlink anchor tags from HTML content.

**Parameters:**

- `self`
- `html_content` (str)

**Returns:** str

##### remove_duplicate_h1_title

```python
def remove_duplicate_h1_title(self, html_content: str, article_title: str) -> str
```

Remove duplicate H1 title from article content if it matches header title.

**Parameters:**

- `self`
- `html_content` (str)
- `article_title` (str)

**Returns:** str

##### wrap_source_url_in_div

```python
def wrap_source_url_in_div(self, html_content: str) -> str
```

Transform source/comments URL paragraphs into semantic div elements.

**Parameters:**

- `self`
- `html_content` (str)

**Returns:** str

##### adjust_paths_for_subfolder

```python
def adjust_paths_for_subfolder(self, html_content: str) -> str
```

Adjust relative paths in HTML content when HTML files are in html/ subfolder.

**Parameters:**

- `self`
- `html_content` (str)

**Returns:** str

##### clean_title_for_display

```python
def clean_title_for_display(self, title: str) -> str
```

Clean title for display by removing underscores, dashes, and formatting.

**Parameters:**

- `self`
- `title` (str)

**Returns:** str

##### format_date_for_header

```python
def format_date_for_header(self, title: str) -> str
```

Format dates in titles specifically for h1 headers.

**Parameters:**

- `self`
- `title` (str)

**Returns:** str

##### generate_error_page

```python
def generate_error_page(self, error_message: str) -> str
```

Generate error page HTML using source template.

**Parameters:**

- `self`
- `error_message` (str)

**Returns:** str


### HTMLGeneratorFactory

Factory for creating source-specific HTML generators.

Implements the Factory pattern to dynamically instantiate the correct
generator based on source identifier. This decouples the main system
from knowing about specific generator implementations.

#### Methods

##### register_generator

```python
def register_generator(cls, source_id: str, generator_class: type) -> None
```

Register a generator class for a source.

Args:
    source_id: Unique source identifier
    generator_class: Generator class that inherits from BaseHTMLGenerator

**Parameters:**

- `cls`
- `source_id` (str)
- `generator_class` (type)

**Returns:** None

##### create_generator

```python
def create_generator(cls, source_id: str) -> BaseHTMLGenerator
```

Create generator instance for the specified source.

Args:
    source_id: Source identifier to create generator for

Returns:
    Source-specific HTML generator instance

Raises:
    ValueError: If source is not registered

**Parameters:**

- `cls`
- `source_id` (str)

**Returns:** BaseHTMLGenerator

##### get_available_sources

```python
def get_available_sources(cls) -> List[str]
```

Get list of all registered source identifiers.

Returns:
    List of available source IDs

**Parameters:**

- `cls`

**Returns:** List[str]

##### detect_source_from_directory

```python
def detect_source_from_directory(cls, directory_name: str) -> Optional[str]
```

Detect source from directory name using all registered generators.

Args:
    directory_name: Name of directory to identify

Returns:
    Source ID if match found, None otherwise

**Parameters:**

- `cls`
- `directory_name` (str)

**Returns:** Optional[str]


### Template

#### Methods

##### __init__

```python
def __init__(self, template_string)
```

**Parameters:**

- `self`
- `template_string`

##### render

```python
def render(self)
```

**Parameters:**

- `self`


## Functions

### replace_source_url

```python
def replace_source_url(match)
```

**Parameters:**

- `match`

