# API Reference

Complete API documentation for Capcat's hybrid architecture components.

## Core Components

### SourceRegistry

Central registry for source discovery and management.

```python
from core.source_system.source_registry import get_source_registry, SourceRegistry
```

#### Class: SourceRegistry

##### `__init__(sources_dir: str = None)`
Initialize the source registry.

**Parameters:**
- `sources_dir` (str, optional): Path to sources directory. Defaults to `sources/active/`

**Example:**
```python
registry = SourceRegistry()
# or
registry = SourceRegistry("/custom/sources/path")
```

##### `discover_sources() -> Dict[str, SourceConfig]`
Discover all available sources (config-driven and custom).

**Returns:**
- `Dict[str, SourceConfig]`: Mapping of source names to configurations

**Raises:**
- `SourceError`: If source discovery fails

**Example:**
```python
sources = registry.discover_sources()
print(f"Discovered {len(sources)} sources")
for name, config in sources.items():
    print(f"- {name}: {config.display_name}")
```

##### `get_source(source_name: str, session=None) -> BaseSource`
Get a source instance by name.

**Parameters:**
- `source_name` (str): Name of the source
- `session` (requests.Session, optional): HTTP session to use

**Returns:**
- `BaseSource`: Source instance

**Raises:**
- `SourceError`: If source not found or cannot be instantiated

**Example:**
```python
source = registry.get_source('hn')
articles = source.get_articles(count=10)
```

##### `get_available_sources() -> List[str]`
Get list of available source names.

**Returns:**
- `List[str]`: List of source names

**Example:**
```python
available = registry.get_available_sources()
print(f"Available sources: {', '.join(available)}")
```

##### `validate_all_sources(deep_validation: bool = False) -> Dict[str, List[str]]`
Validate all registered sources.

**Parameters:**
- `deep_validation` (bool): Whether to perform network tests

**Returns:**
- `Dict[str, List[str]]`: Source names mapped to validation errors

**Example:**
```python
errors = registry.validate_all_sources(deep_validation=True)
for source, error_list in errors.items():
    if error_list:
        print(f"{source}: {error_list}")
```

#### Function: get_source_registry()
Get the global source registry instance.

**Returns:**
- `SourceRegistry`: Global registry instance

**Example:**
```python
registry = get_source_registry()
sources = registry.get_available_sources()
```

---

### BaseSource

Abstract base class for all source implementations.

```python
from core.source_system.base_source import BaseSource, SourceConfig
```

#### Class: BaseSource

##### `__init__(config: SourceConfig, session=None)`
Initialize the base source.

**Parameters:**
- `config` (SourceConfig): Source configuration
- `session` (requests.Session, optional): HTTP session

**Example:**
```python
class CustomSource(BaseSource):
    def __init__(self, config: SourceConfig, session=None):
        super().__init__(config, session)
```

##### `get_articles(count: int = 30) -> List[Dict]`
**Abstract method** - Get articles from the source.

**Parameters:**
- `count` (int): Number of articles to fetch

**Returns:**
- `List[Dict]`: Articles with keys: `title`, `url`, `summary`

**Example Implementation:**
```python
def get_articles(self, count: int = 30) -> List[Dict]:
    response = self.session.get(self.config.base_url)
    soup = self._get_soup(response.text)

    articles = []
    for elem in soup.select('.article-link'):
        articles.append({
            'title': elem.get_text(strip=True),
            'url': self._resolve_url(elem['href']),
            'summary': ''
        })

    return articles[:count]
```

##### `get_article_content(url: str) -> Optional[str]`
Get full content for a specific article.

**Parameters:**
- `url` (str): Article URL

**Returns:**
- `Optional[str]`: Article content as HTML

**Example Implementation:**
```python
def get_article_content(self, url: str) -> Optional[str]:
    response = self.session.get(url)
    soup = self._get_soup(response.text)

    content = soup.select_one('.article-content')
    return str(content) if content else None
```

##### `get_comments(url: str) -> List[Dict]`
Get comments for an article.

**Parameters:**
- `url` (str): Article URL

