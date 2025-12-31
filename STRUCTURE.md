# Capcat Application Structure

This document lists all essential files required for the Capcat application to function properly.

## Essential Application Files

```
Application/
├── capcat.py                          # Main application entry point
├── cli.py                               # Command-line interface parser
├── run_capcat.py                      # Python wrapper for execution
├── requirements.txt                     # Python dependencies
├── docker-compose.yml                   # Docker deployment configuration
└── CLAUDE.md                            # Project configuration and guidelines

## Core System (core/)
├── core/
│   ├── __init__.py                      # Package initialization (if exists)
│   ├── config.py                        # Configuration management
│   ├── logging_config.py                # Logging system
│   ├── exceptions.py                    # Custom exception classes
│   ├── utils.py                         # Utility functions
│   ├── session_pool.py                  # HTTP session pooling
│   ├── formatter.py                     # HTML to Markdown conversion
│   ├── downloader.py                    # Media file downloading
│   ├── progress.py                      # Progress indication system
│   ├── shutdown.py                      # Graceful shutdown handling
│   ├── retry.py                         # Retry logic
│   ├── timeout_wrapper.py               # Timeout handling
│   ├── update_manager.py                # System updates
│   ├── article_fetcher.py               # Article content fetching
│   ├── news_source_adapter.py           # NewsSourceArticleFetcher implementation
│   ├── unified_media_processor.py       # Unified media processing system
│   ├── media_embedding_processor.py     # Media embedding engine
│   ├── media_config.py                  # Source-specific media configurations
│   ├── image_processor.py               # Image processing and website classification
│   ├── website_classifier.py            # Website protection system
│   ├── unified_source_processor.py      # Unified source processing
│   ├── source_config.py                 # Source configuration utilities
│   ├── source_configs.py                # Legacy configuration adapter
│   ├── source_factory.py                # Source creation factory
│   ├── specialized_source_manager.py    # Specialized source management
│   ├── streamlined_comment_processor.py # Comment processing
│   ├── template_renderer.py             # Template rendering system
│   ├── html_generator.py                # HTML generation
│   ├── html_post_processor.py           # Post-processing and web view
│   └── config/                          # Configuration subsystem
│       ├── __init__.py
│       ├── source_base.py
│       └── source_registry.py

## New Source System (core/source_system/)
├── core/source_system/
│   ├── __init__.py                      # Package initialization
│   ├── base_source.py                   # Base source abstract class
│   ├── source_registry.py               # Source auto-discovery and management
│   ├── source_factory.py                # Source instantiation factory
│   ├── source_config.py                 # Source configuration data classes
│   ├── config_driven_source.py          # Config-driven source implementation
│   ├── performance_monitor.py           # Real-time metrics tracking
│   └── validation_engine.py             # Source validation system

## Source Implementations (sources/)
├── sources/
│   ├── __init__.py                      # Package initialization
│   ├── active/                          # Active source configurations
│   │   ├── __init__.py
│   │   ├── bundles.yml                  # Source bundle definitions
│   │   ├── tech_sources.yml             # Tech sources configuration
│   │   ├── news_sources.yml             # News sources configuration
│   │   ├── science_sources.yml          # Science sources configuration
│   │   ├── business_sources.yml         # Business sources configuration
│   │   ├── config_driven/               # YAML-configured sources
│   │   │   └── configs/
│   │   │       └── iq.yaml              # InfoQ tech source
│   │   └── custom/                      # Python-implemented sources
│   │       ├── bbc/                     # BBC News
│   │       │   ├── config.yaml
│   │       │   └── source.py
│   │       ├── gizmodo/                 # Gizmodo tech news
│   │       │   ├── config.yaml
│   │       │   └── source.py
│   │       ├── hn/                      # Hacker News
│   │       │   ├── config.yaml
│   │       │   └── source.py
│   │       ├── ieee/                    # IEEE Spectrum
│   │       │   ├── __init__.py
│   │       │   ├── config.yaml
│   │       │   └── source.py
│   │       ├── lb/                      # Lobsters
│   │       │   ├── config.yaml
│   │       │   └── source.py
│   │       ├── lesswrong/               # LessWrong community
│   │       │   ├── config.yaml
│   │       │   └── source.py
│   │       ├── nature/                  # Nature scientific journal
│   │       │   ├── config.yaml
│   │       │   └── source.py
│   │       └── scientificamerican/      # Scientific American
│   │           ├── config.yaml
│   │           └── source.py
│   ├── specialized/                     # Specialized source implementations
│   │   ├── __init__.py
│   │   ├── medium/                      # Medium.com with paywall detection
│   │   │   ├── config.yaml
│   │   │   └── source.py
│   │   └── substack/                    # Substack.com with paywall detection
│   │       ├── config.yaml
│   │       └── source.py
│   └── base/                            # Legacy base system (still used)
│       ├── __init__.py
│       ├── config_schema.py             # Configuration schema definitions
│       └── factory.py                   # Legacy modular factory

## HTML Generation System (htmlgen/)
├── htmlgen/
│   ├── __init__.py                      # Package initialization
│   ├── base/                            # Base template system
│   │   ├── base_generator.py            # Base HTML generator
│   │   ├── config_schema.yaml           # Configuration schema
│   │   └── templates/                   # Base templates
│   │       ├── article.html             # Article template
│   │       ├── comments.html            # Comments template
│   │       └── news.html                # News index template
│   ├── hn/                              # Hacker News specific
│   │   ├── config.yaml
│   │   └── generator.py
│   ├── lb/                              # Lobsters specific
│   │   ├── config.yaml
│   │   └── generator.py
│   └── lesswrong/                       # LessWrong specific
│       ├── config.yaml
│       └── generator.py

## Template System (templates/)
├── templates/
│   ├── article-with-comments.html       # Template for sources with comments
│   ├── article-no-comments.html         # Template for sources without comments
│   └── comments-with-navigation.html    # Comments page template

## CSS Themes (themes/)
├── themes/
│   ├── base.css                         # Base styling, layout, and syntax highlighting
│   └── design-system.css                # Complete design system (typography, spacing, colors, themes)

## Metrics and Performance (metrics/)
├── metrics/
│   └── source_performance.json          # Performance tracking data

## Documentation (docs/)
├── docs/                                # Comprehensive documentation
│   ├── README.md                        # Documentation overview
│   ├── architecture.md                  # System architecture details
│   ├── quick-start.md                   # Getting started guide
│   ├── configuration.md                 # Configuration guide
│   ├── dependencies.md                  # Dependency management
│   ├── deployment.md                    # Deployment instructions
│   ├── source-development.md            # Source development guide
│   ├── testing.md                       # Testing procedures
│   └── api-reference.md                 # API documentation

## Project Configuration (AGENT/)
├── AGENT/
│   └── cleaner.md                       # Code cleaner agent configuration
```

