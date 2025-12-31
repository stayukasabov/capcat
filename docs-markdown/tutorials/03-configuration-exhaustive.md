# Configuration Exhaustive Reference

Complete documentation of EVERY configuration option, file, environment variable, and setting in Capcat.

Source: Application/core/config.py, Application/docs/configuration.md

## Configuration Hierarchy

Settings are applied in this order (highest to lowest priority):

1. **Command-line arguments** - Immediate override (e.g., `--count 10`)
2. **Environment variables** - Session-specific (e.g., `export CAPCAT_MAX_WORKERS=16`)
3. **Configuration files** - Persistent settings (`capcat.yml`, `capcat.json`)
4. **Default values** - Hard-coded in Application/core/config.py

**Example Resolution:**
```bash
# capcat.yml has: default_count: 20
# Environment: export CAPCAT_DEFAULT_COUNT=40
# Command: ./capcat fetch hn --count 10

# Result: Uses 10 (CLI wins)
```

## Configuration Files

### File Locations

**Search Order:**
1. Path specified with `--config FILE` flag
2. `./capcat.yml` (current directory)
3. `./capcat.json` (current directory)
4. `~/.capcat/capcat.yml` (user home)
5. `~/.capcat/capcat.json` (user home)

**File Format Detection:**
- `.yml` or `.yaml` - YAML format (recommended)
- `.json` - JSON format
- Auto-detected based on extension

### capcat.yml Structure

Complete YAML configuration with ALL options:

```yaml
# Application/capcat.yml - Complete configuration

# ============================================================
# NETWORK CONFIGURATION
# ============================================================
network:
  # HTTP Timeouts (seconds)
  connect_timeout: 10           # Connection establishment timeout
  read_timeout: 30              # Response read timeout (increased for complex articles)
  media_download_timeout: 60    # Media file download timeout
  head_request_timeout: 10      # HEAD request timeout for size checks

  # Connection Pooling
  pool_connections: 20          # Number of connection pools to cache
  pool_maxsize: 20             # Maximum connections per pool

  # User Agent
  user_agent: "Capcat/2.0 (Personal news archiver)"

  # Request Retries
  max_retries: 3               # Maximum retry attempts for failed requests
  retry_delay: 1.0             # Base delay between retries (seconds)

# ============================================================
# PROCESSING CONFIGURATION
# ============================================================
processing:
  # Concurrency Settings
  max_workers: 8               # Parallel ThreadPoolExecutor workers (1-32)

  # File Handling
  max_filename_length: 100     # Maximum filename length before truncation

  # Content Processing
  remove_script_tags: true     # Remove <script> tags from content
  remove_style_tags: true      # Remove <style> tags from content
  remove_nav_tags: true        # Remove <nav> tags from content

  # Media Processing
  download_images: true        # Always download images (embedded in articles)
  download_videos: false       # Download video files (requires --media flag)
  download_audio: false        # Download audio files (requires --media flag)
  download_documents: false    # Download PDF/document files (requires --media flag)

  # Output Settings
  create_comments_file: true   # Create separate comments.md file
  markdown_line_breaks: true   # Preserve line breaks in markdown

# ============================================================
# LOGGING CONFIGURATION
# ============================================================
logging:
  # Log Levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  default_level: "INFO"        # Default log level for all loggers
  file_level: "DEBUG"          # Log level for file output
  console_level: "INFO"        # Log level for console output

  # Log Formatting
  use_colors: true             # Colored console output
  include_timestamps: true     # Include timestamps in logs
  include_module_names: true   # Include module/function names in logs

  # File Logging
  auto_create_log_dir: true    # Automatically create log directories
  max_log_file_size: 10485760  # Max log file size in bytes (10MB)
  log_file_backup_count: 5     # Number of backup log files to keep

# ============================================================
# UI CONFIGURATION
# ============================================================
ui:
  # Progress Animations
  progress_spinner_style: "dots"     # Spinner style: dots, wave, loading, pulse, bounce, modern
  batch_spinner_style: "activity"    # Batch spinner: activity, progress, pulse, wave, dots, scan
  progress_bar_width: 25             # Width of progress bars in characters
  show_progress_animations: true     # Enable/disable progress animations

  # Visual Feedback
  use_emojis: true                   # Use emojis in output (disable per CLAUDE.md)
  use_colors: true                   # Colored terminal output
  show_detailed_progress: false      # Show detailed article-level progress
```

