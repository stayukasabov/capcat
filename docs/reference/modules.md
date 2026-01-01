# Module Reference

Complete reference of all modules, classes, and functions in Capcat.

## Modules by Package


### Core

- [core.article_fetcher](../api/core/article_fetcher.md) - Shared article fetching functionality for Capcat sources
- [core.circuit_breaker](../api/core/circuit_breaker.md) - Circuit Breaker pattern implementation for Capcat
- [core.cli_recovery](../api/core/cli_recovery.md) - CLI error recovery and user guidance system
- [core.cli_validation](../api/core/cli_validation.md) - Enhanced CLI validation and error handling for better user experience
- [core.command_logging](../api/core/command_logging.md) - Enhanced command logging for CLI debugging and audit trail
- [core.config](../api/core/config.md) - Configuration management for Capcat
- [core.config.__init__](../api/core/__init__.md) - Configuration management package for Capcat
- [core.config.source_base](../api/core/source_base.md) - Base configuration classes for news sources
- [core.config.source_registry](../api/core/source_registry.md) - Source Registry for managing all available news sources and their configurations
- [core.constants](../api/core/constants.md) - Application-wide constants for Capcat
- [core.conversion_executor](../api/core/conversion_executor.md) - Shared executor pool for HTML-to-Markdown conversion to prevent nested ThreadPoolExecutor deadlock
- [core.design_system_compiler](../api/core/design_system_compiler.md) - Design System Compiler for Capcat HTML Generation

Compiles CSS custom properties from the design system into hardcoded values
for performance optimization and self-contained HTML generation
- [core.downloader](../api/core/downloader.md) - Media downloader for Capcat
- [core.enhanced_argparse](../api/core/enhanced_argparse.md) - Enhanced ArgumentParser with better error messages and validation
- [core.error_handling](../api/core/error_handling.md) - Comprehensive error handling and recovery system for Capcat
- [core.ethical_scraping](../api/core/ethical_scraping.md) - Ethical scraping utilities for Capcat
- [core.exceptions](../api/core/exceptions.md) - Custom exceptions for Capcat application
- [core.formatter](../api/core/formatter.md) - HTML to Markdown converter for Capcat
- [core.html_generator](../api/core/html_generator.md) - HTML Generator for Capcat - Static Site Generation
Creates self-contained HTML files from markdown content with embedded CSS and JavaScript
- [core.html_post_processor](../api/core/html_post_processor.md) - HTML Post-Processor for Capcat Archives
Handles post-processing HTML generation after article scraping is complete
- [core.image_processor](../api/core/image_processor.md) - Global Image Processor for Capcat
- [core.interactive](../api/core/interactive.md) - Interactive mode for Capcat
- [core.logging_config](../api/core/logging_config.md) - Logging configuration for Capcat
- [core.media_config](../api/core/media_config.md) - Media Configuration Manager for different news sources
- [core.media_executor](../api/core/media_executor.md) - Shared executor pool for media processing to prevent nested ThreadPoolExecutor deadlock
- [core.media_processor](../api/core/media_processor.md) - Media processing component for Capcat
- [core.network_resilience](../api/core/network_resilience.md) - Network Resilience Patterns for Source Processing

Clean architecture implementation applying SOLID principles:
- Single Responsibility: Each class has one clear purpose
- Open/Closed: Extensible via strategy pattern
- Liskov Substitution: RetryStrategy implementations interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions not concretions
- [core.news_source_adapter](../api/core/news_source_adapter.md) - Base NewsSourceAdapter class to eliminate code duplication across source modules
- [core.progress](../api/core/progress.md) - Progress indicators and status reporting for Capcat
- [core.rate_limiter](../api/core/rate_limiter.md) - Rate limiting system for Capcat to prevent overwhelming source servers
- [core.retry](../api/core/retry.md) - Retry mechanisms with exponential backoff for Capcat
- [core.retry_skip](../api/core/retry_skip.md) - Retry-and-Skip Logic for Network Resilience

