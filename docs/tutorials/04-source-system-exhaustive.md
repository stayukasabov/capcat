# Source System Exhaustive Reference

Complete documentation of EVERY source system component, class, method, and operation in Capcat.

Source: Application/core/source_system/

## Architecture Overview

The source system implements a hybrid architecture supporting both config-driven (YAML) and custom (Python) sources with automatic discovery, validation, and management.

### Directory Structure

```
Application/
└── core/
    └── source_system/
        ├── base_source.py              # Abstract base classes
        ├── source_registry.py          # Source discovery and management
        ├── source_factory.py           # Source instantiation
        ├── validation_engine.py        # Configuration validation
        ├── performance_monitor.py      # Performance tracking
        ├── config_driven_source.py     # Config-driven implementation
        └── ...                         # Additional components

sources/
└── active/
    ├── config_driven/
    │   └── configs/
    │       ├── iq.yaml
    │       ├── ieee.yaml
    │       └── ...
    └── custom/
        ├── hn/
        │   ├── source.py
        │   └── config.yaml
        ├── bbc/
        │   ├── source.py
        │   └── config.yaml
        └── ...
```

## Core Data Classes

### SourceConfig
Location: Application/core/source_system/base_source.py:14

**Purpose:** Configuration data class for news sources.

**Complete Field List:**

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Field</th>
      <th>Type</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>name</code></td>
      <td>str</td>
      <td>(required)</td>
      <td>Source identifier (lowercase, no spaces)</td>
    </tr>
    <tr>
      <td><code>display_name</code></td>
      <td>str</td>
      <td>(required)</td>
      <td>Human-readable source name</td>
    </tr>
    <tr>
      <td><code>base_url</code></td>
      <td>str</td>
      <td>(required)</td>
      <td>Base URL for the source</td>
    </tr>
    <tr>
      <td><code>timeout</code></td>
      <td>float</td>
      <td>10.0</td>
      <td>Request timeout in seconds</td>
    </tr>
    <tr>
      <td><code>rate_limit</code></td>
      <td>float</td>
      <td>1.0</td>
      <td>Minimum seconds between requests</td>
    </tr>
    <tr>
      <td><code>supports_comments</code></td>
      <td>bool</td>
      <td>False</td>
      <td>Whether source supports comment fetching</td>
    </tr>
    <tr>
      <td><code>has_comments</code></td>
      <td>bool</td>
      <td>False</td>
      <td>Whether source has comments enabled</td>
    </tr>
    <tr>
      <td><code>category</code></td>
      <td>str</td>
      <td>"general"</td>
      <td>Source category (tech, news, science, etc.)</td>
    </tr>
    <tr>
      <td><code>custom_config</code></td>
      <td>Dict[str, Any]</td>
      <td>{}</td>
      <td>Additional source-specific configuration</td>
    </tr>
  </tbody>
</table>
</div>

**Methods:**

#### __post_init__()
```python
def __post_init__(self):
    """Initialize custom_config as empty dict if None."""
    if self.custom_config is None:
        self.custom_config = {}
```

#### to_dict() -> Dict[str, Any]
Location: Application/core/source_system/base_source.py:34

```python
def to_dict(self) -> Dict[str, Any]:
    """
    Convert to dictionary format for compatibility.

    Returns:
        Dictionary representation of the source configuration
    """
    result = {
        "name": self.name,
        "display_name": self.display_name,
        "base_url": self.base_url,
        "timeout": self.timeout,
        "rate_limit": self.rate_limit,
        "supports_comments": self.supports_comments,
        "has_comments": self.has_comments,
        "category": self.category,
    }

    # Add custom configuration
    if self.custom_config:
        result.update(self.custom_config)

    return result
```

**Usage:**
```python
from core.source_system.base_source import SourceConfig

config = SourceConfig(
    name="example",
    display_name="Example News",
    base_url="https://example.com/",
    timeout=15.0,
    rate_limit=2.0,
    supports_comments=True,
    category="tech",
    custom_config={"api_key": "secret"}
)

# Convert to dictionary
config_dict = config.to_dict()
```