### capcat.json Structure

Complete JSON configuration (equivalent to YAML above):

```json
{
  "network": {
    "connect_timeout": 10,
    "read_timeout": 30,
    "media_download_timeout": 60,
    "head_request_timeout": 10,
    "pool_connections": 20,
    "pool_maxsize": 20,
    "user_agent": "Capcat/2.0 (Personal news archiver)",
    "max_retries": 3,
    "retry_delay": 1.0
  },
  "processing": {
    "max_workers": 8,
    "max_filename_length": 100,
    "remove_script_tags": true,
    "remove_style_tags": true,
    "remove_nav_tags": true,
    "download_images": true,
    "download_videos": false,
    "download_audio": false,
    "download_documents": false,
    "create_comments_file": true,
    "markdown_line_breaks": true
  },
  "logging": {
    "default_level": "INFO",
    "file_level": "DEBUG",
    "console_level": "INFO",
    "use_colors": true,
    "include_timestamps": true,
    "include_module_names": true,
    "auto_create_log_dir": true,
    "max_log_file_size": 10485760,
    "log_file_backup_count": 5
  },
  "ui": {
    "progress_spinner_style": "dots",
    "batch_spinner_style": "activity",
    "progress_bar_width": 25,
    "show_progress_animations": true,
    "use_emojis": true,
    "use_colors": true,
    "show_detailed_progress": false
  }
}
```

## Configuration Data Classes

Source: Application/core/config.py

### NetworkConfig
Location: Application/core/config.py:18

**Purpose:** Network-related configuration settings.

**All Fields:**

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
      <td><code>connect_timeout</code></td>
      <td>int</td>
      <td>10</td>
      <td>Connection establishment timeout (seconds)</td>
    </tr>
    <tr>
      <td><code>read_timeout</code></td>
      <td>int</td>
      <td>30</td>
      <td>Response read timeout (seconds)</td>
    </tr>
    <tr>
      <td><code>media_download_timeout</code></td>
      <td>int</td>
      <td>60</td>
      <td>Media file download timeout (seconds)</td>
    </tr>
    <tr>
      <td><code>head_request_timeout</code></td>
      <td>int</td>
      <td>10</td>
      <td>HEAD request timeout for size checks (seconds)</td>
    </tr>
    <tr>
      <td><code>pool_connections</code></td>
      <td>int</td>
      <td>20</td>
      <td>Number of connection pools to cache</td>
    </tr>
    <tr>
      <td><code>pool_maxsize</code></td>
      <td>int</td>
      <td>20</td>
      <td>Maximum connections per pool</td>
    </tr>
    <tr>
      <td><code>user_agent</code></td>
      <td>str</td>
      <td>"Capcat/2.0 (Personal news archiver)"</td>
      <td>User-Agent HTTP header</td>
    </tr>
    <tr>
      <td><code>max_retries</code></td>
      <td>int</td>
      <td>3</td>
      <td>Maximum retry attempts for failed requests</td>
    </tr>
    <tr>
      <td><code>retry_delay</code></td>
      <td>float</td>
      <td>1.0</td>
      <td>Base delay between retries (seconds)</td>
    </tr>
  </tbody>
</table>
</div>

**Usage:**
```python
from core.config import NetworkConfig

network = NetworkConfig(
    connect_timeout=15,
    read_timeout=45,
    max_retries=5
)
```

### ProcessingConfig
Location: Application/core/config.py:42

**Purpose:** Processing-related configuration settings.