**Returns:**
- `List[Dict]`: Comments with keys: `author`, `text`, `timestamp`

**Example Implementation:**
```python
def get_comments(self, url: str) -> List[Dict]:
    if not self.config.supports_comments:
        return []

    response = self.session.get(url)
    soup = self._get_soup(response.text)

    comments = []
    for elem in soup.select('.comment'):
        comments.append({
            'author': elem.select_one('.author').get_text(strip=True),
            'text': elem.select_one('.text').get_text(strip=True),
            'timestamp': elem.select_one('.timestamp').get('datetime')
        })

    return comments
```

##### `validate_config() -> List[str]`
Validate source-specific configuration.

**Returns:**
- `List[str]`: List of validation errors

**Example Implementation:**
```python
def validate_config(self) -> List[str]:
    errors = []

    if not self.config.base_url:
        errors.append("base_url is required")

    if not self.config.base_url.startswith('https://'):
        errors.append("base_url must use HTTPS")

    return errors
```

##### Utility Methods

###### `_get_soup(html: str) -> BeautifulSoup`
Parse HTML content.

**Parameters:**
- `html` (str): HTML content

**Returns:**
- `BeautifulSoup`: Parsed HTML

###### `_resolve_url(url: str) -> str`
Resolve relative URLs to absolute URLs.

**Parameters:**
- `url` (str): Relative or absolute URL

**Returns:**
- `str`: Absolute URL

###### `_clean_text(text: str) -> str`
Clean and normalize text content.

**Parameters:**
- `text` (str): Raw text

**Returns:**
- `str`: Cleaned text

---

### SourceConfig

Configuration data class for sources.

```python
from core.source_system.base_source import SourceConfig
```

#### Class: SourceConfig

##### `__init__(...)`
Initialize source configuration.

**Parameters:**
- `name` (str): Source name
- `display_name` (str): Human-readable display name
- `base_url` (str): Base URL for the source
- `timeout` (float): Request timeout in seconds
- `rate_limit` (float): Minimum seconds between requests
- `supports_comments` (bool): Whether source supports comments
- `category` (str): Source category
- `custom_config` (Dict): Additional configuration

**Example:**
```python
config = SourceConfig(
    name="example",
    display_name="Example News",
    base_url="https://example.com/",
    timeout=10.0,
    rate_limit=1.0,
    supports_comments=True,
    category="tech",
    custom_config={"api_key": "secret"}
)
```

---

### PerformanceMonitor

Performance monitoring and metrics collection.

```python
from core.source_system.performance_monitor import PerformanceMonitor, get_performance_monitor
```

#### Class: PerformanceMonitor

##### `record_request(source_name: str, success: bool, response_time: float)`
Record a request for performance tracking.

**Parameters:**
- `source_name` (str): Name of the source
- `success` (bool): Whether request was successful
- `response_time` (float): Response time in seconds

**Example:**
```python
monitor = get_performance_monitor()
monitor.record_request('hn', True, 2.5)
```

##### `get_source_metrics(source_name: str) -> SourceMetrics`
Get performance metrics for a source.

**Parameters:**
- `source_name` (str): Name of the source

**Returns:**
- `SourceMetrics`: Performance metrics

**Example:**
```python
metrics = monitor.get_source_metrics('hn')
print(f"Success rate: {metrics.success_rate:.1f}%")
print(f"Avg response time: {metrics.avg_response_time:.2f}s")
```

##### `get_all_metrics() -> Dict[str, SourceMetrics]`
Get metrics for all sources.

**Returns:**
- `Dict[str, SourceMetrics]`: All source metrics

**Example:**
```python
all_metrics = monitor.get_all_metrics()
for source, metrics in all_metrics.items():
    print(f"{source}: {metrics.success_rate:.1f}% success")
```

##### `generate_performance_report() -> str`
Generate human-readable performance report.

**Returns:**
- `str`: Performance report

**Example:**
```python
report = monitor.generate_performance_report()
print(report)
```

#### Function: get_performance_monitor()
Get the global performance monitor instance.

**Returns:**
- `PerformanceMonitor`: Global monitor instance

