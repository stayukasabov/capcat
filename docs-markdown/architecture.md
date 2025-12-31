# Architecture Overview

Capcat 2.0 implements a hybrid architecture that combines config-driven simplicity with custom implementation flexibility.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Capcat 2.0 Architecture                │
├─────────────────────────────────────────────────────────────┤
│  User Interface Layer                                       │
│  ├── Interactive Mode (catch)                             │
│  │   ├── Main menu (bundle/fetch/single/manage/exit)      │
│  │   └── Source management submenu                         │
│  └── CLI Interface (capcat.py)                            │
│      ├── bundle tech|news|science|aggregators              │
│      ├── fetch source1,source2,source3                     │
│      └── single https://example.com/article                │
├─────────────────────────────────────────────────────────────┤
│  Core Processing Layer                                      │
│  ├── SourceRegistry (Discovery & Management)               │
│  ├── SourceFactory (Instantiation & Pooling)              │
│  ├── PerformanceMonitor (Metrics & Health)                 │
│  └── ValidationEngine (Quality Assurance)                  │
├─────────────────────────────────────────────────────────────┤
│  Hybrid Source Layer                                       │
│  ├── Config-Driven Sources (5 sources)                    │
│  │   └── YAML configurations → ConfigDrivenSource          │
│  └── Custom Sources (6 sources)                            │
│      └── Python implementations → BaseSource               │
├─────────────────────────────────────────────────────────────┤
│  Shared Infrastructure                                      │
│  ├── SessionPool (Network Optimization)                    │
│  ├── ArticleFetcher (Content Processing)                   │
│  ├── TemplateSystem (HTML Generation)                      │
│  │   ├── article-with-comments.html                        │
│  │   ├── article-no-comments.html                          │
│  │   └── comments-with-navigation.html                     │
│  ├── UnifiedMediaProcessor (Image/Media Embedding)         │
│  │   ├── MediaEmbeddingProcessor (Core Engine)             │
│  │   ├── ImageProcessor (Global Image Coordinator)        │
│  │   ├── WebsiteClassifier (Aggregator Protection)        │
│  │   ├── MediaConfigManager (Source Configs)              │
│  │   └── Source-specific media processing configs          │
│  ├── MediaDownloader (Images/Videos/Documents)             │
│  └── Formatter (HTML → Markdown)                           │
└─────────────────────────────────────────────────────────────┘
```

## Hybrid Source Types

### Config-Driven Sources (Simple)
**Purpose**: Simplified development for straightforward news sites
**Count**: 5 sources
**Examples**: InfoQ, Straits Times, Gizmodo, IEEE, Scientific American

```yaml
# Example: sources/active/config_driven/configs/iq.yaml
display_name: "InfoQ"
base_url: "https://www.infoq.com/news/"
category: tech
article_selectors:
  - .card__title a
  - .news-headline a
content_selectors:
  - .article__content
  - article.article
```

**Benefits**:
- No Python coding required
- Rapid deployment
- Easy maintenance through configuration updates
- Automatic validation and testing

### Custom Sources (Complex)
**Purpose**: Full flexibility for complex scraping scenarios
**Count**: 6 sources
**Examples**: Hacker News, BBC, CNN, Nature, Lobsters, LessWrong

```python
# Example: sources/active/custom/hn/source.py
class HackerNewsSource(BaseSource):
    def get_articles(self, count=30):
        # Custom logic for Hacker News API integration
        # Comment system handling
        # Anti-bot protection workarounds
        pass
```

**Benefits**:
- Full control over scraping logic
- Comment system integration
- Anti-bot protection handling
- Dynamic content loading support

## Core Components

### 1. SourceRegistry Pattern
**Location**: `core/source_system/source_registry.py`
**Purpose**: Auto-discovery and management of all sources

```python
# Automatic source discovery
registry = get_source_registry()
sources = registry.discover_sources()  # Returns 20 sources