**All Fields:**

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
      <td><code>max_workers</code></td>
      <td>int</td>
      <td>8</td>
      <td>Parallel ThreadPoolExecutor workers</td>
    </tr>
    <tr>
      <td><code>max_filename_length</code></td>
      <td>int</td>
      <td>100</td>
      <td>Maximum filename length before truncation</td>
    </tr>
    <tr>
      <td><code>remove_script_tags</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Remove <script> tags from content</td>
    </tr>
    <tr>
      <td><code>remove_style_tags</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Remove <style> tags from content</td>
    </tr>
    <tr>
      <td><code>remove_nav_tags</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Remove <nav> tags from content</td>
    </tr>
    <tr>
      <td><code>download_images</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Always download images</td>
    </tr>
    <tr>
      <td><code>download_videos</code></td>
      <td>bool</td>
      <td>False</td>
      <td>Download video files (--media flag)</td>
    </tr>
    <tr>
      <td><code>download_audio</code></td>
      <td>bool</td>
      <td>False</td>
      <td>Download audio files (--media flag)</td>
    </tr>
    <tr>
      <td><code>download_documents</code></td>
      <td>bool</td>
      <td>False</td>
      <td>Download PDFs/documents (--media flag)</td>
    </tr>
    <tr>
      <td><code>create_comments_file</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Create separate comments.md file</td>
    </tr>
    <tr>
      <td><code>markdown_line_breaks</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Preserve line breaks in markdown</td>
    </tr>
  </tbody>
</table>
</div>

**Worker Count Guidelines:**
- 1-4 workers: Low-end systems, slow networks
- 5-8 workers: Default, balanced performance
- 9-16 workers: High-end systems, fast networks
- 17-32 workers: Server-grade hardware, very fast networks

**Usage:**
```python
from core.config import ProcessingConfig

processing = ProcessingConfig(
    max_workers=16,
    download_videos=True,
    max_filename_length=150
)
```

### UIConfig
Location: Application/core/config.py:68

**Purpose:** User interface and experience configuration settings.

**All Fields:**

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
      <td><code>progress_spinner_style</code></td>
      <td>str</td>
      <td>"dots"</td>
      <td>Spinner style: dots, wave, loading, pulse, bounce, modern</td>
    </tr>
    <tr>
      <td><code>batch_spinner_style</code></td>
      <td>str</td>
      <td>"activity"</td>
      <td>Batch spinner: activity, progress, pulse, wave, dots, scan</td>
    </tr>
    <tr>
      <td><code>progress_bar_width</code></td>
      <td>int</td>
      <td>25</td>
      <td>Width of progress bars in characters</td>
    </tr>
    <tr>
      <td><code>show_progress_animations</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Enable/disable progress animations</td>
    </tr>
    <tr>
      <td><code>use_emojis</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Use emojis in output</td>
    </tr>
    <tr>
      <td><code>use_colors</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Colored terminal output</td>
    </tr>
    <tr>
      <td><code>show_detailed_progress</code></td>
      <td>bool</td>
      <td>False</td>
      <td>Show detailed article-level progress</td>
    </tr>
  </tbody>
</table>
</div>

**Spinner Styles:**
- `dots`: Simple rotating dots
- `wave`: Wave animation
- `loading`: Loading bar
- `pulse`: Pulsing indicator
- `bounce`: Bouncing animation
- `modern`: Modern spinner
- `activity`: Activity indicator
- `progress`: Progress indicator
- `scan`: Scanning animation

**Usage:**
```python
from core.config import UIConfig

ui = UIConfig(
    progress_spinner_style="wave",
    use_emojis=False,  # Per CLAUDE.md requirement
    show_detailed_progress=True
)
```

### LoggingConfig
Location: Application/core/config.py:88

**Purpose:** Logging-related configuration settings.

**All Fields:**

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
      <td><code>default_level</code></td>
      <td>str</td>
      <td>"INFO"</td>
      <td>Default log level for all loggers</td>
    </tr>
    <tr>
      <td><code>file_level</code></td>
      <td>str</td>
      <td>"DEBUG"</td>
      <td>Log level for file output</td>
    </tr>
    <tr>
      <td><code>console_level</code></td>
      <td>str</td>
      <td>"INFO"</td>
      <td>Log level for console output</td>
    </tr>
    <tr>
      <td><code>use_colors</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Colored console output</td>
    </tr>
    <tr>
      <td><code>include_timestamps</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Include timestamps in logs</td>
    </tr>
    <tr>
      <td><code>include_module_names</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Include module/function names</td>
    </tr>
    <tr>
      <td><code>auto_create_log_dir</code></td>
      <td>bool</td>
      <td>True</td>
      <td>Automatically create log directories</td>
    </tr>
    <tr>
      <td><code>max_log_file_size</code></td>
      <td>int</td>
      <td>10485760</td>
      <td>Max log file size in bytes (10MB)</td>
    </tr>
    <tr>
      <td><code>log_file_backup_count</code></td>
      <td>int</td>
      <td>5</td>
      <td>Number of backup log files to keep</td>
    </tr>
  </tbody>
