# Capcat Package

## Overview

This package contains the following modules:

- [`capcat.__init__`](./__init__.md) - Capcat — A command-line tool designed to solve content preservation challenges with Ethical Scraping
- [`capcat.cli`](./cli.md) - CLI entry point for Capcat
- [`capcat.tui`](./tui.md) - TUI entry point — delegates to core interactive module
- [`capcat.__main__`](./__main__.md)
- [`capcat.core.unified_article_processor`](./unified_article_processor.md) - Unified Article Processor - Universal entry point for all article processing
- [`capcat.core.image_processor`](./image_processor.md) - Global Image Processor for Capcat
- [`capcat.core.source_configs`](./source_configs.md) - Modular source configuration system with backward compatibility
- [`capcat.core.timeout_config`](./timeout_config.md) - Adaptive timeout configuration for Capcat
- [`capcat.core.storage_manager`](./storage_manager.md) - Storage management component for Capcat
- [`capcat.core.streamlined_comment_processor`](./streamlined_comment_processor.md) - Streamlined comment processor for optimizing nested structure handling and reducing conversion time
- [`capcat.core.formatter`](./formatter.md) - HTML to Markdown converter for Capcat
- [`capcat.core.command_logging`](./command_logging.md) - Enhanced command logging for CLI debugging and audit trail
- [`capcat.core.config`](./config.md) - Configuration management for Capcat
- [`capcat.core.logging_config`](./logging_config.md) - Logging configuration for Capcat
- [`capcat.core.downloader`](./downloader.md) - Media downloader for Capcat
- [`capcat.core.theme_utils`](./theme_utils.md) - Theme utilities for hash-based theme persistence
- [`capcat.core.article_fetcher`](./article_fetcher.md) - Shared article fetching functionality for Capcat sources
- [`capcat.core.retry_skip`](./retry_skip.md) - Retry-and-Skip Logic for Network Resilience

Implements intelligent retry-and-skip mechanism for sources that timeout
or refuse connection
- [`capcat.core.unified_source_processor`](./unified_source_processor.md) - Unified Source Processor for Capcat
- [`capcat.core.network_resilience`](./network_resilience.md) - Network Resilience Patterns for Source Processing

Clean architecture implementation applying SOLID principles:
- Single Responsibility: Each class has one clear purpose
- Open/Closed: Extensible via strategy pattern
- Liskov Substitution: RetryStrategy implementations interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions not concretions
- [`capcat.core.session_pool`](./session_pool.md) - Global session pooling for optimal network performance across all sources
- [`capcat.core.constants`](./constants.md) - Application-wide constants for Capcat
- [`capcat.core.shutdown`](./shutdown.md) - Graceful shutdown handling for Capcat
- [`capcat.core.rate_limiter`](./rate_limiter.md) - Rate limiting system for Capcat to prevent overwhelming source servers
- [`capcat.core.__init__`](./__init__.md)
- [`capcat.core.ethical_scraping`](./ethical_scraping.md) - Ethical scraping utilities for Capcat
- [`capcat.core.error_handling`](./error_handling.md) - Comprehensive error handling and recovery system for Capcat
- [`capcat.core.retry`](./retry.md) - Retry mechanisms with exponential backoff for Capcat
- [`capcat.core.conversion_executor`](./conversion_executor.md) - Shared executor pool for HTML-to-Markdown conversion to prevent nested ThreadPoolExecutor deadlock
- [`capcat.core.enhanced_argparse`](./enhanced_argparse.md) - Enhanced ArgumentParser with better error messages and validation
- [`capcat.core.circuit_breaker`](./circuit_breaker.md) - Circuit Breaker pattern implementation for Capcat
- [`capcat.core.utils`](./utils.md) - Core utilities for the Capcat application
- [`capcat.core.cli_validation`](./cli_validation.md) - Enhanced CLI validation and error handling for better user experience
- [`capcat.core.html_post_processor`](./html_post_processor.md) - HTML Post-Processor for Capcat Archives
Handles post-processing HTML generation after article scraping is complete
- [`capcat.core.interactive`](./interactive.md) - Interactive mode for Capcat
- [`capcat.core.exceptions`](./exceptions.md) - Custom exceptions for Capcat application
- [`capcat.core.update_manager`](./update_manager.md) - Update Manager for Capcat
- [`capcat.core.cli_recovery`](./cli_recovery.md) - CLI error recovery and user guidance system
- [`capcat.core.tui_context`](./tui_context.md) - TUI context flag
- [`capcat.core.progress`](./progress.md) - Progress indicators and status reporting for Capcat
- [`capcat.core.media_processor`](./media_processor.md) - Media processing component for Capcat
- [`capcat.core.source_config`](./source_config.md) - Source configuration for optimized URL detection in Capcat
- [`capcat.core.url_utils`](./url_utils.md) - URL validation and normalization utilities for Capcat
- [`capcat.core.design_system_compiler`](./design_system_compiler.md) - Design System Compiler for Capcat HTML Generation

