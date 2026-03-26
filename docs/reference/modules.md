# Module Reference

Complete reference of all modules, classes, and functions in Capcat.

## Modules by Package


### Config

- [Config.sources.active.custom.hn.source](../api/Config/source.md) - Hacker News source implementation for the new source system
- [Config.sources.active.custom.lb.source](../api/Config/source.md) - Lobsters source implementation for the new source system
- [Config.sources.active.custom.medium.source](../api/Config/source.md) - Medium
- [Config.sources.active.custom.substack.source](../api/Config/source.md) - Substack
- [Config.sources.active.custom.twitter.source](../api/Config/source.md) - Twitter/X
- [Config.sources.active.custom.vimeo.source](../api/Config/source.md) - Vimeo specialized source implementation
- [Config.sources.active.custom.youtube.source](../api/Config/source.md) - YouTube specialized source implementation

### Build

- [build.lib.capcat.__init__](../api/build/__init__.md) - Capcat — A command-line tool designed to solve content preservation challenges with Ethical Scraping
- [build.lib.capcat.__main__](../api/build/__main__.md)
- [build.lib.capcat.cli](../api/build/cli.md) - CLI entry point for Capcat
- [build.lib.capcat.commands.__init__](../api/build/__init__.md)
- [build.lib.capcat.commands.add_source](../api/build/add_source.md) - Add-source command — interactive RSS source addition
- [build.lib.capcat.commands.fetch](../api/build/fetch.md) - Batch fetch command — processes multiple sources via the unified processor
- [build.lib.capcat.commands.generate_config](../api/build/generate_config.md) - Generate-config command — launches the interactive source config generator
- [build.lib.capcat.commands.init](../api/build/init.md) - Implementation of capcat init command
- [build.lib.capcat.commands.remove_source](../api/build/remove_source.md) - Remove-source command — interactive source removal with backup/undo support
- [build.lib.capcat.commands.single](../api/build/single.md) - Single article fetch command
- [build.lib.capcat.core.__init__](../api/build/__init__.md)
- [build.lib.capcat.core.article_fetcher](../api/build/article_fetcher.md) - Shared article fetching functionality for Capcat sources
- [build.lib.capcat.core.circuit_breaker](../api/build/circuit_breaker.md) - Circuit Breaker pattern implementation for Capcat
- [build.lib.capcat.core.cli_recovery](../api/build/cli_recovery.md) - CLI error recovery and user guidance system
- [build.lib.capcat.core.cli_validation](../api/build/cli_validation.md) - Enhanced CLI validation and error handling for better user experience
- [build.lib.capcat.core.command_logging](../api/build/command_logging.md) - Enhanced command logging for CLI debugging and audit trail
- [build.lib.capcat.core.config](../api/build/config.md) - Configuration management for Capcat
- [build.lib.capcat.core.config.__init__](../api/build/__init__.md) - Configuration management package for Capcat
- [build.lib.capcat.core.config.source_base](../api/build/source_base.md) - Base configuration classes for news sources
- [build.lib.capcat.core.config.source_registry](../api/build/source_registry.md) - Source Registry for managing all available news sources and their configurations
- [build.lib.capcat.core.constants](../api/build/constants.md) - Application-wide constants for Capcat
- [build.lib.capcat.core.conversion_executor](../api/build/conversion_executor.md) - Shared executor pool for HTML-to-Markdown conversion to prevent nested ThreadPoolExecutor deadlock
- [build.lib.capcat.core.design_system_compiler](../api/build/design_system_compiler.md) - Design System Compiler for Capcat HTML Generation