# Source instantiation with session pooling
source = registry.get_source('hn', session=global_session)
```

**Features**:
- Auto-discovery from `sources/active/`
- Validation during discovery
- Source type management (config vs custom)
- Instance caching for performance

### 2. Factory Pattern Implementation
**Location**: `core/source_system/source_factory.py`
**Purpose**: Unified source creation with monitoring integration

```python
# Factory creates appropriate source type
source = SourceFactory.create_source(config, session)

# Automatic performance monitoring integration
metrics = source.get_performance_metrics()
```

**Features**:
- Unified creation interface
- Performance monitoring integration
- Health checking capabilities
- Session pool optimization

### 3. Performance Monitoring System
**Location**: `core/source_system/performance_monitor.py`
**Purpose**: Real-time metrics and health tracking

```python
@dataclass
class SourceMetrics:
    source_name: str
    total_requests: int = 0
    successful_requests: int = 0
    avg_response_time: float = 0.0
    articles_discovered: int = 0

    @property
    def success_rate(self) -> float:
        return (self.successful_requests / self.total_requests) * 100
```

**Capabilities**:
- Real-time performance tracking
- Success rate monitoring
- Response time analysis
- Health status reporting

### 4. Enhanced Validation Engine
**Location**: `core/source_system/validation_engine.py`
**Purpose**: Comprehensive source validation and quality assurance

**Validation Types**:
- **Basic**: Configuration syntax and format
- **Network**: Connectivity and accessibility testing
- **Selectors**: CSS selector effectiveness
- **Deep**: Live content validation

```python
# Comprehensive validation
results = validation_engine.validate_all_sources(configs, deep=True)
report = validation_engine.generate_validation_report(results)
```

### 5. Interactive Mode System
**Location**: `core/interactive.py`
**Purpose**: User-friendly menu interface for all Capcat operations

**Architecture**:
```python
# Main interactive loop
start_interactive_mode()
├── Main Menu
│   ├── Bundle selection
│   ├── Multi-source fetch
│   ├── Single source fetch
│   ├── Single URL fetch
│   └── Source management submenu
└── Source Management Submenu
    ├── Add RSS source
    ├── Generate config
    ├── Remove sources
    ├── List sources
    └── Test source
```

**Key Features**:
- **Questionary UI Framework**: Terminal-based interactive menus
- **Logging Suppression**: Clean display during navigation
- **Screen Management**: Automatic clearing and formatting
- **CLI Integration**: Constructs argument lists for `run_app()`
- **Error Handling**: Graceful failures with return to menu

**Technology Stack**:
```python
# UI Framework
from questionary import select, checkbox, text, confirm

# Custom styling
custom_style = Style([
    ('selected', 'fg:#d75f00'),  # Orange theme
    ('pointer', 'fg:#d75f00 bold'),
])

# Screen control
print('\033[2J\033[H', end='')  # Clear screen
```

**Integration Points**:
- Uses `cli.py` functions for source lists and bundles
- Calls `run_app()` from `capcat.py` for execution
- Integrates with source registry for discovery
- Uses source management services for add/remove operations

**Benefits**:
- Zero command memorization
- Visual feedback
- Error prevention through validation
- Ideal for new users and daily operations
- Complements CLI for advanced use cases

For detailed documentation, see [Interactive Mode Guide](interactive-mode.html).

## Session Pooling Architecture

```python
# Global session pool for optimal performance
class SessionPool:
    def __init__(self):
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(pool_connections=20, pool_maxsize=20))
        self.session.mount('https://', HTTPAdapter(pool_connections=20, pool_maxsize=20))

# All sources share the same optimized session
global_session = get_global_session()
```

**Benefits**:
- Connection reuse across sources
- Reduced latency
- Improved throughput
- Resource efficiency

## Content Processing Architecture

### Separated Article and Comment Workflows

**Design Principle**: Complete separation of concerns for better maintainability and error isolation.

```python
# Clean separation pattern
class SourceImplementation:
    def fetch_article_content(self, url, ...):
        # Handles ONLY article content extraction and media
        pass

    def fetch_comments(self, comment_url, article_folder):
        # Handles ONLY comment extraction and formatting
        pass
```

### Article Processing Pipeline

```
Article URL → Content Extraction → Media Processing → Markdown Conversion
                                ↓
                          Fallback Image Detection (if needed)
                                ↓
                          Final Article + Additional Images
