# API Functions Exhaustive Reference

Complete documentation of EVERY public API function, method, class, and parameter in Capcat's codebase.

Source: Application/core/, Application/docs/api-reference.md

## Module Organization

### Core Modules

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Module</th>
      <th>Location</th>
      <th>Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>source_system</td>
      <td>core/source_system/</td>
      <td>Source registry, base classes, discovery</td>
    </tr>
    <tr>
      <td>article_fetcher</td>
      <td>core/article_fetcher.py</td>
      <td>Article content fetching</td>
    </tr>
    <tr>
      <td>media_processor</td>
      <td>core/media_processor.py</td>
      <td>Media download and processing</td>
    </tr>
    <tr>
      <td>formatter</td>
      <td>core/formatter.py</td>
      <td>HTML to Markdown conversion</td>
    </tr>
    <tr>
      <td>config</td>
      <td>core/config.py</td>
      <td>Configuration management</td>
    </tr>
    <tr>
      <td>logging_config</td>
      <td>core/logging_config.py</td>
      <td>Logging setup and configuration</td>
    </tr>
    <tr>
      <td>progress</td>
      <td>core/progress.py</td>
      <td>Progress tracking and display</td>
    </tr>
    <tr>
      <td>utils</td>
      <td>core/utils.py</td>
      <td>Utility functions</td>
    </tr>
    <tr>
      <td>downloader</td>
      <td>core/downloader.py</td>
      <td>File download operations</td>
    </tr>
    <tr>
      <td>retry</td>
      <td>core/retry.py</td>
      <td>Network retry logic</td>
    </tr>
    <tr>
      <td>rate_limiter</td>
      <td>core/rate_limiter.py</td>
      <td>Rate limiting</td>
    </tr>
  </tbody>
</table>
</div>

## Source System API

### SourceRegistry Class

Location: Application/core/source_system/source_registry.py:28

**Import:**
```python
from core.source_system.source_registry import SourceRegistry, get_source_registry
```

#### Constructor

**Signature:**
```python
def __init__(self, sources_dir: str = None)
```

**Parameters:**
- `sources_dir` (str, optional) - Path to sources directory
  - Default: Application/sources/active/
  - Must contain config_driven/ and custom/ subdirectories

**Returns:** SourceRegistry instance

**Example:**
```python
# Use default directory
registry = SourceRegistry()

# Use custom directory
registry = SourceRegistry("/custom/sources/path")
```

#### Methods

**discover_sources()**

**Signature:**
```python
def discover_sources(self) -> Dict[str, SourceConfig]
```

**Returns:** Dict[str, SourceConfig] - Source names mapped to configurations

**Raises:** SourceError - If discovery fails

**Behavior:**
1. Clears existing source data
2. Scans config_driven/configs/ for YAML/JSON files
3. Scans custom/ for Python source implementations
4. Validates all discovered sources
5. Returns dictionary of valid sources

**Example:**
```python
registry = SourceRegistry()
sources = registry.discover_sources()

print(f"Discovered {len(sources)} sources:")
for name, config in sources.items():
    print(f"  {name}: {config.display_name} ({config.category})")
```

**get_source()**

**Signature:**
```python
def get_source(self, source_name: str, session: requests.Session = None) -> BaseSource
```

**Parameters:**
- `source_name` (str, required) - Source identifier
- `session` (requests.Session, optional) - HTTP session for connection pooling

**Returns:** BaseSource - Instantiated source object

**Raises:** SourceError - If source not found or cannot be instantiated

**Caching:** Instances are cached for reuse

**Example:**
```python
registry = get_source_registry()

# Get source with default session
source = registry.get_source('hn')

# Get source with custom session
import requests
custom_session = requests.Session()
source = registry.get_source('bbc', session=custom_session)

# Use source
articles = source.discover_articles(count=10)
```

**get_available_sources()**

**Signature:**
```python
def get_available_sources(self) -> List[str]
```

**Returns:** List[str] - List of all source identifiers

**Auto-discovery:** Calls discover_sources() if not already loaded

**Example:**
```python
registry = get_source_registry()
sources = registry.get_available_sources()

print(f"Available sources ({len(sources)}):")
for source_id in sorted(sources):
    print(f"  - {source_id}")
```

**get_source_config()**

