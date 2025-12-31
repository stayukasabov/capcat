#!/usr/bin/env python3
"""
Unified Source Processor for Capcat.
This eliminates the 46+ duplicate process_*_articles functions by providing
a single, configurable processor that works with all sources.

Follows DRY principle while maintaining source-specific optimizations.
"""

import importlib
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Optional, Tuple

from core.circuit_breaker import CircuitBreakerOpenError, call_with_circuit_breaker
from core.config import get_config
from core.exceptions import NetworkError
from core.logging_config import get_logger
from core.progress import get_batch_progress
from core.source_configs import get_source_config, is_source_configured
from core.source_factory import SourceFactory
from core.utils import create_batch_output_directory

# Import new source system for hybrid architecture
try:
    from core.source_system.base_source import Article, SourceError
    from core.source_system.source_factory import get_source_factory

    NEW_SOURCE_SYSTEM_AVAILABLE = True
except ImportError:
    NEW_SOURCE_SYSTEM_AVAILABLE = False


class UnifiedSourceProcessor:
    """
    Unified processor for all news sources.
    Eliminates code duplication while preserving source-specific functionality.
    """

    # Class-level URL cache for cross-source deduplication
    _processed_urls = set()

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()
        # Initialize new source system if available
        self.new_source_factory = None
        if NEW_SOURCE_SYSTEM_AVAILABLE:
            try:
                self.new_source_factory = get_source_factory()
            except Exception as e:
                self.logger.debug(f"New source system not yet ready: {e}")
                self.new_source_factory = None

    @classmethod
    def clear_url_cache(cls):
        """Clear the URL cache for a new processing session."""
        cls._processed_urls.clear()

    @classmethod
    def is_url_processed(cls, url: str) -> bool:
        """Check if a URL has already been processed."""
        return url in cls._processed_urls

    @classmethod
    def mark_url_processed(cls, url: str):
        """Mark a URL as processed."""
        cls._processed_urls.add(url)

    def _is_source_in_new_system(self, source_name: str) -> bool:
        """Check if source is available in the new source system."""
        if not self.new_source_factory:
            return False
        try:
            available_sources = self.new_source_factory.get_available_sources()
            return source_name in available_sources
        except Exception:
            return False

    def process_source_articles(
        self,
        source_name: str,
        count: int,
        output_dir: str,
        quiet: bool = False,
        verbose: bool = False,
        download_files: bool = False,
        batch_mode: bool = False,
    ) -> None:
        """
        Universal article processing function that replaces all 46+ process_*_articles functions.

        Args:
            source_name: The source identifier (e.g., 'hn', 'bbc', 'cnn')
            count: Number of articles to fetch
            quiet: Suppress progress output
            verbose: Enable verbose logging
            download_files: Enable media file downloads
            batch_mode: Whether processing multiple sources (affects retry messages)
        """
        # Check if source is available in the new system first (hybrid approach)
        if self._is_source_in_new_system(source_name):
            return self._process_with_new_system(
                source_name, count, output_dir, quiet, verbose, download_files, batch_mode
            )

        # Fall back to legacy system
        if not is_source_configured(source_name):
            raise ValueError(
                f"Source '{source_name}' is not configured in either system"
            )

        source_config = get_source_config(source_name)
        source_display_name = source_config["name"]

        self.logger.info(
            f"Fetching top {count} articles from {source_display_name}..."
        )

        try:
            # Get articles using appropriate method
            articles = self._get_articles(source_name, source_config, count)

            if not articles:
                raise NetworkError(
                    source_config["base_url"], Exception("No articles found")
                )

            # Only create directory AFTER successful article discovery
            # This prevents empty directories for skipped sources
            if output_dir != ".":
                base_dir = os.path.abspath(output_dir)
            else:
                base_dir = create_batch_output_directory(source_name)

            # Determine if this source has comments
            has_comments = source_config.get("has_comments", False)
            comment_text = " and comments" if has_comments else ""
            self.logger.info(
                f"Found {len(articles)} articles. Fetching content{comment_text} in parallel..."
            )

        except Exception as e:
            self.logger.error(
                f"Failed to initialize {source_display_name} processing: {e}"
            )
            raise

        # Process articles in parallel
        self._process_articles_parallel(
            source_name=source_name,
            source_config=source_config,
            articles=articles,
            base_dir=base_dir,
            download_files=download_files,
            quiet=quiet,
            verbose=verbose,
        )

    def _get_articles(
        self, source_name: str, source_config: dict, count: int
    ) -> List[Tuple[str, str, Optional[str]]]:
        """
        Get articles using either custom scraping function or generic adapter.

        Returns:
            List of (title, url, comment_url) tuples
        """
        # Check if source has custom scraping function
        if "scraping_function" in source_config:
            return self._get_articles_custom(source_name, source_config, count)
        else:
            return self._get_articles_generic(
                source_name, source_config, count
            )

    def _get_articles_custom(
        self, source_name: str, source_config: dict, count: int
    ) -> List[Tuple[str, str, Optional[str]]]:
        """Get articles using custom scraping function."""
        module_name = source_config["module"]
        function_name = source_config["scraping_function"]

        # Import the module dynamically
        module = importlib.import_module(module_name)
        scraping_function = getattr(module, function_name)

        # Call the custom scraping function
        return scraping_function(count)

    def _get_articles_generic(
        self, source_name: str, source_config: dict, count: int
    ) -> List[Tuple[str, str, Optional[str]]]:
        """Get articles using generic configuration-driven adapter."""
        # Create source adapter using factory
        source_adapter = SourceFactory.create_source(source_name)

        # Scrape articles using the adapter
        return source_adapter.scrape_articles(count)

    def _process_articles_parallel(
        self,
        source_name: str,
        source_config: dict,
        articles: List[Tuple],
        base_dir: str,
        download_files: bool,
        quiet: bool,
        verbose: bool,
    ) -> None:
        """Process articles in parallel using ThreadPoolExecutor."""

        # Filter out duplicate URLs
        filtered_articles = []
        duplicate_count = 0

        for i, (title, url, comment_url) in enumerate(articles, 1):
            if self.is_url_processed(url):
                duplicate_count += 1
                self.logger.info(f"Skipping duplicate URL: {url}")
                continue

            # Mark URL as processed to prevent future duplicates
            self.mark_url_processed(url)
            filtered_articles.append((i, title, url, comment_url))

        if duplicate_count > 0:
            source_display_name = source_config["name"]
            self.logger.info(
                f"Skipped {duplicate_count} duplicate articles from {source_display_name}"
            )

        if not filtered_articles:
            self.logger.warning(
                "No new articles to process after deduplication"
            )
            return

        # Prepare article data with indices
        article_data = filtered_articles

        # Configure parallel processing
        max_workers = min(
            self.config.processing.max_workers, len(filtered_articles)
        )
        source_display_name = source_config["name"]

        with get_batch_progress(
            source_display_name,
            len(filtered_articles),
            quiet,
            verbose,
        ) as progress:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                futures = {}
                for article_info in article_data:
                    future = executor.submit(
                        self._process_single_article,
                        source_name,
                        source_config,
                        article_info,
                        base_dir,
                        download_files,
                        progress,
                    )
                    futures[future] = article_info

                # Process completed tasks as they finish
                from concurrent.futures import as_completed, TimeoutError

                successful_count = 0
                failed_count = 0

                # Process with aggressive timeout to prevent hangs
                per_article_timeout = 60
                total_timeout = per_article_timeout * len(futures)
                start_time = time.time()

                try:
                    for future in as_completed(futures, timeout=total_timeout):
                        article_info = futures[future]
                        try:
                            elapsed = time.time() - start_time
                            if elapsed > total_timeout:
                                raise TimeoutError(f"Global timeout exceeded: {elapsed}s")

                            success = future.result(timeout=5)
                            if success:
                                successful_count += 1
                            else:
                                failed_count += 1
                            progress.item_completed(success, article_info[1])
                        except TimeoutError:
                            self.logger.warning(
                                f"Article {article_info[1]} timed out - marking as failed"
                            )
                            failed_count += 1
                            progress.item_completed(False, article_info[1])
                            future.cancel()
                        except Exception as exc:
                            self.logger.error(
                                f"Article {article_info[1]} generated an exception: {exc}"
                            )
                            failed_count += 1
                            progress.item_completed(False, article_info[1])
                except TimeoutError:
                    self.logger.warning(
                        f"Timeout waiting for articles after {total_timeout}s. "
                        f"Completed: {successful_count + failed_count}/{len(futures)}"
                    )
                    for future, article_info in futures.items():
                        if not future.done():
                            self.logger.warning(f"Cancelling stuck article: {article_info[1]}")
                            future.cancel()
                            failed_count += 1
                            progress.item_completed(False, article_info[1])

        # Log summary with skip information
        successful = successful_count
        failed = failed_count
        success_rate = (successful / len(futures)) * 100 if futures else 0

        from core.network_resilience import get_skip_tracker
        skip_tracker = get_skip_tracker()
        skip_summary = skip_tracker.get_summary()

        if skip_summary['total_skipped'] > 0:
            self.logger.info(
                f"{source_display_name} articles summary: {successful} successful, "
                f"{failed} failed, {skip_summary['total_skipped']} skipped "
                f"({success_rate:.1f}% success rate)"
            )
            for source_name, skip_info in skip_summary['skipped'].items():
                self.logger.info(
                    f"  Skipped {source_name}: {skip_info['error_type']} after "
                    f"{skip_info['attempts']} attempts"
                )
        else:
            self.logger.info(
                f"{source_display_name} articles summary: {successful} successful, {failed} failed ({success_rate:.1f}% success rate)"
            )

    def _process_single_article(
        self,
        source_name: str,
        source_config: dict,
        article_info: tuple,
        base_dir: str,
        download_files: bool,
        progress_tracker=None,
    ) -> bool:
        """Process a single article with progress reporting."""
        i, title, url, comment_url = article_info

        # Create progress callback for this article
        def progress_callback(progress: float, stage: str):
            if progress_tracker:
                progress_tracker.update_item_progress(progress, stage)

        try:
            # PHASE 3 INTEGRATION: Check specialized sources first (Twitter, YouTube, etc.)
            from core.unified_article_processor import get_unified_processor as get_article_processor
            article_processor = get_article_processor()

            # Check if this URL should be handled by a specialized source
            if article_processor.specialized_manager.can_handle_url(url):
                self.logger.info(f"Batch processing: Specialized source detected for {url}")

                # Use unified article processor for specialized handling
                success, article_title, article_path = article_processor.process_article(
                    url=url,
                    title=title,
                    index=i,
                    base_folder=base_dir,
                    download_files=download_files,
                    progress_callback=progress_callback,
                    update_mode=False  # Batch mode doesn't use update
                )

                return success

            # Get the appropriate article processing function
            if "scraping_function" in source_config:
                return self._process_article_custom(
                    source_name,
                    source_config,
                    article_info,
                    base_dir,
                    download_files,
                    progress_callback,
                )
            else:
                return self._process_article_generic(
                    source_name,
                    source_config,
                    article_info,
                    base_dir,
                    download_files,
                    progress_callback,
                )

        except Exception as e:
            self.logger.error(f"Failed to process article '{title}': {e}")
            return False

    def _process_article_custom(
        self,
        source_name: str,
        source_config: dict,
        article_info: tuple,
        base_dir: str,
        download_files: bool,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bool:
        """Process article using source-specific functions."""
        i, title, url, comment_url = article_info

        # Import the source module
        module_name = source_config["module"]
        module = importlib.import_module(module_name)

        # Get the article fetching function (usually 'fetch_article_content')
        fetch_function_name = f"{source_name}_fetch_article"
        if hasattr(module, fetch_function_name):
            fetch_function = getattr(module, fetch_function_name)
        elif hasattr(module, "fetch_article_content"):
            fetch_function = getattr(module, "fetch_article_content")
        else:
            # Fall back to generic processing
            return self._process_article_generic(
                source_name,
                source_config,
                article_info,
                base_dir,
                download_files,
                progress_callback,
            )

        # Process the article with progress callback if the function supports it
        try:
            # Try calling with progress callback first
            success = fetch_function(
                title, url, i, base_dir, progress_callback, download_files
            )
        except TypeError:
            # Fall back to old signature if function doesn't support progress callback
            success = fetch_function(title, url, i, base_dir, download_files)

        # Process comments if available and supported
        if (
            success
            and comment_url
            and source_config.get("has_comments", False)
        ):
            comments_function_name = source_config.get("comments_function")
            if comments_function_name and hasattr(
                module, comments_function_name
            ):
                comments_function = getattr(module, comments_function_name)
                # Create article folder path for comments
                from core.utils import sanitize_filename

                safe_title = sanitize_filename(title)
                article_folder_name = f"{i:02d}_{safe_title}"
                article_folder_path = f"{base_dir}/{article_folder_name}"
                comments_function(
                    comment_url, title, i, base_dir, article_folder_path
                )

        return success

    def _process_with_new_system(
        self,
        source_name: str,
        count: int,
        output_dir: str,
        quiet: bool = False,
        verbose: bool = False,
        download_files: bool = False,
        batch_mode: bool = False,
    ) -> None:
        """Process articles using the new source system."""
        self.logger.debug(f"Using new source system for {source_name}")

        try:
            # Create source instance
            source = self.new_source_factory.create_source(source_name)
            source_config = self.new_source_factory.get_source_config(
                source_name
            )

            if not source_config:
                raise ValueError(
                    f"No configuration found for source '{source_name}'"
                )

            self.logger.info(
                f"Fetching top {count} articles from {source_config.display_name}..."
            )

            # UNIVERSAL RETRY-SKIP LOGIC: Applied to all sources
            # Attempts discovery 2 times, then skips if both fail
            try:
                articles = source.discover_articles_with_retry_skip(
                    count=count, max_retries=2, batch_mode=batch_mode
                )

                # None means source skipped after 2 failed attempts
                if articles is None:
                    print(f"\nCapcat Info: Skipped '{source_config.display_name}' - source unavailable (0 articles fetched)\n", flush=True)
                    # Raise exception so caller knows this source failed
                    raise SourceError(
                        f"Source '{source_name}' skipped after all retry attempts failed",
                        source_name=source_name
                    )

            except SourceError:
                # Re-raise SourceError so it's marked as failed, not successful
                raise
            except Exception as e:
                # Catch any unexpected errors
                self.logger.error(
                    f"Error discovering articles from {source_name}: {e}"
                )
                raise SourceError(
                    f"Failed to process {source_name}: {e}",
                    source_name=source_name
                )

            if not articles:
                raise NetworkError(
                    source_config.base_url, Exception("No articles found")
                )

            # Only create directory AFTER successful article discovery
            # This prevents empty directories for skipped sources
            if output_dir != ".":
                base_dir = os.path.abspath(output_dir)
            else:
                base_dir = create_batch_output_directory(source_name)

            self.logger.info(
                f"Found {len(articles)} articles. Fetching content in parallel..."
            )

            # Process articles using new system approach
            self._process_articles_with_new_system(
                source, articles, base_dir, download_files, quiet, verbose
            )

        except SourceError as e:
            self.logger.error(f"New source system error: {e}")
            raise
        except Exception as e:
            self.logger.error(
                f"Failed to process {source_name} with new system: {e}"
            )
            raise

    def _process_articles_with_new_system(
        self,
        source,
        articles,
        base_dir: str,
        download_files: bool,
        quiet: bool,
        verbose: bool,
    ):
        """Process articles using the new source system with parallel execution."""
        # Filter out duplicate URLs
        filtered_articles = []
        duplicate_count = 0

        for i, article in enumerate(articles, 1):
            if self.is_url_processed(article.url):
                duplicate_count += 1
                self.logger.info(f"Skipping duplicate URL: {article.url}")
                continue

            self.mark_url_processed(article.url)
            filtered_articles.append((i, article))

        if duplicate_count > 0:
            self.logger.info(f"Skipped {duplicate_count} duplicate articles")

        if not filtered_articles:
            self.logger.warning(
                "No new articles to process after deduplication"
            )
            return

        # Configure parallel processing
        max_workers = min(
            self.config.processing.max_workers, len(filtered_articles)
        )
        source_display_name = source.config.display_name

        with get_batch_progress(
            source_display_name,
            len(filtered_articles),
            quiet,
            verbose,
        ) as progress:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                futures = {}
                for i, article in filtered_articles:
                    future = executor.submit(
                        self._process_single_article_new_system,
                        source,
                        article,
                        base_dir,
                        download_files,
                        progress,
                        i,
                    )
                    futures[future] = (i, article)

                # Process completed tasks as they finish
                from concurrent.futures import as_completed, TimeoutError

                successful_count = 0
                failed_count = 0

                # Process with aggressive timeout to prevent hangs
                # Give 60 seconds per article as reasonable max time
                per_article_timeout = 60
                total_timeout = per_article_timeout * len(futures)
                start_time = time.time()

                try:
                    for future in as_completed(futures, timeout=total_timeout):
                        i, article = futures[future]
                        try:
                            # Check if we've exceeded per-article timeout
                            elapsed = time.time() - start_time
                            if elapsed > total_timeout:
                                raise TimeoutError(f"Global timeout exceeded: {elapsed}s")

                            success = future.result(timeout=5)  # Short timeout to detect hangs
                            if success:
                                successful_count += 1
                            else:
                                failed_count += 1
                            progress.item_completed(success, article.title)
                        except TimeoutError:
                            self.logger.warning(
                                f"Article {article.title} timed out - marking as failed"
                            )
                            failed_count += 1
                            progress.item_completed(False, article.title)
                            # Cancel the future to release resources
                            future.cancel()
                        except Exception as exc:
                            self.logger.error(
                                f"Article {article.title} generated an exception: {exc}"
                            )
                            failed_count += 1
                            progress.item_completed(False, article.title)
                except TimeoutError:
                    self.logger.warning(
                        f"Timeout waiting for articles after {total_timeout}s. "
                        f"Completed: {successful_count + failed_count}/{len(futures)}"
                    )
                    # Cancel and mark all remaining futures as failed
                    for future, (i, article) in futures.items():
                        if not future.done():
                            self.logger.warning(f"Cancelling stuck article: {article.title}")
                            future.cancel()
                            failed_count += 1
                            progress.item_completed(False, article.title)

        # Log summary
        successful = successful_count
        failed = failed_count
        success_rate = (successful / len(futures)) * 100 if futures else 0

        self.logger.info(
            f"{source_display_name} articles summary: {successful} successful, {failed} failed ({success_rate:.1f}% success rate)"
        )

    def _process_single_article_new_system(
        self,
        source,
        article,
        base_dir: str,
        download_files: bool,
        progress_tracker=None,
        index: int = 1,
    ) -> bool:
        """Process a single article using the new source system."""

        def progress_callback(progress: float, stage: str):
            if progress_tracker:
                progress_tracker.update_item_progress(progress, stage)

        try:
            success, article_path = source.fetch_article_content(
                article, base_dir, progress_callback
            )

            # Process comments if available and supported
            if (
                success
                and hasattr(article, "comment_url")
                and article.comment_url
            ):
                # Check if comments are supported via config or custom_config
                supports_comments = False
                if (
                    hasattr(source.config, "has_comments")
                    and source.config.has_comments
                ):
                    supports_comments = True
                elif (
                    hasattr(source.config, "custom_config")
                    and source.config.custom_config
                    and source.config.custom_config.get("has_comments", False)
                ):
                    supports_comments = True

                if supports_comments and hasattr(source, "fetch_comments"):
                    try:
                        self.logger.info(
                            f"Fetching comments for: {article.title}"
                        )
                        source.fetch_comments(
                            article.comment_url, article.title, article_path
                        )
                    except Exception as comment_error:
                        self.logger.warning(
                            f"Failed to fetch comments for '{article.title}': {comment_error}"
                        )

            return success
        except Exception as e:
            self.logger.error(
                f"Failed to process article '{article.title}': {e}"
            )
            return False

    def _process_article_generic(
        self,
        source_name: str,
        source_config: dict,
        article_info: tuple,
        base_dir: str,
        download_files: bool,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bool:
        """Process article using generic configuration-driven approach."""
        i, title, url, comment_url = article_info

        # Create source adapter
        source_adapter = SourceFactory.create_source(source_name)

        # Process the article using the adapter, including comments and progress callback
        return source_adapter.process_article(
            title,
            url,
            i,
            base_dir,
            comment_url,
            download_files,
            progress_callback,
        )


# Global processor instance
_processor = None


def get_unified_processor() -> UnifiedSourceProcessor:
    """Get global unified processor instance."""
    global _processor
    if _processor is None:
        _processor = UnifiedSourceProcessor()
    return _processor


def process_source_articles(
    source_name: str,
    count: int,
    output_dir: str,
    quiet: bool = False,
    verbose: bool = False,
    download_files: bool = False,
    batch_mode: bool = False,
) -> None:
    """
    Convenience function to process articles from any source.
    This replaces all 46+ individual process_*_articles functions.

    Args:
        source_name: The source identifier (e.g., 'hn', 'bbc', 'cnn')
        count: Number of articles to fetch
        quiet: Suppress progress output
        verbose: Enable verbose logging
        download_files: Enable media file downloads
        batch_mode: Whether processing multiple sources (affects retry messages)
    """
    processor = get_unified_processor()
    processor.process_source_articles(
        source_name, count, output_dir, quiet, verbose, download_files, batch_mode
    )
