# Core Package

## Overview

This package contains the following modules:

- [`core.unified_article_processor`](./unified_article_processor.md) - Unified Article Processor - Universal entry point for all article processing
- [`core.image_processor`](./image_processor.md) - Global Image Processor for Capcat
- [`core.source_configs`](./source_configs.md) - Modular source configuration system with backward compatibility
- [`core.timeout_config`](./timeout_config.md) - Adaptive timeout configuration for Capcat
- [`core.storage_manager`](./storage_manager.md) - Storage management component for Capcat
- [`core.streamlined_comment_processor`](./streamlined_comment_processor.md) - Streamlined comment processor for optimizing nested structure handling and reducing conversion time
- [`core.formatter`](./formatter.md) - HTML to Markdown converter for Capcat
- [`core.config`](./config.md) - Configuration management for Capcat
- [`core.logging_config`](./logging_config.md) - Logging configuration for Capcat
- [`core.downloader`](./downloader.md) - Media downloader for Capcat
- [`core.theme_utils`](./theme_utils.md) - Theme utilities for hash-based theme persistence
- [`core.news_source_adapter`](./news_source_adapter.md) - Base NewsSourceAdapter class to eliminate code duplication across source modules
- [`core.article_fetcher`](./article_fetcher.md) - Shared article fetching functionality for Capcat sources
- [`core.retry_skip`](./retry_skip.md) - Retry-and-Skip Logic for Network Resilience

Implements intelligent retry-and-skip mechanism for sources that timeout
or refuse connection
- [`core.source_factory`](./source_factory.md) - Modernized factory for creating news source adapters
- [`core.unified_source_processor`](./unified_source_processor.md) - Unified Source Processor for Capcat
- [`core.network_resilience`](./network_resilience.md) - Network Resilience Patterns for Source Processing

Clean architecture implementation applying SOLID principles:
- Single Responsibility: Each class has one clear purpose
- Open/Closed: Extensible via strategy pattern
- Liskov Substitution: RetryStrategy implementations interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions not concretions
- [`core.session_pool`](./session_pool.md) - Global session pooling for optimal network performance across all sources
- [`core.constants`](./constants.md) - Application-wide constants for Capcat
- [`core.html_generator`](./html_generator.md) - HTML Generator for Capcat - Static Site Generation
Creates self-contained HTML files from markdown content with embedded CSS and JavaScript
- [`core.shutdown`](./shutdown.md) - Graceful shutdown handling for Capcat
- [`core.rate_limiter`](./rate_limiter.md) - Rate limiting system for Capcat to prevent overwhelming source servers
- [`core.ethical_scraping`](./ethical_scraping.md) - Ethical scraping utilities for Capcat
- [`core.error_handling`](./error_handling.md) - Comprehensive error handling and recovery system for Capcat
- [`core.retry`](./retry.md) - Retry mechanisms with exponential backoff for Capcat
- [`core.circuit_breaker`](./circuit_breaker.md) - Circuit Breaker pattern implementation for Capcat
- [`core.utils`](./utils.md) - Core utilities for the Capcat application
- [`core.html_post_processor`](./html_post_processor.md) - HTML Post-Processor for Capcat Archives
Handles post-processing HTML generation after article scraping is complete
- [`core.interactive`](./interactive.md) - Interactive mode for Capcat
- [`core.exceptions`](./exceptions.md) - Custom exceptions for Capcat application
- [`core.update_manager`](./update_manager.md) - Update Manager for Capcat
- [`core.progress`](./progress.md) - Progress indicators and status reporting for Capcat
- [`core.media_processor`](./media_processor.md) - Media processing component for Capcat
- [`core.source_config`](./source_config.md) - Source configuration for optimized URL detection in Capcat
- [`core.url_utils`](./url_utils.md) - URL validation and normalization utilities for Capcat
- [`core.design_system_compiler`](./design_system_compiler.md) - Design System Compiler for Capcat HTML Generation

