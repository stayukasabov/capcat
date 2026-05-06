---
layout: default
render_with_liquid: false
---

# Module Reference

Complete reference of all modules, classes, and functions in Capcat.

## Modules by Package


### Capcat

- [capcat.cli](../api/capcat/cli.md) - CLI entry point for Capcat
- [capcat.commands.add_source](../api/capcat/add_source.md) - Add-source command - interactive RSS source addition
- [capcat.commands.fetch](../api/capcat/fetch.md) - Batch fetch command - processes multiple sources via the unified processor
- [capcat.commands.generate_config](../api/capcat/generate_config.md) - Generate-config command - launches the interactive source config generator
- [capcat.commands.init](../api/capcat/init.md) - Implementation of capcat init command
- [capcat.commands.remove_source](../api/capcat/remove_source.md) - Remove-source command - interactive source removal with backup/undo support
- [capcat.commands.single](../api/capcat/single.md) - Single article fetch command
- [capcat.core.article_fetcher](../api/capcat/article_fetcher.md) - Shared article fetching functionality for Capcat sources
- [capcat.core.async_pdf_manager](../api/capcat/async_pdf_manager.md) - Asynchronous PDF download manager to prevent thread pool exhaustion
- [capcat.core.circuit_breaker](../api/capcat/circuit_breaker.md) - Circuit Breaker pattern implementation for Capcat
- [capcat.core.cli_recovery](../api/capcat/cli_recovery.md) - CLI error recovery and user guidance system
- [capcat.core.cli_validation](../api/capcat/cli_validation.md) - Enhanced CLI validation and error handling for better user experience
- [capcat.core.command_logging](../api/capcat/command_logging.md) - Enhanced command logging for CLI debugging and audit trail
- [capcat.core.config](../api/capcat/config.md) - Configuration management for Capcat
- [capcat.core.config.source_base](../api/capcat/source_base.md) - Base configuration classes for news sources
- [capcat.core.config.source_registry](../api/capcat/source_registry.md) - Source Registry for managing all available news sources and their configurations
- [capcat.core.constants](../api/capcat/constants.md) - Application-wide constants for Capcat
- [capcat.core.conversion_executor](../api/capcat/conversion_executor.md) - Shared executor pool for HTML-to-Markdown conversion to prevent nested ThreadPoolExecutor deadlock
- [capcat.core.design_system_compiler](../api/capcat/design_system_compiler.md) - Design System Compiler for Capcat HTML Generation

Compiles CSS custom properties from the design system into hardcoded values
for performance optimization and self-contained HTML generation
- [capcat.core.downloader](../api/capcat/downloader.md) - Media downloader for Capcat
- [capcat.core.enhanced_argparse](../api/capcat/enhanced_argparse.md) - Enhanced ArgumentParser with better error messages and validation
- [capcat.core.error_handling](../api/capcat/error_handling.md) - Comprehensive error handling and recovery system for Capcat
- [capcat.core.ethical_scraping](../api/capcat/ethical_scraping.md) - Ethical scraping utilities for Capcat
- [capcat.core.exceptions](../api/capcat/exceptions.md) - Custom exceptions for Capcat application
- [capcat.core.formatter](../api/capcat/formatter.md) - HTML to Markdown converter for Capcat
- [capcat.core.html_post_processor](../api/capcat/html_post_processor.md) - HTML Post-Processor for Capcat Archives
Handles post-processing HTML generation after article scraping is complete
- [capcat.core.image_processor](../api/capcat/image_processor.md) - Global Image Processor for Capcat
- [capcat.core.interactive](../api/capcat/interactive.md) - Interactive mode for Capcat
- [capcat.core.logging_config](../api/capcat/logging_config.md) - Logging configuration for Capcat
- [capcat.core.media_config](../api/capcat/media_config.md) - Media Configuration Manager for different news sources
- [capcat.core.media_executor](../api/capcat/media_executor.md) - Shared executor pool for media processing to prevent nested ThreadPoolExecutor deadlock
- [capcat.core.media_processor](../api/capcat/media_processor.md) - Media processing component for Capcat
- [capcat.core.network_resilience](../api/capcat/network_resilience.md) - Network Resilience Patterns for Source Processing

Clean architecture implementation applying SOLID principles:
- Single Responsibility: Each class has one clear purpose
- Open/Closed: Extensible via strategy pattern
- Liskov Substitution: RetryStrategy implementations interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions not concretions
- [capcat.core.pdf_landing_resolver](../api/capcat/pdf_landing_resolver.md) - Resolve direct PDF URLs to their HTML landing pages where possible
- [capcat.core.progress](../api/capcat/progress.md) - Progress indicators and status reporting for Capcat
- [capcat.core.rate_limiter](../api/capcat/rate_limiter.md) - Rate limiting system for Capcat to prevent overwhelming source servers
- [capcat.core.retry](../api/capcat/retry.md) - Retry mechanisms with exponential backoff for Capcat
- [capcat.core.retry_skip](../api/capcat/retry_skip.md) - Retry-and-Skip Logic for Network Resilience

