#!/usr/bin/env python3
"""
Base configuration classes for news sources.
Provides the foundation for source-specific configuration management.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..logging_config import get_logger


@dataclass
class SourceConfig:
    """Base configuration for news sources."""

    # Basic source information
    name: str
    source_id: str
    base_url: str

    # Network settings
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: Optional[float] = None

    # Request configuration
    user_agent: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)

    # Content extraction selectors
    selectors: Dict[str, str] = field(default_factory=dict)

    # Processing options
    extract_comments: bool = True
    max_articles: int = 30
    enable_media_download: bool = True

    # Source-specific settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default values after creation."""
        if not self.headers:
            self.headers = {}
        if not self.selectors:
            self.selectors = {}
        if not self.custom_settings:
            self.custom_settings = {}

        # Set default user agent if not provided
        if not self.user_agent:
            self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            "name": self.name,
            "source_id": self.source_id,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "rate_limit": self.rate_limit,
            "user_agent": self.user_agent,
            "headers": self.headers,
            "selectors": self.selectors,
            "extract_comments": self.extract_comments,
            "max_articles": self.max_articles,
            "enable_media_download": self.enable_media_download,
            "custom_settings": self.custom_settings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceConfig":
        """Create SourceConfig from dictionary data."""
        return cls(
            name=data["name"],
            source_id=data["source_id"],
            base_url=data["base_url"],
            timeout=data.get("timeout", 30),
            max_retries=data.get("max_retries", 3),
            retry_delay=data.get("retry_delay", 1.0),
            rate_limit=data.get("rate_limit"),
            user_agent=data.get("user_agent"),
            headers=data.get("headers", {}),
            selectors=data.get("selectors", {}),
            extract_comments=data.get("extract_comments", True),
            max_articles=data.get("max_articles", 30),
            enable_media_download=data.get("enable_media_download", True),
            custom_settings=data.get("custom_settings", {}),
        )

    def merge_with(self, other: "SourceConfig") -> "SourceConfig":
        """Merge this configuration with another, with other taking precedence."""
        merged_headers = {**self.headers, **other.headers}
        merged_selectors = {**self.selectors, **other.selectors}
        merged_custom = {**self.custom_settings, **other.custom_settings}

        return SourceConfig(
            name=other.name or self.name,
            source_id=other.source_id or self.source_id,
            base_url=other.base_url or self.base_url,
            timeout=other.timeout if other.timeout != 30 else self.timeout,
            max_retries=(
                other.max_retries
                if other.max_retries != 3
                else self.max_retries
            ),
            retry_delay=(
                other.retry_delay
                if other.retry_delay != 1.0
                else self.retry_delay
            ),
            rate_limit=(
                other.rate_limit
                if other.rate_limit is not None
                else self.rate_limit
            ),
            user_agent=other.user_agent or self.user_agent,
            headers=merged_headers,
            selectors=merged_selectors,
            extract_comments=other.extract_comments,
            max_articles=(
                other.max_articles
                if other.max_articles != 30
                else self.max_articles
            ),
            enable_media_download=other.enable_media_download,
            custom_settings=merged_custom,
        )


@dataclass
class BundleConfig:
    """Configuration for source bundles."""

    name: str
    description: str
    sources: List[str]
    default_count: int = 30
    parallel_processing: bool = True
    bundle_settings: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default values after creation."""
        if not self.bundle_settings:
            self.bundle_settings = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert bundle configuration to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "sources": self.sources,
            "default_count": self.default_count,
            "parallel_processing": self.parallel_processing,
            "bundle_settings": self.bundle_settings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BundleConfig":
        """Create BundleConfig from dictionary data."""
        return cls(
            name=data["name"],
            description=data["description"],
            sources=data["sources"],
            default_count=data.get("default_count", 30),
            parallel_processing=data.get("parallel_processing", True),
            bundle_settings=data.get("bundle_settings", {}),
        )


class SourceConfigLoader:
    """Loads source configurations from various file formats."""

    def __init__(self):
        """Initialize the configuration loader."""
        self.logger = get_logger(__name__)

    def load_from_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load configuration from a file (YAML or JSON).

        Args:
            file_path: Path to the configuration file

        Returns:
            Dictionary containing the configuration data

        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        if not file_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {file_path}"
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix.lower() in [".yml", ".yaml"]:
                    return yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == ".json":
                    return json.load(f) or {}
                else:
                    raise ValueError(
                        f"Unsupported configuration file format: {file_path.suffix}"
                    )

        except Exception as e:
            self.logger.error(
                f"Error loading configuration from {file_path}: {e}"
            )
            raise

    def save_to_file(
        self, data: Dict[str, Any], file_path: Path, format_type: str = "yaml"
    ):
        """
        Save configuration to a file.

        Args:
            data: Configuration data to save
            file_path: Path where to save the file
            format_type: File format ('yaml' or 'json')
        """
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                if format_type.lower() == "yaml":
                    yaml.dump(
                        data, f, default_flow_style=False, sort_keys=False
                    )
                elif format_type.lower() == "json":
                    json.dump(data, f, indent=2, sort_keys=False)
                else:
                    raise ValueError(f"Unsupported format type: {format_type}")

            self.logger.info(f"Configuration saved to {file_path}")

        except Exception as e:
            self.logger.error(
                f"Error saving configuration to {file_path}: {e}"
            )
            raise

    def load_source_config(
        self, file_path: Path, source_id: str
    ) -> Optional[SourceConfig]:
        """
        Load a specific source configuration from a file.

        Args:
            file_path: Path to the configuration file
            source_id: ID of the source to load

        Returns:
            SourceConfig instance or None if not found
        """
        try:
            data = self.load_from_file(file_path)
            sources = data.get("sources", {})

            if source_id not in sources:
                self.logger.warning(
                    f"Source '{source_id}' not found in {file_path}"
                )
                return None

            source_data = sources[source_id]
            source_data["source_id"] = source_id

            return SourceConfig.from_dict(source_data)

        except Exception as e:
            self.logger.error(
                f"Error loading source config for '{source_id}' from {file_path}: {e}"
            )
            return None

    def load_bundle_config(
        self, file_path: Path, bundle_id: str
    ) -> Optional[BundleConfig]:
        """
        Load a specific bundle configuration from a file.

        Args:
            file_path: Path to the configuration file
            bundle_id: ID of the bundle to load

        Returns:
            BundleConfig instance or None if not found
        """
        try:
            data = self.load_from_file(file_path)
            bundles = data.get("bundles", {})

            if bundle_id not in bundles:
                self.logger.warning(
                    f"Bundle '{bundle_id}' not found in {file_path}"
                )
                return None

            bundle_data = bundles[bundle_id]
            bundle_data["name"] = bundle_id

            return BundleConfig.from_dict(bundle_data)

        except Exception as e:
            self.logger.error(
                f"Error loading bundle config for '{bundle_id}' from {file_path}: {e}"
            )
            return None
