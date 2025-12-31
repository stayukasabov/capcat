#!/usr/bin/env python3
"""
Application-wide constants for Capcat.

Centralizes magic numbers and configuration values for maintainability.
All constants follow SCREAMING_SNAKE_CASE convention.
"""

# Content Processing
CONVERSION_TIMEOUT_SECONDS = 30  # HTML to Markdown conversion timeout
DEFAULT_ARTICLE_COUNT = 30  # Default articles to fetch per source

# Network Configuration
DEFAULT_CONNECT_TIMEOUT = 10  # Seconds
DEFAULT_READ_TIMEOUT = 8  # Seconds
MAX_RETRIES = 3  # Maximum retry attempts
RETRY_DELAY_SECONDS = 2.0  # Base delay between retries

# Media Processing
DEFAULT_MAX_IMAGES = 20  # Normal processing limit
MEDIA_FLAG_MAX_IMAGES = 1000  # With --media flag limit
MIN_IMAGE_DIMENSIONS = 150  # Minimum pixels width/height
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB per image

# File System
MAX_FILENAME_LENGTH = 255  # Characters
SAFE_FILENAME_CHARS = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789-_."
)

# Ethical Scraping
DEFAULT_CRAWL_DELAY = 1.0  # Seconds between requests
ROBOTS_CACHE_TTL_MINUTES = 15  # robots.txt cache time-to-live
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
