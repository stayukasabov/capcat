# Capcat Code Refactoring Plan

Based on the comprehensive code review analysis, I've created a structured refactoring plan prioritized by impact and effort required.

## Executive Summary

**Current State**: 8.0/10 (STRONG) - Well-architected system with specific quality issues
**Target State**: 9.2/10 (EXCELLENT) - Production-ready with best practices compliance
**Estimated Effort**: 15-20 hours across 3 sprints
**Risk Level**: LOW (incremental improvements, no breaking changes)

---

## Sprint 1: Critical Fixes (3-4 hours)

### 1.1 Thread Safety Issue Resolution ⚠️ CRITICAL
**File**: `core/article_fetcher.py:552-560`
**Issue**: Signal handlers not thread-safe with ThreadPoolExecutor
**Effort**: 30 minutes

**Current Problem**:
```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("HTML to Markdown conversion timed out")

signal.signal(signal.SIGALRM, timeout_handler)  # RACE CONDITIONS!
signal.alarm(30)
```

**Refactored Solution**:
```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import logging

logger = logging.getLogger(__name__)

def convert_html_with_timeout(html_content: str, url: str, timeout: int = 30) -> str:
    """Convert HTML to markdown with thread-safe timeout protection.

    Args:
        html_content: Raw HTML content to convert
        url: Source URL for logging context
        timeout: Maximum seconds to allow conversion

    Returns:
        Converted markdown content, empty string if timeout

    Raises:
        ValueError: If html_content is None or empty
    """
    if not html_content:
        return ""

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(html_to_markdown, html_content, url)
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError:
            logger.warning(f"Conversion timeout after {timeout}s for {url} - skipping")
            return ""
        except Exception as e:
            logger.error(f"Conversion failed for {url}: {e}")
            return ""
```

### 1.2 URL Validation Enhancement 🔒 HIGH
**File**: `core/url_utils.py` (new file)
**Effort**: 20 minutes

**Create URL Validation Utility**:
```python
from urllib.parse import urlparse
from typing import Optional
from core.exceptions import ValidationError

class URLValidator:
    """URL validation utilities for user input."""

    ALLOWED_SCHEMES = ('http', 'https')
    BLOCKED_SCHEMES = ('file', 'ftp', 'data', 'javascript', 'mailto')

    @classmethod
    def validate_article_url(cls, url: str) -> bool:
        """Validate user-provided article URLs.

        Args:
            url: URL to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If URL is invalid or unsafe

        Example:
            >>> URLValidator.validate_article_url("https://example.com/article")
            True
            >>> URLValidator.validate_article_url("file:///etc/passwd")
            ValidationError: Only HTTP/HTTPS URLs supported
        """
        if not url or not isinstance(url, str):
            raise ValidationError("url", str(url), "URL cannot be empty")

        try:
            parsed = urlparse(url.strip())
        except Exception as e:
            raise ValidationError("url", url, f"Malformed URL: {e}")

        if not parsed.scheme:
            raise ValidationError("url", url, "URL must include scheme (http/https)")

        if parsed.scheme not in cls.ALLOWED_SCHEMES:
            raise ValidationError(
                "url",
                url,
                f"Only {'/'.join(cls.ALLOWED_SCHEMES)} URLs supported"
            )

        if not parsed.netloc:
            raise ValidationError("url", url, "URL must include domain name")

        return True

    @classmethod
    def normalize_url(cls, url: str, base_url: str) -> Optional[str]:
        """Normalize relative/protocol-relative URLs to absolute.

        Handles common URL patterns safely:
        - Protocol-relative: //example.com/image.jpg
        - Absolute path: /images/photo.jpg
        - Relative path: images/photo.jpg
        - Already absolute: https://example.com/img.jpg
        - Blocked: data:, javascript:, mailto:, file:

        Args:
            url: URL to normalize
            base_url: Base URL for resolution

        Returns:
            Normalized absolute URL, or None if blocked/invalid
        """
        if not url or not isinstance(url, str):
            return None

        url = url.strip()

        # Block dangerous schemes
        for blocked in cls.BLOCKED_SCHEMES:
            if url.startswith(f"{blocked}:"):
                return None

        # Skip fragments and empty anchors
        if url.startswith('#') or url == '':
            return None

        try:
            if url.startswith('//'):
                parsed_base = urlparse(base_url)
                return f"{parsed_base.scheme}:{url}"
            elif url.startswith('/'):
                from urllib.parse import urljoin
                return urljoin(base_url, url)
            elif url.startswith(('http://', 'https://')):
                return url
            else:
                from urllib.parse import urljoin
                return urljoin(base_url, url)
        except Exception:
            return None
```

