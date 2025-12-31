#!/usr/bin/env python3
"""
Configuration management for Capcat.
Handles settings from config files, environment variables, and CLI overrides.
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .logging_config import get_logger


@dataclass
class NetworkConfig:
    """Network-related configuration settings."""

    # HTTP timeouts (in seconds)
    connect_timeout: int = 10
    read_timeout: int = 30  # Increased from 8 to handle complex articles
    media_download_timeout: int = (
        60  # Increased from 10 to handle larger files
    )
    head_request_timeout: int = 10  # Increased from 3 to handle slow servers

    # Connection pooling
    pool_connections: int = 20
    pool_maxsize: int = 20

    # User agent string
    user_agent: str = "Capcat/2.0 (Personal news archiver)"

    # Request retries
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class ProcessingConfig:
    """Processing-related configuration settings."""

    # Concurrency settings
    max_workers: int = 8

    # File handling
    max_filename_length: int = 100

    # Content processing
    remove_script_tags: bool = True
    remove_style_tags: bool = True
    remove_nav_tags: bool = True

    # Media processing
    download_images: bool = True
    download_videos: bool = False
    download_audio: bool = False
    download_documents: bool = False

    # Output settings
    create_comments_file: bool = True
    markdown_line_breaks: bool = True


@dataclass
class UIConfig:
    """User interface and experience configuration settings."""

    # Progress bar settings
    progress_spinner_style: str = (
        "dots"  # dots, wave, loading, pulse, bounce, modern
    )
    batch_spinner_style: str = (
        "activity"  # activity, progress, pulse, wave, dots, scan
    )
    progress_bar_width: int = 25
    show_progress_animations: bool = True

    # Visual feedback
    use_emojis: bool = True
    use_colors: bool = True
    show_detailed_progress: bool = False


@dataclass
class LoggingConfig:
    """Logging-related configuration settings."""

    # Log levels
    default_level: str = "INFO"
    file_level: str = "DEBUG"
    console_level: str = "INFO"

    # Log formatting
    use_colors: bool = True
    include_timestamps: bool = True
    include_module_names: bool = True

    # File logging
    auto_create_log_dir: bool = True
    max_log_file_size: int = 10 * 1024 * 1024  # 10MB
    log_file_backup_count: int = 5


@dataclass
class FetchNewsConfig:
    """Main configuration class containing all settings."""

    network: NetworkConfig = None
    processing: ProcessingConfig = None
    logging: LoggingConfig = None
    ui: UIConfig = None

    def __post_init__(self):
        """Initialize sub-configs if not provided.

        Creates default instances for network, processing, logging, and UI
        configurations when not explicitly specified.
        """
        if self.network is None:
            self.network = NetworkConfig()
        if self.processing is None:
            self.processing = ProcessingConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.ui is None:
            self.ui = UIConfig()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of full configuration
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FetchNewsConfig":
        """Create configuration from dictionary.

        Args:
            data: Dictionary with network, processing, logging sections

        Returns:
            New FetchNewsConfig instance
        """
        network_data = data.get("network", {})
        processing_data = data.get("processing", {})
        logging_data = data.get("logging", {})

        return cls(
            network=NetworkConfig(**network_data),
            processing=ProcessingConfig(**processing_data),
            logging=LoggingConfig(**logging_data),
        )


class ConfigManager:
    """Manages configuration loading and merging from multiple sources."""

    def __init__(self):
        """Initialize the configuration manager.

        Creates default configuration and sets load status to false.
        """
        self.logger = get_logger(__name__)
        self._config = FetchNewsConfig()
        self._config_loaded = False

    def load_config(
        self, config_file: Optional[str] = None, load_env: bool = True
    ) -> FetchNewsConfig:
        """Load configuration from files and environment variables.

        Searches default locations if no file specified. Caches loaded config.

        Args:
            config_file: Path to config file (JSON or YAML)
            load_env: Whether to load environment variables

        Returns:
            Loaded configuration instance
        """
        if self._config_loaded:
            return self._config

        # Start with defaults
        self._config = FetchNewsConfig()

        # Load from config file if specified
        if config_file:
            self._load_from_file(config_file)
        else:
            # Try to find default config files
            self._load_default_config_files()

        # Load environment variables
        if load_env:
            self._load_from_env()

        self._config_loaded = True
        return self._config

    def _load_default_config_files(self):
        """Load from default config file locations.

        Searches in order: local dir, ~/.config/capcat/, /etc/capcat/.
        Stops at first found file.
        """
        # Look for config files in order of preference
        config_locations = [
            "capcat.yml",
            "capcat.yaml",
            "capcat.json",
            os.path.expanduser("~/.config/capcat/config.yml"),
            os.path.expanduser("~/.config/capcat/config.yaml"),
            os.path.expanduser("~/.config/capcat/config.json"),
            "/etc/capcat/config.yml",
            "/etc/capcat/config.yaml",
            "/etc/capcat/config.json",
        ]

        for config_path in config_locations:
            if os.path.isfile(config_path):
                self.logger.debug(f"Found config file: {config_path}")
                self._load_from_file(config_path)
                break

    def _load_from_file(self, config_file: str):
        """Load configuration from a file.

        Supports JSON and YAML formats. Merges into existing config.

        Args:
            config_file: Path to configuration file
        """
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                self.logger.warning(f"Config file not found: {config_file}")
                return

            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.suffix.lower() in [".yml", ".yaml"]:
                    try:
                        import yaml

                        data = yaml.safe_load(f)
                    except ImportError:
                        self.logger.error(
                            "PyYAML not installed, cannot load YAML "
                            "config files"
                        )
                        return
                elif config_path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    self.logger.error(
                        f"Unsupported config file format: {config_path.suffix}"
                    )
                    return

            # Merge loaded data with current config
            self._merge_config_data(data)
            self.logger.info(f"Loaded configuration from: {config_file}")

        except Exception as e:
            self.logger.error(f"Failed to load config file {config_file}: {e}")

    def _load_from_env(self):
        """Load configuration from environment variables.

        Maps CAPCAT_* environment variables to configuration settings.
        Handles type conversion for int, float, bool, and str types.
        """
        env_mappings = {
            # Network settings
            "CAPCAT_CONNECT_TIMEOUT": (
                "network", "connect_timeout", int
            ),
            "CAPCAT_READ_TIMEOUT": ("network", "read_timeout", int),
            "CAPCAT_MEDIA_TIMEOUT": (
                "network", "media_download_timeout", int
            ),
            "CAPCAT_HEAD_TIMEOUT": (
                "network", "head_request_timeout", int
            ),
            "CAPCAT_POOL_CONNECTIONS": ("network", "pool_connections", int),
            "CAPCAT_POOL_MAXSIZE": ("network", "pool_maxsize", int),
            "CAPCAT_USER_AGENT": ("network", "user_agent", str),
            "CAPCAT_MAX_RETRIES": ("network", "max_retries", int),
            "CAPCAT_RETRY_DELAY": ("network", "retry_delay", float),
            # Processing settings
            "CAPCAT_MAX_WORKERS": ("processing", "max_workers", int),
            "CAPCAT_MAX_FILENAME_LENGTH": (
                "processing",
                "max_filename_length",
                int,
            ),
            "CAPCAT_DOWNLOAD_IMAGES": (
                "processing",
                "download_images",
                bool,
            ),
            "CAPCAT_DOWNLOAD_VIDEOS": (
                "processing",
                "download_videos",
                bool,
            ),
            "CAPCAT_DOWNLOAD_AUDIO": ("processing", "download_audio", bool),
            "CAPCAT_DOWNLOAD_DOCUMENTS": (
                "processing",
                "download_documents",
                bool,
            ),
            # Logging settings
            "CAPCAT_LOG_LEVEL": ("logging", "default_level", str),
            "CAPCAT_USE_COLORS": ("logging", "use_colors", bool),
        }

        for env_var, (section, key, type_func) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    if type_func == bool:
                        # Handle boolean environment variables
                        converted_value = value.lower() in (
                            "true",
                            "1",
                            "yes",
                            "on",
                        )
                    else:
                        converted_value = type_func(value)

                    # Set the value in the config
                    section_obj = getattr(self._config, section)
                    setattr(section_obj, key, converted_value)
                    self.logger.debug(
                        f"Set {section}.{key} = {converted_value} "
                        f"from {env_var}"
                    )

                except (ValueError, TypeError) as e:
                    self.logger.warning(
                        f"Invalid value for {env_var}: {value} ({e})"
                    )

    def _merge_config_data(self, data: Dict[str, Any]):
        """Merge configuration data into current config.

        Updates existing config object with values from data dict.
        Warns about unknown sections or keys.

        Args:
            data: Dictionary with section.key structure
        """
        for section_name, section_data in data.items():
            if hasattr(self._config, section_name) and isinstance(
                section_data, dict
            ):
                section_obj = getattr(self._config, section_name)
                for key, value in section_data.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
                        self.logger.debug(
                            f"Set {section_name}.{key} = {value}"
                        )
                    else:
                        self.logger.warning(
                            f"Unknown config key: {section_name}.{key}"
                        )
            else:
                self.logger.warning(f"Unknown config section: {section_name}")

    def get_config(self) -> FetchNewsConfig:
        """Get the current configuration.

        Returns:
            Current configuration instance
        """
        if not self._config_loaded:
            return self.load_config()
        return self._config

    def save_config(self, config_file: str, format: str = "yaml"):
        """Save current configuration to a file.

        Creates parent directories if needed. Supports YAML and JSON formats.

        Args:
            config_file: Path to save configuration
            format: Output format - 'yaml', 'yml', or 'json'

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            config_path = Path(config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            data = self._config.to_dict()

            with open(config_path, "w", encoding="utf-8") as f:
                if format.lower() in ["yml", "yaml"]:
                    try:
                        import yaml

                        yaml.safe_dump(
                            data, f, default_flow_style=False, indent=2
                        )
                    except ImportError:
                        self.logger.error(
                            "PyYAML not installed, cannot save YAML config"
                        )
                        return False
                elif format.lower() == "json":
                    json.dump(data, f, indent=2)
                else:
                    self.logger.error(f"Unsupported config format: {format}")
                    return False

            self.logger.info(f"Saved configuration to: {config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save config to {config_file}: {e}")
            return False


# Global configuration manager instance
_config_manager = ConfigManager()


def get_config() -> FetchNewsConfig:
    """Get the global configuration instance.

    Returns:
        Global configuration object (singleton)
    """
    return _config_manager.get_config()


def load_config(
    config_file: Optional[str] = None, load_env: bool = True
) -> FetchNewsConfig:
    """Load configuration from file and/or environment variables.

    Module-level convenience function for global config manager.

    Args:
        config_file: Path to config file (JSON or YAML)
        load_env: Whether to load environment variables

    Returns:
        Loaded configuration instance
    """
    return _config_manager.load_config(config_file, load_env)


def save_config(config_file: str, format: str = "yaml") -> bool:
    """Save current configuration to a file.

    Module-level convenience function for global config manager.

    Args:
        config_file: Path to save configuration
        format: Output format - 'yaml', 'yml', or 'json'

    Returns:
        True if saved successfully, False otherwise
    """
    return _config_manager.save_config(config_file, format)