Compiles CSS custom properties from the design system into hardcoded values
for performance optimization and self-contained HTML generation
- [`core.media_executor`](./media_executor.md) - Shared executor pool for media processing to prevent nested ThreadPoolExecutor deadlock
- [`core.timeout_wrapper`](./timeout_wrapper.md) - Timeout wrapper utilities for preventing hanging operations
- [`core.media_config`](./media_config.md) - Media Configuration Manager for different news sources
- [`core.unified_media_processor`](./unified_media_processor.md) - Unified Media Processor Integration Layer
- [`core.template_renderer`](./template_renderer.md) - Simple Template Renderer for Capcat
Replaces {{placeholder}} variables with actual values from configuration
- [`core.specialized_source_manager`](./specialized_source_manager.md) - Specialized Source Manager for automatic URL-based source activation
- [`core.config.__init__`](./__init__.md) - Configuration management package for Capcat
- [`core.config.source_registry`](./source_registry.md) - Source Registry for managing all available news sources and their configurations
- [`core.config.source_base`](./source_base.md) - Base configuration classes for news sources
- [`core.source_system.bundle_manager`](./bundle_manager.md)
- [`core.source_system.remove_source_command`](./remove_source_command.md) - Professional implementation of the remove-source command using clean architecture
- [`core.source_system.add_source_command`](./add_source_command.md) - Professional implementation of the add-source command using clean architecture principles
- [`core.source_system.removal_ui`](./removal_ui.md) - User interface implementation for remove-source command
- [`core.source_system.feed_discovery`](./feed_discovery.md) - RSS/Atom feed discovery utilities
- [`core.source_system.source_analytics`](./source_analytics.md) - Source usage analytics and statistics
- [`core.source_system.validation_engine`](./validation_engine.md) - Enhanced configuration validation engine for the source system
- [`core.source_system.remove_source_service`](./remove_source_service.md) - Service layer for remove-source command
- [`core.source_system.add_source_service`](./add_source_service.md) - Service layer for the add-source command
- [`core.source_system.bundle_models`](./bundle_models.md) - Data models for bundle management
- [`core.source_system.source_factory`](./source_factory.md) - Source factory for creating and managing news source instances
- [`core.source_system.performance_monitor`](./performance_monitor.md) - Source performance monitoring system for the hybrid architecture
- [`core.source_system.__init__`](./__init__.md) - Source system for specialized source handling
- [`core.source_system.bundle_validator`](./bundle_validator.md) - Bundle validation logic
- [`core.source_system.bundle_ui`](./bundle_ui.md) - User interface components for bundle management
- [`core.source_system.rss_feed_introspector`](./rss_feed_introspector.md)
- [`core.source_system.discovery_strategies`](./discovery_strategies.md) - Discovery strategy implementations for article discovery
- [`core.source_system.source_backup_manager`](./source_backup_manager.md) - Backup and restore functionality for source configurations
- [`core.source_system.questionary_ui`](./questionary_ui.md) - User interface implementation using questionary for interactive prompts
- [`core.source_system.config_driven_source`](./config_driven_source.md) - Config-driven source implementation
- [`core.source_system.feed_parser`](./feed_parser.md) - Feed parser abstraction for RSS and Atom feeds
- [`core.source_system.source_config`](./source_config.md) - Source configuration system for specialized sources
- [`core.source_system.source_config_generator`](./source_config_generator.md)
- [`core.source_system.base_source`](./base_source.md) - Abstract base class for all news sources
- [`core.source_system.source_registry`](./source_registry.md) - Source registry for automatic discovery and management of news sources
- [`core.source_system.enhanced_remove_command`](./enhanced_remove_command.md) - Enhanced remove-source command with advanced features:
- Dry-run mode
- Automatic backups
- Usage analytics
- Batch removal from file
- Undo/restore functionality
- [`core.source_system.bundle_service`](./bundle_service.md) - Service layer for bundle management