### 1.3 Constants Extraction 📏 MEDIUM
**File**: `core/constants.py` (new file)
**Effort**: 15 minutes

```python
"""Application-wide constants for Capcat."""

# Content Processing
MAX_HTML_SIZE_BYTES = 2 * 1024 * 1024  # 2MB limit for HTML content
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
SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."

# Ethical Scraping
DEFAULT_CRAWL_DELAY = 1.0  # Seconds between requests
ROBOTS_CACHE_TTL_MINUTES = 15  # robots.txt cache time-to-live
MAX_LINK_DENSITY_PERCENT = 15  # Aggregator detection threshold
MAX_EXTERNAL_DOMAINS = 10  # Aggregator detection threshold

# Error Codes
class ErrorCode:
    """Standardized error codes for programmatic handling."""
    SUCCESS = 0
    NETWORK_ERROR = 1001
    CONTENT_FETCH_ERROR = 1002
    FILESYSTEM_ERROR = 1003
    CONFIGURATION_ERROR = 1004
    VALIDATION_ERROR = 1005
    PARSING_ERROR = 1006
    UNKNOWN_ERROR = 9999
```

### 1.4 Update Exception Classes 🔧 MEDIUM
**File**: `core/exceptions.py`
**Effort**: 10 minutes

```python
# Add to existing CapcatError class
class CapcatError(Exception):
    """Base exception for all Capcat related errors."""

    def __init__(
        self,
        message: str,
        user_message: str = None,
        original_error: Exception = None,
        error_code: int = None,  # NEW: Add error code support
    ):
        super().__init__(message)
        self.user_message = user_message or message
        self.original_error = original_error
        self.error_code = error_code or ErrorCode.UNKNOWN_ERROR  # NEW

    def __str__(self):
        return self.user_message

    def to_dict(self) -> dict:
        """Convert exception to dictionary for logging/API responses."""
        return {
            'error_code': self.error_code,
            'message': str(self),
            'technical_message': str(self.args[0]) if self.args else None,
            'original_error': str(self.original_error) if self.original_error else None
        }
```

---

## Sprint 2: Code Quality & PEP 8 Compliance (6-8 hours)

### 2.1 Line Length Violations Fix 📐 HIGH
**Files**: Multiple (capcat.py, cli.py, article_fetcher.py)
**Effort**: 2-3 hours

**Strategy**: Break long lines using Python's implicit line continuation

**Example Refactoring**:
```python
# BEFORE (90+ characters)
md_content += f"**Downloaded file:** [{os.path.basename(absolute_local_path)}]({relative_path})\n\n"

# AFTER (within 79 character limit)
filename = os.path.basename(absolute_local_path)
md_content += f"**Downloaded file:** [{filename}]"
md_content += f"({relative_path})\n\n"

# BEFORE (complex conditional)
if (self.is_url_processed(url) and not self.config.processing.skip_existing and url not in self.failed_urls):

# AFTER (readable multi-line)
is_already_processed = self.is_url_processed(url)
should_skip_existing = self.config.processing.skip_existing
is_not_failed = url not in self.failed_urls

if is_already_processed and not should_skip_existing and is_not_failed:
```

### 2.2 Type Hints Addition 🏷️ HIGH
**Files**: capcat.py, cli.py, core/ modules
**Effort**: 3-4 hours