```

**Key Components**:
1. **Primary Content Extraction**: Uses source-specific or CSS selectors
2. **Media Processing**: Downloads images (always) + other media (with --media)
3. **Fallback Image Detection**: Automatic activation when < 2 images found
4. **Markdown Generation**: Clean HTML-to-Markdown conversion

### Fallback Image Detection System

**Smart Content Recovery**: Handles websites without custom configurations by scanning entire pages for content images.

```python
# Automatic activation logic
if primary_image_count < 2:
    logger.info("Activating fallback image detection")

    # Full page analysis
    additional_images = scan_full_page(
        original_html=full_page_html,
        existing_images=found_images,
        ui_filters=intelligent_filters
    )
```

**Intelligent Filtering**:
- **UI Element Detection**: Removes logos, navigation, ads, social icons
- **Size Filtering**: Skips images < 150px dimensions
- **Pattern Matching**: Filters by class, ID, alt text, and URL patterns
- **Duplicate Prevention**: Avoids re-downloading existing images

**Filter Categories**:
```yaml
ui_patterns:
  class_patterns: [logo, icon, avatar, nav, menu, ad, banner, social, share]
  id_patterns: [logo, icon, nav, header, footer, sidebar]
  alt_patterns: [logo, icon, advertisement, navigation, social]
  src_patterns: [logo, icon, avatar, ad, pixel, tracker, beacon, analytics]
```

### Comment Processing Pipeline

```
Comment URL → Comment Extraction → Thread Building → Markdown Generation
                                                  ↓
                               User Privacy Protection (anonymization)
                                                  ↓
                                      comments.md file
```

**Independent Processing Benefits**:
- **Error Isolation**: Comment failures don't affect articles
- **Clean Interfaces**: No parameter pollution
- **Source Flexibility**: Each source handles comments differently
- **Performance**: Parallel processing possible
- **Maintainability**: Clear separation of concerns

**Privacy Protection**:
```python
# Automatic user anonymization
comment_data = {
    'author': 'Anonymous',  # Privacy-compliant
    'original_profile': original_profile_link,  # Reference preserved
    'text': cleaned_comment_text,
    'timestamp': comment_timestamp
}
```

## Unified Media Processing Architecture

### Overview
The Unified Media Processing System eliminates the "whack-a-mole" pattern of fixing image embedding issues source by source. Instead of debugging each source individually, the system provides a single, configurable solution that works across all sources.

### Architecture Components

#### MediaEmbeddingProcessor
**Location**: `core/media_embedding_processor.py`
**Purpose**: Core engine for image extraction, downloading, and URL replacement

```python
from core.unified_media_processor import UnifiedMediaProcessor

# Simple integration for any source
updated_content = UnifiedMediaProcessor.process_article_media(
    content=markdown_content,
    html_content=html_content,
    url=article_url,
    article_folder=article_folder,
    source_name=source_name,
    session=session
)
```

#### MediaConfigManager
**Location**: `core/media_config.py`
**Purpose**: Source-specific media processing configurations

```python
# Predefined configurations for major sources
configs = {
    '': {
        'hero_image_selectors': ['.featured-image img', '.post-thumbnail img'],
        'url_patterns': {'wordpress': ['/wp-content/uploads/']},
        'quality_thresholds': {'min_width': 150, 'min_height': 150}
    },
    '': {
        'hero_image_selectors': ['.featured-image img', '.hero-image img'],
        'url_patterns': {'': ['i..com/', '.com/wp-content/']},
        'skip_patterns': ['advertisement', 'ad-', 'sponsored']
    }
}
```

### Key Features

#### 1. Source-Specific Configuration
- **Hero Image Detection**: Custom selectors per source
- **URL Pattern Recognition**: WordPress, CDN, and custom patterns
- **Quality Filtering**: Size and file type thresholds
- **Skip Patterns**: Advertisements and irrelevant images

#### 2. URL Processing Strategies
- **Protocol-relative URLs**: `//domain.com/image.jpg` → `https://domain.com/image.jpg`
- **WordPress URLs**: `/wp-content/uploads/2025/09/image.jpg` → `images/image.jpg`
- **Relative URLs**: `/media/image.jpg` → `https://domain.com/media/image.jpg`
- **Absolute URLs**: Direct processing with domain validation