Compiles CSS custom properties from the design system into hardcoded values
for performance optimization and self-contained HTML generation
- [`capcat.core.media_executor`](./media_executor.md) - Shared executor pool for media processing to prevent nested ThreadPoolExecutor deadlock
- [`capcat.core.timeout_wrapper`](./timeout_wrapper.md) - Timeout wrapper utilities for preventing hanging operations
- [`capcat.core.media_config`](./media_config.md) - Media Configuration Manager for different news sources
- [`capcat.core.unified_media_processor`](./unified_media_processor.md) - Unified Media Processor Integration Layer
- [`capcat.core.template_renderer`](./template_renderer.md) - Simple Template Renderer for Capcat
Replaces {{placeholder}} variables with actual values from configuration
- [`capcat.core.specialized_source_manager`](./specialized_source_manager.md) - Specialized Source Manager for automatic URL-based source activation
- [`capcat.htmlgen.__init__`](./__init__.md) - HTML generation module for Capcat
- [`capcat.htmlgen.factory`](./factory.md) - Factory for creating ArticleHTMLGenerator instances
- [`capcat.htmlgen.generator`](./generator.md) - HTML Generator for Capcat - Static Site Generation
Creates self-contained HTML files from markdown content with embedded CSS and JavaScript
- [`capcat.sources.__init__`](./__init__.md)
- [`capcat.commands.fetch`](./fetch.md) - Batch fetch command — processes multiple sources via the unified processor
- [`capcat.commands.add_source`](./add_source.md) - Add-source command — interactive RSS source addition
- [`capcat.commands.remove_source`](./remove_source.md) - Remove-source command — interactive source removal with backup/undo support
- [`capcat.commands.single`](./single.md) - Single article fetch command
- [`capcat.commands.generate_config`](./generate_config.md) - Generate-config command — launches the interactive source config generator
- [`capcat.commands.__init__`](./__init__.md)
- [`capcat.commands.init`](./init.md) - Implementation of capcat init command
- [`capcat.sources.specialized.__init__`](./__init__.md) - Specialized source implementations for platforms like Medium and Substack
- [`capcat.sources.builtin.__init__`](./__init__.md)
- [`capcat.sources.base.__init__`](./__init__.md) - Base classes and interfaces for the source system
- [`capcat.sources.builtin.custom.lb.source`](./source.md) - Lobsters source implementation for the new source system
- [`capcat.sources.builtin.custom.hn.source`](./source.md) - Hacker News source implementation for the new source system
- [`capcat.sources.specialized.twitter.__init__`](./__init__.md) - Twitter/X
- [`capcat.sources.specialized.twitter.source`](./source.md) - Twitter/X
- [`capcat.sources.specialized.substack.source`](./source.md) - Substack
- [`capcat.sources.specialized.vimeo.__init__`](./__init__.md) - Vimeo specialized source
- [`capcat.sources.specialized.vimeo.source`](./source.md) - Vimeo specialized source implementation
- [`capcat.sources.specialized.medium.source`](./source.md) - Medium
- [`capcat.sources.specialized.youtube.__init__`](./__init__.md) - YouTube specialized source
- [`capcat.sources.specialized.youtube.source`](./source.md) - YouTube specialized source implementation
- [`capcat.core.config.__init__`](./__init__.md) - Configuration management package for Capcat
- [`capcat.core.config.source_registry`](./source_registry.md) - Source Registry for managing all available news sources and their configurations
- [`capcat.core.config.source_base`](./source_base.md) - Base configuration classes for news sources
- [`capcat.core.source_system.bundle_manager`](./bundle_manager.md)
- [`capcat.core.source_system.remove_source_command`](./remove_source_command.md) - Base classes and implementations for the remove-source command
- [`capcat.core.source_system.add_source_command`](./add_source_command.md) - Professional implementation of the add-source command using clean architecture principles
- [`capcat.core.source_system.removal_ui`](./removal_ui.md) - User interface implementation for remove-source command
- [`capcat.core.source_system.feed_discovery`](./feed_discovery.md) - RSS/Atom feed discovery utilities
- [`capcat.core.source_system.source_analytics`](./source_analytics.md) - Source usage analytics and statistics
- [`capcat.core.source_system.validation_engine`](./validation_engine.md) - Enhanced configuration validation engine for the source system
- [`capcat.core.source_system.remove_source_service`](./remove_source_service.md) - Service layer for remove-source command
- [`capcat.core.source_system.add_source_service`](./add_source_service.md) - Service layer for the add-source command
- [`capcat.core.source_system.bundle_models`](./bundle_models.md) - Data models for bundle management
- [`capcat.core.source_system.source_factory`](./source_factory.md) - Source factory for creating and managing news source instances
- [`capcat.core.source_system.performance_monitor`](./performance_monitor.md) - Source performance monitoring system for the hybrid architecture
- [`capcat.core.source_system.__init__`](./__init__.md)
- [`capcat.core.source_system.bundle_validator`](./bundle_validator.md) - Bundle validation logic
- [`capcat.core.source_system.bundle_ui`](./bundle_ui.md) - User interface components for bundle management
- [`capcat.core.source_system.rss_feed_introspector`](./rss_feed_introspector.md)
- [`capcat.core.source_system.discovery_strategies`](./discovery_strategies.md) - Discovery strategy implementations for article discovery
- [`capcat.core.source_system.source_backup_manager`](./source_backup_manager.md) - Backup and restore functionality for source configurations
- [`capcat.core.source_system.questionary_ui`](./questionary_ui.md) - User interface implementation using questionary for interactive prompts
- [`capcat.core.source_system.config_driven_source`](./config_driven_source.md) - Config-driven source implementation
- [`capcat.core.source_system.feed_parser`](./feed_parser.md) - Feed parser abstraction for RSS and Atom feeds
- [`capcat.core.source_system.source_config`](./source_config.md) - Source configuration system for specialized sources
- [`capcat.core.source_system.source_config_generator`](./source_config_generator.md)
- [`capcat.core.source_system.base_source`](./base_source.md) - Abstract base class for all news sources
- [`capcat.core.source_system.source_registry`](./source_registry.md) - Source registry for automatic discovery and management of news sources
- [`capcat.core.source_system.enhanced_remove_command`](./enhanced_remove_command.md) - Enhanced remove-source command with advanced features:
- Dry-run mode
- Automatic backups
- Usage analytics
- Batch removal from file
- Undo/restore functionality
- [`capcat.core.source_system.bundle_service`](./bundle_service.md) - Service layer for bundle management