**Signature:**
```python
def get_source_config(self, source_name: str) -> Optional[SourceConfig]
```

**Parameters:**
- `source_name` (str, required) - Source identifier

**Returns:** Optional[SourceConfig] - Configuration or None if not found

**Example:**
```python
registry = get_source_registry()
config = registry.get_source_config('hn')

if config:
    print(f"Name: {config.display_name}")
    print(f"URL: {config.base_url}")
    print(f"Category: {config.category}")
    print(f"Timeout: {config.timeout}s")
else:
    print("Source not found")
```

**get_sources_by_category()**

**Signature:**
```python
def get_sources_by_category(self, category: str) -> List[str]
```

**Parameters:**
- `category` (str, required) - Category name (tech, news, science, ai, sports, etc.)

**Returns:** List[str] - Source identifiers in category

**Example:**
```python
registry = get_source_registry()

# Get all tech sources
tech_sources = registry.get_sources_by_category('tech')
print(f"Tech sources: {', '.join(tech_sources)}")

# Get all categories
categories = {}
for source_id in registry.get_available_sources():
    config = registry.get_source_config(source_id)
    if config.category not in categories:
        categories[config.category] = []
    categories[config.category].append(source_id)

for category, sources in sorted(categories.items()):
    print(f"{category}: {len(sources)} sources")
```

**validate_all_sources()**

**Signature:**
```python
def validate_all_sources(self, deep_validation: bool = False) -> Dict[str, List[str]]
```

**Parameters:**
- `deep_validation` (bool, optional) - Whether to perform network connectivity tests
  - False: Only validate configuration fields
  - True: Test network connectivity and article discovery

**Returns:** Dict[str, List[str]] - Source names mapped to error lists (empty list = valid)

**Example:**
```python
registry = get_source_registry()

# Basic validation only
errors = registry.validate_all_sources(deep_validation=False)

# Deep validation with network tests
errors = registry.validate_all_sources(deep_validation=True)

# Report errors
for source_name, error_list in errors.items():
    if error_list:
        print(f"{source_name}: FAILED")
        for error in error_list:
            print(f"  - {error}")
    else:
        print(f"{source_name}: OK")
```

### Global Registry Function

**get_source_registry()**

**Signature:**
```python
def get_source_registry() -> SourceRegistry
```

**Returns:** SourceRegistry - Global singleton registry instance

**Behavior:**
- Returns cached instance if exists
- Creates new instance and runs discovery on first call
- Thread-safe singleton pattern

**Example:**
```python
from core.source_system.source_registry import get_source_registry

# Get global registry
registry = get_source_registry()

# All calls return same instance
registry1 = get_source_registry()
registry2 = get_source_registry()
assert registry1 is registry2  # True
```

## BaseSource Abstract Class

Location: Application/core/source_system/base_source.py:78

**Import:**
```python
from core.source_system.base_source import BaseSource, SourceConfig, Article
```

### Constructor

**Signature:**
```python
def __init__(self, config: SourceConfig, session: requests.Session = None)
```

**Parameters:**
- `config` (SourceConfig, required) - Source configuration
- `session` (requests.Session, optional) - HTTP session

**Attributes Created:**
- `self.config` - SourceConfig instance
- `self.session` - requests.Session instance
- `self.logger` - Logger instance

### Abstract Properties

**source_type**

**Signature:**
```python
@property
@abstractmethod
def source_type(self) -> str
```

**Returns:** str - "config_driven" or "custom"

**Example Implementation:**
```python
@property
def source_type(self) -> str:
    return "custom"
```

### Abstract Methods

**discover_articles()**

**Signature:**
```python
@abstractmethod
def discover_articles(self, count: int) -> List[Article]
```

**Parameters:**
- `count` (int, required) - Maximum number of articles to discover

**Returns:** List[Article] - Article objects with title, url, optional metadata

**Raises:** SourceError - If discovery fails

**Example Implementation:**
```python
def discover_articles(self, count: int) -> List[Article]:
    response = self.session.get(self.config.base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    for link in soup.select('.article-link')[:count]:
        articles.append(Article(
            title=link.get_text(strip=True),
            url=self._resolve_url(link['href']),
            summary=link.get('aria-label', ''),
            tags=['general']
        ))

    self.logger.info(f"Discovered {len(articles)} articles")
    return articles
```