Compiles CSS custom properties from the design system into hardcoded values
for performance optimization and self-contained HTML generation
- [build.lib.capcat.core.downloader](../api/build/downloader.md) - Media downloader for Capcat
- [build.lib.capcat.core.enhanced_argparse](../api/build/enhanced_argparse.md) - Enhanced ArgumentParser with better error messages and validation
- [build.lib.capcat.core.error_handling](../api/build/error_handling.md) - Comprehensive error handling and recovery system for Capcat
- [build.lib.capcat.core.ethical_scraping](../api/build/ethical_scraping.md) - Ethical scraping utilities for Capcat
- [build.lib.capcat.core.exceptions](../api/build/exceptions.md) - Custom exceptions for Capcat application
- [build.lib.capcat.core.formatter](../api/build/formatter.md) - HTML to Markdown converter for Capcat
- [build.lib.capcat.core.html_post_processor](../api/build/html_post_processor.md) - HTML Post-Processor for Capcat Archives
Handles post-processing HTML generation after article scraping is complete
- [build.lib.capcat.core.image_processor](../api/build/image_processor.md) - Global Image Processor for Capcat
- [build.lib.capcat.core.interactive](../api/build/interactive.md) - Interactive mode for Capcat
- [build.lib.capcat.core.logging_config](../api/build/logging_config.md) - Logging configuration for Capcat
- [build.lib.capcat.core.media_config](../api/build/media_config.md) - Media Configuration Manager for different news sources
- [build.lib.capcat.core.media_executor](../api/build/media_executor.md) - Shared executor pool for media processing to prevent nested ThreadPoolExecutor deadlock
- [build.lib.capcat.core.media_processor](../api/build/media_processor.md) - Media processing component for Capcat
- [build.lib.capcat.core.network_resilience](../api/build/network_resilience.md) - Network Resilience Patterns for Source Processing

Clean architecture implementation applying SOLID principles:
- Single Responsibility: Each class has one clear purpose
- Open/Closed: Extensible via strategy pattern
- Liskov Substitution: RetryStrategy implementations interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions not concretions
- [build.lib.capcat.core.progress](../api/build/progress.md) - Progress indicators and status reporting for Capcat
- [build.lib.capcat.core.rate_limiter](../api/build/rate_limiter.md) - Rate limiting system for Capcat to prevent overwhelming source servers
- [build.lib.capcat.core.retry](../api/build/retry.md) - Retry mechanisms with exponential backoff for Capcat
- [build.lib.capcat.core.retry_skip](../api/build/retry_skip.md) - Retry-and-Skip Logic for Network Resilience

