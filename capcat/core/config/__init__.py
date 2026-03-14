#!/usr/bin/env python3
"""
Configuration management package for Capcat.

This package provides comprehensive configuration management including:
- Source-specific configurations
- Bundle definitions
- User profile management
- Environment-specific settings
- Dynamic configuration loading

Example usage:
    from capcat.core.config import get_source_registry, SourceConfig

    # Get the global source registry
    registry = get_source_registry()

    # Get configuration for a specific source
    hn_config = registry.get_source_config('hn')

    # Get bundle configuration
    tech_bundle = registry.get_bundle_config('tech')

    # List available sources
    sources = registry.list_available_sources()
"""

from __future__ import annotations

from pathlib import Path

from .source_base import BundleConfig, SourceConfig, SourceConfigLoader
from .source_registry import (
    SourceRegistry,
    get_source_registry,
    reset_source_registry,
)

# Import original config functions for backward compatibility
try:
    from ..config import (
        FetchNewsConfig,
        LoggingConfig,
        NetworkConfig,
        ProcessingConfig,
        get_config,
        load_config,
        save_config,
    )
except ImportError:
    # Fallback if the original config module isn't available
    def get_config():
        """Fallback get_config function."""

        class FallbackConfig:
            """Minimal hard-coded defaults used when capcat.yml is absent."""

            class network:
                """Network timeout and connection pool defaults."""
                connect_timeout = 10
                read_timeout = 8
                media_download_timeout = 10
                head_request_timeout = 3
                pool_connections = 20
                pool_maxsize = 20
                user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                max_retries = 3
                retry_delay = 1.0

            class processing:
                """Article processing and media download defaults."""
                max_workers = 8
                max_filename_length = 100
                remove_script_tags = True
                remove_style_tags = True
                remove_nav_tags = True
                download_images = True
                download_videos = True
                download_audio = True
                download_documents = True

            class logging:
                """Logging output defaults."""
                default_level = "INFO"
                use_colors = True

            def to_dict(self):
                """Convert config to dictionary format for compatibility."""
                return {
                    "network": {
                        "connect_timeout": self.network.connect_timeout,
                        "read_timeout": self.network.read_timeout,
                        "media_download_timeout": self.network.media_download_timeout,
                        "head_request_timeout": self.network.head_request_timeout,
                        "pool_connections": self.network.pool_connections,
                        "pool_maxsize": self.network.pool_maxsize,
                        "user_agent": self.network.user_agent,
                        "max_retries": self.network.max_retries,
                        "retry_delay": self.network.retry_delay,
                    },
                    "processing": {
                        "max_workers": self.processing.max_workers,
                        "max_filename_length": self.processing.max_filename_length,
                        "remove_script_tags": self.processing.remove_script_tags,
                        "remove_style_tags": self.processing.remove_style_tags,
                        "remove_nav_tags": self.processing.remove_nav_tags,
                        "download_images": self.processing.download_images,
                        "download_videos": self.processing.download_videos,
                        "download_audio": self.processing.download_audio,
                        "download_documents": self.processing.download_documents,
                    },
                    "logging": {
                        "default_level": self.logging.default_level,
                        "use_colors": self.logging.use_colors,
                    },
                }

        return FallbackConfig()

    load_config = get_config
    save_config = lambda x, _="yaml": True

    class FetchNewsConfig:
        """Stub for FetchNewsConfig when the main config module is unavailable."""

    class NetworkConfig:
        """Stub for NetworkConfig when the main config module is unavailable."""

    class ProcessingConfig:
        """Stub for ProcessingConfig when the main config module is unavailable."""

    class LoggingConfig:
        """Stub for LoggingConfig when the main config module is unavailable."""


__all__ = [
    # New configuration system
    "SourceConfig",
    "BundleConfig",
    "SourceConfigLoader",
    "SourceRegistry",
    "get_source_registry",
    "reset_source_registry",
    # Original config functions for backward compatibility
    "get_config",
    "load_config",
    "save_config",
    "FetchNewsConfig",
    "NetworkConfig",
    "ProcessingConfig",
    "LoggingConfig",
    # Project-model path resolution
    "NoProjectError",
    "find_project_root",
    "get_news_dir",
    "get_capcats_dir",
]

__version__ = "2.0.0"


class NoProjectError(Exception):
    """Raised when no capcat project root (.capcat/) is found."""


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from start to find the directory containing .capcat/.

    Args:
        start: Starting directory. Defaults to cwd.

    Returns:
        Path to the project root.

    Raises:
        NoProjectError: If no .capcat/ found up to filesystem root.
    """
    current = (start or Path.cwd()).resolve()
    while True:
        if (current / ".capcat").is_dir():
            return current
        parent = current.parent
        if parent == current:
            raise NoProjectError(
                "Not a capcat project. Run 'capcat init' to initialize one."
            )
        current = parent


def get_news_dir(project_root: Path | None = None) -> Path:
    """Return the News output directory, creating it if absent.

    Args:
        project_root: Project root path. Defaults to find_project_root().

    Returns:
        Path to the News/ directory (guaranteed to exist).
    """
    root = project_root or find_project_root()
    news = root / "News"
    if not news.exists():
        news.mkdir(parents=True)
        print(f"Created output directory: {news}")
    return news


def get_capcats_dir(project_root: Path | None = None) -> Path:
    """Return the Capcats output directory, creating it if absent.

    Args:
        project_root: Project root path. Defaults to find_project_root().

    Returns:
        Path to the Capcats/ directory (guaranteed to exist).
    """
    root = project_root or find_project_root()
    capcats = root / "Capcats"
    if not capcats.exists():
        capcats.mkdir(parents=True)
        print(f"Created output directory: {capcats}")
    return capcats