#### 3. Markdown Integration
- **BeautifulSoup Parsing**: Extract images from original HTML
- **Regex URL Replacement**: Multiple strategies for reliable replacement
- **Local Path Generation**: Consistent `images/filename.jpg` format
- **Content Preservation**: Maintains alt text and image context

### Integration Points

The unified system integrates at the NewsSourceArticleFetcher level in `core/news_source_adapter.py`:

```python
# Automatic source detection from URL domain
source_name = self._detect_source_from_url(url)

# Process media with unified system
updated_content = UnifiedMediaProcessor.process_article_media(
    content=article_content,
    html_content=response.text,
    url=url,
    article_folder=article_folder_path,
    source_name=source_name,
    session=self.session
)
```

### Benefits Achieved

1. **Eliminated "Whack-a-Mole" Pattern**: Single fix applies to all 25+ sources
2. **Configurable Processing**: Easy to add new sources or adjust existing ones
3. **Consistent Behavior**: Same processing logic across all sources
4. **Maintainable Architecture**: Centralized instead of scattered fixes
5. **Robust Error Handling**: Graceful fallbacks and comprehensive logging

### Performance Metrics

```
| Source   | Images Processed | Success Rate | Processing Time |
|----------|------------------|--------------|-----------------|
| Gizmodo  | 27 images        | 100%         | ~6.6s          |
| Futurism | 17 images        | 100%         | ~5.7s          |
| IEEE     | 1 image          | 100%         | ~2.2s          |
```

## Performance Characteristics

```
| Metric           | Config-Driven | Custom      | Hybrid Average |
|------------------|---------------|-------------|----------------|
| Development Time | 15-30 min     | 2-4 hours   | 45 min         |
| Code Lines       | ~10 (YAML)    | ~200-400    | ~100           |
| Maintenance      | Config update | Code change | Mixed          |
| Flexibility      | Limited       | Full        | Optimal        |
| Performance      | Excellent     | Variable    | Excellent      |
```

## Simple Protection System

### Overview
The Simple Protection System provides efficient protection against link aggregators and oversized images using clear, maintainable rules. It replaces the complex Website Classifier with simple heuristics that are easy to understand and modify.

### Protection Rules

```
┌──────────────────────────────────────────────────────────────────┐
│                      Simple Protection Rules                    │
├──────────────────────┬─────────────────────────────────────────────┤
│ Protection Type      │ Rule                                        │
├──────────────────────┼─────────────────────────────────────────────┤
│ Aggregator Detection │ Link density > 15% OR > 10 external domains│
│ Per-Image Filtering  │ Skip images > 5MB OR < 150px               │
│ Image Count Limit    │ Maximum 20 images per article              │
│ --media Flag         │ Increases limit to 1000 images             │
└──────────────────────┴─────────────────────────────────────────────┘
```

### Simple Detection Logic

**Aggregator Detection**:
- Link density > 15% of content (links per word count)
- Links to > 10 different external domains
- Navigation links automatically excluded from analysis

**Per-Image Filtering**:
- HEAD request checks image size before download
- Skip images > 5MB (unless --media flag used)
- Skip images < 150px (likely icons/decorative)
- Skip non-image content types

### Real-World Protection Examples

**Aggregator Site Example**:
```
Input: News aggregator with many external links
Analysis:
  - Word count: 200, Links: 35 → Link density: 17.5% (above 15%)
  - External domains: 12 (above 10 threshold)
Result: BLOCKED (aggregator detected)
```

**Normal Article Example**:
```
Input: Technical article about React optimization
Analysis:
  - Word count: 800, Links: 5 → Link density: 0.6% (below 15%)
  - External domains: 2 (below 10 threshold)
Result: ALLOWED (up to 20 images)
```

### --media Flag Integration