### Article
Location: Application/core/source_system/base_source.py:59

**Purpose:** Data class representing a news article.

**Complete Field List:**

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Field</th>
      <th>Type</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>title</code></td>
      <td>str</td>
      <td>(required)</td>
      <td>Article title</td>
    </tr>
    <tr>
      <td><code>url</code></td>
      <td>str</td>
      <td>(required)</td>
      <td>Article URL</td>
    </tr>
    <tr>
      <td><code>comment_url</code></td>
      <td>Optional[str]</td>
      <td>None</td>
      <td>URL for fetching comments</td>
    </tr>
    <tr>
      <td><code>author</code></td>
      <td>Optional[str]</td>
      <td>None</td>
      <td>Article author name</td>
    </tr>
    <tr>
      <td><code>published_date</code></td>
      <td>Optional[str]</td>
      <td>None</td>
      <td>Publication date</td>
    </tr>
    <tr>
      <td><code>summary</code></td>
      <td>Optional[str]</td>
      <td>None</td>
      <td>Article summary/excerpt</td>
    </tr>
    <tr>
      <td><code>tags</code></td>
      <td>List[str]</td>
      <td>[]</td>
      <td>Article tags/categories</td>
    </tr>
  </tbody>
</table>
</div>

**Methods:**

#### __post_init__()
```python
def __post_init__(self):
    """Initialize tags as empty list if None."""
    if self.tags is None:
        self.tags = []
```

**Usage:**
```python
from core.source_system.base_source import Article

article = Article(
    title="Example Article",
    url="https://example.com/article/123",
    comment_url="https://example.com/article/123/comments",
    author="John Doe",
    published_date="2025-11-25",
    summary="This is an example article.",
    tags=["tech", "ai", "news"]
)
```

## Abstract Base Class

### BaseSource
Location: Application/core/source_system/base_source.py:78

**Purpose:** Abstract base class for all news sources defining the contract all implementations must follow.

**Constructor:**

#### __init__(config: SourceConfig, session: Optional[requests.Session] = None)
Location: Application/core/source_system/base_source.py:86

```python
def __init__(
    self, config: SourceConfig, session: Optional[requests.Session] = None
):
    """
    Initialize the source with configuration.

    Args:
        config: Source configuration
        session: Optional HTTP session for connection pooling
    """
    self.config = config
    self.session = session or requests.Session()
    self.logger = self._get_logger()

    # Initialize performance monitoring
    self._setup_performance_monitoring()
```

**Attributes:**
- `self.config` (SourceConfig) - Source configuration
- `self.session` (requests.Session) - HTTP session for requests
- `self.logger` (logging.Logger) - Logger instance

**Abstract Properties:**

#### source_type -> str
Location: Application/core/source_system/base_source.py:103

```python
@property
@abstractmethod
def source_type(self) -> str:
    """Return the source type ('config_driven' or 'custom')."""
    pass
```

**Must return:** "config_driven" or "custom"

**Abstract Methods:**

#### discover_articles(count: int) -> List[Article]
Location: Application/core/source_system/base_source.py:109

```python
@abstractmethod
def discover_articles(self, count: int) -> List[Article]:
    """
    Discover articles from the source.

    Args:
        count: Maximum number of articles to discover

    Returns:
        List of Article objects

    Raises:
        SourceError: If article discovery fails
    """
    pass
```

**Implementation Requirements:**
- Fetch article listings from source
- Parse article metadata (title, URL, optional summary)
- Return up to `count` articles
- Handle network errors gracefully
- Respect rate limiting

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
            summary=''
        ))

    return articles