Implements intelligent retry-and-skip mechanism for sources that timeout
or refuse connection
- [core.session_pool](../api/core/session_pool.md) - Global session pooling for optimal network performance across all sources
- [core.shutdown](../api/core/shutdown.md) - Graceful shutdown handling for Capcat
- [core.source_config](../api/core/source_config.md) - Source configuration for optimized URL detection in Capcat
- [core.source_configs](../api/core/source_configs.md) - Modular source configuration system with backward compatibility
- [core.source_factory](../api/core/source_factory.md) - Modernized factory for creating news source adapters
- [core.source_system.__init__](../api/core/__init__.md) - Source system for specialized source handling
- [core.source_system.add_source_command](../api/core/add_source_command.md) - Professional implementation of the add-source command using clean architecture principles
- [core.source_system.add_source_service](../api/core/add_source_service.md) - Service layer for the add-source command
- [core.source_system.base_source](../api/core/base_source.md) - Abstract base class for all news sources
- [core.source_system.bundle_manager](../api/core/bundle_manager.md)
- [core.source_system.bundle_models](../api/core/bundle_models.md) - Data models for bundle management
- [core.source_system.bundle_service](../api/core/bundle_service.md) - Service layer for bundle management
- [core.source_system.bundle_ui](../api/core/bundle_ui.md) - User interface components for bundle management
- [core.source_system.bundle_validator](../api/core/bundle_validator.md) - Bundle validation logic
- [core.source_system.config_driven_source](../api/core/config_driven_source.md) - Config-driven source implementation
- [core.source_system.discovery_strategies](../api/core/discovery_strategies.md) - Discovery strategy implementations for article discovery
- [core.source_system.enhanced_remove_command](../api/core/enhanced_remove_command.md) - Enhanced remove-source command with advanced features:
- Dry-run mode
- Automatic backups
- Usage analytics
- Batch removal from file
- Undo/restore functionality
- [core.source_system.feed_discovery](../api/core/feed_discovery.md) - RSS/Atom feed discovery utilities
- [core.source_system.feed_parser](../api/core/feed_parser.md) - Feed parser abstraction for RSS and Atom feeds
- [core.source_system.performance_monitor](../api/core/performance_monitor.md) - Source performance monitoring system for the hybrid architecture
- [core.source_system.questionary_ui](../api/core/questionary_ui.md) - User interface implementation using questionary for interactive prompts
- [core.source_system.removal_ui](../api/core/removal_ui.md) - User interface implementation for remove-source command
- [core.source_system.remove_source_command](../api/core/remove_source_command.md) - Professional implementation of the remove-source command using clean architecture
- [core.source_system.remove_source_service](../api/core/remove_source_service.md) - Service layer for remove-source command
- [core.source_system.rss_feed_introspector](../api/core/rss_feed_introspector.md)
- [core.source_system.source_analytics](../api/core/source_analytics.md) - Source usage analytics and statistics
- [core.source_system.source_backup_manager](../api/core/source_backup_manager.md) - Backup and restore functionality for source configurations
- [core.source_system.source_config](../api/core/source_config.md) - Source configuration system for specialized sources
- [core.source_system.source_config_generator](../api/core/source_config_generator.md)
- [core.source_system.source_factory](../api/core/source_factory.md) - Source factory for creating and managing news source instances
- [core.source_system.source_registry](../api/core/source_registry.md) - Source registry for automatic discovery and management of news sources
- [core.source_system.validation_engine](../api/core/validation_engine.md) - Enhanced configuration validation engine for the source system
- [core.specialized_source_manager](../api/core/specialized_source_manager.md) - Specialized Source Manager for automatic URL-based source activation
- [core.storage_manager](../api/core/storage_manager.md) - Storage management component for Capcat
- [core.streamlined_comment_processor](../api/core/streamlined_comment_processor.md) - Streamlined comment processor for optimizing nested structure handling and reducing conversion time
- [core.template_renderer](../api/core/template_renderer.md) - Simple Template Renderer for Capcat
Replaces {{placeholder}} variables with actual values from configuration
- [core.theme_utils](../api/core/theme_utils.md) - Theme utilities for hash-based theme persistence
- [core.timeout_config](../api/core/timeout_config.md) - Adaptive timeout configuration for Capcat
- [core.timeout_wrapper](../api/core/timeout_wrapper.md) - Timeout wrapper utilities for preventing hanging operations
- [core.unified_article_processor](../api/core/unified_article_processor.md) - Unified Article Processor - Universal entry point for all article processing
- [core.unified_media_processor](../api/core/unified_media_processor.md) - Unified Media Processor Integration Layer
- [core.unified_source_processor](../api/core/unified_source_processor.md) - Unified Source Processor for Capcat
- [core.update_manager](../api/core/update_manager.md) - Update Manager for Capcat
- [core.url_utils](../api/core/url_utils.md) - URL validation and normalization utilities for Capcat
- [core.utils](../api/core/utils.md) - Core utilities for the Capcat application

