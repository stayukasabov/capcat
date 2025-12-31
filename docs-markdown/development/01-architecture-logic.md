# Development Architecture & Logic

## Overview

Capcat implements a hybrid modular architecture combining config-driven simplicity with custom code flexibility. This document explains the technical architecture, design patterns, and implementation logic for junior developers.

---

## System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                         │
├────────────────────────────────────────────────────────────────┤
│  CLI Interface (cli.py)         Interactive Mode (interactive.py)│
│  - Argument parsing             - Menu-driven workflow         │
│  - Command routing              - User-friendly prompts        │
│  - Input validation             - Error recovery              │
└───────────────────┬────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────────────┐
│                     CORE ORCHESTRATION                         │
├────────────────────────────────────────────────────────────────┤
│  Main Application (capcat.py)                                  │
│  - Workflow coordination        - Error handling              │
│  - Resource management          - Graceful shutdown           │
│  - Logging configuration        - Progress tracking           │
└───────────────────┬────────────────────────────────────────────┘
                    │
        ┌───────────┴──────────┬────────────────┐
        ▼                      ▼                ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│    SOURCE    │    │     CONTENT      │    │    OUTPUT    │
│   SYSTEM     │    │   PROCESSING     │    │  GENERATION  │
└──────────────┘    └──────────────────┘    └──────────────┘
```

### Architectural Layers

#### Layer 1: User Interface

**Purpose**: Accept user input and display results

**Components**:
1. `cli.py` - Command-line argument parsing
2. `interactive.py` - Interactive menu system
3. `capcat` (bash wrapper) - Entry point automation

**Responsibilities**:
- Parse command-line arguments
- Validate user input
- Route commands to appropriate handlers
- Display progress and results
- Handle user cancellation (Ctrl+C)

**Key Design Decisions**:
- Subcommand architecture (like git, docker)
- Questionary library for interactive menus
- Bash wrapper handles venv activation automatically

#### Layer 2: Core Orchestration

**Purpose**: Coordinate all system components

**Components**:
1. `capcat.py` - Main application logic
2. `core/config.py` - Configuration management
3. `core/logging_config.py` - Logging setup
4. `core/shutdown.py` - Graceful shutdown handling

**Responsibilities**:
- Initialize all subsystems
- Coordinate source fetching workflow
- Manage shared resources (sessions, connections)
- Handle errors and recovery
- Clean up on exit

**Key Design Patterns**:
- Dependency injection for testability
- Context managers for resource cleanup
- Singleton pattern for registry/factory

#### Layer 3: Source System

**Purpose**: Discover, instantiate, and manage news sources

**Components**:
```
core/source_system/
├── source_registry.py       # Source discovery and registration
├── source_factory.py        # Source instantiation
├── base_source.py           # Abstract base class
├── config_driven_source.py  # YAML-based sources
└── performance_monitor.py   # Metrics and health tracking
```

**Architecture**: Hybrid system supporting two source types

##### Config-Driven Sources (Simple)

**Purpose**: Quick source addition via YAML configuration

**Location**: `sources/active/config_driven/configs/*.yaml`

**Example**:
```yaml
# sources/active/config_driven/configs/iq.yaml
display_name: "InfoQ"
base_url: "https://www.infoq.com/news/"
category: tech

# Article discovery
article_selectors:
  - .card__title a
  - .news-headline a

# Content extraction
content_selectors:
  - .article__content
  - article.article

# Image handling
image_selectors:
  - .article__image img
  - figure img

# Optional: Custom settings
max_articles: 50
timeout: 30
```

**Processing Flow**:
```
1. Registry discovers YAML files
2. Validator checks schema compliance
3. ConfigDrivenSource loads configuration
4. Source uses BeautifulSoup for extraction
5. Selectors applied in order until match
6. Content converted to Markdown
```

**Advantages**:
- No Python coding required
- 15-30 minute setup time
- Easy to maintain and update
- Automatic validation
- Community contributions simple

**Limitations**:
- No JavaScript execution
- No complex logic (comments, pagination)
- No anti-bot workarounds
- Basic selector matching only

##### Custom Sources (Complex)

**Purpose**: Full control for complex scraping scenarios

**Location**: `sources/active/custom/<source_name>/source.py`

**Example Structure**:
```python
# sources/active/custom/hn/source.py
from core.source_system.base_source import BaseSource, Article

class HackerNewsSource(BaseSource):
    """
    Hacker News source with comment integration
    """

    def __init__(self, config, session=None):
        super().__init__(config, session)
        self.api_base = "https://hacker-news.firebaseio.com/v0"

    def get_articles(self, count=30):
        """
        Fetch articles from Hacker News API

        Returns:
            List[Article]: Article objects with content
        """
        # Fetch top story IDs
        story_ids = self._fetch_top_stories(count)

        # Fetch article details in parallel
        articles = self._fetch_articles_parallel(story_ids)

        # Fetch comments for each article
        for article in articles:
            article.comments = self._fetch_comments(article.id)

        return articles

    def _fetch_top_stories(self, count):
        """Fetch top story IDs from API"""
        response = self.session.get(f"{self.api_base}/topstories.json")
        return response.json()[:count]

    def _fetch_article_content(self, story_id):
        """Fetch individual article"""
        # Custom logic for HN API
        pass

    def _fetch_comments(self, story_id):
        """Recursively fetch comment tree"""
        # Custom comment parsing
        pass
```

**Advantages**:
- Full Python flexibility
- API integration possible
- Comment system support
- Anti-bot protection handling
- Complex pagination logic
- JavaScript execution (Selenium)

**Use Cases**:
- Sites with anti-bot protection
- API-based sources
- Complex comment systems
- Dynamic content loading
- Multi-page articles

#### Layer 4: Content Processing

**Purpose**: Fetch, parse, and convert content

**Components**:
```
core/
├── article_fetcher.py           # Content fetching and parsing
├── unified_media_processor.py   # Media handling
├── downloader.py                # File downloads
└── html_converter.py            # HTML to Markdown
```

**Processing Pipeline**:

```
1. Article Discovery
   └─> Source.get_articles(count) returns Article objects

2. Content Fetching
   └─> ArticleFetcher.fetch_content(url)
       ├─> HTTP request with retry logic
       ├─> BeautifulSoup parsing
       └─> Content extraction via selectors

3. Media Processing
   └─> UnifiedMediaProcessor.process(content)
       ├─> Identify images, videos, documents
       ├─> Download media files
       ├─> Convert to relative paths
       └─> Embed in Markdown

4. Format Conversion
   └─> HTMLConverter.to_markdown(html)
       ├─> Clean HTML (remove scripts, ads)
       ├─> Convert to Markdown (markdownify)
       ├─> Format code blocks
       └─> Generate final output

5. File Generation
   └─> FileWriter.write(article, output_path)
       ├─> Create folder structure
       ├─> Write article.md
       ├─> Save images/media
       └─> Generate HTML (optional)
```

**Key Algorithms**:

##### Media Embedding Algorithm
```python
def embed_media(article_content, media_files):
    """
    Replace remote media URLs with local file references

    Logic:
    1. Parse HTML/Markdown for media tags
    2. Download each media file
    3. Generate local path (images/01.jpg)
    4. Replace URL with relative path
    5. Update content with new references
    """
    media_map = {}

    for idx, media_url in enumerate(extract_media_urls(content)):
        # Download file
        local_path = download_media(media_url, f"images/{idx:02d}")

        # Map old URL to new path
        media_map[media_url] = local_path

    # Replace all occurrences
    for old_url, new_path in media_map.items():
        content = content.replace(old_url, new_path)

    return content, media_map
```

##### Content Extraction Algorithm
```python
def extract_content(html, selectors):
    """
    Extract article content using CSS selectors

    Logic:
    1. Try each selector in order
    2. Return first successful match
    3. Fallback to readability algorithm
    4. Clean extracted content
    """
    soup = BeautifulSoup(html, 'lxml')

    # Try each configured selector
    for selector in selectors:
        content = soup.select_one(selector)
        if content and len(content.get_text()) > 100:
            return clean_content(content)

    # Fallback: Readability algorithm
    return extract_via_readability(html)
```

#### Layer 5: Output Generation

**Purpose**: Create organized file structures and formats

**Components**:
```
core/
├── utils.py              # Folder creation and naming
├── formatter.py          # Text formatting
└── htmlgen/
    ├── generator.py      # HTML generation
    └── templates/        # Jinja2 templates
```

**Output Structure Logic**:

```python
def create_output_structure(article, batch_mode=True):
    """
    Generate output folder structure

    Batch mode:
        ../News/news_DD-MM-YYYY/Source_DD-MM-YYYY/NN_Title/

    Single mode:
        ../Capcats/cc_DD-MM-YYYY-Title/
    """
    date_str = datetime.now().strftime('%d-%m-%Y')

    if batch_mode:
        # Batch: organized by date and source
        base_dir = f"../News/news_{date_str}"
        source_dir = f"{article.source}_{date_str}"
        article_dir = f"{article.number:02d}_{slugify(article.title)}"

        path = Path(base_dir) / source_dir / article_dir
    else:
        # Single: direct archiving
        article_name = f"cc_{date_str}-{slugify(article.title)}"
        path = Path("../Capcats") / article_name

    # Create structure
    path.mkdir(parents=True, exist_ok=True)
    (path / "images").mkdir(exist_ok=True)
    (path / "files").mkdir(exist_ok=True)

    return path
```

**Naming Convention Logic**:
```python
def slugify(title, max_length=60):
    """
    Convert article title to filesystem-safe name

    Logic:
    1. Convert to lowercase
    2. Replace spaces with underscores
    3. Remove special characters
    4. Truncate to max_length
    5. Remove trailing underscores
    """
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '_', slug)
    slug = slug[:max_length].rstrip('_')

    return slug
```

---

## Core Design Patterns

### 1. Factory Pattern (Source Creation)

**Problem**: Need to create different source types dynamically

**Solution**: SourceFactory centralizes source instantiation

```python
class SourceFactory:
    @staticmethod
    def create_source(config, session=None):
        """
        Create appropriate source type based on configuration

        Returns:
            ConfigDrivenSource or CustomSource instance
        """
        if config.source_type == 'config_driven':
            return ConfigDrivenSource(config, session)
        elif config.source_type == 'custom':
            return load_custom_source(config, session)
        else:
            raise ValueError(f"Unknown source type: {config.source_type}")
```

**Benefits**:
- Centralized creation logic
- Easy to add new source types
- Consistent initialization
- Testable in isolation

### 2. Registry Pattern (Source Discovery)

**Problem**: Need to automatically discover available sources

**Solution**: SourceRegistry maintains source inventory

```python
class SourceRegistry:
    def __init__(self):
        self._sources = {}
        self._configs = {}

    def discover_sources(self):
        """
        Auto-discover sources from filesystem

        Process:
        1. Scan sources/active/config_driven/configs/*.yaml
        2. Scan sources/active/custom/*/source.py
        3. Validate each source
        4. Register in internal registry
        """
        # Discover config-driven sources
        config_dir = Path("sources/active/config_driven/configs")
        for yaml_file in config_dir.glob("*.yaml"):
            config = self._load_config(yaml_file)
            if self._validate_config(config):
                self._register_source(config)

        # Discover custom sources
        custom_dir = Path("sources/active/custom")
        for source_dir in custom_dir.iterdir():
            if (source_dir / "source.py").exists():
                config = self._load_custom_config(source_dir)
                self._register_source(config)

    def get_source(self, source_id, session=None):
        """Retrieve source instance by ID"""
        config = self._configs.get(source_id)
        if not config:
            raise ValueError(f"Source not found: {source_id}")

        return SourceFactory.create_source(config, session)
```

**Benefits**:
- Automatic source discovery
- No manual registration needed
- Validation at discovery time
- Single source of truth

### 3. Strategy Pattern (Content Extraction)

**Problem**: Different sources need different extraction strategies

**Solution**: Pluggable extraction strategies

```python
class ExtractionStrategy:
    def extract_content(self, html):
        raise NotImplementedError

class SelectorStrategy(ExtractionStrategy):
    def __init__(self, selectors):
        self.selectors = selectors

    def extract_content(self, html):
        soup = BeautifulSoup(html, 'lxml')
        for selector in self.selectors:
            content = soup.select_one(selector)
            if content:
                return content
        return None

class ReadabilityStrategy(ExtractionStrategy):
    def extract_content(self, html):
        # Use readability algorithm
        return extract_readable_content(html)

class APIStrategy(ExtractionStrategy):
    def extract_content(self, api_response):
        # Parse API JSON response
        return api_response['content']
```

**Benefits**:
- Flexible extraction methods
- Easy to add new strategies
- Sources choose appropriate strategy
- Testable in isolation

### 4. Session Pooling Pattern (Connection Reuse)

**Problem**: Creating new HTTP connections for each request is slow

**Solution**: Shared session pool for all sources

```python
class SessionPool:
    def __init__(self):
        self._session = None

    def get_session(self):
        """
        Get or create shared requests.Session

        Benefits:
        - Connection reuse (HTTP keep-alive)
        - Cookie persistence
        - Retry logic configuration
        - Timeout management
        """
        if self._session is None:
            self._session = requests.Session()

            # Configure retry logic
            retry = Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry)

            self._session.mount('http://', adapter)
            self._session.mount('https://', adapter)

            # Set default headers
            self._session.headers.update({
                'User-Agent': 'Capcat/2.0 (News Archiver)'
            })

        return self._session

    def close(self):
        """Clean up session"""
        if self._session:
            self._session.close()
            self._session = None
```

**Benefits**:
- Faster subsequent requests (connection reuse)
- Consistent retry logic
- Centralized header management
- Resource cleanup on exit

### 5. Observer Pattern (Progress Tracking)

**Problem**: Need to report progress without tight coupling

**Solution**: Progress observers notify UI components

```python
class ProgressTracker:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        """Register progress observer"""
        self._observers.append(observer)

    def update_progress(self, current, total, message=""):
        """Notify all observers of progress update"""
        for observer in self._observers:
            observer.on_progress(current, total, message)

class TerminalProgressObserver:
    def on_progress(self, current, total, message):
        """Display progress bar in terminal"""
        percentage = (current / total) * 100
        bar = "=" * int(percentage / 2)
        print(f"\r[{bar:<50}] {percentage:.0f}% {message}", end="")

class LogProgressObserver:
    def on_progress(self, current, total, message):
        """Log progress to file"""
        logger.info(f"Progress: {current}/{total} - {message}")
```

**Benefits**:
- Decoupled progress reporting
- Multiple output formats (terminal, log, GUI)
- Easy to add new observers
- Core logic unaware of UI

---

## Data Flow

### Complete Article Fetching Flow

```
User Input
    |
    v
[CLI Parser]
    |
    ├─> Parse command (fetch, bundle, single)
    ├─> Validate arguments
    └─> Extract parameters (count, sources, options)
    |
    v
[Source Registry]
    |
    ├─> Resolve source IDs (hn -> HackerNewsSource)
    ├─> Expand bundles (tech -> [gizmodo, futurism, ieee])
    └─> Validate sources exist
    |
    v
[Source Factory]
    |
    ├─> Create source instances
    ├─> Inject shared session
    └─> Configure source parameters
    |
    v
[Parallel Processing]
    |
    ├─> For each source concurrently:
    │   |
    │   └─> [Source.get_articles(count)]
    │       |
    │       ├─> Discover article URLs
    │       ├─> Fetch article content
    │       ├─> Extract text/media
    │       └─> Return Article objects
    |
    v
[Content Processing]
    |
    ├─> For each article:
    │   |
    │   ├─> [ArticleFetcher.fetch_content(url)]
    │   │   ├─> HTTP request with retries
    │   │   ├─> Parse HTML with BeautifulSoup
    │   │   └─> Extract via selectors
    │   |
    │   ├─> [UnifiedMediaProcessor.process(article)]
    │   │   ├─> Identify media URLs
    │   │   ├─> Download files (parallel)
    │   │   ├─> Convert to local paths
    │   │   └─> Embed in content
    │   |
    │   └─> [HTMLConverter.to_markdown(html)]
    │       ├─> Clean HTML
    │       ├─> Convert to Markdown
    │       └─> Format output
    |
    v
[Output Generation]
    |
    ├─> [FileWriter.create_structure()]
    │   ├─> Generate folder paths
    │   └─> Create directories
    |
    ├─> [FileWriter.write_article()]
    │   ├─> Write article.md
    │   ├─> Save metadata
    │   └─> Copy media files
    |
    └─> [HTMLGenerator.generate()] (if --html)
        ├─> Load template
        ├─> Render HTML
        └─> Write html/index.html
    |
    v
[Completion]
    |
    ├─> Display summary
    ├─> Log statistics
    └─> Clean up resources
```

---

## Error Handling Strategy

### Error Hierarchy

```python
CapcatError (Base exception)
├── ConfigurationError
│   ├── InvalidConfigError
│   └── MissingConfigError
├── SourceError
│   ├── SourceNotFoundError
│   ├── SourceUnavailableError
│   └── ArticleFetchError
├── NetworkError
│   ├── ConnectionError
│   ├── TimeoutError
│   └── DNSError
├── ProcessingError
│   ├── ParseError
│   ├── ConversionError
│   └── MediaDownloadError
└── FileSystemError
    ├── PermissionError
    ├── DiskFullError
    └── PathError
```

### Error Handling Patterns

```python
def fetch_with_retry(url, max_retries=3):
    """
    Fetch URL with exponential backoff retry

    Logic:
    1. Try request
    2. If fails, wait and retry
    3. Exponential backoff: 1s, 2s, 4s
    4. After max_retries, raise exception
    """
    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            return response

        except requests.Timeout:
            if attempt == max_retries - 1:
                raise TimeoutError(f"Request timeout after {max_retries} attempts")
            time.sleep(2 ** attempt)  # Exponential backoff

        except requests.ConnectionError:
            if attempt == max_retries - 1:
                raise NetworkError(f"Connection failed after {max_retries} attempts")
            time.sleep(2 ** attempt)

        except requests.HTTPError as e:
            if e.response.status_code >= 500:
                # Server error, retry
                if attempt == max_retries - 1:
                    raise SourceUnavailableError(f"Server error: {e}")
                time.sleep(2 ** attempt)
            else:
                # Client error, don't retry
                raise ArticleFetchError(f"HTTP {e.response.status_code}: {e}")
```

### Graceful Degradation

```python
def process_articles(articles):
    """
    Process articles with graceful failure handling

    Strategy:
    - Continue processing on individual failures
    - Collect errors for reporting
    - Save successful articles
    - Report summary at end
    """
    successful = []
    failed = []

    for article in articles:
        try:
            processed = process_article(article)
            successful.append(processed)

        except MediaDownloadError as e:
            # Save article without media
            logger.warning(f"Media download failed: {e}")
            article.media_warning = str(e)
            successful.append(article)

        except ProcessingError as e:
            # Skip this article, continue with others
            logger.error(f"Failed to process article: {e}")
            failed.append((article, e))

        except Exception as e:
            # Unexpected error, log and continue
            logger.exception(f"Unexpected error: {e}")
            failed.append((article, e))

    # Report summary
    logger.info(f"Processed {len(successful)}/{len(articles)} articles")
    if failed:
        logger.warning(f"Failed articles: {len(failed)}")
        for article, error in failed:
            logger.warning(f"  - {article.title}: {error}")

    return successful, failed
```

---

## Performance Optimizations

### 1. Parallel Article Fetching

```python
def fetch_articles_parallel(sources, count):
    """
    Fetch articles from multiple sources concurrently

    Performance gain: 5x faster than sequential
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=len(sources)) as executor:
        # Submit all source fetching tasks
        future_to_source = {
            executor.submit(source.get_articles, count): source
            for source in sources
        }

        # Collect results as they complete
        results = {}
        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                articles = future.result(timeout=300)  # 5 min timeout
                results[source.id] = articles
            except Exception as e:
                logger.error(f"Source {source.id} failed: {e}")
                results[source.id] = []

    return results