Implements intelligent retry-and-skip mechanism for sources that timeout
or refuse connection
- [capcat.core.session_pool](../api/capcat/session_pool.md) - Global session pooling for optimal network performance across all sources
- [capcat.core.shutdown](../api/capcat/shutdown.md) - Graceful shutdown handling for Capcat
- [capcat.core.source_config](../api/capcat/source_config.md) - Source configuration for optimized URL detection in Capcat
- [capcat.core.source_config_mirror](../api/capcat/source_config_mirror.md) - Mirror builtin source configs to userspace Config/sources/active/
- [capcat.core.source_configs](../api/capcat/source_configs.md) - Modular source configuration system with backward compatibility
- [capcat.core.source_system.add_source_command](../api/capcat/add_source_command.md) - Professional implementation of the add-source command using clean architecture principles
- [capcat.core.source_system.add_source_service](../api/capcat/add_source_service.md) - Service layer for the add-source command
- [capcat.core.source_system.base_source](../api/capcat/base_source.md) - Abstract base class for all news sources
- [capcat.core.source_system.bundle_manager](../api/capcat/bundle_manager.md)
- [capcat.core.source_system.bundle_models](../api/capcat/bundle_models.md) - Data models for bundle management
- [capcat.core.source_system.bundle_service](../api/capcat/bundle_service.md) - Service layer for bundle management
- [capcat.core.source_system.bundle_ui](../api/capcat/bundle_ui.md) - User interface components for bundle management
- [capcat.core.source_system.bundle_validator](../api/capcat/bundle_validator.md) - Bundle validation logic
- [capcat.core.source_system.config_driven_source](../api/capcat/config_driven_source.md) - Config-driven source implementation
- [capcat.core.source_system.discovery_strategies](../api/capcat/discovery_strategies.md) - Discovery strategy implementations for article discovery
- [capcat.core.source_system.enhanced_remove_command](../api/capcat/enhanced_remove_command.md) - Enhanced remove-source command with advanced features:
- Dry-run mode
- Automatic backups
- Usage analytics
- Batch removal from file
- Undo/restore functionality
- [capcat.core.source_system.feed_discovery](../api/capcat/feed_discovery.md) - RSS/Atom feed discovery utilities
- [capcat.core.source_system.feed_parser](../api/capcat/feed_parser.md) - Feed parser abstraction for RSS and Atom feeds
- [capcat.core.source_system.performance_monitor](../api/capcat/performance_monitor.md) - Source performance monitoring system for the hybrid architecture
- [capcat.core.source_system.questionary_ui](../api/capcat/questionary_ui.md) - User interface implementation using questionary for interactive prompts
- [capcat.core.source_system.removal_ui](../api/capcat/removal_ui.md) - User interface implementation for remove-source command
- [capcat.core.source_system.remove_source_command](../api/capcat/remove_source_command.md) - Base classes and implementations for the remove-source command
- [capcat.core.source_system.remove_source_service](../api/capcat/remove_source_service.md) - Service layer for remove-source command
- [capcat.core.source_system.rss_feed_introspector](../api/capcat/rss_feed_introspector.md)
- [capcat.core.source_system.source_analytics](../api/capcat/source_analytics.md) - Source usage analytics and statistics
- [capcat.core.source_system.source_backup_manager](../api/capcat/source_backup_manager.md) - Backup and restore functionality for source configurations
- [capcat.core.source_system.source_config](../api/capcat/source_config.md) - Source configuration system for specialized sources
- [capcat.core.source_system.source_config_generator](../api/capcat/source_config_generator.md)
- [capcat.core.source_system.source_factory](../api/capcat/source_factory.md) - Source factory for creating and managing news source instances
- [capcat.core.source_system.source_registry](../api/capcat/source_registry.md) - Source registry for automatic discovery and management of news sources
- [capcat.core.source_system.validation_engine](../api/capcat/validation_engine.md) - Enhanced configuration validation engine for the source system
- [capcat.core.storage_manager](../api/capcat/storage_manager.md) - Storage management component for Capcat
- [capcat.core.streamlined_comment_processor](../api/capcat/streamlined_comment_processor.md) - Streamlined comment processor for optimizing nested structure handling and reducing conversion time
- [capcat.core.template_renderer](../api/capcat/template_renderer.md) - Simple Template Renderer for Capcat
Replaces {{placeholder}} variables with actual values from configuration
- [capcat.core.theme_utils](../api/capcat/theme_utils.md) - Theme utilities for hash-based theme persistence
- [capcat.core.timeout_config](../api/capcat/timeout_config.md) - Adaptive timeout configuration for Capcat
- [capcat.core.timeout_wrapper](../api/capcat/timeout_wrapper.md) - Timeout wrapper utilities for preventing hanging operations
- [capcat.core.tui_context](../api/capcat/tui_context.md) - TUI context flag and per-fetch result accumulation
- [capcat.core.unified_article_processor](../api/capcat/unified_article_processor.md) - Unified Article Processor - Universal entry point for all article processing
- [capcat.core.unified_media_processor](../api/capcat/unified_media_processor.md) - Unified Media Processor Integration Layer
- [capcat.core.unified_source_processor](../api/capcat/unified_source_processor.md) - Unified Source Processor for Capcat
- [capcat.core.update_manager](../api/capcat/update_manager.md) - Update Manager for Capcat
- [capcat.core.url_utils](../api/capcat/url_utils.md) - URL validation and normalization utilities for Capcat
- [capcat.core.utils](../api/capcat/utils.md) - Core utilities for the Capcat application
- [capcat.htmlgen.factory](../api/capcat/factory.md) - Factory for creating ArticleHTMLGenerator instances
- [capcat.htmlgen.generator](../api/capcat/generator.md) - HTML Generator for Capcat - Static Site Generation
Creates self-contained HTML files from markdown content with embedded CSS and JavaScript
- [capcat.scripts.generate_source_config](../api/capcat/generate_source_config.md) - Interactive script to generate comprehensive YAML configuration files
for config-driven sources in Capcat
- [capcat.sources.builtin.custom.hn.source](../api/capcat/source.md) - Hacker News source implementation using the official Firebase API
- [capcat.sources.builtin.custom.lb.source](../api/capcat/source.md) - Lobsters source implementation for the new source system
- [capcat.sources.builtin.custom.medium.source](../api/capcat/source.md) - Medium
- [capcat.sources.builtin.custom.substack.source](../api/capcat/source.md) - Substack
- [capcat.sources.builtin.custom.twitter.source](../api/capcat/source.md) - Twitter/X
- [capcat.sources.builtin.custom.vimeo.source](../api/capcat/source.md) - Vimeo specialized source implementation
- [capcat.sources.builtin.custom.youtube.source](../api/capcat/source.md) - YouTube specialized source implementation
- [capcat.tui](../api/capcat/tui.md) - TUI entry point - delegates to core interactive module