### Htmlgen

- [htmlgen.__init__](../api/htmlgen/__init__.md) - Compartmentalized HTML Generation System for Capcat
- [htmlgen.base.base_generator](../api/htmlgen/base_generator.md) - Base HTML Generator for Compartmentalized HTML Generation System
- [htmlgen.hn.generator](../api/htmlgen/generator.md) - Hacker News specific HTML generator implementation
- [htmlgen.lb.generator](../api/htmlgen/generator.md) - Lobsters specific HTML generator implementation
- [htmlgen.lesswrong.generator](../api/htmlgen/generator.md) - LessWrong specific HTML generator implementation

### Root

- [__version__](../api/root/__version__.md) - Capcat version information
- [add_jekyll_frontmatter](../api/root/add_jekyll_frontmatter.md) - Add Jekyll front matter to all HTML files so Jekyll processes them
- [build_site](../api/root/build_site.md) - Build script: Replace Jekyll includes with actual HTML content
- [capcat](../api/root/capcat.md) - Capcat - News Article Archiving System

A free and open-source tool to make people's lives easier
- [cleanup_development_files](../api/root/cleanup_development_files.md) - Remove internal development files from git tracking
- [cleanup_repo](../api/root/cleanup_repo.md) - Repository cleanup script: Remove unnecessary files from git tracking
- [cli](../api/root/cli.md) - Professional CLI interface for Capcat using subcommand architecture
- [convert_docs_to_html](../api/root/convert_docs_to_html.md) - Convert Markdown documentation to clean HTML with minimal styling
- [convert_to_markdown](../api/root/convert_to_markdown.md)
- [delete_h4_colon](../api/root/delete_h4_colon.md) - Delete colon after </h4> tags
- [fix_ascii_formatting](../api/root/fix_ascii_formatting.md) - Fix ASCII formatting in HTML tutorial files
- [fix_breadcrumbs](../api/root/fix_breadcrumbs.md) - Fix breadcrumbs: Remove 'user' from breadcrumb navigation
- [fix_colon_formatting](../api/root/fix_colon_formatting.md) - fix_colon_formatting
- [fix_ethical_scraping_links](../api/root/fix_ethical_scraping_links.md) - Fix ethical-scraping
- [fix_footer_typo](../api/root/fix_footer_typo.md) - Fix typo in footer: edngineering → engineering
- [fix_mismatched_tags](../api/root/fix_mismatched_tags.md) - Fix mismatched pre/div tags in HTML files
- [fix_sources_in_docs](../api/root/fix_sources_in_docs.md) - Fix hardcoded outdated sources in documentation
- [quick_cli_fix](../api/root/quick_cli_fix.md) - Quick CLI validation fix to catch common flag mistakes
- [remove_br_tags](../api/root/remove_br_tags.md) - Remove all <br> tags from HTML files
- [remove_hr_tags](../api/root/remove_hr_tags.md) - Script to remove all <hr> tags from HTML files in website/docs/ directory
- [replace_h4_with_h3](../api/root/replace_h4_with_h3.md) - H4 to H3 Tag Replacement Script
--------------------------------
Replaces all <h4> tags with <h3> tags in HTML files within website/docs/

Requirements Analysis:
1
- [replace_strong_tags](../api/root/replace_strong_tags.md) - Replace all <strong> tags with <h3> tags in HTML files
- [replace_strong_with_h4](../api/root/replace_strong_with_h4.md) - Strong to H4 Tag Replacement Script

Replaces all <strong> tags with <h4> tags in HTML files within website/docs/ directory
- [run_capcat](../api/root/run_capcat.md) - Capcat - News Article Archiving System (Enhanced Python Wrapper)

Refactored wrapper with robust dependency management, intelligent error
handling, and comprehensive validation
- [update_html_includes](../api/root/update_html_includes.md) - Update all HTML files in docs/ to use includes system for header and footer
- [update_html_jekyll](../api/root/update_html_jekyll.md) - Update all HTML files in docs/ to use Jekyll includes for header and footer
- [update_includes](../api/root/update_includes.md) - Update script: Replace old header/footer HTML with new includes

### Scripts

