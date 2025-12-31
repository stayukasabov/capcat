# Configuration Guide

Comprehensive guide for configuring Capcat's hybrid architecture system and individual sources.

## Configuration Hierarchy

Capcat uses a hierarchical configuration system with the following precedence (highest to lowest):

1. **Command-line arguments** (highest priority)
2. **Environment variables**
3. **Configuration files** (`capcat.yml`, `capcat.json`)
4. **Default values** (lowest priority)

## System Configuration

### Configuration Files

Create configuration files in the application root directory:

#### YAML Configuration (Recommended)
```yaml
# capcat.yml
network:
  connect_timeout: 10
  read_timeout: 8
  user_agent: "Mozilla/5.0 (compatible; Capcat/2.0)"
  max_retries: 3
  retry_delay: 1.0

processing:
  max_workers: 8
  download_images: true
  download_videos: false
  download_audio: false
  download_documents: false

logging:
  default_level: "INFO"
  use_colors: true

output:
  base_path: "../"
  date_format: "%d-%m-%Y"
  create_date_folders: true
```

#### JSON Configuration
```json
{
  "network": {
    "connect_timeout": 10,
    "read_timeout": 8,
    "user_agent": "Mozilla/5.0 (compatible; Capcat/2.0)",
    "max_retries": 3,
    "retry_delay": 1.0
  },
  "processing": {
    "max_workers": 8,
    "download_images": true,
    "download_videos": false,
    "download_audio": false,
    "download_documents": false
  },
  "logging": {
    "default_level": "INFO",
    "use_colors": true
  },
  "output": {
    "base_path": "../",
    "date_format": "%d-%m-%Y",
    "create_date_folders": true
  }
}
```

### Environment Variables

All configuration options can be overridden with environment variables using the `CAPCAT_` prefix:

```bash
# Network configuration
export CAPCAT_NETWORK_CONNECT_TIMEOUT=15
export CAPCAT_NETWORK_READ_TIMEOUT=10
export CAPCAT_NETWORK_USER_AGENT="Custom User Agent"

# Processing configuration
export CAPCAT_PROCESSING_MAX_WORKERS=12
export CAPCAT_PROCESSING_DOWNLOAD_VIDEOS=true

# Logging configuration
export CAPCAT_LOGGING_DEFAULT_LEVEL=DEBUG
export CAPCAT_LOGGING_USE_COLORS=false
```

### Command-Line Overrides

Command-line arguments override all other configuration sources:

```bash
# Override worker count
./capcat bundle tech --count 10 --workers 12

# Override media downloading
./capcat fetch hn,bbc --count 15 --media

# Override output path
./capcat single https://example.com/article --output /custom/path

# Enable file logging (all commands)
./capcat --log-file capcat.log bundle tech --count 10

# Verbose console + file logging
./capcat -V -L debug.log fetch hn --count 15
```

## Configuration Sections

### Network Configuration

Controls HTTP requests and network behavior.

```yaml
network:
  connect_timeout: 10          # Connection timeout (seconds)
  read_timeout: 8             # Read timeout (seconds)
  user_agent: "Mozilla/5.0 (compatible; Capcat/2.0)"
  max_retries: 3              # Maximum retry attempts
  retry_delay: 1.0            # Delay between retries (seconds)
  pool_connections: 20        # Connection pool size
  pool_maxsize: 20           # Maximum pool size
```

**Options:**
- `connect_timeout`: Maximum time to wait for connection establishment
- `read_timeout`: Maximum time to wait for response data
- `user_agent`: User-Agent header for HTTP requests
- `max_retries`: Number of retry attempts for failed requests
- `retry_delay`: Base delay between retry attempts
- `pool_connections`: Number of connection pools to cache
- `pool_maxsize`: Maximum number of connections to save in pool

### Processing Configuration

Controls article processing and download behavior.

```yaml
processing:
  max_workers: 8              # Parallel processing workers
  download_images: true       # Download and embed images
  download_videos: false      # Download video files
  download_audio: false       # Download audio files
  download_documents: false   # Download PDF/document files
  skip_existing: true         # Skip existing articles
  content_timeout: 30         # Content fetching timeout
```

**Options:**
- `max_workers`: Number of parallel ThreadPoolExecutor workers
- `download_images`: Always download images (embedded in articles)
- `download_videos`: Download video files (requires --media flag)
- `download_audio`: Download audio files (requires --media flag)
- `download_documents`: Download PDF/document files (requires --media flag)
- `skip_existing`: Skip articles that already exist
- `content_timeout`: Timeout for content fetching operations

