# Component Details

## Source System Components

### Source Factory (`core.source_system.source_factory`)

Responsible for creating source instances based on configuration.

**Key Methods:**
- `create_source(source_name: str)` - Creates source instance
- `get_available_sources()` - Lists all available sources
- `validate_source(source_name: str)` - Validates source configuration

### Source Registry (`core.source_system.source_registry`)

Auto-discovers and manages available sources.

**Discovery Process:**
1. Scans `sources/active/` directory
2. Loads YAML configs for config-driven sources
3. Imports Python modules for custom sources
4. Validates source implementations
5. Registers sources with metadata

### Base Source (`core.source_system.base_source`)

Abstract base class defining the source interface.

**Required Methods:**
- `get_articles(count: int)` - Fetch article list
- `get_article_content(url: str)` - Download article content

## Processing Components

### Article Fetcher (`core.article_fetcher`)

Coordinates the article processing pipeline.

**Responsibilities:**
- Parallel article processing
- Error handling and retry logic
- Progress tracking
- Resource management

### Media Processor (`core.unified_media_processor`)

Handles all media-related operations.

**Features:**
- Image downloading and optimization
- Video/audio handling (with --media flag)
- Media type detection
- File organization

### Content Formatter (`core.formatter`)

Converts HTML content to Markdown.

**Processing Steps:**
1. HTML parsing and cleaning
2. Image reference extraction
3. Link processing
4. Markdown conversion
5. Content sanitization

## Configuration Components

### Configuration Manager (`core.config`)

Centralized configuration management.

**Configuration Sources:**
1. Command-line arguments (highest priority)
2. Environment variables
3. Config files (`capcat.yml`)
4. Default values (lowest priority)

### Source Configuration (`core.source_config`)

Source-specific configuration and metadata.

**Source Types:**
- **Config-Driven**: YAML-based configuration
- **Custom**: Python implementation with full control