```python
# Normal behavior (without --media)
max_images = 20  # Standard limit

# With --media flag
if media_enabled:
    max_images = 1000  # Very high limit
    # Per-image 5MB limit still applies for safety
```

**Edge Case Handling**:
- `--media` flag increases image count limit to 1000
- Per-image size checking still applies for safety
- Aggregator detection still blocks problematic sites
- Simple, predictable behavior

### Architecture Integration

**Location**: `core/simple_protection.py`
**Integration Point**: `core/image_processor.py`

```python
# Simple protection check during image processing
protection_result = self.protection.check_content(html_content, base_url)

# Skip if aggregator detected
if protection_result.is_aggregator:
    logger.warning(f"Skipping aggregator site: {base_url}")
    return {}
```

**Performance Characteristics**:
- **Fast Analysis**: Content metrics extracted in ~10ms
- **No Network Calls**: Uses only downloaded content
- **Memory Efficient**: Processes content in streaming fashion
- **Logging**: Detailed classification reasoning for debugging

## Configuration Management

**Hierarchy** (highest to lowest priority):
1. Command-line arguments
2. Environment variables
3. Configuration files (`capcat.yml`)
4. Default values

```yaml
# Example: capcat.yml
network:
  connect_timeout: 10
  read_timeout: 8
  user_agent: "Mozilla/5.0 (compatible; Capcat/2.0)"

processing:
  max_workers: 8
  download_images: true
  download_videos: false

logging:
  default_level: "INFO"
  use_colors: true
```

## Template System Architecture

**Universal HTML Generation**: Consistent navigation and professional output across all sources.

### Template Components

```
templates/
├── article-with-comments.html     # For sources supporting comments (HN, Lobsters, LessWrong)
├── article-no-comments.html       # For sources without comments (BBC, CNN, Nature, etc.)
└── comments-with-navigation.html  # For all comments pages (Back to Article button)
```

### Template Configuration

```yaml
# Source template configuration
template:
  variant: "article-with-comments"  # or "article-no-comments"
  navigation:
    back_to_news_url: "../../news.html"
    back_to_news_text: "Back to News"
    has_comments: true
    comments_url: "comments.html"
    comments_text: "View Comments"
```

### Navigation Logic

- **Article Pages (with comments)**: "Back to News" + "View Comments"
- **Article Pages (no comments)**: "Back to News" only
- **Comments Pages**: "Back to Article" only

### Source Detection

Template system automatically detects 30+ source patterns:
- Hacker-News, Lobsters, LessWrong → `article-with-comments`
- BBC, CNN, Nature → `article-no-comments`
- All comments pages → `comments-with-navigation`

### Benefits

- **100% Navigation Consistency**: Same patterns across all sources
- **Professional Appearance**: Template-driven HTML with themes
- **Easy Maintenance**: Update all sources by modifying templates
- **Scalable**: Add new sources with simple YAML configuration

## Testing Architecture

**Test Levels**:
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Cross-component functionality
3. **Source Tests**: Individual source validation
4. **System Tests**: End-to-end workflow validation

```python
# Comprehensive testing framework
python test_comprehensive_sources.py  # Tests all 20 sources
python test_validation_engine.py      # Tests validation system
python test_performance_monitor.py    # Tests monitoring system
```

## Extension Points

### Adding New Config-Driven Sources
```yaml
# 1. Create YAML configuration
# sources/active/config_driven/configs/newsource.yaml
display_name: "New Source"
base_url: "https://newsource.com/"
article_selectors: [".headline a"]
content_selectors: [".article-content"]

# 2. Source automatically discovered and available
```

### Adding New Custom Sources
```python
# 1. Create source directory and files
# sources/active/custom/newsource/
# ├── source.py          # BaseSource implementation
# └── config.yaml        # Source configuration

# 2. Implement BaseSource contract
class NewSource(BaseSource):
    def get_articles(self, count=30):
        # Custom implementation
        pass
```

## Error Handling Strategy

**Graceful Degradation**:
- Individual source failures don't affect others
- Partial success reported clearly
- Detailed error logging for debugging
- Automatic retry mechanisms for transient failures