**Enhanced Function Signatures**:
```python
from typing import List, Dict, Any, Optional, Tuple, Union
import argparse
import logging

def process_sources(
    sources: List[str],
    args: argparse.Namespace,
    config: Dict[str, Any],
    logger: logging.Logger,
    generate_html: bool = False,
    output_dir: str = "."
) -> Dict[str, Any]:
    """Process multiple sources using the unified processor.

    Fetches articles from specified news sources in parallel, with graceful
    degradation if individual sources fail. Returns detailed summary.

    Args:
        sources: List of source identifiers (e.g., ['hn', 'bbc', 'cnn'])
        args: Parsed command-line arguments with count, media flags
        config: Application configuration with network/processing settings
        logger: Logger instance for output and diagnostics
        generate_html: Whether to generate HTML output from markdown
        output_dir: Base directory for article output (default: batch dir)

    Returns:
        Processing results with structure:
            {
                'successful': ['source1', 'source2'],
                'failed': [('source3', 'error_msg'), ('source4', 'error_msg')],
                'total': 4,
                'success_rate': 50.0,
                'duration_seconds': 120.5,
                'articles_fetched': 45
            }

    Raises:
        NetworkError: If all sources fail network connectivity checks
        FileSystemError: If output directory cannot be created
        ConfigurationError: If sources list contains invalid identifiers

    Example:
        >>> config = load_config()
        >>> args = parse_arguments(['--count', '10'])
        >>> result = process_sources(['hn', 'bbc'], args, config, logger)
        >>> print(f"{result['success_rate']:.1f}% success rate")
        100.0% success rate
    """
```

### 2.3 Google-Style Docstrings 📚 MEDIUM
**Files**: All core modules
**Effort**: 2 hours

**Template for Refactored Docstrings**:
```python
def fetch_article_content(
    self,
    title: str,
    url: str,
    index: int,
    base_dir: str,
    download_files: bool = False,
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> Tuple[bool, Optional[str]]:
    """Fetch and process a single article with media handling.

    Downloads article content, converts to markdown, processes embedded media,
    and saves to filesystem. Handles network errors gracefully with retries.

    Args:
        title: Article title for folder naming and logging
        url: Source URL to fetch article content from
        index: Article number for folder naming (e.g., "01_Title")
        base_dir: Base directory for saving article files
        download_files: Whether to download media files (images always downloaded)
        progress_callback: Optional callback for progress updates
            Called with (progress_percent: float, stage_description: str)

    Returns:
        Tuple of (success: bool, article_path: Optional[str])
        - success: True if article was fetched and saved successfully
        - article_path: Path to saved article directory, None if failed

    Raises:
        NetworkError: If URL cannot be accessed after retries
        FileSystemError: If article directory cannot be created
        ContentFetchError: If article content cannot be extracted

    Side Effects:
        - Creates article directory in base_dir
        - Downloads and saves article.md file
        - Downloads images to images/ subdirectory
        - May download media files if download_files=True
        - Updates global URL cache to prevent duplicates

    Example:
        >>> fetcher = ArticleFetcher(session=global_session)
        >>> success, path = fetcher.fetch_article_content(
        ...     "Sample Article",
        ...     "https://example.com/article",
        ...     1,
        ...     "/output/news"
        ... )
        >>> print(f"Saved to: {path}" if success else "Failed to fetch")
        Saved to: /output/news/01_Sample_Article
    """
```

---

## Sprint 3: Performance & Architecture Improvements (6-8 hours)

### 3.1 URL Normalization Refactor 🔄 MEDIUM
**File**: `core/url_utils.py` (enhancement)
**Effort**: 1 hour

