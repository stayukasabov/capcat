#!/usr/bin/env python3
"""
Unified Source Processor for Capcat.
This eliminates the 46+ duplicate process_*_articles functions by providing
a single, configurable processor that works with all sources.

Follows DRY principle while maintaining source-specific optimizations.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from datetime import date as _date
from pathlib import Path
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from capcat.core.source_system.base_source import SourceConfig

from capcat.core.config import get_config
from capcat.core.exceptions import NetworkError
from capcat.core.logging_config import get_logger
from capcat.core.progress import get_batch_progress
from capcat.core.shutdown import get_shutdown
from capcat.core.storage_manager import find_article_md, find_comments_md, inject_comments_wikilink, inject_frontmatter
from capcat.core.utils import create_batch_output_directory

# Import new source system for hybrid architecture
try:
    from capcat.core.source_system.base_source import SourceError
    from capcat.core.source_system.source_factory import get_source_factory

    NEW_SOURCE_SYSTEM_AVAILABLE = True
except ImportError:
    NEW_SOURCE_SYSTEM_AVAILABLE = False

try:
    from capcat.core.source_config_mirror import SourceConfigMirror
    from capcat.core.config import find_project_root, NoProjectError
    from capcat.core.tui_context import is_tui_active
    MIRROR_AVAILABLE = True
except ImportError:
    MIRROR_AVAILABLE = False


@dataclass
class FetchResult:
    saved: int
    skipped: list[tuple[str, int]] = field(default_factory=list)


def _resolve_count(
    cli_count: Optional[int],
    source_config: "SourceConfig",
    config=None,
) -> int:
    """Resolve article count: CLI flag > capcat.yml sources list > source YAML > global config default.

    Args:
        cli_count: Value from --count flag, or None if not provided.
        source_config: The source's SourceConfig (has article_count field).
        config: FetchNewsConfig instance (used for vault overrides and global fallback).

    Returns:
        Number of articles to fetch.
    """
    if cli_count is not None:
        return cli_count
    if config is not None:
        vault_count = config.source_overrides.get(source_config.name, {}).get("article_count")
        if vault_count is not None:
            return int(vault_count)
    if source_config.article_count is not None:
        return source_config.article_count
    if config is not None:
        return config.processing.article_count
    return get_config().processing.article_count


def _build_article_metadata(article, source) -> dict:
    """Build frontmatter metadata dict for an article."""
    tags = list(dict.fromkeys([source.config.name, source.config.category]))
    return {
        "title": article.title,
        "url": article.url,
        "source": source.config.display_name,
        "source_code": source.config.name,
        "category": source.config.category,
        "date": article.published_date or None,
        "captured": str(_date.today()),
        "tags": tags,
    }


def _build_comments_metadata(article, source) -> dict:
    """Build frontmatter metadata dict for a comments file."""
    tags = list(dict.fromkeys(["comments", source.config.name]))
    return {
        "title": f"Comments: {article.title}",
        "article_url": article.url,
        "source_code": source.config.name,
        "captured": str(_date.today()),
        "tags": tags,
    }


class UnifiedSourceProcessor:
    """
    Unified processor for all news sources.
    Eliminates code duplication while preserving source-specific functionality.
    """

    # Class-level URL cache for cross-source deduplication
    _processed_urls = set()

    def __init__(self, project_root: Optional[Path] = None):
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.project_root = project_root
        # Initialize new source system if available
        self.new_source_factory = None
        if NEW_SOURCE_SYSTEM_AVAILABLE:
            try:
                self.new_source_factory = get_source_factory(project_root=project_root)
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

    def _assert_all_sources_in_new_system(self) -> None:
        """
        Assert that every source in the legacy config is also registered in the new system.
        Raises ValueError listing any sources that would fall through to the deleted legacy path.
        """
        from capcat.core.source_configs import SOURCE_CONFIGURATIONS
        legacy_names = list(SOURCE_CONFIGURATIONS.keys())
        missing = [name for name in legacy_names if not self._is_source_in_new_system(name)]
        if missing:
            raise ValueError(
                f"Sources in legacy config but not in new registry: {missing}. "
                "Register them in the new source system before proceeding."
            )

    def process_source_articles(
        self,
        source_name: str,
        count: Optional[int],
        output_dir: str,
        quiet: bool = False,
        verbose: bool = False,
        download_files: bool = False,
        batch_mode: bool = False,
        generate_html: bool = False,
        download_pdfs: bool = False,
    ) -> None:
        """
        Universal article processing function. All sources route through the new system.

        Args:
            source_name: The source identifier (e.g., 'hn', 'bbc', 'cnn')
            count: Number of articles to fetch
            quiet: Suppress progress output
            verbose: Enable verbose logging
            download_files: Enable media file downloads
            batch_mode: Whether processing multiple sources (affects retry messages)
            generate_html: Generate HTML version after fetching
            download_pdfs: Enable PDF downloads (--pdfs flag)
        """
        if not self._is_source_in_new_system(source_name):
            raise ValueError(
                f"Source '{source_name}' is not registered in the source system. "
                "Add a YAML config to capcat/sources/builtin/config_driven/configs/ "
                "or a source.py to capcat/sources/builtin/custom/."
            )
        return self._process_with_new_system(
            source_name, count, output_dir, quiet, verbose, download_files,
            batch_mode, generate_html, download_pdfs,
        )

    def _process_with_new_system(
        self,
        source_name: str,
        count: Optional[int],
        output_dir: str,
        quiet: bool = False,
        verbose: bool = False,
        download_files: bool = False,
        batch_mode: bool = False,
        generate_html: bool = False,
        download_pdfs: bool = False,
    ) -> None:
        """Process articles using the new source system."""
        # Run source config mirror (first-run copy or upgrade diff)
        if MIRROR_AVAILABLE:
            try:
                project_root = self.project_root
                if project_root is None:
                    project_root = find_project_root()
                mirror = SourceConfigMirror(project_root, tui_mode=is_tui_active())
                if not mirror.is_mirrored():
                    mirror.run_first_mirror()
                else:
                    mirror.check_for_upgrades()
            except NoProjectError:
                pass  # Not in a project — skip mirror
            except Exception as exc:
                self.logger.warning(f"Source config mirror failed: {exc}")

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

            # Resolve per-source count (CLI > source YAML > global config)
            resolved_count = _resolve_count(count, source_config, get_config())

            self.logger.info(
                f"Fetching top {resolved_count} articles from {source_config.display_name}..."
            )

            # UNIVERSAL RETRY-SKIP LOGIC: Applied to all sources
            # Attempts discovery 2 times, then skips if both fail
            try:
                articles = source.discover_articles_with_retry_skip(
                    count=resolved_count, max_retries=2, batch_mode=batch_mode
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
                source, articles, base_dir, download_files, quiet, verbose, download_pdfs
            )

            # Drain pending PDF downloads before returning.
            try:
                from capcat.core.async_pdf_manager import get_pdf_manager, shutdown_pdf_manager
                pdf_mgr = get_pdf_manager()
                if pdf_mgr.worker_thread is not None and pdf_mgr.worker_thread.is_alive():
                    drained = pdf_mgr.wait_until_idle(timeout=120.0)
                    if not drained:
                        self.logger.warning(
                            "PDF download drain timed out after 120s — "
                            "some PDFs may not have completed"
                        )
                shutdown_pdf_manager()
            except Exception as _pdf_exc:
                self.logger.warning(f"PDF manager shutdown error: {_pdf_exc}")

            if generate_html:
                from capcat.core.html_post_processor import launch_web_view
                from pathlib import Path
                # For default output, base_dir is News_DD-MM-YYYY/Source_DD-MM-YYYY/.
                # Process from the parent (News_DD-MM-YYYY/) so index.html is created
                # at the correct level, not inside the source subfolder.
                html_root = str(Path(base_dir).parent) if output_dir == "." else base_dir
                launch_web_view(html_root)

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
        download_pdfs: bool = False,
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
            executor = ThreadPoolExecutor(max_workers=max_workers)
            try:
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
                        download_pdfs,
                    )
                    futures[future] = (i, article)

                successful_count = 0
                failed_count = 0

                # Process with aggressive timeout to prevent hangs
                # Give 60 seconds per article as reasonable max time
                per_article_timeout = 60
                total_timeout = per_article_timeout * len(futures)
                start_time = time.time()

                shutdown = get_shutdown()  # MUST be after executor is constructed

                try:
                    for future in as_completed(futures, timeout=total_timeout):
                        if shutdown and shutdown.should_shutdown():
                            break
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

            finally:
                # Always runs — on normal exit, on shutdown break, and on timeout.
                # cancel_futures=True prevents queued futures from starting.
                # Calling shutdown() twice is idempotent per Python docs.
                executor.shutdown(wait=False, cancel_futures=True)

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
        download_pdfs: bool = False,
    ) -> bool:
        """Process a single article using the new source system."""

        def progress_callback(progress: float, stage: str):
            if progress_tracker:
                progress_tracker.update_item_progress(progress, stage)

        try:
            import inspect as _inspect
            _params = _inspect.signature(source.fetch_article_content).parameters
            _fetch_kwargs = {"download_files": download_files}
            if "download_pdfs" in _params:
                _fetch_kwargs["download_pdfs"] = download_pdfs
            success, article_path = source.fetch_article_content(
                article, base_dir, progress_callback, **_fetch_kwargs
            )
            comments_written = False

            # Process comments if available and supported
            if (
                success
                and self.config.processing.create_comments_file
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
                        comments_written = source.fetch_comments(
                            article.comment_url, article.title, article_path
                        )
                        if comments_written:
                            comments_md = find_comments_md(Path(article_path))
                            if comments_md:
                                inject_comments_wikilink(article_path, comments_md.stem)
                            else:
                                self.logger.warning(
                                    f"Comments file not found after fetch_comments returned True: {article_path}"
                                )
                    except Exception as comment_error:
                        self.logger.warning(
                            f"Failed to fetch comments for '{article.title}': {comment_error}"
                        )

            # Inject YAML frontmatter — article always, comments if written
            if success:
                article_md = find_article_md(Path(article_path))
                if article_md:
                    inject_frontmatter(
                        str(article_md),
                        _build_article_metadata(article, source),
                    )
                if comments_written:
                    comments_md = find_comments_md(Path(article_path))
                    if comments_md:
                        inject_frontmatter(
                            str(comments_md),
                            _build_comments_metadata(article, source),
                        )

            return success
        except Exception as e:
            self.logger.error(
                f"Failed to process article '{article.title}': {e}"
            )
            return False


# Global processor instance
_processor = None


def get_unified_processor(project_root: Optional[Path] = None) -> UnifiedSourceProcessor:
    """Get global unified processor instance."""
    global _processor
    if project_root is not None:
        return UnifiedSourceProcessor(project_root=project_root)
    if _processor is None:
        _processor = UnifiedSourceProcessor()
    return _processor


def process_source_articles(
    source_name: str,
    count: Optional[int],
    output_dir: str,
    quiet: bool = False,
    verbose: bool = False,
    download_files: bool = False,
    batch_mode: bool = False,
    generate_html: bool = False,
    project_root: Optional[Path] = None,
    download_pdfs: bool = False,
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
        project_root: Optional project root override
        download_pdfs: Enable PDF downloads (--pdfs flag)
    """
    processor = get_unified_processor(project_root=project_root)
    processor.process_source_articles(
        source_name, count, output_dir, quiet, verbose, download_files, batch_mode,
        generate_html, download_pdfs,
    )
