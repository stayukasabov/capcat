#!/usr/bin/env python3
"""
Application-wide constants for Capcat.

Centralizes magic numbers and configuration values for maintainability.
All constants follow SCREAMING_SNAKE_CASE convention.
"""

# Network Configuration
DEFAULT_CONNECT_TIMEOUT = 10  # Seconds
DEFAULT_READ_TIMEOUT = 8  # Seconds
MAX_RETRIES = 3  # Maximum retry attempts
RETRY_DELAY_SECONDS = 2.0  # Base delay between retries

# File System
SAFE_FILENAME_CHARS = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789-_."
)

# Ethical Scraping
MAX_LINK_DENSITY_PERCENT = 15  # Aggregator detection threshold
MAX_EXTERNAL_DOMAINS = 10  # Aggregator detection threshold


class ErrorCode:
    """Standardized error codes for programmatic handling.

    Usage:
        try:
            fetch_article(url)
        except NetworkError as e:
            if e.error_code == ErrorCode.NETWORK_ERROR:
                retry_with_backoff()
    """

    SUCCESS = 0
    NETWORK_ERROR = 1001
    CONTENT_FETCH_ERROR = 1002
    FILESYSTEM_ERROR = 1003
    CONFIGURATION_ERROR = 1004
    VALIDATION_ERROR = 1005
    PARSING_ERROR = 1006
    UNKNOWN_ERROR = 9999