---

### ValidationEngine

Configuration validation and quality assurance.

```python
from core.source_system.validation_engine import ValidationEngine, ValidationResult
```

#### Class: ValidationEngine

##### `validate_source_config(config: SourceConfig) -> List[ValidationResult]`
Validate a single source configuration.

**Parameters:**
- `config` (SourceConfig): Source configuration

**Returns:**
- `List[ValidationResult]`: Validation results

**Example:**
```python
engine = ValidationEngine()
results = engine.validate_source_config(config)
for result in results:
    if not result.is_valid:
        print(f"Error: {result.message}")
```

##### `validate_all_sources(configs: Dict[str, SourceConfig], deep_validation: bool = False)`
Validate all source configurations.

**Parameters:**
- `configs` (Dict[str, SourceConfig]): Source configurations
- `deep_validation` (bool): Whether to perform network tests

**Returns:**
- `Dict[str, List[ValidationResult]]`: Validation results by source

**Example:**
```python
results = engine.validate_all_sources(configs, deep_validation=True)
```

##### `generate_validation_report(results: Dict) -> str`
Generate comprehensive validation report.

**Parameters:**
- `results` (Dict): Validation results from validate_all_sources

**Returns:**
- `str`: Markdown validation report

**Example:**
```python
report = engine.generate_validation_report(results)
with open('validation_report.md', 'w') as f:
    f.write(report)
```

#### Class: ValidationResult

##### Properties
- `is_valid` (bool): Whether validation passed
- `message` (str): Validation message
- `severity` (str): Severity level ("error", "warning", "info")
- `category` (str): Category ("network", "config", "selectors", "general")

**Example:**
```python
result = ValidationResult(
    is_valid=False,
    message="Invalid CSS selector",
    severity="error",
    category="selectors"
)
```

---

### SessionPool

Global session management for optimal performance.

```python
from core.session_pool import get_global_session, SessionPool
```

#### Function: get_global_session()
Get the global HTTP session instance.

**Returns:**
- `requests.Session`: Optimized session with connection pooling

**Example:**
```python
session = get_global_session()
response = session.get('https://example.com/')
```

#### Class: SessionPool

##### `get_session() -> requests.Session`
Get a configured session instance.

**Returns:**
- `requests.Session`: Configured session

**Example:**
```python
pool = SessionPool()
session = pool.get_session()
```

---

## Article Processing

### ArticleFetcher

Core article content fetching with separated concerns.

```python
from core.article_fetcher import ArticleFetcher
```

#### Class: ArticleFetcher

##### `fetch_article_content(title: str, url: str, index: int, base_folder: str, progress_callback=None) -> Tuple[bool, Optional[str], Optional[str]]`
Fetch and save article content in markdown format.

**Note:** This method handles ONLY article content. Comments should be fetched separately using source-specific methods.

**Parameters:**
- `title` (str): Article title
- `url` (str): Article URL
- `index` (int): Article index number
- `base_folder` (str): Base directory to save to
- `progress_callback` (Optional[Callable]): Progress update callback

**Returns:**
- `Tuple[bool, Optional[str], Optional[str]]`: (success, article_folder_path, article_title)

**Example:**
```python
fetcher = ArticleFetcher()
success, folder_path, title = fetcher.fetch_article_content(
    title="Example Article",
    url="https://example.com/article",
    index=1,
    base_folder="/path/to/articles"
)

if success:
    print(f"Article saved to: {folder_path}")
```

##### Fallback Image Detection System

**Automatic Activation**: When primary image extraction finds < 2 images, the fallback system automatically:

1. **Full Page Scanning**: Analyzes entire original HTML before article filtering
2. **Intelligent UI Filtering**: Removes logos, icons, ads, navigation elements, tracking pixels
3. **Size Filtering**: Skips images < 150px dimensions
4. **Duplicate Prevention**: Avoids re-downloading existing images
5. **Seamless Integration**: Adds as "Additional Images" section in markdown