**fetch_article_content()**

**Signature:**
```python
@abstractmethod
def fetch_article_content(
    self,
    article: Article,
    output_dir: str,
    progress_callback: Callable = None
) -> Tuple[bool, Optional[str]]
```

**Parameters:**
- `article` (Article, required) - Article to fetch
- `output_dir` (str, required) - Directory to save content
- `progress_callback` (Callable, optional) - Progress update function

**Returns:** Tuple[bool, Optional[str]]
- (True, "/path/to/article") - Success
- (False, None) - Failure

**Raises:** SourceError - If fetch fails

**Example Implementation:**
```python
def fetch_article_content(
    self,
    article: Article,
    output_dir: str,
    progress_callback=None
) -> Tuple[bool, Optional[str]]:
    try:
        # Fetch content
        response = self.session.get(article.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract content
        content = soup.select_one('.article-content')
        if not content:
            self.logger.error(f"No content found for {article.url}")
            return False, None

        # Convert to markdown
        from core.formatter import html_to_markdown
        markdown = html_to_markdown(str(content), article.url)

        # Save to file
        os.makedirs(output_dir, exist_ok=True)
        article_path = os.path.join(output_dir, 'article.md')

        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(f"# {article.title}\n\n")
            f.write(f"URL: {article.url}\n\n")
            f.write(markdown)

        self.logger.info(f"Saved article to {article_path}")
        return True, article_path

    except Exception as e:
        self.logger.error(f"Failed to fetch article: {e}")
        return False, None
```

### Concrete Methods

**fetch_comments()**

**Signature:**
```python
def fetch_comments(
    self,
    article: Article,
    output_dir: str,
    progress_callback: Callable = None
) -> bool
```

**Parameters:**
- `article` (Article, required) - Article to fetch comments for
- `output_dir` (str, required) - Directory to save comments
- `progress_callback` (Callable, optional) - Progress update function

**Returns:** bool - True if comments fetched, False otherwise

**Behavior:**
- Returns False immediately if `supports_comments` is False
- Delegates to `_fetch_comments_impl()` if supported
- Optional method - not required for all sources

**Example Usage:**
```python
source = registry.get_source('hn')
article = Article(
    title="Example",
    url="https://news.ycombinator.com/item?id=12345",
    comment_url="https://news.ycombinator.com/item?id=12345"
)

success = source.fetch_comments(article, "/output/dir")
if success:
    print("Comments fetched successfully")
```

**validate_config()**

**Signature:**
```python
def validate_config(self) -> List[str]
```

**Returns:** List[str] - Validation error messages (empty = valid)

**Validation Checks:**
- Name not empty
- Display name not empty
- Base URL not empty and starts with http:// or https://
- Timeout > 0
- Rate limit >= 0

**Example:**
```python
source = registry.get_source('hn')
errors = source.validate_config()

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Configuration is valid")
```

## Data Classes

### SourceConfig

Location: Application/core/source_system/base_source.py:14

**Import:**
```python
from core.source_system.base_source import SourceConfig
```

**Constructor:**
```python
@dataclass
class SourceConfig:
    name: str
    display_name: str
    base_url: str
    timeout: float = 10.0
    rate_limit: float = 1.0
    supports_comments: bool = False
    has_comments: bool = False
    category: str = "general"
    custom_config: Dict[str, Any] = None
```

**Fields:**
- `name` (str, required) - Source identifier
- `display_name` (str, required) - Human-readable name
- `base_url` (str, required) - Base URL
- `timeout` (float, default=10.0) - Request timeout seconds
- `rate_limit` (float, default=1.0) - Minimum seconds between requests
- `supports_comments` (bool, default=False) - Comments support flag
- `has_comments` (bool, default=False) - Comments enabled flag
- `category` (str, default="general") - Category name
- `custom_config` (Dict, default=None) - Additional configuration

**Methods:**

**to_dict()**

**Signature:**
```python
def to_dict(self) -> Dict[str, Any]
```

**Returns:** Dict[str, Any] - Dictionary representation

**Example:**
```python
config = SourceConfig(
    name="example",
    display_name="Example News",
    base_url="https://example.com/",
    category="tech"
)

config_dict = config.to_dict()
print(config_dict)
# {
#   'name': 'example',
#   'display_name': 'Example News',
#   'base_url': 'https://example.com/',
#   'timeout': 10.0,
#   'rate_limit': 1.0,
#   'supports_comments': False,
#   'has_comments': False,
#   'category': 'tech'
# }
```