## Dependency Files

### Essential Dependencies (requirements.txt)
```
requests>=2.31.0
beautifulsoup4>=4.12.0
PyYAML>=6.0
markdownify>=0.11.6
```

### Additional Dependencies
- **requests**: HTTP client for web scraping
- **beautifulsoup4**: HTML parsing and DOM manipulation
- **PyYAML**: YAML configuration file parsing
- **markdownify**: HTML to Markdown conversion

## Optional/Development Files

### Utility Scripts (optional but useful)
```
├── add_template_configs.py              # Template configuration helper
├── analyze_optimizations.py             # Performance analysis
├── cleanup_sessions.py                  # Session cleanup utility
├── color_demo.py                        # Color scheme demonstration
├── color_matcher.py                     # Color matching utility
├── fix_title.py                         # Title fixing utility
├── migrate_sources.py                   # Source migration helper
├── optimize_sessions.py                 # Session optimization
├── regenerate_html.py                   # HTML regeneration utility
└── verify_self_link_fix.py              # Link verification utility
```

### Session Reports (Session/)
- Historical session reports for tracking development progress
- Not required for application function but useful for documentation

### Development Documentation
- Multiple `.md` files with development notes, testing procedures, and project documentation
- Essential for understanding and maintaining the system but not required for runtime

## Minimal Running Configuration

For the application to function at its most basic level, these files are absolutely essential:

### Core Application
- `capcat.py` - Main entry point
- `cli.py` - Command-line interface
- `requirements.txt` - Dependencies

### Core System
- `core/config.py` - Configuration management
- `core/logging_config.py` - Logging
- `core/exceptions.py` - Exception handling
- `core/utils.py` - Basic utilities
- `core/session_pool.py` - HTTP sessions
- `core/formatter.py` - HTML to Markdown
- `core/unified_media_processor.py` - Media processing
- `core/news_source_adapter.py` - Content fetching
- `core/unified_source_processor.py` - Source processing

### Source System
- `core/source_system/` - Entire directory (new source architecture)
- `sources/active/` - All active source configurations and implementations
- At least one working source (e.g., `sources/active/custom/hn/`)

### Templates
- `templates/article-with-comments.html`
- `themes/base.css`

This minimal configuration would allow basic article fetching and processing functionality.

## System Architecture Notes

1. **Hybrid Architecture**: Combines config-driven sources (YAML) with custom implementations (Python)
2. **Unified Media Processing**: Single system handles all media downloads and embedding
3. **Modular Design**: Sources can be added/removed without affecting core system
4. **Template-based Output**: Consistent HTML generation across all sources
5. **Performance Monitoring**: Built-in metrics and performance tracking
6. **Graceful Degradation**: Individual source failures don't affect the entire system

## File Ownership and Dependencies

- **Core files** (`core/`): Required for basic functionality
- **Source files** (`sources/active/`): Required for content fetching
- **Template files** (`templates/`, `themes/`): Required for HTML output
- **Documentation files** (`docs/`): Essential for maintenance but not runtime
- **Utility scripts**: Optional helpers for development and maintenance
- **Session files**: Historical records, not required for functionality