```

### 2. Connection Pooling

**Benefit**: Reuse TCP connections instead of creating new ones

```python
# Without pooling
for url in urls:
    response = requests.get(url)  # New connection each time
    # 100-500ms connection overhead per request

# With pooling (via Session)
session = requests.Session()
for url in urls:
    response = session.get(url)  # Reuse existing connection
    # ~10ms overhead after first connection
```

**Performance Impact**:
- First request: 500ms (connection + data)
- Subsequent requests: 150ms (data only)
- 70% time reduction for multi-request sources

### 3. Lazy Loading

```python
class Article:
    def __init__(self, url, title):
        self.url = url
        self.title = title
        self._content = None  # Lazy loaded
        self._comments = None  # Lazy loaded

    @property
    def content(self):
        """Lazy load content only when accessed"""
        if self._content is None:
            self._content = fetch_content(self.url)
        return self._content

    @property
    def comments(self):
        """Lazy load comments only when accessed"""
        if self._comments is None:
            self._comments = fetch_comments(self.url)
        return self._comments
```

**Benefit**: Don't fetch content not needed (e.g., comments if --no-comments)

### 4. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def fetch_source_config(source_id):
    """
    Cache source configurations

    Avoids: Re-reading YAML files multiple times
    """
    config_path = Path(f"sources/active/config_driven/configs/{source_id}.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)
```