**Filtering Patterns:**
- **Class patterns**: logo, icon, avatar, nav, menu, ad, banner, social, share
- **ID patterns**: logo, icon, nav, header, footer, sidebar
- **Alt text patterns**: logo, icon, advertisement, navigation, social
- **URL patterns**: logo, icon, avatar, ad, pixel, tracker, beacon, analytics

**Example Output:**
```markdown
# Article Title

Original article content...

## Additional Images

*The following images were found using comprehensive page scanning:*

![Fallback Image 1](images/content-image1.jpg)

![Fallback Image 2](images/content-image2.png)
```

---

## Unified Media Processing

### UnifiedMediaProcessor

Central interface for unified media processing across all sources.

```python
from core.unified_media_processor import UnifiedMediaProcessor
```

#### Class: UnifiedMediaProcessor

##### `process_article_media(content: str, html_content: str, url: str, article_folder: str, source_name: str, session: requests.Session) -> str`

Process all media embedding for an article using the unified system.

**Parameters:**
- `content` (str): Markdown content of the article
- `html_content` (str): Original HTML content
- `url` (str): Source URL of the article
- `article_folder` (str): Path to article folder
- `source_name` (str): Name of the news source (for configuration)
- `session` (requests.Session): HTTP session for downloading

**Returns:**
- `str`: Updated markdown content with local image references

**Example:**
```python
updated_content = UnifiedMediaProcessor.process_article_media(
    content=markdown_content,
    html_content=html_content,
    url=article_url,
    article_folder=article_folder,
    source_name="futurism",
    session=session
)
```

##### `add_media_config_to_source(source_config_path: str, source_name: str) -> None`

Add media processing configuration to a source's config file.

**Parameters:**
- `source_config_path` (str): Path to source's config.yaml file
- `source_name` (str): Name of the source

##### `get_integration_code_example(source_name: str) -> str`

Get example code for integrating unified media processing into a source.

**Parameters:**
- `source_name` (str): Name of the source

**Returns:**
- `str`: Example Python code for integration

### MediaEmbeddingProcessor

Core engine for media extraction, downloading, and URL replacement.

```python
from core.media_embedding_processor import MediaEmbeddingProcessor
```

#### Class: MediaEmbeddingProcessor

##### `__init__(source_config: Dict[str, Any], session: requests.Session)`

Initialize media processor with source-specific configuration.

**Parameters:**
- `source_config` (Dict[str, Any]): Source-specific media processing configuration
- `session` (requests.Session): HTTP session for downloading

##### `process_media_embedding(content: str, soup: BeautifulSoup, article_folder: str, base_url: str) -> str`

Main method to process all media embedding.

**Parameters:**
- `content` (str): Markdown content
- `soup` (BeautifulSoup): BeautifulSoup object of original HTML
- `article_folder` (str): Path to article folder
- `base_url` (str): Base URL of the source

**Returns:**
- `str`: Updated markdown content with local image references

### MediaConfigManager

Manages media processing configurations for different news sources.

```python
from core.media_config import MediaConfigManager
```

#### Class: MediaConfigManager

##### `get_source_config(source_name: str) -> Dict[str, Any]`

Get media processing configuration for a specific source.

**Parameters:**
- `source_name` (str): Name of the news source

**Returns:**
- `Dict[str, Any]`: Dictionary with media processing configuration

**Example:**
```python
config = MediaConfigManager.get_source_config('futurism')
# Returns:
# {
#     'media_processing': {
#         'hero_image_selectors': ['.featured-image img', '.post-thumbnail img'],
#         'url_patterns': {'wordpress': ['/wp-content/uploads/']},
#         'quality_thresholds': {'min_width': 150, 'min_height': 150}
#     }
# }
```

##### `get_all_source_names() -> List[str]`

Get list of all configured source names.

**Returns:**
- `List[str]`: List of configured source names

**Supported Sources:**
- futurism, gizmodo, ieee, hn, bbc, cnn, nature

## Comment Processing

### Source-Specific Comment Fetching

Comments are fetched independently from articles using source-specific methods.

#### Hacker News Comments