Implements intelligent retry-and-skip mechanism for sources that timeout
or refuse connection
- [build.lib.capcat.core.session_pool](../api/build/session_pool.md) - Global session pooling for optimal network performance across all sources
- [build.lib.capcat.core.shutdown](../api/build/shutdown.md) - Graceful shutdown handling for Capcat
- [build.lib.capcat.core.source_config](../api/build/source_config.md) - Source configuration for optimized URL detection in Capcat
- [build.lib.capcat.core.source_config_mirror](../api/build/source_config_mirror.md) - Mirror builtin source configs to userspace Config/sources/active/
- [build.lib.capcat.core.source_configs](../api/build/source_configs.md) - Modular source configuration system with backward compatibility
- [build.lib.capcat.core.source_system.__init__](../api/build/__init__.md)
- [build.lib.capcat.core.source_system.add_source_command](../api/build/add_source_command.md) - Professional implementation of the add-source command using clean architecture principles
- [build.lib.capcat.core.source_system.add_source_service](../api/build/add_source_service.md) - Service layer for the add-source command
- [build.lib.capcat.core.source_system.base_source](../api/build/base_source.md) - Abstract base class for all news sources
- [build.lib.capcat.core.source_system.bundle_manager](../api/build/bundle_manager.md)
- [build.lib.capcat.core.source_system.bundle_models](../api/build/bundle_models.md) - Data models for bundle management
- [build.lib.capcat.core.source_system.bundle_service](../api/build/bundle_service.md) - Service layer for bundle management
- [build.lib.capcat.core.source_system.bundle_ui](../api/build/bundle_ui.md) - User interface components for bundle management
- [build.lib.capcat.core.source_system.bundle_validator](../api/build/bundle_validator.md) - Bundle validation logic
- [build.lib.capcat.core.source_system.config_driven_source](../api/build/config_driven_source.md) - Config-driven source implementation
- [build.lib.capcat.core.source_system.discovery_strategies](../api/build/discovery_strategies.md) - Discovery strategy implementations for article discovery
- [build.lib.capcat.core.source_system.enhanced_remove_command](../api/build/enhanced_remove_command.md) - Enhanced remove-source command with advanced features:
- Dry-run mode
- Automatic backups
- Usage analytics
- Batch removal from file
- Undo/restore functionality
- [build.lib.capcat.core.source_system.feed_discovery](../api/build/feed_discovery.md) - RSS/Atom feed discovery utilities
- [build.lib.capcat.core.source_system.feed_parser](../api/build/feed_parser.md) - Feed parser abstraction for RSS and Atom feeds
- [build.lib.capcat.core.source_system.performance_monitor](../api/build/performance_monitor.md) - Source performance monitoring system for the hybrid architecture
- [build.lib.capcat.core.source_system.questionary_ui](../api/build/questionary_ui.md) - User interface implementation using questionary for interactive prompts
- [build.lib.capcat.core.source_system.removal_ui](../api/build/removal_ui.md) - User interface implementation for remove-source command
- [build.lib.capcat.core.source_system.remove_source_command](../api/build/remove_source_command.md) - Base classes and implementations for the remove-source command
- [build.lib.capcat.core.source_system.remove_source_service](../api/build/remove_source_service.md) - Service layer for remove-source command
- [build.lib.capcat.core.source_system.rss_feed_introspector](../api/build/rss_feed_introspector.md)
- [build.lib.capcat.core.source_system.source_analytics](../api/build/source_analytics.md) - Source usage analytics and statistics
- [build.lib.capcat.core.source_system.source_backup_manager](../api/build/source_backup_manager.md) - Backup and restore functionality for source configurations
- [build.lib.capcat.core.source_system.source_config](../api/build/source_config.md) - Source configuration system for specialized sources
- [build.lib.capcat.core.source_system.source_config_generator](../api/build/source_config_generator.md)
- [build.lib.capcat.core.source_system.source_factory](../api/build/source_factory.md) - Source factory for creating and managing news source instances
- [build.lib.capcat.core.source_system.source_registry](../api/build/source_registry.md) - Source registry for automatic discovery and management of news sources
- [build.lib.capcat.core.source_system.validation_engine](../api/build/validation_engine.md) - Enhanced configuration validation engine for the source system
- [build.lib.capcat.core.specialized_source_manager](../api/build/specialized_source_manager.md) - Specialized Source Manager for automatic URL-based source activation
- [build.lib.capcat.core.storage_manager](../api/build/storage_manager.md) - Storage management component for Capcat
- [build.lib.capcat.core.streamlined_comment_processor](../api/build/streamlined_comment_processor.md) - Streamlined comment processor for optimizing nested structure handling and reducing conversion time
- [build.lib.capcat.core.template_renderer](../api/build/template_renderer.md) - Simple Template Renderer for Capcat
Replaces {{placeholder}} variables with actual values from configuration
- [build.lib.capcat.core.theme_utils](../api/build/theme_utils.md) - Theme utilities for hash-based theme persistence
- [build.lib.capcat.core.timeout_config](../api/build/timeout_config.md) - Adaptive timeout configuration for Capcat
- [build.lib.capcat.core.timeout_wrapper](../api/build/timeout_wrapper.md) - Timeout wrapper utilities for preventing hanging operations
- [build.lib.capcat.core.tui_context](../api/build/tui_context.md) - TUI context flag
- [build.lib.capcat.core.unified_article_processor](../api/build/unified_article_processor.md) - Unified Article Processor - Universal entry point for all article processing
- [build.lib.capcat.core.unified_media_processor](../api/build/unified_media_processor.md) - Unified Media Processor Integration Layer
- [build.lib.capcat.core.unified_source_processor](../api/build/unified_source_processor.md) - Unified Source Processor for Capcat
- [build.lib.capcat.core.update_manager](../api/build/update_manager.md) - Update Manager for Capcat
- [build.lib.capcat.core.url_utils](../api/build/url_utils.md) - URL validation and normalization utilities for Capcat
- [build.lib.capcat.core.utils](../api/build/utils.md) - Core utilities for the Capcat application
- [build.lib.capcat.htmlgen.__init__](../api/build/__init__.md) - HTML generation module for Capcat
- [build.lib.capcat.htmlgen.factory](../api/build/factory.md) - Factory for creating ArticleHTMLGenerator instances
- [build.lib.capcat.htmlgen.generator](../api/build/generator.md) - HTML Generator for Capcat - Static Site Generation
Creates self-contained HTML files from markdown content with embedded CSS and JavaScript
- [build.lib.capcat.scripts.__init__](../api/build/__init__.md)
- [build.lib.capcat.scripts.generate_source_config](../api/build/generate_source_config.md) - Interactive script to generate comprehensive YAML configuration files
for config-driven sources in Capcat
- [build.lib.capcat.sources.__init__](../api/build/__init__.md)
- [build.lib.capcat.sources.base.__init__](../api/build/__init__.md) - Base classes and interfaces for the source system
- [build.lib.capcat.sources.builtin.__init__](../api/build/__init__.md)
- [build.lib.capcat.sources.builtin.custom.hn.source](../api/build/source.md) - Hacker News source implementation for the new source system
- [build.lib.capcat.sources.builtin.custom.lb.source](../api/build/source.md) - Lobsters source implementation for the new source system
- [build.lib.capcat.sources.specialized.__init__](../api/build/__init__.md) - Specialized source implementations for platforms like Medium and Substack
- [build.lib.capcat.sources.specialized.medium.source](../api/build/source.md) - Medium
- [build.lib.capcat.sources.specialized.substack.source](../api/build/source.md) - Substack
- [build.lib.capcat.sources.specialized.twitter.__init__](../api/build/__init__.md) - Twitter/X
- [build.lib.capcat.sources.specialized.twitter.source](../api/build/source.md) - Twitter/X
- [build.lib.capcat.sources.specialized.vimeo.__init__](../api/build/__init__.md) - Vimeo specialized source
- [build.lib.capcat.sources.specialized.vimeo.source](../api/build/source.md) - Vimeo specialized source implementation
- [build.lib.capcat.sources.specialized.youtube.__init__](../api/build/__init__.md) - YouTube specialized source
- [build.lib.capcat.sources.specialized.youtube.source](../api/build/source.md) - YouTube specialized source implementation
- [build.lib.capcat.tui](../api/build/tui.md) - TUI entry point — delegates to core interactive module