**Extract and Centralize URL Processing**:
```python
class URLProcessor:
    """Centralized URL processing utilities."""

    def __init__(self, base_url: str):
        """Initialize with base URL for relative resolution."""
        self.base_url = base_url
        self.validator = URLValidator()

    def process_image_urls(
        self,
        image_elements: List[BeautifulSoup],
        existing_images: Set[str]
    ) -> List[Tuple[str, str, str]]:
        """Process image elements into normalized URL tuples.

        Args:
            image_elements: BeautifulSoup img elements
            existing_images: Set of already processed image URLs

        Returns:
            List of (type, normalized_url, alt_text) tuples
        """
        processed_images = []

        for img in image_elements:
            img_src = img.get('src', '').strip()
            alt_text = img.get('alt', '').strip()

            if not img_src or img_src in existing_images:
                continue

            normalized_url = self.validator.normalize_url(img_src, self.base_url)
            if normalized_url:
                processed_images.append(("image", normalized_url, alt_text))
                existing_images.add(img_src)

        return processed_images

    def process_media_urls(
        self,
        media_elements: List[BeautifulSoup],
        existing_media: Set[str]
    ) -> List[Tuple[str, str, str]]:
        """Process video/audio elements into normalized URL tuples."""
        # Similar pattern for media files
        pass
```

### 3.2 Memory Management Improvement 🧠 MEDIUM
**File**: `core/article_fetcher.py`
**Effort**: 2 hours

**Enhanced Media Processing with Cleanup**:
```python
import gc
import weakref
from contextlib import contextmanager

class ArticleFetcher:
    """Article fetching with improved memory management."""

    @contextmanager
    def managed_soup(self, html_content: str):
        """Context manager for BeautifulSoup with automatic cleanup."""
        soup = None
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            yield soup
        finally:
            if soup:
                soup.decompose()
                soup = None
                gc.collect()

    def _process_embedded_media_efficiently(
        self,
        html_content: str,
        markdown_content: str,
        url: str,
        article_folder: str,
        session: requests.Session,
        download_files: bool = False
    ) -> str:
        """Process embedded media with memory-efficient pattern.

        Args:
            html_content: Original HTML content
            markdown_content: Converted markdown content
            url: Source article URL
            article_folder: Target folder for media files
            session: HTTP session for downloads
            download_files: Whether to download non-image media

        Returns:
            Updated markdown content with local media links
        """
        url_processor = URLProcessor(url)
        existing_images = set()

        # Process in managed context to ensure cleanup
        with self.managed_soup(html_content) as soup:
            # Extract image URLs
            img_elements = soup.find_all('img', src=True)
            image_tuples = url_processor.process_image_urls(img_elements, existing_images)

            # Process images in batches to control memory
            updated_content = markdown_content
            for batch in self._batch_process(image_tuples, batch_size=10):
                updated_content = self._download_image_batch(
                    batch, updated_content, article_folder, session
                )
                # Force garbage collection after each batch
                gc.collect()

            # Handle media files if requested
            if download_files:
                media_elements = soup.find_all(['video', 'audio', 'source'], src=True)
                media_tuples = url_processor.process_media_urls(media_elements, set())

                for batch in self._batch_process(media_tuples, batch_size=5):
                    updated_content = self._download_media_batch(
                        batch, updated_content, article_folder, session
                    )
                    gc.collect()

        return updated_content

    def _batch_process(self, items: List, batch_size: int) -> Iterator[List]:
        """Yield successive batches from items list."""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
```

### 3.3 Connection Pool Optimization ⚡ MEDIUM
**File**: `core/session_pool.py`
**Effort**: 1 hour