</table>
</div>

**Log Levels:**
- `DEBUG`: Detailed debugging information (most verbose)
- `INFO`: General information messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only
- `CRITICAL`: Critical errors only (least verbose)

**Usage:**
```python
from core.config import LoggingConfig

logging = LoggingConfig(
    default_level="DEBUG",
    use_colors=False,
    max_log_file_size=20971520  # 20MB
)
```

### FetchNewsConfig
Location: Application/core/config.py:108

**Purpose:** Main configuration class containing all settings.

**Structure:**
```python
@dataclass
class FetchNewsConfig:
    network: NetworkConfig = None
    processing: ProcessingConfig = None
    logging: LoggingConfig = None
    ui: UIConfig = None
```

**Methods:**

#### __post_init__()
```python
def __post_init__(self):
    """Initialize sub-configs if not provided."""
    if self.network is None:
        self.network = NetworkConfig()
    if self.processing is None:
        self.processing = ProcessingConfig()
    if self.logging is None:
        self.logging = LoggingConfig()
    if self.ui is None:
        self.ui = UIConfig()
```

#### to_dict() -> Dict[str, Any]
```python
def to_dict(self) -> Dict[str, Any]:
    """Convert configuration to dictionary."""
    return asdict(self)
```

#### from_dict(data: Dict[str, Any]) -> FetchNewsConfig
```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "FetchNewsConfig":
    """Create configuration from dictionary."""
    network_data = data.get("network", {})
    processing_data = data.get("processing", {})
    logging_data = data.get("logging", {})

    return cls(
        network=NetworkConfig(**network_data),
        processing=ProcessingConfig(**processing_data),
        logging=LoggingConfig(**logging_data),
    )
```

**Usage:**
```python
from core.config import FetchNewsConfig, NetworkConfig, ProcessingConfig

config = FetchNewsConfig(
    network=NetworkConfig(connect_timeout=15),
    processing=ProcessingConfig(max_workers=16)
)

# Convert to dictionary
config_dict = config.to_dict()

# Create from dictionary
loaded_config = FetchNewsConfig.from_dict(config_dict)
```

## Environment Variables

All configuration options can be overridden with environment variables using `CAPCAT_` prefix.

### Environment Variable Format

**Pattern:** `CAPCAT_<SECTION>_<FIELD>`

**Case:** All uppercase with underscores

**Examples:**
```bash
# Network settings
export CAPCAT_NETWORK_CONNECT_TIMEOUT=15
export CAPCAT_NETWORK_READ_TIMEOUT=45
export CAPCAT_NETWORK_USER_AGENT="MyBot/1.0"
export CAPCAT_NETWORK_MAX_RETRIES=5
export CAPCAT_NETWORK_RETRY_DELAY=2.0

# Processing settings
export CAPCAT_PROCESSING_MAX_WORKERS=16
export CAPCAT_PROCESSING_DOWNLOAD_VIDEOS=true
export CAPCAT_PROCESSING_MAX_FILENAME_LENGTH=150

# Logging settings
export CAPCAT_LOGGING_DEFAULT_LEVEL=DEBUG
export CAPCAT_LOGGING_USE_COLORS=false
export CAPCAT_LOGGING_FILE_LEVEL=INFO

# UI settings
export CAPCAT_UI_PROGRESS_SPINNER_STYLE=wave
export CAPCAT_UI_USE_EMOJIS=false
export CAPCAT_UI_SHOW_DETAILED_PROGRESS=true
```

### Complete Environment Variable List