### Capcat

- [capcat.__init__](../api/capcat/__init__.md) - Capcat — A command-line tool designed to solve content preservation challenges with Ethical Scraping
- [capcat.__main__](../api/capcat/__main__.md)
- [capcat.cli](../api/capcat/cli.md) - CLI entry point for Capcat
- [capcat.commands.__init__](../api/capcat/__init__.md)
- [capcat.commands.add_source](../api/capcat/add_source.md) - Add-source command — interactive RSS source addition
- [capcat.commands.fetch](../api/capcat/fetch.md) - Batch fetch command — processes multiple sources via the unified processor
- [capcat.commands.generate_config](../api/capcat/generate_config.md) - Generate-config command — launches the interactive source config generator
- [capcat.commands.init](../api/capcat/init.md) - Implementation of capcat init command
- [capcat.commands.remove_source](../api/capcat/remove_source.md) - Remove-source command — interactive source removal with backup/undo support
- [capcat.commands.single](../api/capcat/single.md) - Single article fetch command
- [capcat.core.__init__](../api/capcat/__init__.md)
- [capcat.core.article_fetcher](../api/capcat/article_fetcher.md) - Shared article fetching functionality for Capcat sources
- [capcat.core.circuit_breaker](../api/capcat/circuit_breaker.md) - Circuit Breaker pattern implementation for Capcat
- [capcat.core.cli_recovery](../api/capcat/cli_recovery.md) - CLI error recovery and user guidance system
- [capcat.core.cli_validation](../api/capcat/cli_validation.md) - Enhanced CLI validation and error handling for better user experience
- [capcat.core.command_logging](../api/capcat/command_logging.md) - Enhanced command logging for CLI debugging and audit trail
- [capcat.core.config](../api/capcat/config.md) - Configuration management for Capcat
- [capcat.core.config.__init__](../api/capcat/__init__.md) - Configuration management package for Capcat
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
- [capcat.core.source_system.__init__](../api/capcat/__init__.md)
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
- [capcat.core.tui_context](../api/capcat/tui_context.md) - TUI context flag
- [capcat.core.unified_article_processor](../api/capcat/unified_article_processor.md) - Unified Article Processor - Universal entry point for all article processing
- [capcat.core.unified_media_processor](../api/capcat/unified_media_processor.md) - Unified Media Processor Integration Layer
- [capcat.core.unified_source_processor](../api/capcat/unified_source_processor.md) - Unified Source Processor for Capcat
- [capcat.core.update_manager](../api/capcat/update_manager.md) - Update Manager for Capcat
- [capcat.core.url_utils](../api/capcat/url_utils.md) - URL validation and normalization utilities for Capcat
- [capcat.core.utils](../api/capcat/utils.md) - Core utilities for the Capcat application
- [capcat.htmlgen.__init__](../api/capcat/__init__.md) - HTML generation module for Capcat
- [capcat.htmlgen.factory](../api/capcat/factory.md) - Factory for creating ArticleHTMLGenerator instances
- [capcat.htmlgen.generator](../api/capcat/generator.md) - HTML Generator for Capcat - Static Site Generation
Creates self-contained HTML files from markdown content with embedded CSS and JavaScript
- [capcat.scripts.__init__](../api/capcat/__init__.md)
- [capcat.scripts.generate_source_config](../api/capcat/generate_source_config.md) - Interactive script to generate comprehensive YAML configuration files
for config-driven sources in Capcat
- [capcat.sources.__init__](../api/capcat/__init__.md)
- [capcat.sources.base.__init__](../api/capcat/__init__.md) - Base classes and interfaces for the source system
- [capcat.sources.builtin.__init__](../api/capcat/__init__.md)
- [capcat.sources.builtin.custom.hn.source](../api/capcat/source.md) - Hacker News source implementation for the new source system
- [capcat.sources.builtin.custom.lb.source](../api/capcat/source.md) - Lobsters source implementation for the new source system
- [capcat.sources.builtin.custom.medium.source](../api/capcat/source.md) - Medium
- [capcat.sources.builtin.custom.substack.source](../api/capcat/source.md) - Substack
- [capcat.sources.builtin.custom.twitter.source](../api/capcat/source.md) - Twitter/X
- [capcat.sources.builtin.custom.vimeo.source](../api/capcat/source.md) - Vimeo specialized source implementation
- [capcat.sources.builtin.custom.youtube.source](../api/capcat/source.md) - YouTube specialized source implementation
- [capcat.tui](../api/capcat/tui.md) - TUI entry point — delegates to core interactive module

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