```python
# Article and comments are fetched separately
source = registry.get_source('hn')

# 1. Fetch article content
success, folder_path, title = source.fetch_article_content(
    title=article.title,
    url=article.url,
    index=0,
    base_folder=output_dir
)

# 2. Fetch comments separately if article was successful
if success and article.comment_url:
    source.fetch_comments(
        comment_url=article.comment_url,
        article_title=title,
        article_folder_path=folder_path
    )
```

#### Lobsters Comments

```python
# Similar pattern for Lobsters
source = registry.get_source('lb')

# Article fetching
success, folder_path, title = source.fetch_article_content(...)

# Independent comment fetching
if success and comment_url:
    source.fetch_comments(comment_url, title, folder_path)
```

### Benefits of Separated Workflows

1. **Clean Signatures**: Article methods don't have comment parameters
2. **Independent Processing**: Comments can fail without losing articles
3. **Better Error Handling**: Isolated error domains
4. **Source Flexibility**: Each source handles comments differently
5. **Maintainability**: Clear separation of concerns

**Error Isolation Example:**
```python
try:
    # Article fetching
    success, folder, title = fetcher.fetch_article_content(...)

    # Comment fetching (independent)
    if success and comment_url:
        try:
            source.fetch_comments(comment_url, title, folder)
        except Exception as e:
            logger.debug(f"Comments failed: {e}")
            # Article is still saved successfully

except Exception as e:
    logger.error(f"Article fetch failed: {e}")
```

---

## Configuration Classes

### NetworkConfig

Network-related configuration.

```python
from core.config import NetworkConfig

config = NetworkConfig(
    connect_timeout=10,
    read_timeout=8,
    user_agent="Custom User Agent"
)
```

### ProcessingConfig

Processing-related configuration.

```python
from core.config import ProcessingConfig

config = ProcessingConfig(
    max_workers=8,
    download_images=True,
    download_videos=False
)
```

## Data Classes

### SourceMetrics

Performance metrics data class.

```python
from core.source_system.performance_monitor import SourceMetrics

@dataclass
class SourceMetrics:
    source_name: str
    source_type: str
    total_requests: int = 0
    successful_requests: int = 0
    avg_response_time: float = 0.0
    articles_discovered: int = 0
    articles_fetched: int = 0
    articles_failed: int = 0
    last_error: Optional[str] = None

    @property
    def success_rate(self) -> float:
        return (self.successful_requests / self.total_requests) * 100
```

## Exception Classes

### SourceError

Base exception for source-related errors.

```python
from core.source_system.base_source import SourceError

try:
    source = registry.get_source('nonexistent')
except SourceError as e:
    print(f"Source error: {e}")
```

### ConfigurationError

Configuration-related errors.

```python
from core.source_system.base_source import ConfigurationError

try:
    config = load_invalid_config()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Usage Examples

### Complete Source Implementation
```python
from typing import List, Dict, Optional
from core.source_system.base_source import BaseSource, SourceConfig

class ExampleSource(BaseSource):
    def get_articles(self, count: int = 30) -> List[Dict]:
        response = self.session.get(self.config.base_url)
        response.raise_for_status()

        soup = self._get_soup(response.text)
        articles = []

        for link in soup.select('.article-link')[:count]:
            articles.append({
                'title': self._clean_text(link.get_text()),
                'url': self._resolve_url(link['href']),
                'summary': ''
            })

        return articles

    def get_article_content(self, url: str) -> Optional[str]:
        response = self.session.get(url)
        soup = self._get_soup(response.text)

        content = soup.select_one('.article-content')
        return str(content) if content else None

    def validate_config(self) -> List[str]:
        errors = []
        if not self.config.base_url:
            errors.append("base_url is required")
        return errors
```

### Registry Usage
```python
# Get registry and discover sources
registry = get_source_registry()
available = registry.get_available_sources()

# Create source instance
source = registry.get_source('hn')

# Fetch articles
articles = source.get_articles(count=10)

# Get performance metrics
monitor = get_performance_monitor()
metrics = monitor.get_source_metrics('hn')
```

---

*This API reference covers all public interfaces in the Capcat hybrid architecture. For implementation examples, see the Source Development Guide.*