**Network:**
```bash
CAPCAT_NETWORK_CONNECT_TIMEOUT=10
CAPCAT_NETWORK_READ_TIMEOUT=30
CAPCAT_NETWORK_MEDIA_DOWNLOAD_TIMEOUT=60
CAPCAT_NETWORK_HEAD_REQUEST_TIMEOUT=10
CAPCAT_NETWORK_POOL_CONNECTIONS=20
CAPCAT_NETWORK_POOL_MAXSIZE=20
CAPCAT_NETWORK_USER_AGENT="Capcat/2.0 (Personal news archiver)"
CAPCAT_NETWORK_MAX_RETRIES=3
CAPCAT_NETWORK_RETRY_DELAY=1.0
```

**Processing:**
```bash
CAPCAT_PROCESSING_MAX_WORKERS=8
CAPCAT_PROCESSING_MAX_FILENAME_LENGTH=100
CAPCAT_PROCESSING_REMOVE_SCRIPT_TAGS=true
CAPCAT_PROCESSING_REMOVE_STYLE_TAGS=true
CAPCAT_PROCESSING_REMOVE_NAV_TAGS=true
CAPCAT_PROCESSING_DOWNLOAD_IMAGES=true
CAPCAT_PROCESSING_DOWNLOAD_VIDEOS=false
CAPCAT_PROCESSING_DOWNLOAD_AUDIO=false
CAPCAT_PROCESSING_DOWNLOAD_DOCUMENTS=false
CAPCAT_PROCESSING_CREATE_COMMENTS_FILE=true
CAPCAT_PROCESSING_MARKDOWN_LINE_BREAKS=true
```

**Logging:**
```bash
CAPCAT_LOGGING_DEFAULT_LEVEL="INFO"
CAPCAT_LOGGING_FILE_LEVEL="DEBUG"
CAPCAT_LOGGING_CONSOLE_LEVEL="INFO"
CAPCAT_LOGGING_USE_COLORS=true
CAPCAT_LOGGING_INCLUDE_TIMESTAMPS=true
CAPCAT_LOGGING_INCLUDE_MODULE_NAMES=true
CAPCAT_LOGGING_AUTO_CREATE_LOG_DIR=true
CAPCAT_LOGGING_MAX_LOG_FILE_SIZE=10485760
CAPCAT_LOGGING_LOG_FILE_BACKUP_COUNT=5
```

**UI:**
```bash
CAPCAT_UI_PROGRESS_SPINNER_STYLE="dots"
CAPCAT_UI_BATCH_SPINNER_STYLE="activity"
CAPCAT_UI_PROGRESS_BAR_WIDTH=25
CAPCAT_UI_SHOW_PROGRESS_ANIMATIONS=true
CAPCAT_UI_USE_EMOJIS=true
CAPCAT_UI_USE_COLORS=true
CAPCAT_UI_SHOW_DETAILED_PROGRESS=false
```

### Environment Variable Usage

**Temporary Override:**
```bash
# Override for single command
CAPCAT_PROCESSING_MAX_WORKERS=16 ./capcat bundle tech

# Override multiple settings
CAPCAT_LOGGING_DEFAULT_LEVEL=DEBUG \
CAPCAT_PROCESSING_MAX_WORKERS=16 \
./capcat fetch hn --count 20
```

**Session-Wide:**
```bash
# Set for current shell session
export CAPCAT_PROCESSING_MAX_WORKERS=16
export CAPCAT_LOGGING_DEFAULT_LEVEL=DEBUG

./capcat bundle tech
./capcat fetch hn
```

**Persistent (Shell Profile):**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export CAPCAT_PROCESSING_MAX_WORKERS=16' >> ~/.bashrc
echo 'export CAPCAT_LOGGING_DEFAULT_LEVEL=INFO' >> ~/.bashrc
```

## Bundle Configuration

Source: Application/sources/active/bundles.yml

### bundles.yml Structure

Complete bundle configuration:

```yaml
bundles:
  tech:
    description: "Consumer technology news sources"
    sources:
      - ieee
      - mashable
    default_count: 30

  techpro:
    description: "Professional developer news sources"
    sources:
      - hn
      - lb
      - iq
    default_count: 30

  news:
    description: "General news sources"
    sources:
      - bbc
      - guardian
    default_count: 25

  science:
    description: "Science and research sources"
    sources:
      - nature
      - scientificamerican
    default_count: 20

  ai:
    description: "AI, Machine Learning, and Rationality sources"
    sources:
      - mitnews
    default_count: 20

  sports:
    description: "World sports news sources"
    sources:
      - bbcsport
    default_count: 25

  all:
    description: "All available sources"
    sources: []  # Populated dynamically from registry
    default_count: 10