### Legacy

- [legacy.cli](../api/legacy/cli.md) - Professional CLI interface for Capcat using subcommand architecture
- [legacy.run_capcat](../api/legacy/run_capcat.md) - Capcat - News Article Archiving System (Enhanced Python Wrapper)

Refactored wrapper with robust dependency management, intelligent error
handling, and comprehensive validation

### Root

- [__version__](../api/root/__version__.md) - Capcat version information
- [add_jekyll_frontmatter](../api/root/add_jekyll_frontmatter.md) - Add Jekyll front matter to all HTML files so Jekyll processes them
- [build_site](../api/root/build_site.md) - Build script: Replace Jekyll includes with actual HTML content
- [capcat_legacy](../api/root/capcat_legacy.md) - Capcat - News Article Archiving System

A free and open-source tool to make people's lives easier
- [cleanup_development_files](../api/root/cleanup_development_files.md) - Remove internal development files from git tracking
- [cleanup_repo](../api/root/cleanup_repo.md) - Repository cleanup script: Remove unnecessary files from git tracking
- [cli](../api/root/cli.md) - Professional CLI interface for Capcat using subcommand architecture
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

- **Total Modules**: 347
- **Total Classes**: 614
- **Total Functions**: 750
- **Public Functions**: 594
- **Documentation Coverage**: 79.2%