---

## Testing Strategy

### Unit Testing

```python
# Test individual components in isolation

class TestSourceRegistry:
    def test_discover_sources(self):
        registry = SourceRegistry()
        sources = registry.discover_sources()

        assert len(sources) > 0
        assert 'hn' in sources
        assert 'bbc' in sources

    def test_get_source(self):
        registry = SourceRegistry()
        registry.discover_sources()

        source = registry.get_source('hn')

        assert isinstance(source, BaseSource)
        assert source.id == 'hn'
        assert source.display_name == 'Hacker News'
```

### Integration Testing

```python
# Test component interactions

class TestArticleFetching:
    def test_fetch_and_process_article(self):
        source = HackerNewsSource(config, session)
        articles = source.get_articles(count=5)

        assert len(articles) == 5

        for article in articles:
            # Test content fetching
            assert article.content is not None
            assert len(article.content) > 100

            # Test media processing
            assert article.images is not None

            # Test output generation
            output_path = generate_output(article)
            assert output_path.exists()
            assert (output_path / "article.md").exists()
```

### End-to-End Testing

```python
# Test complete user workflows

def test_bundle_command():
    """Test: ./capcat bundle tech --count 10"""
    result = subprocess.run(
        ["./capcat", "bundle", "tech", "--count", "10"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "articles saved" in result.stdout

    # Verify output structure
    news_dir = Path("../News")
    assert news_dir.exists()

    # Check created folders
    date_str = datetime.now().strftime('%d-%m-%Y')
    batch_dir = news_dir / f"news_{date_str}"
    assert batch_dir.exists()

    # Count articles
    article_dirs = list(batch_dir.rglob("*/article.md"))
    assert len(article_dirs) >= 10  # Should have ~30 (10 per source)
```