```

### Bundle Fields

**Required Fields:**
- `description` (str) - Human-readable bundle description
- `sources` (list) - List of source IDs in bundle

**Optional Fields:**
- `default_count` (int) - Default article count (overridden by --count flag)

### Bundle Auto-Discovery

**Category Matching:**
Bundles automatically include sources with matching category:

```yaml
# Bundle named "tech"
tech:
  sources:
    - ieee      # Explicit
    - mashable  # Explicit

# All sources with category: tech are automatically included:
# - gizmodo (category: tech, not in bundles.yml)
# - futurism (category: tech, not in bundles.yml)
```

**Implementation:** Application/core/interactive.py:460
```python
category_sources = registry.get_sources_by_category(name)
for source_id in category_sources:
    if source_id not in bundle_sources:
        bundle_sources.append(source_id)
```

### Creating Custom Bundles

**Manual Editing:**
```bash
# Edit bundles file
vim sources/active/bundles.yml

# Add new bundle
custom:
  description: "My custom bundle"
  sources:
    - hn
    - bbc
    - nature
  default_count: 15
```

**Interactive Management:**
```bash
./capcat catch
# Select: Manage Sources
# Select: Manage Bundles
# Select: Create New Bundle
```

## Source Configuration

### Config-Driven Sources

Location: sources/active/config_driven/configs/*.yaml

**Minimal Configuration:**
```yaml
# sources/active/config_driven/configs/example.yaml
display_name: "Example News"
base_url: "https://example.com/"
category: "tech"
timeout: 10.0
rate_limit: 1.0

article_selectors:
  - ".headline a"

content_selectors:
  - ".article-content"
```

**Complete Configuration:**
```yaml
# Complete config-driven source
display_name: "Complete Example"
base_url: "https://example.com/"
category: "tech"
timeout: 15.0
rate_limit: 2.0
supports_comments: false

# RSS Configuration
rss_config:
  feed_url: "https://example.com/feed.xml"
  use_rss_content: true
  content_field: "description"

# Article Discovery
article_selectors:
  - ".headline a"
  - ".article-title a"
  - "h2.title a"

# Content Extraction
content_selectors:
  - ".article-content"
  - ".post-body"
  - "div.content"

# URL Filtering
skip_patterns:
  - "/about"
  - "/contact"
  - "/advertising"
  - "?utm_"
  - "/sponsored"

# Image Processing
image_processing:
  # Image selectors (CSS selectors for finding images)
  selectors:
    - "img"
    - ".content img"
    - "article img"

  # URL pattern filtering (only download images matching these patterns)
  url_patterns:
    - "example.com/"
    - "cdn.example.com/"

  # Allow URLs without file extensions (for modern CDNs)
  allow_extensionless: true

  # Skip images in specific containers (applied during extraction)
  skip_selectors:
    - ".sidebar img"           # Skip sidebar images
    - ".navigation img"        # Skip navigation images
    - ".header img"            # Skip header/logo images
    - ".related-articles img"  # Skip related article thumbnails

  # Advanced filtering: limit number of images
  max_images: 10  # Optional: limit to first N images (applied after skip_selectors)

  # Advanced filtering: minimum image size in bytes
  min_image_size: 10240  # Optional: 10KB minimum (filters small icons/thumbnails)

# Custom Headers
custom_config:
  headers:
    Accept: "text/html,application/xhtml+xml"
    Accept-Language: "en-US,en;q=0.5"
  user_agent: "Custom Bot 1.0"

  # Metadata Extraction
  meta_selectors:
    author: ".byline .author"
    date: ".publish-date"
    tags: ".article-tags a"

  # Content Cleaning
  remove_selectors:
    - ".advertisement"
    - ".related-links"
    - ".social-share"