- [scripts.add_doc_navigation](../api/scripts/add_doc_navigation.md) - Add chapter navigation links to documentation HTML files
- [scripts.apply_mermaid_design_system](../api/scripts/apply_mermaid_design_system.md) - Apply design system CSS variables to Mermaid diagram styling in diagrams/*
- [scripts.convert_md_tables_to_html](../api/scripts/convert_md_tables_to_html.md) - Convert Markdown Tables to Centered HTML Tables

Scans all markdown files in website/docs/ directory and converts
markdown tables to centered HTML tables with proper styling
- [scripts.doc_generator](../api/scripts/doc_generator.md) - Documentation Generator for Capcat

Automatically extracts and generates comprehensive documentation from the codebase
- [scripts.extract_and_summarize](../api/scripts/extract_and_summarize.md) - This script extracts text from HTML files in the AgentBrew folder, 
chunks it, and creates markdown files with placeholders for summaries
- [scripts.final_extractor](../api/scripts/final_extractor.md) - This script intelligently extracts meaningful text content from HTML files, 
chunks it, and creates markdown files with placeholders for summaries
- [scripts.generate_diagrams](../api/scripts/generate_diagrams.md) - Generate Architecture Diagrams for Capcat

Creates Mermaid diagrams for system architecture, data flow, and component relationships
- [scripts.generate_source_config](../api/scripts/generate_source_config.md) - Interactive script to generate comprehensive YAML configuration files
for config-driven sources in Capcat
- [scripts.intelligent_html_extractor](../api/scripts/intelligent_html_extractor.md) - This script intelligently extracts text content from HTML files, 
chunks it, and creates markdown files with placeholders for summaries
- [scripts.rename_ink_to_imprint](../api/scripts/rename_ink_to_imprint.md) - Rename all instances of --cream to --paper in website/css/ files
- [scripts.replace_exhaustive](../api/scripts/replace_exhaustive.md) - Replace "Exhaustive" with "Comprehensive" in all website files
- [scripts.replace_menus_with_menu](../api/scripts/replace_menus_with_menu.md) - Replace 'menus' with 'menu' in text under Mermaid diagrams in diagrams/*
- [scripts.run_docs](../api/scripts/run_docs.md) - Documentation Generation Runner

Convenient script to generate all documentation types
- [scripts.setup_dependencies](../api/scripts/setup_dependencies.md) - Automated Dependency Setup and Repair Script for Capcat

This script provides robust virtual environment management with:
- Intelligent venv validation and repair
- Dependency verification and installation
- Path corruption detection and fixing
- Fallback mechanisms for common issues
- Comprehensive logging and diagnostics

Usage:
    python3 scripts/setup_dependencies
- [scripts.update_footer_text](../api/scripts/update_footer_text.md) - Update footer text in website HTML files
- [scripts.update_svg_color](../api/scripts/update_svg_color.md) - Update SVG fill color in all documentation HTML files

### Sources

- [sources.__init__](../api/sources/__init__.md)
- [sources.active.__init__](../api/sources/__init__.md)
- [sources.active.custom.hn.source](../api/sources/source.md) - Hacker News source implementation for the new source system
- [sources.active.custom.lb.source](../api/sources/source.md) - Lobsters source implementation for the new source system
- [sources.base.__init__](../api/sources/__init__.md) - Base classes and interfaces for the source system
- [sources.base.config_schema](../api/sources/config_schema.md) - Base configuration schema for news sources
- [sources.base.factory](../api/sources/factory.md) - Clean factory pattern for creating news source adapters
- [sources.specialized.__init__](../api/sources/__init__.md) - Specialized source implementations for platforms like Medium and Substack
- [sources.specialized.medium.source](../api/sources/source.md) - Medium
- [sources.specialized.substack.source](../api/sources/source.md) - Substack
- [sources.specialized.twitter.__init__](../api/sources/__init__.md) - Twitter/X
- [sources.specialized.twitter.source](../api/sources/source.md) - Twitter/X
- [sources.specialized.vimeo.__init__](../api/sources/__init__.md) - Vimeo specialized source
- [sources.specialized.vimeo.source](../api/sources/source.md) - Vimeo specialized source implementation
- [sources.specialized.youtube.__init__](../api/sources/__init__.md) - YouTube specialized source
- [sources.specialized.youtube.source](../api/sources/source.md) - YouTube specialized source implementation

## Statistics

- **Total Modules**: 141
- **Total Classes**: 224
- **Total Functions**: 299
- **Public Functions**: 264
- **Documentation Coverage**: 88.3%