### Logging Configuration

Controls logging behavior and output.

```yaml
logging:
  default_level: "INFO"       # Default log level (DEBUG, INFO, WARNING, ERROR)
  use_colors: true           # Colored console output
```

**Log Levels:**
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only
- `CRITICAL`: Critical errors only

**File Logging:**

File logging is controlled via CLI flags, not configuration files:

```bash
# Enable file logging with --log-file or -L flag
./capcat --log-file capcat.log bundle tech --count 10

# Verbose console + file logging
./capcat -V -L debug.log fetch hn --count 15

# Timestamped log files
./capcat -L logs/news-$(date +%Y%m%d-%H%M%S).log bundle news --count 10
```

**Log Output Formats:**
- **Console**: Colored output with log level indicators (user-friendly)
- **File**: Timestamped entries with module names and full context (debugging)

### Output Configuration

Controls output directory structure and file naming.

```yaml
output:
  base_path: "../"           # Base output directory
  date_format: "%d-%m-%Y"    # Date format for folders
  create_date_folders: true  # Create date-based folders
  sanitize_filenames: true   # Clean invalid filename characters
  max_filename_length: 100   # Maximum filename length
```

**Options:**
- `base_path`: Base directory for all output
- `date_format`: Python strftime format for date folders
- `create_date_folders`: Create date-based organization
- `sanitize_filenames`: Remove invalid filesystem characters
- `max_filename_length`: Truncate long filenames

## Source Configuration

### Config-Driven Sources

Simple sources use YAML configuration files in `sources/active/config_driven/configs/`.

#### Basic Configuration
```yaml
# sources/active/config_driven/configs/example.yaml
display_name: "Example News"
base_url: "https://example.com/news/"
category: "general"          # tech, science, business, general
timeout: 10.0
rate_limit: 1.0             # Minimum seconds between requests

# Required: Article discovery
article_selectors:
  - ".headline a"
  - ".article-title a"
  - "h2.title a"

# Required: Content extraction
content_selectors:
  - ".article-content"
  - ".post-body"
  - "div.content"
```

#### Advanced Configuration
```yaml
# Advanced config-driven source
display_name: "Advanced News"
base_url: "https://advanced.com/"
category: "tech"
timeout: 15.0
rate_limit: 2.0
supports_comments: false

article_selectors:
  - ".headline a"
  - ".story-link"

content_selectors:
  - ".article-content"
  - ".story-body"

# Skip unwanted URLs
skip_patterns:
  - "/about"
  - "/contact"
  - "/advertising"
  - "?utm_"
  - "/sponsored"

# Custom headers
custom_config:
  headers:
    Accept: "text/html,application/xhtml+xml"
    Accept-Language: "en-US,en;q=0.5"
  user_agent: "Custom Bot 1.0"

  # Custom selectors for metadata
  meta_selectors:
    author: ".byline .author"
    date: ".publish-date"
    tags: ".article-tags a"

  # Content cleaning
  remove_selectors:
    - ".advertisement"
    - ".related-links"
    - ".social-share"
```

### Custom Sources

Complex sources use Python implementations with YAML configuration.

#### Configuration File
```yaml
# sources/active/custom/example/config.yaml
display_name: "Example Custom"
base_url: "https://example.com/"
category: "tech"
timeout: 10.0
rate_limit: 1.0
supports_comments: true

# Custom source-specific configuration
custom_config:
  api_endpoint: "/api/v1/articles"
  api_key: "${EXAMPLE_API_KEY}"  # Environment variable
  max_pages: 5
  items_per_page: 50

  # Authentication
  auth_type: "bearer"  # bearer, basic, api_key
  auth_header: "Authorization"

  # Rate limiting
  requests_per_minute: 60
  burst_limit: 10

  # Content processing
  extract_metadata: true
  process_images: true
  follow_redirects: true
```

#### Python Implementation
```python
# sources/active/custom/example/source.py
class ExampleSource(BaseSource):
    def __init__(self, config: SourceConfig, session=None):
        super().__init__(config, session)

        # Access custom configuration
        self.api_key = config.custom_config.get('api_key')
        self.api_endpoint = config.custom_config.get('api_endpoint')
        self.max_pages = config.custom_config.get('max_pages', 5)

    def _get_headers(self):
        headers = super()._get_headers()

        # Add API authentication
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        return headers
```

## Configuration Validation

### Automatic Validation

Capcat automatically validates configurations during source discovery:

```python
# Check configuration validity
from core.source_system.source_registry import get_source_registry

registry = get_source_registry()
errors = registry.validate_all_sources(deep_validation=True)

for source_name, error_list in errors.items():
    if error_list:
        print(f"{source_name}: {', '.join(error_list)}")
```

### Manual Validation

```bash
# Validate all sources
python -c "
from core.source_system.validation_engine import ValidationEngine
from core.source_system.source_registry import get_source_registry

registry = get_source_registry()
engine = ValidationEngine()

configs = registry.discover_sources()
results = engine.validate_all_sources(configs, deep_validation=True)
report = engine.generate_validation_report(results)
print(report)
"
```

## Environment-Specific Configuration

### Development Environment
```yaml
# capcat-dev.yml
network:
  connect_timeout: 5
  read_timeout: 5
  max_retries: 1

processing:
  max_workers: 4
  download_videos: false

logging:
  default_level: "DEBUG"
  use_colors: true
  log_to_file: true
```

### Production Environment
```yaml
# capcat-prod.yml
network:
  connect_timeout: 15
  read_timeout: 10
  max_retries: 3
  retry_delay: 2.0

processing:
  max_workers: 16
  download_images: true
  download_videos: true

logging:
  default_level: "INFO"
  use_colors: false
  log_to_file: true
  format: "json"
```

### Testing Environment
```yaml
# capcat-test.yml
network:
  connect_timeout: 3
  read_timeout: 3
  max_retries: 0

processing:
  max_workers: 2
  download_images: false
  download_videos: false

logging:
  default_level: "WARNING"
  use_colors: false
```

## Security Configuration

### API Keys and Secrets

Use environment variables for sensitive data:

```yaml
# Configuration file
custom_config:
  api_key: "${NEWS_API_KEY}"
  secret_token: "${SECRET_TOKEN}"
  database_url: "${DATABASE_URL}"
```

```bash
# Environment variables
export NEWS_API_KEY="your-api-key-here"
export SECRET_TOKEN="your-secret-token"
export DATABASE_URL="postgresql://user:pass@localhost/db"
```

### User Agent Configuration

Use realistic user agents to avoid being blocked:

```yaml
network:
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
```

### Rate Limiting

Configure appropriate rate limits to respect server resources:

```yaml
# Global rate limiting
network:
  retry_delay: 2.0

# Per-source rate limiting
rate_limit: 1.5  # Minimum 1.5 seconds between requests
```

## Performance Tuning

### High-Performance Configuration
```yaml
network:
  connect_timeout: 8
  read_timeout: 6
  pool_connections: 50
  pool_maxsize: 50

processing:
  max_workers: 16  # Adjust based on CPU cores
  skip_existing: true
  content_timeout: 20
```

### Memory-Constrained Configuration
```yaml
processing:
  max_workers: 4
  download_videos: false
  download_audio: false
  download_documents: false

logging:
  log_to_file: false  # Reduce memory usage
```

## Configuration Examples

### News Aggregation Setup
```yaml
# Optimized for news aggregation
processing:
  max_workers: 12
  download_images: true
  download_videos: false

sources:
  priority:
    - "bbc"
    - "cnn"
    - "reuters"

bundles:
  daily_news:
    - "bbc"
    - "cnn"
    - "aljazeera"
    count: 50
```

### Research Configuration
```yaml
# Optimized for research/archival
processing:
  download_images: true
  download_videos: true
  download_documents: true
  skip_existing: false

logging:
  default_level: "DEBUG"
  log_to_file: true

output:
  create_date_folders: true
  sanitize_filenames: true
```

## Configuration Management

### Loading Custom Configuration
```bash
# Specify configuration file
export CAPCAT_CONFIG_FILE="config/production.yml"
./capcat bundle tech --count 10

# Multiple configuration files (merged in order)
export CAPCAT_CONFIG_FILES="config/base.yml,config/production.yml"
```

### Configuration Validation Script
```python
#!/usr/bin/env python3
"""Configuration validation script."""

import yaml
from pathlib import Path
from core.config import load_config, validate_config

def validate_config_file(config_path):
    """Validate a configuration file."""
    try:
        config = load_config(config_path)
        errors = validate_config(config)

        if errors:
            print(f"Configuration errors in {config_path}:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"Configuration valid: {config_path}")

    except Exception as e:
        print(f"Failed to load {config_path}: {e}")

if __name__ == "__main__":
    for config_file in ["capcat.yml", "capcat.json"]:
        if Path(config_file).exists():
            validate_config_file(config_file)
```

---

*This configuration guide covers all aspects of Capcat configuration management. For source-specific configuration details, see the Source Development Guide.*