# Template Configuration
template:
  variant: "article-no-comments"
  navigation:
    back_to_news_url: "../../news.html"
    back_to_news_text: "Back to News"
    has_comments: false
```

### Custom Sources

Location: sources/active/custom/<source-name>/config.yaml

**Configuration:**
```yaml
# sources/active/custom/hn/config.yaml
display_name: "Hacker News"
base_url: "https://news.ycombinator.com/"
category: "tech"
timeout: 10.0
rate_limit: 1.0
supports_comments: true

template:
  variant: "article-with-comments"
  navigation:
    back_to_news_url: "../../news.html"
    back_to_news_text: "Back to News"
    has_comments: true
    comments_url: "comments.html"
    comments_text: "View Comments"
```

## Configuration Management API

### ConfigManager Class
Location: Application/core/config.py:161

**Methods:**

#### __init__()
```python
def __init__(self):
    """Initialize the configuration manager."""
    self.logger = get_logger(__name__)
    self._config = FetchNewsConfig()
    self._config_loaded = False
```

#### load_config(config_file: Optional[str] = None, load_env: bool = True) -> FetchNewsConfig
```python
def load_config(
    self, config_file: Optional[str] = None, load_env: bool = True
) -> FetchNewsConfig:
    """Load configuration from files and environment variables.

    Args:
        config_file: Path to config file (JSON or YAML)
        load_env: Whether to load environment variables

    Returns:
        Loaded configuration instance
    """
```

**Behavior:**
1. Return cached config if already loaded
2. Start with defaults (FetchNewsConfig())
3. Load from specified file or search default locations
4. Load environment variables if load_env=True
5. Cache and return config

**Usage:**
```python
from core.config import ConfigManager

manager = ConfigManager()

# Load from default locations
config = manager.load_config()

# Load from specific file
config = manager.load_config(config_file="custom.yml")

# Load without environment variables
config = manager.load_config(load_env=False)
```

### Helper Functions

#### get_config() -> FetchNewsConfig
```python
def get_config() -> FetchNewsConfig:
    """Get the global configuration instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.load_config()
```

#### load_config(config_file: Optional[str] = None) -> FetchNewsConfig
```python
def load_config(config_file: Optional[str] = None) -> FetchNewsConfig:
    """Load configuration from file or defaults."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.load_config(config_file)
```

**Usage:**
```python
from core.config import get_config, load_config

# Get global config
config = get_config()

# Load specific config
config = load_config("custom.yml")
```

## Configuration Examples

### High-Performance Setup
```yaml
network:
  connect_timeout: 15
  read_timeout: 60
  media_download_timeout: 120
  max_retries: 5

processing:
  max_workers: 16
  download_videos: true
  download_audio: true
  download_documents: true

logging:
  default_level: "WARNING"
  use_colors: true
```

### Debug Setup
```yaml
network:
  connect_timeout: 30
  max_retries: 1

processing:
  max_workers: 4

logging:
  default_level: "DEBUG"
  file_level: "DEBUG"
  console_level: "DEBUG"
  include_timestamps: true
  include_module_names: true

ui:
  show_detailed_progress: true
```

### Minimal Setup
```yaml
processing:
  download_videos: false
  download_audio: false
  download_documents: false

logging:
  default_level: "ERROR"
  use_colors: false

ui:
  show_progress_animations: false
  use_emojis: false
```

## Source Code Locations

Configuration classes:
- `NetworkConfig` - Application/core/config.py:18
- `ProcessingConfig` - Application/core/config.py:42
- `UIConfig` - Application/core/config.py:68
- `LoggingConfig` - Application/core/config.py:88
- `FetchNewsConfig` - Application/core/config.py:108
- `ConfigManager` - Application/core/config.py:161

Helper functions:
- `get_config()` - Application/core/config.py
- `load_config()` - Application/core/config.py

## Related Documentation

- CLI Commands: docs/tutorials/01-cli-commands-exhaustive.md
- Source Development: docs/tutorials/06-source-development-exhaustive.md
- API Reference: docs/tutorials/05-api-functions-exhaustive.md