---

## Configuration Management

### Configuration Hierarchy

```
1. Command-line arguments (highest priority)
2. Environment variables
3. Config file (capcat.yml)
4. Default values (lowest priority)
```

### Config File Structure

```yaml
# capcat.yml

# Default settings
default_count: 30
output_directory: "../News"
media_downloads: false  # images only
html_generation: false

# Network settings
timeout: 30
max_retries: 3
user_agent: "Capcat/2.0"

# Source preferences
preferred_sources:
  - hn
  - bbc
  - nature

# Bundle definitions (custom)
custom_bundles:
  mytech:
    sources: [hn, lb, iq, ieee]
    description: "My tech bundle"

# Logging
log_level: INFO
log_file: "capcat.log"

# Privacy
anonymize_usernames: true
```

### Config Loading Logic

```python
def get_config():
    """
    Load configuration from multiple sources

    Priority:
    1. CLI args override everything
    2. Environment variables override file
    3. Config file overrides defaults
    4. Built-in defaults
    """
    # Start with defaults
    config = {
        'default_count': 30,
        'output_directory': '../News',
        'media_downloads': False,
        'html_generation': False,
        'timeout': 30,
    }

    # Load from config file if exists
    config_file = Path('capcat.yml')
    if config_file.exists():
        with open(config_file) as f:
            file_config = yaml.safe_load(f)
            config.update(file_config)

    # Override with environment variables
    if 'CAPCAT_OUTPUT_DIR' in os.environ:
        config['output_directory'] = os.environ['CAPCAT_OUTPUT_DIR']

    if 'CAPCAT_DEFAULT_COUNT' in os.environ:
        config['default_count'] = int(os.environ['CAPCAT_DEFAULT_COUNT'])

    # CLI arguments applied by argparse in cli.py

    return config
```