```

#### fetch_article_content(article: Article, output_dir: str, progress_callback=None) -> Tuple[bool, Optional[str]]
Location: Application/core/source_system/base_source.py:125

```python
@abstractmethod
def fetch_article_content(
    self, article: Article, output_dir: str, progress_callback=None
) -> Tuple[bool, Optional[str]]:
    """
    Fetch and save article content.

    Args:
        article: Article to fetch
        output_dir: Directory to save content
        progress_callback: Optional progress callback function

    Returns:
        Tuple of (success, article_path)

    Raises:
        SourceError: If content fetching fails
    """
    pass
```

**Implementation Requirements:**
- Fetch article HTML content
- Extract main article content
- Download and process media (images, videos)
- Convert to Markdown format
- Save to output directory
- Return success status and article path

**Return Values:**
- `(True, "/path/to/article")` - Success
- `(False, None)` - Failure

**Example Implementation:**
```python
def fetch_article_content(
    self, article: Article, output_dir: str, progress_callback=None
) -> Tuple[bool, Optional[str]]:
    try:
        response = self.session.get(article.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        content = soup.select_one('.article-content')
        if not content:
            return False, None

        # Process content, download media, convert to markdown
        markdown = self._convert_to_markdown(content)

        # Save to output directory
        article_path = os.path.join(output_dir, 'article.md')
        with open(article_path, 'w') as f:
            f.write(markdown)

        return True, article_path

    except Exception as e:
        self.logger.error(f"Failed to fetch article: {e}")
        return False, None
```

**Concrete Methods:**

#### fetch_comments(article: Article, output_dir: str, progress_callback=None) -> bool
Location: Application/core/source_system/base_source.py:145

```python
def fetch_comments(
    self, article: Article, output_dir: str, progress_callback=None
) -> bool:
    """
    Fetch and save article comments (if supported).

    Args:
        article: Article to fetch comments for
        output_dir: Directory to save comments
        progress_callback: Optional progress callback function

    Returns:
        True if comments were fetched successfully, False otherwise
    """
    if not self.config.supports_comments:
        return False
    return self._fetch_comments_impl(
        article, output_dir, progress_callback
    )
```

**Behavior:**
- Returns `False` immediately if `supports_comments` is False
- Delegates to `_fetch_comments_impl()` if comments supported
- Optional method - not all sources implement comments

#### _fetch_comments_impl(article: Article, output_dir: str, progress_callback=None) -> bool
Location: Application/core/source_system/base_source.py:165

```python
def _fetch_comments_impl(
    self, article: Article, output_dir: str, progress_callback=None
) -> bool:
    """
    Implementation of comment fetching (override in subclasses that support comments).

    Args:
        article: Article to fetch comments for
        output_dir: Directory to save comments
        progress_callback: Optional progress callback function

    Returns:
        True if comments were fetched successfully, False otherwise
    """
    return False
```

**Override this method** in subclasses that support comments.

**Example Implementation:**
```python
def _fetch_comments_impl(
    self, article: Article, output_dir: str, progress_callback=None
) -> bool:
    if not article.comment_url:
        return False

    try:
        response = self.session.get(article.comment_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        comments = []
        for comment_elem in soup.select('.comment'):
            comments.append({
                'author': comment_elem.select_one('.author').get_text(),
                'text': comment_elem.select_one('.text').get_text(),
                'timestamp': comment_elem.select_one('.timestamp').get('datetime')
            })

        # Save comments to file
        comments_path = os.path.join(output_dir, 'comments.md')
        with open(comments_path, 'w') as f:
            for comment in comments:
                f.write(f"**{comment['author']}** - {comment['timestamp']}\n\n")
                f.write(f"{comment['text']}\n\n---\n\n")

        return True

    except Exception as e:
        self.logger.error(f"Failed to fetch comments: {e}")
        return False
```

#### validate_config() -> List[str]
Location: Application/core/source_system/base_source.py:181

```python
def validate_config(self) -> List[str]:
    """
    Validate the source configuration.

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    if not self.config.name:
        errors.append("Source name is required")

    if not self.config.display_name:
        errors.append("Source display name is required")

    if not self.config.base_url:
        errors.append("Source base URL is required")
    elif not self.config.base_url.startswith(("http://", "https://")):
        errors.append(
            "Source base URL must start with http:// or https://"
        )

    if self.config.timeout <= 0:
        errors.append("Timeout must be positive")

    if self.config.rate_limit < 0:
        errors.append("Rate limit cannot be negative")

    return errors
```

**Validation Checks:**
- Name not empty
- Display name not empty
- Base URL not empty
- Base URL starts with http:// or https://
- Timeout > 0
- Rate limit >= 0

**Usage:**
```python
source = registry.get_source('hn')
errors = source.validate_config()

if errors:
    print(f"Configuration errors: {errors}")
else:
    print("Configuration valid")
```

## Source Registry

### SourceRegistry
Location: Application/core/source_system/source_registry.py:28

**Purpose:** Registry for managing and discovering news sources. Supports auto-discovery and validation.

**Constructor:**

#### __init__(sources_dir: str = None)
Location: Application/core/source_system/source_registry.py:36

```python
def __init__(self, sources_dir: str = None):
    """
    Initialize the source registry.

    Args:
        sources_dir: Path to sources directory (defaults to sources/ relative to app root)
    """
    self.logger = get_logger(__name__)
    self._sources: Dict[str, Type[BaseSource]] = {}
    self._configs: Dict[str, SourceConfig] = {}
    self._source_instances: Dict[str, BaseSource] = {}
    self.validation_engine = ValidationEngine()

    # Determine sources directory - now uses active/ subdirectory
    if sources_dir is None:
        app_root = Path(__file__).parent.parent.parent
        self.sources_dir = app_root / "sources" / "active"
    else:
        self.sources_dir = Path(sources_dir)
```

**Attributes:**
- `self._sources` - Dictionary of source classes by name
- `self._configs` - Dictionary of source configurations by name
- `self._source_instances` - Dictionary of instantiated sources (cache)
- `self.validation_engine` - ValidationEngine instance
- `self.sources_dir` - Path to sources directory

**Default sources directory:** `Application/sources/active/`

**Methods:**

#### discover_sources() -> Dict[str, SourceConfig]
Location: Application/core/source_system/source_registry.py:60

```python
def discover_sources(self) -> Dict[str, SourceConfig]:
    """
    Discover all available sources (both config-driven and custom).

    Returns:
        Dictionary mapping source names to their configurations

    Raises:
        SourceError: If source discovery fails
    """
    self.logger.debug("Starting source discovery")

    try:
        # Clear existing data
        self._sources.clear()
        self._configs.clear()
        self._source_instances.clear()

        # Discover config-driven sources
        self._discover_config_driven_sources()

        # Discover custom sources
        self._discover_custom_sources()

        self.logger.debug(
            f"Source discovery completed. Found {len(self._configs)} sources"
        )
        return self._configs.copy()

    except Exception as e:
        raise SourceError(f"Source discovery failed: {e}")
```

**Behavior:**
1. Clear existing source data
2. Discover config-driven sources from `sources/active/config_driven/configs/`
3. Discover custom sources from `sources/active/custom/`
4. Return dictionary of all discovered sources

**Discovery Process:**

**Config-Driven Discovery:**
1. Scan `sources/active/config_driven/configs/` for `.yaml`, `.yml`, `.json` files
2. Load each configuration file
3. Create SourceConfig from file data
4. Validate configuration
5. Register source if valid

**Custom Discovery:**
1. Scan `sources/active/custom/` for directories
2. Look for `source.py` in each directory
3. Look for `config.yaml` (or `.yml`, `.json`) in each directory
4. Load configuration
5. Import source class from `source.py`
6. Register source

#### _discover_config_driven_sources()
Location: Application/core/source_system/source_registry.py:92

```python
def _discover_config_driven_sources(self):
    """Discover sources defined by configuration files."""
    config_dir = self.sources_dir / "config_driven" / "configs"

    if not config_dir.exists():
        self.logger.debug(
            f"Config-driven sources directory not found: {config_dir}"
        )
        return

    self.logger.debug(
        f"Discovering config-driven sources in: {config_dir}"
    )

    for config_file in config_dir.iterdir():
        if config_file.suffix in {".yaml", ".yml", ".json"}:
            try:
                config = self._load_config_file(config_file)
                source_name = config_file.stem

                # Create SourceConfig
                source_config = SourceConfig(
                    name=source_name,
                    display_name=config.get(
                        "display_name", source_name.title()
                    ),
                    base_url=config["base_url"],
                    timeout=config.get("timeout", 10.0),
                    rate_limit=config.get("rate_limit", 1.0),
                    supports_comments=config.get(
                        "supports_comments", False
                    ),
                    category=config.get("category", "general"),
                    custom_config=config,
                )

                # Validate configuration
                errors = self._validate_config_driven_config(source_config)
                if errors:
                    self.logger.warning(
                        f"Config validation failed for {source_name}: {errors}"
                    )
                    continue

                self._configs[source_name] = source_config
                self.logger.debug(
                    f"Registered config-driven source: {source_name}"
                )

            except Exception as e:
                self.logger.warning(
                    f"Failed to load config-driven source {config_file}: {e}"
                )
```

**File Format Support:**
- `.yaml` - YAML format
- `.yml` - YAML format
- `.json` - JSON format

**Source Name:** Derived from filename (stem without extension)

#### _discover_custom_sources()
Location: Application/core/source_system/source_registry.py:146

```python
def _discover_custom_sources(self):
    """Discover custom source implementations."""
    custom_dir = self.sources_dir / "custom"

    if not custom_dir.exists():
        self.logger.debug(
            f"Custom sources directory not found: {custom_dir}"
        )
        return

    self.logger.debug(f"Discovering custom sources in: {custom_dir}")

    for source_dir in custom_dir.iterdir():
        if source_dir.is_dir() and not source_dir.name.startswith("_"):
            try:
                self._load_custom_source(source_dir)
            except Exception as e:
                self.logger.warning(
                    f"Failed to load custom source {source_dir.name}: {e}"
                )
```

**Discovery Rules:**
- Only directories (not files)
- Ignore directories starting with `_`
- Each directory represents one source

#### get_source(source_name: str, session=None) -> BaseSource
Location: Application/core/source_system/source_registry.py (method continues beyond line 200)

```python
def get_source(self, source_name: str, session=None) -> BaseSource:
    """
    Get a source instance by name.

    Args:
        source_name: Name of the source
        session: Optional HTTP session to use

    Returns:
        Source instance

    Raises:
        SourceError: If source not found or cannot be instantiated
    """
    # Check cache first
    if source_name in self._source_instances:
        return self._source_instances[source_name]

    # Get configuration
    if source_name not in self._configs:
        raise SourceError(f"Source not found: {source_name}")

    config = self._configs[source_name]

    # Instantiate source
    source = self._instantiate_source(source_name, config, session)

    # Cache instance
    self._source_instances[source_name] = source

    return source
```

**Caching:** Source instances are cached after first instantiation

**Usage:**
```python
registry = get_source_registry()
source = registry.get_source('hn')
articles = source.discover_articles(count=10)
```

#### get_available_sources() -> List[str]
```python
def get_available_sources(self) -> List[str]:
    """
    Get list of available source names.

    Returns:
        List of source names
    """
    if not self._configs:
        self.discover_sources()
    return list(self._configs.keys())
```

**Usage:**
```python
registry = get_source_registry()
sources = registry.get_available_sources()
print(f"Available sources: {', '.join(sources)}")
```

#### get_source_config(source_name: str) -> Optional[SourceConfig]
```python
def get_source_config(self, source_name: str) -> Optional[SourceConfig]:
    """
    Get source configuration by name.

    Args:
        source_name: Name of the source

    Returns:
        Source configuration or None if not found
    """
    if not self._configs:
        self.discover_sources()
    return self._configs.get(source_name)
```

**Usage:**
```python
registry = get_source_registry()
config = registry.get_source_config('hn')
print(f"Base URL: {config.base_url}")
print(f"Category: {config.category}")
```

#### get_sources_by_category(category: str) -> List[str]
```python
def get_sources_by_category(self, category: str) -> List[str]:
    """
    Get sources by category.

    Args:
        category: Category name (tech, news, science, etc.)

    Returns:
        List of source names in category
    """
    if not self._configs:
        self.discover_sources()

    return [
        name for name, config in self._configs.items()
        if config.category == category
    ]
```

**Usage:**
```python
registry = get_source_registry()
tech_sources = registry.get_sources_by_category('tech')
print(f"Tech sources: {', '.join(tech_sources)}")
```

#### validate_all_sources(deep_validation: bool = False) -> Dict[str, List[str]]
```python
def validate_all_sources(self, deep_validation: bool = False) -> Dict[str, List[str]]:
    """
    Validate all registered sources.

    Args:
        deep_validation: Whether to perform network tests

    Returns:
        Dictionary mapping source names to validation errors
    """
    if not self._configs:
        self.discover_sources()

    errors = {}
    for source_name, config in self._configs.items():
        source_errors = []

        # Basic validation
        if not config.name:
            source_errors.append("Missing source name")
        if not config.base_url:
            source_errors.append("Missing base URL")

        # Deep validation (network tests)
        if deep_validation:
            try:
                source = self.get_source(source_name)
                test_articles = source.discover_articles(count=1)
                if not test_articles:
                    source_errors.append("Failed to discover any articles")
            except Exception as e:
                source_errors.append(f"Network test failed: {e}")

        if source_errors:
            errors[source_name] = source_errors

    return errors
```

**Validation Types:**
- **Basic:** Configuration field validation
- **Deep:** Network connectivity and article discovery tests

**Usage:**
```python
registry = get_source_registry()

# Basic validation
errors = registry.validate_all_sources(deep_validation=False)

# Deep validation (with network tests)
errors = registry.validate_all_sources(deep_validation=True)

for source, error_list in errors.items():
    if error_list:
        print(f"{source}: {', '.join(error_list)}")
```

### Global Registry Functions

#### get_source_registry() -> SourceRegistry
```python
_registry_instance = None

def get_source_registry() -> SourceRegistry:
    """Get the global source registry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = SourceRegistry()
        _registry_instance.discover_sources()
    return _registry_instance
```

**Usage:**
```python
from core.source_system.source_registry import get_source_registry

registry = get_source_registry()
sources = registry.get_available_sources()
```

## Exception Classes

### SourceError
Location: Application/core/source_system/base_source.py

```python
class SourceError(Exception):
    """Base exception for source-related errors."""
    pass
```

**Usage:**
```python
from core.source_system.base_source import SourceError

try:
    source = registry.get_source('nonexistent')
except SourceError as e:
    print(f"Source error: {e}")
```

### ConfigurationError
Location: Application/core/source_system/base_source.py

```python
class ConfigurationError(SourceError):
    """Configuration-related errors."""
    pass
```

**Usage:**
```python
from core.source_system.base_source import ConfigurationError

try:
    config = load_invalid_config()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Source Code Locations

Core classes:
- `SourceConfig` - Application/core/source_system/base_source.py:14
- `Article` - Application/core/source_system/base_source.py:59
- `BaseSource` - Application/core/source_system/base_source.py:78
- `SourceRegistry` - Application/core/source_system/source_registry.py:28

Global functions:
- `get_source_registry()` - Application/core/source_system/source_registry.py

Exception classes:
- `SourceError` - Application/core/source_system/base_source.py
- `ConfigurationError` - Application/core/source_system/base_source.py

## Related Documentation

- API Functions: docs/tutorials/05-api-functions-exhaustive.md
- Source Development: docs/tutorials/06-source-development-exhaustive.md
- Configuration: docs/tutorials/03-configuration-exhaustive.md
