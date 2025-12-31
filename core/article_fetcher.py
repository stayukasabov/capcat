#!/usr/bin/env python3
"""
Shared article fetching functionality for Capcat sources.

This module contains the base ArticleFetcher class that eliminates
code duplication between source-specific implementations.
"""

import io
import os
import sys
import threading
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Callable, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pynput import keyboard

from .config import get_config
from .downloader import (
    download_file,
    is_audio_url,
    is_document_url,
    is_video_url,
)
from .formatter import html_to_markdown
from .logging_config import get_logger
from .rate_limiter import acquire_rate_limit
from .retry import network_retry
from .timeout_config import get_timeout_for_source, record_response_time
from .timeout_wrapper import safe_network_operation

# Global update mode flag that can be accessed by all ArticleFetcher instances
_GLOBAL_UPDATE_MODE = False

# PDF download skip feature constants
LARGE_PDF_THRESHOLD_MB = 5
SKIP_PROMPT_TIMEOUT_SECONDS = 20
BYTES_TO_MB = 1024 * 1024


@contextmanager
def _suppress_stderr():
    """
    Context manager to temporarily suppress stderr output at OS level.

    Used to suppress pynput's misleading accessibility warning on macOS.
    The warning says "Input event monitoring will not be possible" but
    keyboard detection actually works correctly. Uses os.dup2() for
    OS-level redirection to catch warnings from subprocesses/threads.

    Falls back to Python-level redirection in test environments where
    stderr is replaced with StringIO.
    """
    # Check if stderr has fileno (real file descriptor)
    try:
        stderr_fd = sys.stderr.fileno()
        has_fileno = True
    except (AttributeError, io.UnsupportedOperation):
        has_fileno = False

    if has_fileno:
        # OS-level redirection for production (catches subprocess warnings)
        saved_stderr_fd = os.dup(stderr_fd)
        devnull_fd = None
        try:
            devnull_fd = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull_fd, stderr_fd)
            yield
        finally:
            os.dup2(saved_stderr_fd, stderr_fd)
            os.close(saved_stderr_fd)
            if devnull_fd is not None:
                os.close(devnull_fd)
    else:
        # Python-level redirection for test environments
        old_stderr = sys.stderr
        devnull = None
        try:
            devnull = open(os.devnull, 'w')
            sys.stderr = devnull
            yield
        finally:
            sys.stderr = old_stderr
            if devnull is not None:
                devnull.close()


def set_global_update_mode(update_mode: bool):
    """Set the global update mode flag."""
    global _GLOBAL_UPDATE_MODE
    _GLOBAL_UPDATE_MODE = update_mode


def get_global_update_mode() -> bool:
    """Get the global update mode flag."""
    return _GLOBAL_UPDATE_MODE
from .utils import sanitize_filename
from concurrent.futures import (
    TimeoutError as FutureTimeoutError
)
from core.constants import CONVERSION_TIMEOUT_SECONDS
from core.conversion_executor import get_conversion_executor


def convert_html_with_timeout(
    html_content: str,
    url: str,
    timeout: int = CONVERSION_TIMEOUT_SECONDS
) -> str:
    """Convert HTML to markdown with thread-safe timeout protection.

    Uses concurrent.futures for thread-safe timeout handling, replacing
    signal-based approach which caused race conditions in parallel processing.

    Args:
        html_content: Raw HTML content to convert
        url: Source URL for logging context
        timeout: Maximum seconds to allow conversion (default: 30)

    Returns:
        Converted markdown content, empty string if timeout or error

    Raises:
        None - All exceptions are caught and logged

    Example:
        >>> html = "<html><body><h1>Test</h1></body></html>"
        >>> markdown = convert_html_with_timeout(html, "https://example.com")
        >>> print(markdown)
        # Test

    Thread Safety:
        This function is thread-safe and can be called concurrently
        from multiple threads without race conditions.
    """
    logger = get_logger("convert_html_with_timeout")

    # Handle empty or invalid content
    if not html_content or not isinstance(html_content, str):
        return ""

    html_content = html_content.strip()
    if not html_content:
        return ""

    # Execute conversion in shared thread pool with timeout
    # Using shared executor prevents nested ThreadPoolExecutor deadlock
    executor = get_conversion_executor()
    future = executor.submit(html_to_markdown, html_content, url)
    try:
        result = future.result(timeout=timeout)
        return result if result else ""
    except FutureTimeoutError:
        logger.warning(
            f"Conversion timeout after {timeout}s for {url} - skipping"
        )
        return ""
    except Exception as e:
        logger.error(f"Conversion failed for {url}: {e}")
        return ""