### Article

Location: Application/core/source_system/base_source.py:59

**Import:**
```python
from core.source_system.base_source import Article
```

**Constructor:**
```python
@dataclass
class Article:
    title: str
    url: str
    comment_url: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = None
```

**Fields:**
- `title` (str, required) - Article title
- `url` (str, required) - Article URL
- `comment_url` (Optional[str], default=None) - Comments URL
- `author` (Optional[str], default=None) - Author name
- `published_date` (Optional[str], default=None) - Publication date
- `summary` (Optional[str], default=None) - Article summary
- `tags` (List[str], default=None) - Article tags

**Example:**
```python
article = Article(
    title="Breaking News: AI Breakthrough",
    url="https://example.com/article/123",
    comment_url="https://example.com/article/123/comments",
    author="John Doe",
    published_date="2025-11-25",
    summary="Researchers announce major AI advancement...",
    tags=["ai", "tech", "research"]
)

print(f"{article.title} by {article.author}")
print(f"URL: {article.url}")
print(f"Tags: {', '.join(article.tags)}")
```

## ArticleFetcher API

Location: Application/core/article_fetcher.py:110

**Import:**
```python
from core.article_fetcher import ArticleFetcher, convert_html_with_timeout
```

### Global Functions

**convert_html_with_timeout()**

**Signature:**
```python
def convert_html_with_timeout(
    html_content: str,
    url: str,
    timeout: int = 30
) -> str
```

**Parameters:**
- `html_content` (str, required) - Raw HTML to convert
- `url` (str, required) - Source URL for logging
- `timeout` (int, default=30) - Maximum conversion time seconds

**Returns:** str - Converted Markdown content (empty string on error)

**Thread Safety:** Thread-safe, can be called concurrently

**Behavior:**
- Validates input (non-empty string)
- Executes conversion in isolated thread
- Times out after specified seconds
- Returns empty string on timeout or error
- Logs all failures

**Example:**
```python
from core.article_fetcher import convert_html_with_timeout

html = "<html><body><h1>Title</h1><p>Content</p></body></html>"
markdown = convert_html_with_timeout(html, "https://example.com")

print(markdown)
# # Title
#
# Content
```

**set_global_update_mode()**

**Signature:**
```python
def set_global_update_mode(update_mode: bool)
```

**Parameters:**
- `update_mode` (bool, required) - Enable/disable update mode

**Behavior:**
- Sets global flag for all ArticleFetcher instances
- Controls whether existing articles are overwritten

**Example:**
```python
from core.article_fetcher import set_global_update_mode

# Enable update mode
set_global_update_mode(True)

# Process articles (will overwrite existing)
# ...

# Disable update mode
set_global_update_mode(False)
```

**get_global_update_mode()**

**Signature:**
```python
def get_global_update_mode() -> bool
```

**Returns:** bool - Current update mode status

**Example:**
```python
from core.article_fetcher import get_global_update_mode

if get_global_update_mode():
    print("Update mode is enabled - will overwrite existing articles")
else:
    print("Update mode is disabled - will skip existing articles")
```

## Configuration API

Location: Application/core/config.py

**Import:**
```python
from core.config import get_config, load_config, FetchNewsConfig
from core.config import NetworkConfig, ProcessingConfig, LoggingConfig, UIConfig
```

### Global Functions

**get_config()**

**Signature:**
```python
def get_config() -> FetchNewsConfig
```

**Returns:** FetchNewsConfig - Global configuration instance

**Behavior:**
- Returns cached config if already loaded
- Creates new ConfigManager and loads config on first call
- Searches default config file locations
- Loads environment variables

**Example:**
```python
from core.config import get_config

config = get_config()
print(f"Max workers: {config.processing.max_workers}")
print(f"Timeout: {config.network.connect_timeout}s")
print(f"Log level: {config.logging.default_level}")
```

**load_config()**

**Signature:**
```python
def load_config(config_file: Optional[str] = None) -> FetchNewsConfig
```

**Parameters:**
- `config_file` (Optional[str], default=None) - Path to config file

**Returns:** FetchNewsConfig - Loaded configuration