**Error Categories**:
- **Network**: Timeouts, connection failures
- **Parsing**: Invalid HTML, missing selectors
- **Configuration**: Invalid YAML, missing fields
- **Logic**: Custom source implementation errors

## HTML Generation Architecture

Capcat 2.0 features a **compartmentalized HTML generation system** that replaces monolithic conditional logic with source-specific configurations and templates.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                 HTML Generation System                     │
├─────────────────────────────────────────────────────────────┤
│  Factory Pattern                                           │
│  ├── HTMLGeneratorFactory                                  │
│  └── Source-specific Generator Instances                   │
├─────────────────────────────────────────────────────────────┤
│  Base System                                               │
│  ├── BaseHTMLGenerator (Abstract)                          │
│  ├── Base Templates ({{}} syntax)                          │
│  └── Configuration Schema                                  │
├─────────────────────────────────────────────────────────────┤
│  Source-Specific Implementations                           │
│  ├── htmlgen/hn/                                          │
│  │   ├── config.yaml                                      │
│  │   ├── generator.py                                     │
│  │   └── templates/ (overrides)                           │
│  ├── htmlgen//                                   │
│  └── htmlgen/lb/                                          │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

**1. Configuration-Driven Behavior**
```yaml
# htmlgen/hn/config.yaml
comments:
  enabled: true
  pattern: '\*\*Anonymous\*\*\s*\(\[profile\]\([^)]*\)\)'
  conditional_display: true

navigation:
  breadcrumb_style: "technical"
  date_format: "YYYY-MM-DD"

layout:
  template_set: "base"
  custom_css_classes:
    - "hn-style"
    - "tech-focused"
```

**2. Template System with Override Capability**
- **Base Templates**: `htmlgen/base/templates/` using clean `{{}}` syntax
- **Source Overrides**: `htmlgen/[source]/templates/` for custom layouts
- **Fallback Logic**: Jinja2 with string replacement fallback

**3. Privacy-Compliant Comment Processing**
```python
def count_comments(self, comments_file: Path) -> int:
    pattern = self.source_config['comments']['pattern']
    matches = re.findall(pattern, content)
    return len(matches)
```

**4. Validation and Testing**
- JSON Schema validation for all configurations
- Comprehensive test suite with 100% pass rate
- Source-specific pattern validation

### Benefits

- **Maintainability**: No more monolithic conditional logic
- **Extensibility**: Easy to add new sources with YAML config
- **Consistency**: Standardized configuration schema
- **Privacy**: Built-in anonymization pattern support
- **Performance**: Template caching and optimization
- **Testing**: Isolated testing per source

### Usage Example

```python
# Automatic factory instantiation
generator = HTMLGeneratorFactory.create_generator("hn")

# Source-specific behavior from config
comment_count = generator.count_comments(comments_file)
should_show = generator.should_show_comment_link(comment_count)

# Template rendering with source customization
html_content = generator.render_template("article.html", context)
```

## Privacy & Anonymization Architecture

**Comment Processing Pipeline**:
1. **Collection**: Comments fetched from source APIs
2. **Anonymization**: Usernames replaced with "Anonymous"
3. **Link Preservation**: Profile URLs preserved for reference
4. **Pattern Recognition**: Source-specific regex patterns match anonymized format
5. **HTML Generation**: Templates render privacy-compliant output

**Legal Compliance Features**:
- No personal username storage
- Anonymous-only display in all outputs
- Functional profile links preserved
- Transparent privacy policy
- Source attribution maintained

## Design Principles

1. **Separation of Concerns**: Config vs logic clearly separated
2. **Single Responsibility**: Each component has focused purpose
3. **Open/Closed**: Open for extension, closed for modification
4. **DRY**: No code duplication across sources
5. **Performance**: Session pooling and connection optimization
6. **Testability**: Comprehensive testing at all levels
7. **Maintainability**: Clear patterns and documentation
8. **Privacy by Design**: Built-in anonymization and compliance
9. **Template Modularity**: Reusable components with override capability

---

*This architecture provides the foundation for scalable, maintainable news source management with optimal performance characteristics.*