# core.constants

**File:** `Application/core/constants.py`

## Description

Application-wide constants for Capcat.

Centralizes magic numbers and configuration values for maintainability.
All constants follow SCREAMING_SNAKE_CASE convention.

## Constants

### CONVERSION_TIMEOUT_SECONDS

**Value:** `30`

### DEFAULT_ARTICLE_COUNT

**Value:** `30`

### DEFAULT_CONNECT_TIMEOUT

**Value:** `10`

### DEFAULT_READ_TIMEOUT

**Value:** `8`

### MAX_RETRIES

**Value:** `3`

### RETRY_DELAY_SECONDS

**Value:** `2.0`

### DEFAULT_MAX_IMAGES

**Value:** `20`

### MEDIA_FLAG_MAX_IMAGES

**Value:** `1000`

### MIN_IMAGE_DIMENSIONS

**Value:** `150`

### MAX_IMAGE_SIZE_BYTES

**Value:** `5 * 1024 * 1024`

### MAX_FILENAME_LENGTH

**Value:** `255`

### SAFE_FILENAME_CHARS

**Value:** `'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.'`

### DEFAULT_CRAWL_DELAY

**Value:** `1.0`

### ROBOTS_CACHE_TTL_MINUTES

**Value:** `15`

### MAX_LINK_DENSITY_PERCENT

**Value:** `15`

### MAX_EXTERNAL_DOMAINS

**Value:** `10`

### SUCCESS

**Value:** `0`

### NETWORK_ERROR

**Value:** `1001`

### CONTENT_FETCH_ERROR

**Value:** `1002`

### FILESYSTEM_ERROR

**Value:** `1003`

### CONFIGURATION_ERROR

**Value:** `1004`

### VALIDATION_ERROR

**Value:** `1005`

### PARSING_ERROR

**Value:** `1006`

### UNKNOWN_ERROR

**Value:** `9999`

## Classes

### ErrorCode

Standardized error codes for programmatic handling.

Usage:
    try:
        fetch_article(url)
    except NetworkError as e:
        if e.error_code == ErrorCode.NETWORK_ERROR:
            retry_with_backoff()