class ArticleFetcher(ABC):
    """
    Base class for article fetching with shared functionality.

    This eliminates code duplication between HN and Lobsters implementations
    while allowing source-specific customizations.
    """

    def __init__(
        self, session: requests.Session, download_files: bool = False,
        source_code: str = "unknown", generate_html: bool = False
    ):
        """
        Initialize with a requests session for connection pooling.

        Args:
            session: Requests session for connection pooling
            download_files: Whether to download all media files
            source_code: Source identifier for rate limiting
                (e.g., 'hn', 'scientificamerican')
            generate_html: Whether to generate HTML output files
        """
        self.session = session
        # Whether to download all files (PDFs, audio, video)
        self.download_files = download_files
        self.source_code = source_code
        self.generate_html = generate_html
        self.logger = get_logger(self.__class__.__name__)

        # Initialize MediaProcessor for delegating media operations
        from .media_processor import MediaProcessor
        self.media_processor = MediaProcessor(session, download_files)

    def set_download_files(self, download_files: bool):
        """Dynamically set the download_files flag."""
        self.download_files = download_files

    def _create_markdown_link_replacement(
        self,
        markdown_content: str,
        original_url: str,
        local_path: str,
        fallback_text: str,
        is_image: bool = False
    ) -> str:
        """
        Replace markdown link/image references with local paths.

        Consolidates duplicate URL replacement logic that appears 4+ times
        in the codebase. Handles both image and link syntax with proper
        f-string formatting to prevent syntax errors.

        Args:
            markdown_content: Markdown text to process
            original_url: URL to replace (will be escaped for regex)
            local_path: Local file path to use instead
            fallback_text: Text to use if link text is empty
            is_image: True for image syntax (![]()),
                False for link syntax ([])

        Returns:
            Updated markdown content with replaced URLs

        Example:
            >>> content = "![](http://example.com/img.jpg)"
            >>> result = self._create_markdown_link_replacement(
            ...     content, "http://example.com/img.jpg",
            ...     "images/img.jpg", "image", is_image=True
            ... )
            >>> print(result)
            ![image](images/img.jpg)
        """
        import re

        escaped_url = re.escape(original_url)
        prefix = "!" if is_image else ""

        # Strategy 1: Replace [text](url) or ![text](url) with proper escaping
        pattern = rf"{prefix}\[([^\]]*)\]\({escaped_url}\)"

        def replacement_func(match):
            """Create replacement text with fallback for empty groups."""
            link_text = match.group(1) if match.group(1) else fallback_text
            return f"{prefix}[{link_text}]({local_path})"

        markdown_content = re.sub(pattern, replacement_func, markdown_content)

        # Strategy 2: Direct URL replacement in parentheses
        markdown_content = markdown_content.replace(
            f"]({original_url})", f"]({local_path})"
        )

        # Strategy 3: Replace any remaining instances
        markdown_content = markdown_content.replace(original_url, local_path)

        return markdown_content

    @network_retry
    def _fetch_url_with_retry(
        self, url: str, timeout: int = None
    ) -> requests.Response:
        """
        Fetch URL with automatic retry logic, rate limiting, and
        adaptive timeouts.

        This method provides:
        - Adaptive timeouts based on source performance
        - Rate limiting based on source-specific configuration
        - Up to 3 retry attempts (via @network_retry decorator)
        - Exponential backoff (1s, 2s, 4s)
        - Automatic handling of connection errors and timeouts
        - Response time tracking for adaptive learning

        Args:
            url: URL to fetch
            timeout: Optional timeout override (uses adaptive if None)

        Returns:
            Response object

        Raises:
            requests.exceptions.RequestException: After all retries exhausted
        """
        # Ethical scraping checks
        from core.ethical_scraping import get_ethical_manager
        ethical_manager = get_ethical_manager()
        can_fetch, reason = ethical_manager.can_fetch(url)
        if not can_fetch:
            raise requests.RequestException(
                f"URL blocked by robots.txt: {reason}"
            )

        # Apply rate limiting before making request
        # This prevents overwhelming source servers
        acquire_rate_limit(self.source_code, blocking=True)

        # Get adaptive timeout for this source if not specified
        if timeout is None:
            timeout_config = get_timeout_for_source(self.source_code)
            timeout = timeout_config.as_tuple()
            self.logger.debug(
                f"Using adaptive timeout for {self.source_code}: "
                f"{timeout_config.connect_timeout}s connect, "
                f"{timeout_config.read_timeout}s read"
            )

        # Track response time for adaptive learning
        start_time = time.time()

        try:
            response = self.session.get(url, timeout=timeout)

            # Check for HTTP errors but don't raise - let caller handle
            # This allows us to create proper error articles instead of
            # failing silently
            if response.status_code >= 400:
                self.logger.warning(
                    f"HTTP {response.status_code} for {url}"
                )

            response.raise_for_status()

            # Record successful response time
            duration = time.time() - start_time
            record_response_time(self.source_code, duration)

            return response

        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self.logger.debug(
                f"Timeout for {self.source_code} after {duration:.1f}s"
            )
            raise

    @abstractmethod
    def should_skip_url(self, url: str, title: str) -> bool:
        """
        Source-specific logic to determine if a URL should be skipped.

        Args:
            url: The article URL to check
            title: The article title

        Returns:
            True if the URL should be skipped, False otherwise
        """
        pass

    def fetch_article_content(
        self,
        title: str,
        url: str,
        index: int,
        base_folder: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Fetch and save the content of an article in markdown format.

        This method handles ONLY article content fetching. Comments should be
        fetched separately using source-specific comment fetching methods.

        Args:
            title: Article title
            url: Article URL
            index: Article index number
            base_folder: Base directory to save to
            progress_callback: Optional callback function for progress
                updates (progress, stage)

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (success,
                article_folder_path, article_title)
        """
        try:
            # Use source-specific URL filtering
            if self.should_skip_url(url, title):
                self.logger.debug(f"Skipping internal/filtered link: {title}")
                return False, None, None

            # PHASE 3 INTEGRATION: Check specialized sources first (Twitter, YouTube, etc.)
            from core.unified_article_processor import get_unified_processor as get_article_processor
            article_processor = get_article_processor()

            # Check if this URL should be handled by a specialized source
            if article_processor.specialized_manager.can_handle_url(url):
                self.logger.info(f"Single article: Specialized source detected for {url}")

                # Get global update mode setting
                from core.article_fetcher import get_global_update_mode

                # Use unified article processor for specialized handling
                return article_processor.process_article(
                    url=url,
                    title=title,
                    index=index,
                    base_folder=base_folder,
                    download_files=self.download_files,
                    progress_callback=progress_callback,
                    update_mode=get_global_update_mode()
                )

            # Check if the URL directly points to a media/document file with
            # timeout protection
            file_type = None
            is_pdf_file = False
            try:
                # Check for PDF files first (always handled, regardless of
                # --media flag)
                is_pdf_file = self._is_pdf_url(url)

                if is_pdf_file:
                    file_type = "pdf"
                elif self.download_files:
                    # Use timeout wrappers for media type checks (can hang on
                    # slow servers)
                    is_doc = safe_network_operation(
                        is_document_url, url, timeout=10
                    )
                    is_audio = safe_network_operation(
                        is_audio_url, url, timeout=10
                    )
                    is_video = safe_network_operation(
                        is_video_url, url, timeout=10
                    )

                    if is_doc:
                        file_type = "document"
                    elif is_audio:
                        file_type = "audio"
                    elif is_video:
                        file_type = "video"
            except Exception as e:
                self.logger.debug(f"Could not check media type for {url}: {e}")
                # Continue with regular web page processing

            if file_type:
                result = self._handle_media_file(
                    title, url, index, base_folder, file_type
                )
                if not result[0]:  # If handling failed
                    self.logger.debug(
                        f"Could not handle media file {url}, trying as "
                        f"web content"
                    )
                    # Fall back to regular web content processing
                    return self._fetch_web_content(
                        title, url, index, base_folder, progress_callback
                    )
                return result

            # Fetch regular web page content
            return self._fetch_web_content(
                title, url, index, base_folder, progress_callback
            )

        except Exception as e:
            # Only show detailed error in verbose mode - use debug level for
            # technical details
            self.logger.debug(
                f"Failed to fetch article '{title}' from {url}: {str(e)}"
            )
            # Show user-friendly message
            self.logger.info(f"Could not process article: {title}")
            return False, None, None

    def _is_pdf_url(self, url: str) -> bool:
        """Check if a URL points specifically to a PDF file."""
        return self.media_processor.is_pdf_url(url)

    def _handle_media_file(
        self,
        title: str,
        url: str,
        index: int,
        base_folder: str,
        file_type: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Handle direct media file downloads (documents, audio, video, PDF).
        """
        # Create individual folder for this article
        safe_title = sanitize_filename(title)
        article_folder_name = self._get_unique_folder_name(
            base_folder, safe_title
        )
        article_folder_path = os.path.join(base_folder, article_folder_name)
        os.makedirs(article_folder_path, exist_ok=True)

        # Special handling for PDF files
        if file_type == "pdf":
            # The download_file function will create the "files" folder, so we
            # pass the article folder
            local_path = download_file(
                url, article_folder_path, file_type, True
            )  # Force download for PDFs
            if local_path:
                # Ensure we have an absolute path
                if not os.path.isabs(local_path):
                    absolute_local_path = os.path.join(
                        article_folder_path, local_path
                    )
                else:
                    absolute_local_path = local_path

                # Get relative path from article folder to the file
                relative_path = os.path.relpath(
                    absolute_local_path, article_folder_path
                )

                # Create placeholder markdown with specific title
                md_content = (
                    f"## This is a placeholder for your downloaded file\n\n"
                )
                md_content += f"**Source URL:** [{url}]({url})\n\n"
                md_content += (
                    f"**Downloaded file:** "
                    f"[{os.path.basename(absolute_local_path)}]"
                    f"({relative_path})\n\n"
                )
                md_content += "---\n\n"
                md_content += (
                    f"The PDF file has been downloaded and is available "
                    f"in the files folder.\n\n"
                )

                # Create filename for article content
                filename = os.path.join(article_folder_path, "article.md")

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(md_content)

                # Clean up empty images folder if no images were downloaded
                self._cleanup_empty_images_folder(article_folder_path)

                self.logger.info(f"Successfully saved PDF: {title}")
                return True, title, article_folder_path
            else:
                self.logger.debug(f"Could not download PDF: {title}")
                return False, None, None

        # Handle other media types (existing logic)
        local_path = download_file(
            url, article_folder_path, file_type, self.download_files
        )
        if local_path:
            # Create a simple markdown file that links to the downloaded file
            md_content = f"# {title}\n\n"
            md_content += f"**Source URL:** [{url}]({url})\n\n"
            md_content += "---\n\n"

            if file_type == "document":
                md_content += "## Document\n\n"
                md_content += (
                    f"This article is a document file. You can access it "
                    f"[here]({local_path}).\n\n"
                )
            elif file_type == "audio":
                md_content += "## Audio\n\n"
                md_content += (
                    f"This article is an audio file. You can listen to it "
                    f"[here]({local_path}).\n\n"
                )
                md_content += (
                    f'<audio controls>\n  <source src="{local_path}" '
                    f'type="audio/mpeg">\n  Your browser does not support '
                    f'the audio element.\n</audio>\n\n'
                )
            elif file_type == "video":
                md_content += "## Video\n\n"
                md_content += (
                    f"This article is a video file. You can watch it "
                    f"[here]({local_path}).\n\n"
                )
                md_content += (
                    f'<video controls width="1280" height="720">\n  '
                    f'<source src="{local_path}" type="video/mp4">\n  '
                    f'Your browser does not support the video element.\n'
                    f'</video>\n\n'
                )

            # Create filename for article content
            filename = os.path.join(article_folder_path, "article.md")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(md_content)

            # Clean up empty images folder if no images were downloaded
            self._cleanup_empty_images_folder(article_folder_path)

            self.logger.info(f"Successfully saved {file_type}: {title}")
            return True, title, article_folder_path
        else:
            self.logger.debug(f"Could not download {file_type}: {title}")
            return False, None, None

    def _create_skipped_pdf_placeholder(
        self,
        title: str,
        url: str,
        index: int,
        base_folder: str
    ) -> Tuple[bool, str, str]:
        """
        Create placeholder content for a skipped PDF download.

        Args:
            title: Article title
            url: PDF URL that was skipped
            index: Article index
            base_folder: Base folder for article storage

        Returns:
            Tuple of (success, title, content_path)
        """
        try:
            # Create content file path
            content_path = os.path.join(base_folder, f"{index:02d}_content.txt")

            # Create placeholder content
            placeholder_content = (
                f"PDF Download Skipped\n"
                f"{'=' * 50}\n\n"
                f"This large PDF file was skipped by user choice.\n\n"
                f"Title: {title}\n"
                f"URL: {url}\n\n"
                f"To download this PDF, visit the URL above directly.\n"
            )

            # Write placeholder file
            os.makedirs(os.path.dirname(content_path), exist_ok=True)
            with open(content_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)

            self.logger.info(f"✓ Created skip placeholder for: {title}")
            return True, title, content_path

        except Exception as e:
            self.logger.error(f"Failed to create skip placeholder: {e}")
            return False, None, None

    def _check_pdf_size_and_prompt(
        self,
        url: str,
        title: str,
        is_direct_pdf: bool = False
    ) -> bool:
        """
        Check PDF file size and prompt user to skip if large.

        Args:
            url: PDF file URL
            title: Article title
            is_direct_pdf: True if URL itself is a PDF (not discovered in content)

        Returns:
            True if user wants to skip, False to proceed
        """
        config = get_config()

        try:
            # Make HEAD request to get Content-Length
            response = self.session.head(
                url,
                timeout=config.network.connect_timeout,
                allow_redirects=True
            )

            # Check if Content-Length header exists
            if 'Content-Length' not in response.headers:
                self.logger.debug(
                    f"No Content-Length header for {url}, proceeding with download"
                )
                return False

            # Get file size in MB
            size_bytes = int(response.headers['Content-Length'])
            size_mb = size_bytes / BYTES_TO_MB

            # If file is smaller than threshold, proceed without prompt
            if size_mb < LARGE_PDF_THRESHOLD_MB:
                return False

            # File is large, prompt user with context
            return self._prompt_user_skip(title, size_mb, is_direct_pdf=is_direct_pdf)

        except (ValueError, KeyError) as e:
            # Invalid Content-Length header value
            self.logger.debug(
                f"Invalid Content-Length for {url}: {e}. Proceeding with download."
            )
            return False
        except requests.exceptions.RequestException as e:
            # Network error during HEAD request
            self.logger.warning(
                f"Network error checking PDF size for {url}: {e}. "
                f"Proceeding with download."
            )
            return False
        except Exception as e:
            # Unexpected errors
            self.logger.warning(
                f"Unexpected error checking PDF size for {url}: {e}. "
                f"Proceeding with download."
            )
            return False

    def _prompt_user_skip(
        self,
        title: str,
        size_mb: float,
        is_direct_pdf: bool = False
    ) -> bool:
        """
        Prompt user to skip large PDF download with ESC key.

        Args:
            title: Article title
            size_mb: File size in megabytes
            is_direct_pdf: True if URL itself is a PDF (not discovered in content)

        Returns:
            True if ESC pressed (skip), False on timeout (proceed)
        """
        esc_pressed = threading.Event()

        def on_press(key):
            """Handle key press events."""
            try:
                # Check if ESC key was pressed
                if key == keyboard.Key.esc:
                    esc_pressed.set()
                    return False  # Stop listener
            except AttributeError:
                pass

        # Start keyboard listener in background
        # Suppress pynput's misleading accessibility warning on stderr
        # The warning is emitted asynchronously after listener starts,
        # so we suppress stderr during and after startup with longer sleep
        with _suppress_stderr():
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            # Sleep to allow async warning to be emitted and suppressed
            # Warning appears 0.5-1s after start on macOS
            time.sleep(1.0)

        # Context-aware message
        context_msg = "operation will stop" if is_direct_pdf else "bundle will continue"

        # Display prompt with countdown
        print(
            f"\n{'=' * 60}\n"
            f"Large PDF detected ({size_mb:.1f} MB): {title}\n"
            f"Press ESC within {SKIP_PROMPT_TIMEOUT_SECONDS} seconds to skip ({context_msg})\n"
            f"{'=' * 60}",
            flush=True
        )

        try:
            # Countdown loop
            for remaining in range(SKIP_PROMPT_TIMEOUT_SECONDS, 0, -1):
                if esc_pressed.is_set():
                    if is_direct_pdf:
                        print("\n✓ Skipped - stopping process...", flush=True)
                    else:
                        print("\n✓ Skipped - continuing with next article...", flush=True)
                    return True

                # Show countdown
                sys.stdout.write(f"\r{remaining} seconds remaining... ")
                sys.stdout.flush()
                time.sleep(1)

            # Timeout reached - proceed with download
            print("\n✓ Starting download...", flush=True)
            return False

        finally:
            # Clean up listener
            listener.stop()

    def _fetch_web_content(
        self,
        title: str,
        url: str,
        index: int,
        base_folder: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Fetch and process regular web page content."""
        config = get_config()

        # Check for PDF files and prompt user for large files
        is_direct_pdf_url = url.lower().endswith('.pdf')
        if is_direct_pdf_url:
            should_skip = self._check_pdf_size_and_prompt(
                url, title, is_direct_pdf=True
            )
            if should_skip:
                # Direct PDF URL skip → success (user choice) but no content
                self.logger.info(f"✓ User skipped large PDF - stopping process")
                return True, None, None

        # Report initial progress
        if progress_callback:
            progress_callback(0.0, "fetching content")

        # Attempt to fetch the URL
        try:
            # Use retry-enabled fetch (automatically retries on
            # connection errors)
            response = self._fetch_url_with_retry(
                url, timeout=config.network.read_timeout
            )

        except requests.exceptions.HTTPError as e:
            # HTTP error (4xx, 5xx status codes)
            # Note: Response objects with error codes evaluate as False,
            # must use 'is not None'
            status_code = (
                e.response.status_code if e.response is not None
                else "Unknown"
            )
            error_type = f"HTTP {status_code}"

            # Attempt RSS feed discovery for 403 errors (likely bot protection)
            rss_feed = None
            if status_code == 403:
                self.logger.info(
                    f"403 Forbidden - attempting RSS feed discovery for {url}"
                )
                rss_feed = self._discover_rss_feed(url)

            # Create clean error article instead of failing silently
            return self._create_error_article(
                title=title,
                url=url,
                error_type=error_type,
                error_details=str(e),
                base_folder=base_folder,
                rss_feed_url=rss_feed
            )

        except requests.exceptions.Timeout as e:
            # Connection timeout
            return self._create_error_article(
                title=title,
                url=url,
                error_type="Connection Timeout",
                error_details=(
                    f"The server took too long to respond: {str(e)}"
                ),
                base_folder=base_folder
            )

        except requests.exceptions.ConnectionError as e:
            # Network connection error
            return self._create_error_article(
                title=title,
                url=url,
                error_type="Connection Error",
                error_details=(
                    f"Could not establish connection: {str(e)}"
                ),
                base_folder=base_folder
            )

        except requests.exceptions.RequestException as e:
            # Other network errors
            self.logger.debug(
                f"Network error fetching {url} after retries: {e}"
            )
            return self._create_error_article(
                title=title,
                url=url,
                error_type="Network Error",
                error_details=str(e),
                base_folder=base_folder
            )

        except Exception as e:
            # Unexpected errors
            self.logger.debug(f"Unexpected error fetching {url}: {e}")
            return self._create_error_article(
                title=title,
                url=url,
                error_type="Unexpected Error",
                error_details=str(e),
                base_folder=base_folder
            )

        # Check if response is a PDF file
        content_type = response.headers.get('Content-Type', '').lower()
        is_pdf = (
            'application/pdf' in content_type or
            url.lower().endswith('.pdf')
        )

        if is_pdf:
            # Handle PDF article URLs with streaming download
            # Don't use the response - download with progress instead
            return self._handle_pdf_article(
                title=title,
                url=url,
                base_folder=base_folder,
                progress_callback=progress_callback
            )

        # Report parsing progress
        if progress_callback:
            progress_callback(0.2, "parsing")

        # Store original full page HTML for fallback image detection
        original_full_html = response.text

        try:
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            self.logger.debug(f"Failed to parse HTML from {url}: {e}")
            return False, None, None

        # Remove script and style elements
        for script in soup(
            ["script", "style", "nav", "header", "footer", "aside"]
        ):
            script.decompose()

        # Report cleanup progress
        if progress_callback:
            progress_callback(0.3, "cleaning content")

        # Get page title (prefer meta title, fallback to h1, then
        # provided title)
        page_title = title  # Default to provided title

        # Try to get a better title from the page
        if soup.title and soup.title.string:
            page_title = soup.title.string.strip()
        elif soup.find("h1"):
            h1 = soup.find("h1")
            if h1 and h1.get_text().strip():
                page_title = h1.get_text().strip()

        # Title is already properly decoded by BeautifulSoup
        # No additional text processing needed

        # Create individual folder for this article
        safe_title = sanitize_filename(page_title)

        # Handle potential duplicate folder names by appending a counter
        article_folder_name = self._get_unique_folder_name(
            base_folder, safe_title
        )
        article_folder_path = os.path.join(base_folder, article_folder_name)

        try:
            os.makedirs(article_folder_path, exist_ok=True)
        except Exception as e:
            self.logger.debug(
                f"Failed to create directory {article_folder_path}: {e}"
            )
            return False, None, None

        # MANDATORY: Create images folder for ALL articles (regardless of
        # --media flag)
        # This ensures compliance with media download requirements
        images_folder = os.path.join(article_folder_path, "images")
        try:
            os.makedirs(images_folder, exist_ok=True)
            self.logger.debug(
                f"Created mandatory images folder: {images_folder}"
            )
        except Exception as e:
            self.logger.debug(
                f"Failed to create images directory {images_folder}: {e}"
            )
            # Continue processing - images folder creation failure shouldn't
            # stop article processing

        # Create a separate directory for raw HTML files
        raw_html_dir = os.path.join(article_folder_path, "raw_html")
        try:
            os.makedirs(raw_html_dir, exist_ok=True)
        except Exception as e:
            self.logger.debug(f"Could not create raw HTML directory: {e}")
            raw_html_dir = article_folder_path  # Fallback to article folder

        # Save raw HTML immediately for future processing
        try:
            raw_html_path = os.path.join(raw_html_dir, "raw_content.html")
            with open(raw_html_path, "w", encoding="utf-8") as f:
                f.write(str(soup))
            self.logger.debug(f"Saved raw HTML to: {raw_html_path}")
        except Exception as e:
            self.logger.debug(f"Could not save raw HTML: {e}")

        # Report conversion progress
        if progress_callback:
            progress_callback(0.5, "converting to markdown")

        # Convert HTML to Markdown with thread-safe timeout protection
        markdown_content = convert_html_with_timeout(str(soup), url)

        if not markdown_content:
            self.logger.warning(
                f"Failed to convert HTML to Markdown for {url}"
            )
            return False, None, None

        # Content is already properly processed by formatter and BeautifulSoup
        # No additional text processing needed

        # Remove duplicate title if it appears at the beginning of the content
        markdown_lines = markdown_content.strip().split("\n")
        if (
            markdown_lines
            and markdown_lines[0].startswith("# ")
            and markdown_lines[0][2:].strip() == page_title.strip()
        ):
            # Remove the first line (duplicate title)
            markdown_content = "\n".join(markdown_lines[1:]).strip()

        # Remove stray "html" text that sometimes appears at the beginning
        if markdown_content.startswith("html\n"):
            markdown_content = markdown_content[5:].strip()
        elif markdown_content.startswith("html"):
            markdown_content = markdown_content[4:].strip()

        # Save preliminary content immediately (before media processing)
        article_content = f"# {page_title}\n"
        article_content += f"**Source URL:** [{url}]({url})\n"
        article_content += "---\n"
        article_content += markdown_content

        # Add footer with source URL to encourage visiting original article
        article_content += f"\n\n---\n\n**Source URL:** [{url}]({url})"

        # Add comments URL if available (for HN and Lobsters)
        # Note: comment_url should be handled separately from article fetching
        # TODO: Separate comment fetching from article fetching completely

        # Save the preliminary article
        filename = os.path.join(article_folder_path, "article.md")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(article_content)
        except Exception as e:
            self.logger.debug(
                f"Failed to save preliminary article to {filename}: {e}"
            )
            return False, None, None

        # Report media processing progress with descriptive context
        if progress_callback:
            # Analyze content complexity for descriptive progress updates
            img_count = len(soup.find_all("img"))
            video_count = len(soup.find_all("video"))
            audio_count = len(soup.find_all("audio"))
            link_count = len(soup.find_all("a", href=True))

            # Create descriptive progress message based on content complexity
            media_desc_parts = []
            if img_count > 10:
                media_desc_parts.append(f"{img_count} images")
            elif img_count > 0:
                media_desc_parts.append(
                    f"{img_count} image{'s' if img_count != 1 else ''}"
                )

            if video_count > 0 and self.download_files:
                media_desc_parts.append(
                    f"{video_count} video{'s' if video_count != 1 else ''}"
                )

            if audio_count > 0 and self.download_files:
                media_desc_parts.append(
                    f"{audio_count} audio file"
                    f"{'s' if audio_count != 1 else ''}"
                )

            if media_desc_parts:
                if img_count > 25 or (
                    self.download_files
                    and (video_count > 3 or audio_count > 3)
                ):
                    # Heavy processing case
                    media_description = (
                        f"processing {', '.join(media_desc_parts)} "
                        f"(heavy content)"
                    )
                else:
                    # Normal processing case
                    media_description = (
                        f"processing {', '.join(media_desc_parts)}"
                    )
            else:
                media_description = "processing media"

            progress_callback(0.7, media_description)

        # Process and download embedded media with fallback system
        media_processed = False
        media_warning = ""
        fallback_images_found = 0

        try:
            # Process embedded media synchronously within the article thread
            # This eliminates thread-within-thread conflicts and ensures
            # reliable image embedding
            markdown_content = self._process_embedded_media_efficiently(
                soup, markdown_content, article_folder_path, url
            )
            media_processed = True

            # Check if we should activate fallback image detection
            # Count images found by primary method
            import re

            primary_images = re.findall(
                r"!\[[^\]]*\]\([^)]+\)", markdown_content
            )
            primary_image_count = len(primary_images)

            self.logger.debug(
                f"Primary method found {primary_image_count} images"
            )

            # Activate fallback if few images found and images folder exists
            # (indicating image processing was attempted)
            images_folder = os.path.join(article_folder_path, "images")
            should_use_fallback = (
                primary_image_count < 2  # Few images found
                and (
                    os.path.exists(images_folder) or primary_image_count == 0
                )  # Image processing was attempted
            )

            if should_use_fallback:
                self.logger.info(
                    f"Primary method found only {primary_image_count} "
                    f"images, activating fallback system"
                )

                # Extract existing image URLs to avoid duplicates
                existing_image_urls = set()
                for match in re.finditer(
                    r"!\[[^\]]*\]\(([^)]+)\)", markdown_content
                ):
                    img_url = match.group(1)
                    # Convert local paths back to original URLs if needed
                    if (
                        not img_url.startswith(("http://", "https://"))
                        and "images/" in img_url
                    ):
                        continue  # Skip already downloaded images
                    existing_image_urls.add(img_url)

                # Run fallback image detection
                try:
                    fallback_image_urls = self._fallback_image_detection(
                        original_full_html,
                        existing_image_urls,
                        article_folder_path,
                        url,
                    )
                    fallback_images_found = len(fallback_image_urls)

                    if fallback_images_found > 0:
                        # Add fallback images to markdown content
                        fallback_section = "\n\n## Additional Images\n\n"
                        fallback_section += (
                            "*The following images were found using "
                            "comprehensive page scanning:*\n\n"
                        )

                        for i, img_url in enumerate(fallback_image_urls, 1):
                            # Try to find the local path for downloaded image
                            from urllib.parse import urlparse

                            parsed = urlparse(img_url)
                            filename = (
                                os.path.basename(parsed.path)
                                or f"fallback_image_{i}.jpg"
                            )
                            local_path = f"images/{filename}"

                            fallback_section += (
                                f"![Fallback Image {i}]({local_path})\n\n"
                            )

                        markdown_content += fallback_section

                except Exception as fallback_error:
                    self.logger.debug(
                        f"Fallback image detection failed: {fallback_error}"
                    )
                    fallback_images_found = 0

        except Exception as e:
            self.logger.debug(
                f"Could not process embedded media for {url}: {e}"
            )
            if self.download_files:
                media_warning = (
                    "\n\n> **⚠️ Media Processing Note**: Media "
                    "processing encountered an error during full media "
                    "download. The article text has been saved, but some "
                    "media files may be missing. You can view the original "
                    "article at the source URL above for complete media "
                    "content.\n\n"
                )
            else:
                media_warning = (
                    "\n\n> **⚠️ Media Processing Note**: Media "
                    "processing encountered an error. The article text has "
                    "been saved, but images may be missing. Use `--media` "
                    "flag for full media downloads, or view the original "
                    "article at the source URL above.\n\n"
                )

        # Report final saving progress
        if progress_callback:
            progress_callback(0.9, "saving article")

        # Update the article with processed content
        updated_article_content = f"# {page_title}\n\n"
        updated_article_content += f"**Source URL:** [{url}]({url})\n\n"
        if media_warning:
            updated_article_content += media_warning
        updated_article_content += "---\n\n"
        updated_article_content += markdown_content

        # Add footer with source URL to encourage visiting original article
        updated_article_content += f"\n\n---\n\n**Source URL:** [{url}]({url})"

        # Add comments URL if available (for HN and Lobsters)
        # Note: comment_url should be handled separately from article fetching
        # TODO: Separate comment fetching from article fetching completely

        with open(filename, "w", encoding="utf-8") as f:
            f.write(updated_article_content)

        if not media_processed and media_warning:
            self.logger.info(
                f"Saved text-only version due to media processing "
                f"issues: {page_title}"
            )

        # Delete the raw HTML directory after processing
        try:
            import shutil

            raw_html_dir = os.path.join(article_folder_path, "raw_html")
            if os.path.exists(raw_html_dir) and os.path.isdir(raw_html_dir):
                shutil.rmtree(raw_html_dir)
                self.logger.debug(
                    f"Deleted raw HTML directory: {raw_html_dir}"
                )
        except Exception as e:
            self.logger.debug(f"Could not delete raw HTML directory: {e}")

        # Report completion
        if progress_callback:
            progress_callback(1.0, "completed")

        # Clean up empty images folder if no images were downloaded
        self._cleanup_empty_images_folder(article_folder_path)

        self.logger.info(f"Successfully saved article: {page_title}")
        return True, page_title, article_folder_path

    def _cleanup_empty_images_folder(self, article_folder_path: str) -> None:
        """Remove images folder if it exists but is empty."""
        self.media_processor.cleanup_empty_images_folder(article_folder_path)

    def _parse_srcset(self, srcset: str) -> str:
        """Parse srcset attribute and return the highest resolution image URL."""
        return self.media_processor.parse_srcset(srcset)

    # OLD METHOD REMOVED - Now using single
    # _process_embedded_media_efficiently() method

    def _remove_image_from_markdown(
        self, markdown_content: str, image_src: str
    ) -> str:
        """
        Remove image references from markdown content when download fails.
        """
        import re

        # Escape special regex characters in the image source
        escaped_src = re.escape(image_src)

        # Pattern 1: Remove standard markdown image syntax ![alt](src)
        pattern1 = rf"!\[[^\]]*\]\({escaped_src}\)"
        markdown_content = re.sub(pattern1, "", markdown_content)

        # Pattern 2: Remove link syntax that might reference an image
        # [text](src)
        pattern2 = rf"\[([^\]]*)\]\({escaped_src}\)"

        # Only remove if the link text suggests it's an image (contains
        # image-related keywords)
        def replace_if_image_link(match):
            link_text = match.group(1)  # Get the text between brackets
            image_keywords = [
                "image",
                "img",
                "avatar",
                "photo",
                "picture",
                "icon",
                "logo",
            ]
            if any(
                keyword.lower() in link_text.lower()
                for keyword in image_keywords
            ):
                return ""  # Remove the entire link
            # Keep non-image links but remove broken URL
            return f"[{link_text}]()"

        markdown_content = re.sub(
            pattern2, replace_if_image_link, markdown_content
        )

        # Pattern 3: Only remove direct references to the URL if it looks like
        # an image URL
        if any(
            ext in image_src.lower()
            for ext in [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".webp",
                ".svg",
                "_next/image",
            ]
        ):
            markdown_content = markdown_content.replace(image_src, "")

        # Clean up any empty image references that might be left
        markdown_content = re.sub(r"!\[\]\(\)", "", markdown_content)
        markdown_content = re.sub(r"\[\]\(\)", "", markdown_content)

        # Clean up multiple consecutive newlines that might result from
        # removals
        markdown_content = re.sub(r"\n\s*\n\s*\n+", "\n\n", markdown_content)

        return markdown_content

    def _process_document_links(
        self,
        soup: BeautifulSoup,
        markdown_content: str,
        article_folder_path: str,
        base_url: str,
    ) -> str:
        """Process and download document files linked in the content."""
        # Find all anchor tags with href attributes
        link_tags = soup.find_all("a", href=True)

        for link in link_tags:
            href = link.get("href")
            if href:
                # Skip obviously invalid URLs
                if (
                    href.startswith("javascript:")
                    or href.startswith("mailto:")
                    or href.startswith("#")
                    or href.startswith("data:")
                ):
                    continue

                # Convert relative URLs to absolute
                original_href = href  # Keep the original for replacement
                if href.startswith("/"):
                    href = urljoin(base_url, href)
                elif not href.startswith(("http://", "https://")):
                    # Skip relative paths that don't start with /
                    continue

                # Check if this is a document link (only download if --files
                # flag is set)
                try:
                    if is_document_url(href) and self.download_files:
                        # Download the document
                        local_path = download_file(
                            href,
                            article_folder_path,
                            "document",
                            self.download_files,
                        )
                        if local_path:
                            # Replace the link reference in markdown
                            link_text = link.get_text().strip()
                            if not link_text:
                                link_text = "document"

                            # Replace document link references with local path
                            markdown_content = self._create_markdown_link_replacement(
                                markdown_content,
                                original_href,
                                local_path,
                                link_text,
                                is_image=False
                            )
                except Exception as e:
                    self.logger.debug(
                        f"Could not process document link {href}: {e}"
                    )
                    continue

        return markdown_content

    def _process_embedded_media_efficiently(
        self,
        soup: BeautifulSoup,
        markdown_content: str,
        article_folder_path: str,
        base_url: str,
    ) -> str:
        """
        Process and download embedded media files efficiently with batch
        processing.
        """
        self.logger.debug(
            f"Starting efficient media processing for {base_url}"
        )

        # Store base URL for cleanup function
        self._current_base_url = base_url

        # Extract all links first to analyze them
        all_links = []

        # Get image links from both HTML soup and markdown content
        img_tags = soup.find_all("img")
        self.logger.debug(f"Found {len(img_tags)} img tags in soup")

        # Also extract image URLs from markdown content (in case HTML was
        # already converted)
        import re

        markdown_images = re.findall(
            r"!\[[^\]]*\]\(([^)]+)\)", markdown_content
        )
        self.logger.debug(
            f"Found {len(markdown_images)} markdown images: {markdown_images}"
        )

        for img in img_tags:
            img_src = img.get("src")
            if not img_src:
                # Try to get lazy-loaded images if src is not available
                img_src = img.get("data-src", "")
            if not img_src:
                img_src = img.get("data-lazy", "")

            # Skip data URLs and other non-network URLs
            if img_src and not (
                img_src.startswith("data:")
                or img_src.startswith("javascript:")
                or img_src.startswith("mailto:")
            ):
                if img_src.startswith("//"):
                    # Protocol-relative URL - use same protocol as base URL
                    base_parsed = urlparse(base_url)
                    img_src = f"{base_parsed.scheme}:{img_src}"
                elif img_src.startswith("/"):
                    img_src = urljoin(base_url, img_src)
                elif img_src.startswith(("http://", "https://")):
                    pass  # Already absolute
                else:
                    img_src = urljoin(base_url, img_src)

                all_links.append(("image", img_src, img.get("alt", "image")))

        # Process markdown images that weren't found in HTML soup
        for img_src in markdown_images:
            if img_src and not (
                img_src.startswith("data:")
                or img_src.startswith("javascript:")
                or img_src.startswith("mailto:")
            ):
                # Convert relative URLs to absolute
                if img_src.startswith("//"):
                    # Protocol-relative URL - use same protocol as base URL
                    base_parsed = urlparse(base_url)
                    img_src = f"{base_parsed.scheme}:{img_src}"
                elif img_src.startswith("/"):
                    img_src = urljoin(base_url, img_src)
                elif not img_src.startswith(("http://", "https://")):
                    img_src = urljoin(base_url, img_src)

                # Check if this image URL is already in our links to avoid
                # duplicates
                duplicate_found = any(
                    link[1] == img_src
                    for link in all_links
                    if link[0] == "image"
                )
                if not duplicate_found:
                    all_links.append(("image", img_src, "image"))

        # Get document links
        link_tags = soup.find_all("a", href=True)
        for link in link_tags:
            href = link.get("href")
            if href and not (
                href.startswith("javascript:")
                or href.startswith("mailto:")
                or href.startswith("#")
                or href.startswith("data:")
            ):
                # Convert relative URLs to absolute
                if href.startswith("//"):
                    # Protocol-relative URL - use same protocol as base URL
                    base_parsed = urlparse(base_url)
                    href = f"{base_parsed.scheme}:{href}"
                elif href.startswith("/"):
                    href = urljoin(base_url, href)
                elif not href.startswith(("http://", "https://")):
                    # Skip relative paths that don't start with /
                    continue

                # Check if this link points to an image - if so, classify as
                # image, not document
                href_lower = href.lower()
                if href_lower.endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".tiff",
                        ".tif",
                        ".webp",
                        ".svg",
                        ".ico",
                    )
                ):
                    # This is an image link, add it as image type if not
                    # already added
                    duplicate_found = any(
                        link[1] == href
                        for link in all_links
                        if link[0] == "image"
                    )
                    if not duplicate_found:
                        all_links.append(
                            ("image", href, link.get_text().strip() or "image")
                        )
                else:
                    # This is a regular document link
                    all_links.append(
                        (
                            "document",
                            href,
                            link.get_text().strip() or "document",
                        )
                    )

        # Get video and audio links
        video_tags = soup.find_all("video")
        for video in video_tags:
            video_src = video.get("src")
            if video_src:
                if video_src.startswith("//"):
                    # Protocol-relative URL - use same protocol as base URL
                    base_parsed = urlparse(base_url)
                    video_src = f"{base_parsed.scheme}:{video_src}"
                elif video_src.startswith("/"):
                    video_src = urljoin(base_url, video_src)
                elif not video_src.startswith(("http://", "https://")):
                    continue
                all_links.append(("video", video_src, "video"))

            # Check source elements within video tags
            source_elements = video.find_all("source")
            for source in source_elements:
                src = source.get("src")
                if src:
                    if src.startswith("//"):
                        # Protocol-relative URL - use same protocol as base URL
                        base_parsed = urlparse(base_url)
                        src = f"{base_parsed.scheme}:{src}"
                    elif src.startswith("/"):
                        src = urljoin(base_url, src)
                    elif not src.startswith(("http://", "https://")):
                        continue
                    all_links.append(("video", src, "video"))

        audio_tags = soup.find_all("audio")
        for audio in audio_tags:
            audio_src = audio.get("src")
            if audio_src:
                if audio_src.startswith("//"):
                    # Protocol-relative URL - use same protocol as base URL
                    base_parsed = urlparse(base_url)
                    audio_src = f"{base_parsed.scheme}:{audio_src}"
                elif audio_src.startswith("/"):
                    audio_src = urljoin(base_url, audio_src)
                elif not audio_src.startswith(("http://", "https://")):
                    continue
                all_links.append(("audio", audio_src, "audio"))

            # Check source elements within audio tags
            source_elements = audio.find_all("source")
            for source in source_elements:
                src = source.get("src")
                if src:
                    if src.startswith("//"):
                        # Protocol-relative URL - use same protocol as base URL
                        base_parsed = urlparse(base_url)
                        src = f"{base_parsed.scheme}:{src}"
                    elif src.startswith("/"):
                        src = urljoin(base_url, src)
                    elif not src.startswith(("http://", "https://")):
                        continue
                    all_links.append(("audio", src, "audio"))

        # Process links intelligently to minimize network requests
        processed_count = 0
        skipped_count = 0

        # Track downloaded URLs to avoid duplicates
        download_cache = {}  # url -> (local_path, link_type)

        # First pass: Quick filtering based on extensions
        quick_filtered_links = []
        for link_type, url, alt_text in all_links:
            parsed_url = urlparse(url)
            path_lower = parsed_url.path.lower()

            # Quick extension-based filtering
            if link_type == "image":
                if path_lower.endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".tiff",
                        ".tif",
                        ".webp",
                        ".svg",
                        ".ico",
                    )
                ):
                    quick_filtered_links.append((link_type, url, alt_text))
                # Also include links that look like they might be images based
                # on common patterns
                elif any(
                    pattern in path_lower
                    for pattern in ["image", "img", "photo", "pic"]
                ):
                    quick_filtered_links.append((link_type, url, alt_text))
            elif link_type == "document" and self.download_files:
                # Only process documents if --files flag is set
                # Exclude HTML files - they should be processed as web pages,
                # not downloaded as documents
                if path_lower.endswith(
                    (
                        ".pdf",
                        ".doc",
                        ".docx",
                        ".xls",
                        ".xlsx",
                        ".ppt",
                        ".pptx",
                        ".txt",
                        ".rtf",
                        ".odt",
                        ".ods",
                        ".odp",
                    )
                ):
                    quick_filtered_links.append((link_type, url, alt_text))
                # Include common document patterns but exclude HTML-related
                # patterns
                elif any(
                    pattern in path_lower
                    for pattern in [
                        "document",
                        "doc",
                        "pdf",
                        "download",
                        "xls",
                        "ppt",
                    ]
                ):
                    # Make sure it's not an HTML file
                    if not path_lower.endswith((".html", ".htm")):
                        quick_filtered_links.append((link_type, url, alt_text))
            elif link_type == "audio" and self.download_files:
                # Only process audio if --files flag is set
                if path_lower.endswith(
                    (
                        ".mp3",
                        ".wav",
                        ".ogg",
                        ".flac",
                        ".aac",
                        ".m4a",
                        ".wma",
                        ".opus",
                    )
                ):
                    quick_filtered_links.append((link_type, url, alt_text))
                # Include common audio patterns
                elif any(
                    pattern in path_lower
                    for pattern in ["audio", "sound", "mp3", "wav"]
                ):
                    quick_filtered_links.append((link_type, url, alt_text))
            elif link_type == "video" and self.download_files:
                # Only process video if --files flag is set
                if path_lower.endswith(
                    (
                        ".mp4",
                        ".avi",
                        ".mkv",
                        ".mov",
                        ".wmv",
                        ".flv",
                        ".webm",
                        ".m4v",
                        ".3gp",
                    )
                ):
                    quick_filtered_links.append((link_type, url, alt_text))
                # Include common video patterns
                elif any(
                    pattern in path_lower
                    for pattern in ["video", "movie", "mp4", "mov"]
                ):
                    quick_filtered_links.append((link_type, url, alt_text))
            else:
                # For unknown types, do quick filtering for common media
                # extensions
                # Only include images by default, other media types require
                # --files flag
                if path_lower.endswith((".jpg", ".jpeg", ".png", ".gif")):
                    quick_filtered_links.append((link_type, url, alt_text))
                elif self.download_files and path_lower.endswith(
                    (".pdf", ".mp3", ".mp4", ".wav", ".mov")
                ):
                    quick_filtered_links.append((link_type, url, alt_text))

        self.logger.debug(
            f"=== DEBUG: About to log all_links, length: {len(all_links)} ==="
        )
        self.logger.debug(f"All links before filtering: {len(all_links)}")
        for link in all_links:
            self.logger.debug(f"  {link[0]}: {link[1]}")

        self.logger.info(
            f"Found {len(all_links)} total media links, "
            f"{len(quick_filtered_links)} passed quick filtering"
        )

        # Second pass: Batch process with concurrency and smart retries
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed

        config = get_config()
        max_workers = (
            min(config.processing.max_workers, len(quick_filtered_links))
            if quick_filtered_links
            else 1
        )

        def process_single_media(link_info):
            link_type, url, alt_text = link_info

            # Check cache first to avoid duplicate downloads
            if url in download_cache:
                cached_local_path, cached_link_type = download_cache[url]
                self.logger.debug(
                    f"Using cached download for {url}: {cached_local_path}"
                )
                return link_type, url, alt_text, cached_local_path, True

            try:
                # Use the existing download functions but with better error
                # handling
                local_path = download_file(
                    url, article_folder_path, link_type, self.download_files
                )
                if local_path:
                    # Cache the successful download
                    download_cache[url] = (local_path, link_type)
                    return link_type, url, alt_text, local_path, True
                else:
                    return link_type, url, alt_text, None, False
            except Exception as e:
                self.logger.debug(
                    f"Skipped {link_type} download for {url}: {e}"
                )
                return link_type, url, alt_text, None, False

        # Process media with concurrency
        if quick_filtered_links:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_link = {
                    executor.submit(process_single_media, link_info): link_info
                    for link_info in quick_filtered_links
                }

                for future in as_completed(future_to_link):
                    link_info = future_to_link[future]
                    try:
                        link_type, url, alt_text, local_path, success = (
                            future.result()
                        )
                        if success and local_path:
                            processed_count += 1
                            # Update markdown content with local path
                            # Track URL replacement attempts
                            self.logger.debug(
                                f"Attempting to replace URL: {url} -> "
                                f"{local_path}"
                            )
                            original_content_length = len(markdown_content)
                            content_contains_url = url in markdown_content

                            if link_type == "image":
                                # Replace image references with local path
                                markdown_content = self._create_markdown_link_replacement(
                                    markdown_content,
                                    url,
                                    local_path,
                                    alt_text,
                                    is_image=True
                                )

                                # Debug: also try replacing with the original
                                # relative/protocol-relative URL if this was
                                # converted
                                if url.startswith("http"):
                                    # Try to find the original relative URL in
                                    # markdown
                                    parsed = urlparse(url)
                                    relative_url = parsed.path
                                    # Try both with and without leading slash
                                    relative_url_variants = [
                                        relative_url,
                                        relative_url.lstrip("/"),
                                    ]

                                    # Also try protocol-relative URL
                                    # (//domain/path)
                                    protocol_relative_url = (
                                        f"//{parsed.netloc}{parsed.path}"
                                    )
                                    if parsed.query:
                                        protocol_relative_url += (
                                            f"?{parsed.query}"
                                        )
                                    relative_url_variants.append(
                                        protocol_relative_url
                                    )

                                    for variant in relative_url_variants:
                                        if (
                                            variant
                                            and variant in markdown_content
                                        ):
                                            self.logger.debug(
                                                f"Also replacing relative"
                                                f"/protocol-relative URL "
                                                f"{variant} with {local_path}"
                                            )
                                            markdown_content = self._create_markdown_link_replacement(
                                                markdown_content,
                                                variant,
                                                local_path,
                                                alt_text,
                                                is_image=True
                                            )

                            else:
                                # Replace document/audio/video links with local path
                                markdown_content = self._create_markdown_link_replacement(
                                    markdown_content,
                                    url,
                                    local_path,
                                    alt_text,
                                    is_image=False
                                )

                            # Check if replacement worked
                            new_content_length = len(markdown_content)
                            url_still_present = url in markdown_content
                            self.logger.debug(
                                f"URL replacement result: Content length "
                                f"{original_content_length} -> "
                                f"{new_content_length}, URL still present: "
                                f"{url_still_present}"
                            )
                            if content_contains_url and url_still_present:
                                self.logger.warning(
                                    f"FAILED to replace URL {url} with "
                                    f"{local_path}"
                                )
                        else:
                            skipped_count += 1
                            # Clean up broken image/media references when
                            # download fails
                            link_type, url, alt_text = link_info[:3]
                            markdown_content = (
                                self._cleanup_failed_media_reference(
                                    markdown_content, url, link_type, alt_text
                                )
                            )
                    except Exception as e:
                        skipped_count += 1
                        self.logger.debug(
                            f"Error processing media {link_info}: {e}"
                        )
                        # Also clean up on exception
                        link_type, url, alt_text = link_info[:3]
                        markdown_content = (
                            self._cleanup_failed_media_reference(
                                markdown_content, url, link_type, alt_text
                            )
                        )

        self.logger.info(
            f"Successfully processed {processed_count} media files, "
            f"skipped {skipped_count}"
        )

        return markdown_content

    def _fallback_image_detection(
        self,
        full_page_html: str,
        existing_images: set,
        article_folder_path: str,
        base_url: str,
    ) -> List[str]:
        """
        Fallback image detection system that scans the entire page for images
        when the primary extraction method finds few images.

        Args:
            full_page_html: Original full page HTML before article extraction
            existing_images: Set of image URLs already found by primary method
            article_folder_path: Path to save downloaded images
            base_url: Base URL for resolving relative image paths

        Returns:
            List of additional image URLs found and downloaded
        """
        self.logger.info("Activating fallback image detection system")

        # Parse the full page HTML
        full_soup = BeautifulSoup(full_page_html, "html.parser")
        all_img_tags = full_soup.find_all("img")

        self.logger.debug(
            f"Found {len(all_img_tags)} total img tags on full page"
        )

        # UI element patterns to filter out
        ui_patterns = {
            "class_patterns": [
                "logo",
                "icon",
                "avatar",
                "profile",
                "nav",
                "menu",
                "header",
                "footer",
                "ad",
                "advertisement",
                "banner",
                "sidebar",
                "social",
                "share",
                "button",
                "close",
                "arrow",
                "chevron",
                "loading",
                "spinner",
            ],
            "id_patterns": [
                "logo",
                "icon",
                "nav",
                "menu",
                "header",
                "footer",
                "ad",
                "banner",
                "sidebar",
                "social",
                "avatar",
                "profile",
            ],
            "alt_patterns": [
                "logo",
                "icon",
                "avatar",
                "profile",
                "advertisement",
                "ad",
                "banner",
                "nav",
                "menu",
                "social",
                "share",
                "button",
                "arrow",
                "loading",
            ],
            "src_patterns": [
                "logo",
                "icon",
                "avatar",
                "profile",
                "ad",
                "banner",
                "pixel",
                "tracker",
                "beacon",
                "analytics",
                "1x1",
                "transparent",
            ],
        }

        candidate_images = []

        for img in all_img_tags:
            img_src = img.get("src")
            if not img_src:
                # Try lazy-loading attributes
                img_src = (
                    img.get("data-src")
                    or img.get("data-lazy")
                    or img.get("data-original")
                )

            if not img_src or img_src.startswith(
                ("data:", "javascript:", "mailto:")
            ):
                continue

            # Convert to absolute URL
            if img_src.startswith("/"):
                img_src = urljoin(base_url, img_src)
            elif not img_src.startswith(("http://", "https://")):
                img_src = urljoin(base_url, img_src)

            # Skip if already processed
            if img_src in existing_images:
                continue

            # Apply intelligent filtering
            if self._should_skip_image(img, img_src, ui_patterns):
                self.logger.debug(f"Skipping UI element image: {img_src}")
                continue

            # Check image dimensions if available
            width = img.get("width")
            height = img.get("height")
            if width and height:
                try:
                    w, h = int(width), int(height)
                    if w < 150 or h < 150:  # Skip small images
                        self.logger.debug(
                            f"Skipping small image ({w}x{h}): {img_src}"
                        )
                        continue
                except ValueError:
                    pass  # Non-numeric dimensions, proceed

            candidate_images.append(
                (img_src, img.get("alt", "fallback-image"))
            )

        self.logger.info(
            f"Found {len(candidate_images)} candidate images after filtering"
        )

        # Download the candidate images
        downloaded_images = []
        for img_src, alt_text in candidate_images:
            try:
                self.logger.debug(f"Downloading fallback image: {img_src}")
                local_path = download_file(
                    img_src, article_folder_path, "image"
                )
                if local_path:
                    downloaded_images.append(img_src)
                    self.logger.debug(
                        f"Successfully downloaded fallback image: {local_path}"
                    )
            except Exception as e:
                self.logger.debug(
                    f"Failed to download fallback image {img_src}: {e}"
                )
                continue

        self.logger.info(
            f"Fallback system downloaded {
                len(downloaded_images)} additional images"
        )
        return downloaded_images

    def _should_skip_image(
        self, img_tag, img_src: str, ui_patterns: dict
    ) -> bool:
        """
        Determine if an image should be skipped based on UI element patterns.

        Args:
            img_tag: BeautifulSoup img tag
            img_src: Image source URL
            ui_patterns: Dictionary of patterns to match against

        Returns:
            True if image should be skipped (is likely a UI element)
        """
        # Check class attributes
        img_classes = img_tag.get("class", [])
        if isinstance(img_classes, list):
            img_classes = " ".join(img_classes).lower()
        else:
            img_classes = str(img_classes).lower()

        for pattern in ui_patterns["class_patterns"]:
            if pattern in img_classes:
                return True

        # Check id attribute
        img_id = str(img_tag.get("id", "")).lower()
        for pattern in ui_patterns["id_patterns"]:
            if pattern in img_id:
                return True

        # Check alt text
        alt_text = str(img_tag.get("alt", "")).lower()
        for pattern in ui_patterns["alt_patterns"]:
            if pattern in alt_text:
                return True

        # Check src URL for common UI image names
        src_lower = img_src.lower()
        for pattern in ui_patterns["src_patterns"]:
            if pattern in src_lower:
                return True

        # Check if image is very likely a tracking pixel or beacon
        if any(
            term in src_lower
            for term in ["pixel", "beacon", "track", "analytics", "1x1"]
        ):
            return True

        return False

    def _cleanup_failed_media_reference(
        self, markdown_content: str, url: str, link_type: str, alt_text: str
    ) -> str:
        """Clean up broken media references when download fails."""
        import re
        from urllib.parse import urlparse

        escaped_url = re.escape(url)

        if link_type == "image":
            # Handle different image reference patterns

            # Pattern 1: Standard images ![alt](url)
            pattern1 = rf"!\[([^\]]*)\]\({escaped_url}\)"

            # Check if this is a relative path that should become an absolute
            # link
            if url.startswith("/"):
                # Convert broken relative image to a link to the source page
                base_url = getattr(self, "_current_base_url", "")
                if base_url:
                    from urllib.parse import urljoin, urlparse

                    # Extract base domain from the current base URL
                    parsed_base = urlparse(base_url)
                    domain_base = (
                        f"{parsed_base.scheme}://{parsed_base.netloc}"
                    )
                    absolute_url = urljoin(domain_base, url)
                    replacement = (
                        f'[{alt_text or "Image"}]({absolute_url}) '
                        f'*(Image unavailable)*'
                    )
                    markdown_content = re.sub(
                        pattern1, replacement, markdown_content
                    )
                else:
                    # Remove the image entirely if we can't make it a proper
                    # link
                    markdown_content = re.sub(
                        pattern1,
                        f'*({alt_text or "Image unavailable"})*',
                        markdown_content,
                    )
            else:
                # For absolute URLs that failed, convert to a link
                replacement = (
                    f'[{alt_text or "Image"}]({url}) *(Image unavailable)*'
                )
                markdown_content = re.sub(
                    pattern1, replacement, markdown_content
                )

            # Pattern 2: Handle nested images like [text ![alt](url)](link)
            nested_pattern = (
                rf"\[([^\[\]]*?)!\[[^\]]*\]\({escaped_url}\)([^\]]*?)\]"
            )
            markdown_content = re.sub(
                nested_pattern, r"[\1\2]", markdown_content
            )

        elif link_type in ["document", "audio", "video"]:
            # For failed document/media links, just keep as regular links with
            # a note
            pattern = rf"\[([^\]]*)\]\({escaped_url}\)"
            markdown_content = re.sub(
                pattern,
                lambda m: f"[{m.group(1)}]({url}) *({link_type} unavailable)*",
                markdown_content,
            )

        return markdown_content

    def _get_next_available_index(
        self, base_folder: str, suggested_index: int
    ) -> int:
        """Get the next available index to avoid duplicate folder numbering."""
        try:
            if not os.path.exists(base_folder):
                return suggested_index

            # Get all existing numbered folders
            existing_numbers = set()
            for item in os.listdir(base_folder):
                if (
                    os.path.isdir(os.path.join(base_folder, item))
                    and "_" in item
                ):
                    try:
                        number_part = item.split("_")[0]
                        if number_part.isdigit():
                            existing_numbers.add(int(number_part))
                    except (ValueError, IndexError):
                        continue

            # If suggested index is available, use it
            if suggested_index not in existing_numbers:
                return suggested_index

            # Otherwise, find the next available number
            next_available = (
                max(existing_numbers) + 1 if existing_numbers else 1
            )
            return max(next_available, suggested_index)

        except Exception as e:
            self.logger.debug(f"Error getting next available index: {e}")
            return suggested_index

    def _get_unique_folder_name(
        self, base_folder: str, base_title: str
    ) -> str:
        """
        Get folder name - always returns base_title to allow overwrite.
        When user runs repeatedly, content is replaced instead of
        creating duplicates.
        """
        try:
            # ALWAYS use the original name (allow overwrite)
            # This prevents _2, _3 numbered folders when re-running
            # fetch/bundle
            return base_title

        except Exception as e:
            self.logger.debug(f"Error getting folder name: {e}")
            return base_title

    def _discover_rss_feed(self, base_url: str) -> Optional[str]:
        """
        Attempt to discover RSS/Atom feed for a website.

        Args:
            base_url: Base URL of the website

        Returns:
            Feed URL if found, None otherwise
        """
        try:
            from urllib.parse import urlparse, urljoin

            parsed = urlparse(base_url)
            base_domain = f"{parsed.scheme}://{parsed.netloc}"

            # Common RSS/Atom feed locations
            common_feeds = [
                '/feed/',
                '/rss/',
                '/feed/rss/',
                '/rss.xml',
                '/feed.xml',
                '/atom.xml',
                '/index.xml',
            ]

            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; FeedDiscovery/1.0)'
            }

            for feed_path in common_feeds:
                feed_url = urljoin(base_domain, feed_path)
                try:
                    response = self.session.get(
                        feed_url,
                        headers=headers,
                        timeout=5,
                        allow_redirects=True
                    )
                    if response.status_code == 200:
                        content_type = (
                            response.headers.get('Content-Type', '').lower()
                        )
                        # Check if it's actually a feed
                        if (any(t in content_type
                                for t in ['xml', 'rss', 'atom']) or
                            any(t in response.text[:500].lower()
                                for t in ['<rss', '<feed', '<?xml'])):
                            self.logger.info(
                                f"Discovered RSS/Atom feed: {feed_url}"
                            )
                            return feed_url
                except Exception:
                    continue

            return None

        except Exception as e:
            self.logger.debug(f"RSS feed discovery failed: {e}")
            return None

    def _download_pdf_with_progress(
        self,
        url: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> bytes:
        """
        Download PDF with streaming and progress reporting.

        Args:
            url: PDF URL to download
            progress_callback: Optional callback for progress updates

        Returns:
            PDF content as bytes
        """
        from core.progress import ProgressIndicator
        config = get_config()

        # Start progress indicator IMMEDIATELY (before network request)
        # Use show_count=False to hide chunk counts (e.g., 634/689) for single file downloads
        progress_indicator = None
        if not progress_callback:
            progress_indicator = ProgressIndicator(
                "Downloading PDF",
                total=None,
                show_spinner=True,
                show_count=False
            )
            progress_indicator.start()

        # Stream the download
        response = self.session.get(
            url,
            stream=True,
            timeout=config.network.read_timeout
        )
        response.raise_for_status()

        # Get total size and update progress indicator with size info
        total_size = int(response.headers.get('content-length', 0))
        total_mb = total_size / BYTES_TO_MB if total_size > 0 else 0

        # Update progress indicator with file size information
        if progress_indicator and total_size > 0:
            total_chunks = (total_size // 8192) + 1
            progress_indicator.total = total_chunks
            progress_indicator.message = f"Downloading PDF ({total_mb:.1f} MB)"

        # Download in chunks with progress
        downloaded = 0
        chunks = []
        chunk_count = 0

        try:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunks.append(chunk)
                    downloaded += len(chunk)
                    chunk_count += 1

                    # Update ProgressIndicator if used
                    if progress_indicator:
                        progress_indicator.update(1)

                    # Report progress via callback if provided (batch mode)
                    if total_size > 0 and progress_callback:
                        progress = downloaded / total_size
                        progress_callback(progress, "downloading")
        finally:
            # Clean up progress indicator manually to avoid dice character
            if progress_indicator:
                # Stop spinner thread
                if progress_indicator._spinner_thread:
                    progress_indicator._stop_event.set()
                    progress_indicator._spinner_thread.join(timeout=0.1)

                # Clear line and restore cursor
                progress_indicator._clear_line()
                progress_indicator._show_cursor()

                # Re-enable console logging
                from core.logging_config import set_progress_active
                set_progress_active(False)

                # Show clean completion message without dice
                self.logger.info(f"Downloaded {total_mb:.1f} MB")

        return b''.join(chunks)

    def _handle_pdf_article(
        self,
        title: str,
        url: str,
        base_folder: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Handle article URLs that are PDF files.

        Downloads the PDF file with streaming progress and extracts text content.

        Args:
            title: Article title
            url: PDF URL
            base_folder: Base folder for output
            progress_callback: Optional progress callback

        Returns:
            Tuple of (success, title, folder_path)
        """
        try:
            # Create article folder
            safe_title = sanitize_filename(title)
            article_folder_name = self._get_unique_folder_name(
                base_folder, safe_title
            )
            article_folder = os.path.join(base_folder, article_folder_name)
            os.makedirs(article_folder, exist_ok=True)

            # Download PDF with streaming progress (0.0 - 0.7)
            # In single mode (no callback), _download_pdf_with_progress will use ProgressIndicator
            # In batch mode (with callback), wrap and scale progress
            if progress_callback:
                def download_progress(progress, status):
                    # Scale progress to 0.0-0.7 range
                    progress_callback(progress * 0.7, status)

                pdf_content = self._download_pdf_with_progress(
                    url=url,
                    progress_callback=download_progress
                )
            else:
                # Single mode - let _download_pdf_with_progress handle ProgressIndicator
                pdf_content = self._download_pdf_with_progress(
                    url=url,
                    progress_callback=None
                )

            if progress_callback:
                progress_callback(0.75, "saving PDF")

            # Extract original filename from URL
            from urllib.parse import urlparse, unquote
            parsed_url = urlparse(url)
            original_filename = os.path.basename(unquote(parsed_url.path))

            # Ensure it has .pdf extension
            if not original_filename.lower().endswith('.pdf'):
                original_filename += '.pdf'

            # Save PDF with original filename
            pdf_path = os.path.join(article_folder, original_filename)
            with open(pdf_path, 'wb') as f:
                f.write(pdf_content)

            self.logger.info(f"Saved PDF file: {pdf_path} ({len(pdf_content)} bytes)")

            if progress_callback:
                progress_callback(0.8, "creating placeholder")

            # Create markdown placeholder with link to downloaded PDF
            pdf_size_mb = len(pdf_content) / BYTES_TO_MB

            markdown_content = f"# {title}\n\n"
            markdown_content += f"## This is a placeholder for your downloaded PDF file\n\n"
            markdown_content += f"**Source URL:** [{url}]({url})\n\n"
            markdown_content += f"**Downloaded file:** [{original_filename}]({original_filename}) ({pdf_size_mb:.2f} MB)\n"

            # Save markdown placeholder
            md_path = os.path.join(article_folder, "article.md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            # Generate HTML output if enabled
            if self.generate_html:
                if progress_callback:
                    progress_callback(0.8, "generating HTML")

                from core.html_generator import HTMLGenerator
                html_gen = HTMLGenerator()

                try:
                    html_gen.generate_article_html(
                        markdown_path=md_path,
                        output_dir=article_folder,
                        theme=None  # Use default theme
                    )
                except Exception as e:
                    self.logger.warning(f"HTML generation failed: {e}, skipping HTML output")

            if progress_callback:
                progress_callback(1.0, "complete")

            self.logger.info(f"Successfully processed PDF article: {title}")
            return True, title, article_folder

        except Exception as e:
            self.logger.error(f"Failed to process PDF article {url}: {e}")
            return False, None, None

    def _create_error_article(
        self,
        title: str,
        url: str,
        error_type: str,
        error_details: str,
        base_folder: str,
        rss_feed_url: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create a clean error article when fetching fails.

        Args:
            title: Article title
            url: Original article URL
            error_type: Type of error (e.g., "403 Forbidden",
                "Connection Timeout")
            error_details: Detailed error message
            base_folder: Base directory to save to
            rss_feed_url: Optional RSS feed URL if discovered

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (success,
                article_title, article_folder_path)
        """
        try:
            # Create folder for this article
            safe_title = sanitize_filename(title)
            article_folder_name = self._get_unique_folder_name(
                base_folder, safe_title
            )
            article_folder_path = os.path.join(
                base_folder, article_folder_name
            )
            os.makedirs(article_folder_path, exist_ok=True)

            # Determine error category and recommendation
            # Check both error_type and error_details for patterns
            combined_error = f"{error_type} {error_details}".lower()
            error_category = "Unknown Error"
            recommendation = (
                "Try accessing the article directly via the source URL "
                "below."
            )

            if "403" in combined_error or "forbidden" in combined_error:
                error_category = "Access Denied (403 Forbidden)"
                recommendation = (
                    "This website uses protection (likely Cloudflare) that "
                    "blocks automated access."
                )
            elif "404" in combined_error or "not found" in combined_error:
                error_category = "Article Not Found (404)"
                recommendation = (
                    "The article may have been removed or the URL is "
                    "incorrect."
                )
            elif "timeout" in combined_error:
                error_category = "Connection Timeout"
                recommendation = (
                    "The server took too long to respond. Try again later."
                )
            elif "connection" in combined_error:
                error_category = "Connection Error"
                recommendation = (
                    "Could not establish connection to the server. Check "
                    "your network or try again later."
                )
            elif any(code in combined_error
                     for code in ["500", "502", "503", "504"]):
                error_category = "Server Error"
                recommendation = (
                    "The website's server is experiencing issues. Try "
                    "again later."
                )

            # Build error article content
            article_content = f"# {title}\n\n"
            article_content += f"## Cannot Fetch Article\n\n"
            article_content += f"**Error:** {error_category}\n\n"
            article_content += f"**Source URL:** [{url}]({url})\n\n"
            article_content += "---\n\n"
            article_content += f"### Error Details\n\n"
            article_content += f"```\n{error_details}\n```\n\n"
            article_content += f"### Recommendation\n\n"
            article_content += f"{recommendation}\n\n"

            if rss_feed_url:
                article_content += f"### Alternative Access\n\n"
                article_content += (
                    f"An RSS/Atom feed was discovered for this "
                    f"website:\n\n"
                )
                article_content += (
                    f"**Feed URL:** [{rss_feed_url}]({rss_feed_url})\n\n"
                )
                article_content += (
                    f"Consider configuring this source to use the RSS feed "
                    f"instead of direct HTTP access.\n\n"
                )

            article_content += "---\n\n"
            article_content += (
                f"**Note:** This is an automatically generated error "
                f"message. "
            )
            article_content += (
                f"Visit the source URL above to read the original "
                f"article.\n"
            )

            # Save error article
            filename = os.path.join(article_folder_path, "article.md")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(article_content)

            self.logger.warning(
                f"Created error article for '{title}': {error_category}"
            )

            return True, title, article_folder_path

        except Exception as e:
            self.logger.error(
                f"Failed to create error article for '{title}': {e}"
            )
            return False, None, None


class HackerNewsArticleFetcher(ArticleFetcher):
    """Hacker News specific article fetcher."""

    def __init__(self, session, download_files: bool = False):
        super().__init__(session, download_files)

    def should_skip_url(self, url: str, title: str) -> bool:
        """Skip Hacker News internal links."""
        return url.startswith("https://news.ycombinator.com")


class LobstersArticleFetcher(ArticleFetcher):
    """Lobsters specific article fetcher."""

    def __init__(self, session, download_files: bool = False):
        super().__init__(session, download_files)

    def should_skip_url(self, url: str, title: str) -> bool:
        """
        Skip Lobste.rs internal links that don't point to external content.
        """
        return url.startswith("https://lobste.rs") and not url.startswith(
            "https://lobste.rs/s/"
        )