**Behavior:**
- Loads from specified file or searches defaults
- Supports YAML and JSON formats
- Merges with environment variables
- Caches loaded config

**Example:**
```python
from core.config import load_config

# Load from default locations
config = load_config()

# Load from specific file
config = load_config("custom-config.yml")

# Access configuration
print(f"User agent: {config.network.user_agent}")
print(f"Download images: {config.processing.download_images}")
```

## Logging API

Location: Application/core/logging_config.py

**Import:**
```python
from core.logging_config import get_logger, setup_logging
```

### Functions

**get_logger()**

**Signature:**
```python
def get_logger(name: str = None) -> logging.Logger
```

**Parameters:**
- `name` (str, optional) - Logger name (defaults to caller's module name)

**Returns:** logging.Logger - Configured logger instance

**Example:**
```python
from core.logging_config import get_logger

# Get logger for current module
logger = get_logger(__name__)

# Use logger
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

**setup_logging()**

**Signature:**
```python
def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    use_colors: bool = True
) -> None
```

**Parameters:**
- `log_level` (str, default="INFO") - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file` (str, optional) - Path to log file
- `use_colors` (bool, default=True) - Enable colored console output

**Behavior:**
- Configures root logger
- Sets up console handler with optional colors
- Sets up file handler if log_file specified
- Formats with timestamps and module names

**Example:**
```python
from core.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(
    log_level="DEBUG",
    log_file="capcat.log",
    use_colors=True
)

# Use logger
logger = get_logger(__name__)
logger.debug("Logging is configured")
```

## Utility Functions API

Location: Application/core/utils.py

**Import:**
```python
from core.utils import (
    sanitize_filename,
    create_output_directory_capcat,
    resolve_url
)
```

### Functions

**sanitize_filename()**

**Signature:**
```python
def sanitize_filename(filename: str, max_length: int = 100) -> str
```

**Parameters:**
- `filename` (str, required) - Filename to sanitize
- `max_length` (int, default=100) - Maximum filename length

**Returns:** str - Sanitized filename

**Behavior:**
- Removes invalid filesystem characters
- Truncates to max_length
- Preserves file extension
- Replaces spaces with underscores

**Example:**
```python
from core.utils import sanitize_filename

# Sanitize filename
clean = sanitize_filename("My Article: Cool Stuff (2025).md")
print(clean)
# My_Article_Cool_Stuff_2025.md

# With length limit
short = sanitize_filename("Very Long Article Title That Exceeds Limit", max_length=20)
print(short)
# Very_Long_Article_...
```

**create_output_directory_capcat()**

**Signature:**
```python
def create_output_directory_capcat(
    base_dir: str,
    article_title: str,
    source_name: str = "",
    date_str: str = None
) -> str
```

**Parameters:**
- `base_dir` (str, required) - Base output directory
- `article_title` (str, required) - Article title
- `source_name` (str, default="") - Source identifier
- `date_str` (str, optional) - Date string (auto-generated if None)

**Returns:** str - Created directory path

**Behavior:**
- Creates date-based directory structure
- Sanitizes article title for folder name
- Creates numbered prefix for sorting
- Returns full path to article directory

**Example:**
```python
from core.utils import create_output_directory_capcat

output_dir = create_output_directory_capcat(
    base_dir="../News",
    article_title="Breaking News Article",
    source_name="bbc",
    date_str="25-11-2025"
)

print(output_dir)
# ../News/news_25-11-2025/BBC_25-11-2025/01_Breaking_News_Article/
```

## Source Code Locations

Core API modules:
- SourceRegistry - Application/core/source_system/source_registry.py:28
- BaseSource - Application/core/source_system/base_source.py:78
- SourceConfig - Application/core/source_system/base_source.py:14
- Article - Application/core/source_system/base_source.py:59
- ArticleFetcher - Application/core/article_fetcher.py:110
- FetchNewsConfig - Application/core/config.py:108
- get_logger - Application/core/logging_config.py

## Related Documentation

- CLI Commands: docs/tutorials/01-cli-commands-exhaustive.md
- Source System: docs/tutorials/04-source-system-exhaustive.md
- Configuration: docs/tutorials/03-configuration-exhaustive.md
- Source Development: docs/tutorials/06-source-development-exhaustive.md