### Debug

- [debug.content-extraction-debugger](../api/debug/content-extraction-debugger.md) - Content Extraction Debugging Tool for Capcat
Helps diagnose why articles return empty markdown or fail to fetch
- [debug.fix-sources](../api/debug/fix-sources.md) - Source Fix Tool
Automatically suggests and applies fixes for problematic sources
- [debug.log-analyzer](../api/debug/log-analyzer.md) - Capcat Log Analyzer
Analyzes Capcat logs to identify patterns in failures and warnings
- [debug.quick-troubleshoot](../api/debug/quick-troubleshoot.md) - Quick Troubleshoot Script
Immediately diagnose the three failing URLs from the error messages
- [debug.simple-troubleshoot](../api/debug/simple-troubleshoot.md) - Simple troubleshoot script without emojis per CLAUDE
- [debug.source-tester](../api/debug/source-tester.md) - Source Configuration Tester
Tests Capcat source configurations and suggests fixes

### Htmlgen

- [htmlgen.base.base_generator](../api/htmlgen/base_generator.md) - Base HTML Generator for Compartmentalized HTML Generation System
- [htmlgen.hn.generator](../api/htmlgen/generator.md) - Hacker News specific HTML generator implementation
- [htmlgen.lb.generator](../api/htmlgen/generator.md) - Lobsters specific HTML generator implementation
- [htmlgen.lesswrong.generator](../api/htmlgen/generator.md) - LessWrong specific HTML generator implementation

### Legacy

- [legacy.cli](../api/legacy/cli.md) - Professional CLI interface for Capcat using subcommand architecture
- [legacy.run_capcat](../api/legacy/run_capcat.md) - Capcat - News Article Archiving System (Enhanced Python Wrapper)

Refactored wrapper with robust dependency management, intelligent error
handling, and comprehensive validation

### Root

- [add_jekyll_frontmatter](../api/root/add_jekyll_frontmatter.md) - Add Jekyll front matter to all HTML files so Jekyll processes them
- [build_site](../api/root/build_site.md) - Build script: Replace Jekyll includes with actual HTML content
- [capcat_legacy](../api/root/capcat_legacy.md) - Capcat - News Article Archiving System

A free and open-source tool to make people's lives easier
- [cleanup_development_files](../api/root/cleanup_development_files.md) - Remove internal development files from git tracking
- [cleanup_repo](../api/root/cleanup_repo.md) - Repository cleanup script: Remove unnecessary files from git tracking
- [convert_docs_to_html](../api/root/convert_docs_to_html.md) - Convert Markdown documentation to clean HTML with minimal styling
- [convert_to_markdown](../api/root/convert_to_markdown.md)
- [delete_h4_colon](../api/root/delete_h4_colon.md) - Delete colon after </h4> tags
- [quick_cli_fix](../api/root/quick_cli_fix.md) - Quick CLI validation fix to catch common flag mistakes
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

- [sources.active.custom.hn.source](../api/sources/source.md) - Hacker News source implementation for the new source system
- [sources.active.custom.lb.source](../api/sources/source.md) - Lobsters source implementation for the new source system
- [sources.base.config_schema](../api/sources/config_schema.md) - Base configuration schema for news sources
- [sources.base.factory](../api/sources/factory.md) - Clean factory pattern for creating news source adapters

## Statistics

- **Total Modules**: 138
- **Total Classes**: 225
- **Total Functions**: 365
- **Public Functions**: 286
- **Documentation Coverage**: 78.4%