---

## Security Considerations

### 1. Input Validation

```python
def validate_count(count):
    """Validate article count parameter"""
    if not isinstance(count, int):
        raise ValidationError("Count must be integer")

    if count < 1:
        raise ValidationError("Count must be positive")

    if count > 1000:
        raise ValidationError("Count limited to 1000 (performance)")

    return count

def validate_url(url):
    """Validate single article URL"""
    parsed = urllib.parse.urlparse(url)

    if not parsed.scheme in ['http', 'https']:
        raise ValidationError("URL must use http or https")

    if not parsed.netloc:
        raise ValidationError("Invalid URL format")

    return url
```

### 2. Path Sanitization

```python
def sanitize_path(user_input):
    """
    Prevent path traversal attacks

    Blocks: ../../../etc/passwd
    """
    # Remove path traversal attempts
    cleaned = user_input.replace('..', '')

    # Remove absolute paths
    cleaned = cleaned.lstrip('/')

    # Remove special characters
    cleaned = re.sub(r'[^\w\s-]', '', cleaned)

    return cleaned
```

### 3. Username Anonymization

```python
def anonymize_comment(comment_html):
    """
    Replace usernames with 'Anonymous' for privacy

    Preserves: Profile links (for attribution)
    Removes: Identifying usernames in text
    """
    soup = BeautifulSoup(comment_html, 'lxml')

    # Find username elements
    for username_elem in soup.find_all(class_='username'):
        original_username = username_elem.get_text()
        profile_url = username_elem.find('a')['href']

        # Replace with anonymous
        username_elem.string = 'Anonymous'

        # Preserve profile link (for attribution)
        username_elem['data-original-profile'] = profile_url

    return str(soup)
```

---

**Document Status**: Living document
**Last Updated**: 2025-01-06
**Target Audience**: Junior developers, new team members
**Prerequisites**: Python basics, HTTP fundamentals
**Next Steps**: Read 02-development-workflow.md