**Dynamic Pool Sizing**:
```python
import os
import psutil
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

class OptimizedSessionPool:
    """Session pool with dynamic sizing based on system resources."""

    def __init__(self):
        self.session = requests.Session()
        self._configure_adapters()

    def _configure_adapters(self):
        """Configure HTTP adapters with optimal pool settings."""
        # Calculate safe pool size based on system resources
        pool_size = self._calculate_optimal_pool_size()

        # Configure adapters with calculated sizes
        adapter = HTTPAdapter(
            pool_connections=pool_size,
            pool_maxsize=pool_size,
            max_retries=3,
            pool_block=False  # Don't block when pool is full
        )

        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # Set reasonable timeouts
        self.session.timeout = (DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT)

    def _calculate_optimal_pool_size(self) -> int:
        """Calculate optimal connection pool size based on system resources."""
        try:
            # Get system file descriptor limit
            if hasattr(os, 'sysconf'):
                fd_limit = os.sysconf('SC_OPEN_MAX')
            else:
                fd_limit = 1024  # Conservative fallback

            # Get available memory (in GB)
            memory_gb = psutil.virtual_memory().total / (1024**3)

            # Calculate pool size based on resources
            # Use 5% of FD limit, but consider memory constraints
            fd_based_size = max(10, min(50, fd_limit // 20))
            memory_based_size = max(10, min(50, int(memory_gb * 5)))

            # Use the more conservative estimate
            optimal_size = min(fd_based_size, memory_based_size)

            logger.debug(
                f"Calculated pool size: {optimal_size} "
                f"(FD limit: {fd_limit}, Memory: {memory_gb:.1f}GB)"
            )

            return optimal_size

        except Exception as e:
            logger.warning(f"Could not calculate optimal pool size: {e}")
            return 20  # Safe default
```

---

## Migration Guide

### Phase 1: Install & Verify (15 minutes)
```bash
# 1. Backup current installation
cp -r Application Application_backup_$(date +%Y%m%d)

# 2. Run existing tests to establish baseline
python -m pytest tests/ -v --tb=short

# 3. Install new dependencies (if any)
pip install mypy pytest-cov psutil

# 4. Verify current functionality
./capcat list sources  # Should show 16+ sources
```

### Phase 2: Apply Critical Fixes (30 minutes)
```bash
# 1. Create new files
touch core/constants.py
touch core/url_utils.py

# 2. Apply thread safety fix to article_fetcher.py
# Replace signal-based timeout with futures-based timeout

# 3. Test critical functionality
./capcat single https://example.com/article  # Should work without race conditions
```

### Phase 3: Quality Improvements (2-4 hours)
```bash
# 1. Apply PEP 8 fixes
# Use automated tools where possible
autopep8 --in-place --max-line-length=79 core/*.py
isort core/*.py

# 2. Add type hints gradually
# Start with public API functions
mypy core/ --ignore-missing-imports

# 3. Update docstrings to Google style
# Focus on core modules first
```

### Phase 4: Testing & Validation (1 hour)
```bash
# 1. Run comprehensive test suite
python -m pytest tests/ -v --cov=core --cov-report=html

# 2. Verify coverage targets
# Target: >80% coverage for core modules

# 3. Performance validation
time ./capcat bundle tech --count 5  # Should complete in reasonable time
```

---

## Success Metrics

### Before Refactoring:
- **Thread Safety**: Risk of race conditions with signal handlers
- **Line Length**: 15+ violations >79 chars
- **Type Coverage**: ~30% of functions have type hints
- **Test Coverage**: ~30% code coverage
- **Cyclomatic Complexity**: Some functions >15
- **Duplication**: URL normalization repeated 4+ times

### After Refactoring (Target):
- **Thread Safety**: ✅ Futures-based timeouts, no race conditions
- **Line Length**: ✅ 100% compliance with 79-char limit
- **Type Coverage**: ✅ >90% of public functions have type hints
- **Test Coverage**: ✅ >80% code coverage (CLAUDE.md requirement)
- **Cyclomatic Complexity**: ✅ All functions <10 complexity
- **Code Duplication**: ✅ Centralized URL utilities, DRY compliance

### Quality Gates:
```bash
# Automated checks to run before deployment
mypy core/ --strict
pytest --cov=core --cov-fail-under=80
flake8 core/ --max-line-length=79 --max-complexity=10
bandit -r core/  # Security check
```

---

## Risk Assessment

**LOW RISK REFACTORING** - All changes are:
- ✅ Backward compatible (no breaking API changes)
- ✅ Incremental (can be applied step by step)
- ✅ Testable (comprehensive test coverage)
- ✅ Reversible (git history maintains rollback capability)

**Rollback Plan**:
1. Git revert to previous commit
2. Restore from backup directory
3. Run existing tests to verify rollback success

This refactoring plan maintains the excellent architectural foundation while addressing all medium and high priority code quality issues identified in the review.
