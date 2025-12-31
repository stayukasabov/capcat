#!/usr/bin/env python3
"""
Capcat - News Article Archiving System

A free and open-source tool to make people's lives easier.

Author: Stayu Kasabov (https://stayux.com)
License: MIT-Style Non-Commercial
Copyright (c) 2025 Stayu Kasabov
"""

import argparse
import os
import sys
from typing import Dict, List, Optional, Tuple

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import error handling first
from core.error_handling import (
    startup_check, handle_error, ErrorContext, DependencyError
)

# Perform startup validation and auto-repair
if not startup_check():
    print("Error: Failed to validate or repair dependencies. "
          "Please check your installation.")
    sys.exit(1)

from cli import parse_arguments
from core.config import get_config, load_config
from core.exceptions import FileSystemError, CapcatError
from core.html_post_processor import launch_web_view
from core.logging_config import get_logger, setup_logging
from core.progress import get_batch_progress
from core.shutdown import GracefulShutdown
from core.source_config import detect_source
from core.source_system.source_registry import get_source_registry
from core.source_system.base_source import Article, SourceError

# Import new hybrid source system
from core.source_system.source_factory import get_source_factory
from core.unified_source_processor import (
    UnifiedSourceProcessor,
    process_source_articles,
)
from core.utils import create_output_directory_capcat

# Hybrid Architecture Note:
# - The unified processor handles existing sources with current architecture
# - The new source system will be used for new sources and gradual migration


def process_sources(
    sources: List[str],
    args: argparse.Namespace,
    config,
    logger,
    generate_html: bool = False,
    output_dir: str = "."
) -> Dict[str, any]:
    """Process multiple sources using the unified processor.

    Args:
        sources: List of source identifiers to process (e.g., 'hn', 'bbc')
        args: Parsed command-line arguments containing count, quiet, verbose
        config: Configuration object with system settings
        logger: Logger instance for output
        generate_html: Whether to generate HTML output after processing
        output_dir: Output directory path for saved articles

    Returns:
        Dictionary with keys:
            - 'successful': List of successfully processed sources
            - 'failed': List of tuples (source, error_message)
            - 'total': Total number of sources attempted

    Raises:
        SourceError: If source cannot be loaded from registry
    """
    # Clear URL cache at the beginning of each session to prevent
    # cross-session duplicates
    UnifiedSourceProcessor.clear_url_cache()
    logger.debug("Cleared URL deduplication cache for new session")

    successful_sources = []
    failed_sources = []
    is_batch = len(sources) > 1  # Detect if processing multiple sources

    for source in sources:
        try:
            logger.info(f"Processing {source} articles...")

            # Use the unified processor for all sources
            process_source_articles(
                source_name=source,
                count=getattr(args, "count", 30),
                output_dir=output_dir,
                quiet=getattr(args, "quiet", False),
                verbose=getattr(args, "verbose", False),
                download_files=getattr(args, "media", False),
                batch_mode=is_batch,
            )
            successful_sources.append(source)
            logger.info(f"Successfully processed {source}")

        except SourceError as e:
            # Source was skipped (timeout/unavailable) - don't show as error
            failed_sources.append((source, "Source unavailable"))
            if is_batch:
                logger.info(f"Continuing with remaining sources...")
        except Exception as e:
            # Unexpected error
            logger.error(f"Error processing {source}: {e}")
            failed_sources.append((source, str(e)))
            if is_batch:
                logger.warning(
                    f"Skipping {source} and continuing with remaining sources"
                )

    return {
        'successful': successful_sources,
        'failed': failed_sources,
        'total': len(sources)
    }


def _scrape_with_specialized_source(
    url: str,
    output_dir: str,
    verbose: bool = False,
    files: bool = False,
    generate_html: bool = False,
) -> Tuple[bool, Optional[str]]:
    """Handle article scraping with specialized sources.

    Supports Medium, Substack, and similar platforms with paywall detection.

    Args:
        url: Article URL to scrape
        output_dir: Directory to save article content
        verbose: Enable verbose logging output
        files: Download all media files (PDFs, audio, video)
        generate_html: Generate HTML version of article

    Returns:
        Tuple of (success status, output directory path). Returns
        (True, path) on success, (False, path) or (False, None) on failure.

    Raises:
        SpecializedSourceError: If source detection or scraping fails
    """
    from datetime import datetime

    from core.specialized_source_manager import get_specialized_source_manager

    logger = get_logger(__name__)
    specialized_manager = get_specialized_source_manager()

    # Get appropriate specialized source
    source_result = specialized_manager.get_source_for_url(url)
    if not source_result:
        logger.error(f"No specialized source available for URL: {url}")
        return False, None

    source_instance, source_id = source_result

    # Determine output directory
    if output_dir == ".":
        application_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(application_dir)
        capcats_dir = os.path.join(project_root, "Capcats")
    else:
        capcats_dir = output_dir

    os.makedirs(capcats_dir, exist_ok=True)

    # Create date-stamped folder for specialized content
    formatted_date = datetime.now().strftime("%d-%m-%Y")
    source_folder = f"{source_id.title()}_{formatted_date}"
    final_output_dir = os.path.join(capcats_dir, source_folder)
    os.makedirs(final_output_dir, exist_ok=True)

    logger.info(
        f"Processing {source_id.title()} article with paywall detection..."
    )

    try:
        # Create article object
        from core.source_system.base_source import Article

        # Title will be extracted during processing
        article = Article(title="", url=url)

        # Fetch content with specialized handling
        success, folder_path = source_instance.fetch_article_content(
            article, final_output_dir, progress_callback=None
        )

        if success:
            logger.info(
                f"Successfully saved {source_id.title()} content to: "
                f"{folder_path}"
            )

            # Generate HTML if requested
            if generate_html:
                try:
                    from core.html_generator import HTMLGenerator

                    html_generator = HTMLGenerator()

                    # Find the article markdown file
                    article_md = os.path.join(folder_path, "article.md")
                    if os.path.exists(article_md):
                        html_generator.generate_html_file(
                            markdown_file=article_md,
                            article_folder=folder_path,
                            source_name=source_id.title(),
                        )
                        logger.info(
                            f"Generated HTML for {source_id.title()} article"
                        )
                except Exception as e:
                    logger.warning(f"Failed to generate HTML: {e}")

            logger.info(f"Output location: {final_output_dir}")
            return True, final_output_dir
        else:
            logger.error(f"Failed to fetch {source_id.title()} content")
            return False, final_output_dir

    except Exception as e:
        logger.error(f"Error processing {source_id.title()} article: {e}")
        return False, final_output_dir


def scrape_single_article(
    url: str,
    output_dir: str,
    verbose: bool = False,
    files: bool = False,
    generate_html: bool = False,
    update_mode: bool = False,
) -> Tuple[bool, Optional[str]]:
    """Scrape a single article from any supported source.

    Attempts specialized sources first (Medium, Substack), then falls back
    to generic scraping. Auto-detects source and creates organized output.

    Args:
        url: Article URL to scrape
        output_dir: Base directory for output (uses ../Capcats/ if ".")
        verbose: Enable verbose logging output
        files: Download all media files (PDFs, audio, video)
        generate_html: Generate HTML version of article
        update_mode: Update existing article instead of creating new

    Returns:
        Tuple of (success status, output directory path). Returns
        (True, path) on success, (False, path) or (False, None) on failure.

    Raises:
        SourceError: If source detection fails
        IOError: If output directory cannot be created
    """
    logger = get_logger(__name__)

    # Check if specialized source can handle this URL
    from core.specialized_source_manager import (
        get_specialized_source_manager
    )

    specialized_manager = get_specialized_source_manager()

    if specialized_manager.can_handle_url(url):
        logger.info(f"Attempting specialized source for URL: {url}")
        success, base_dir = _scrape_with_specialized_source(
            url, output_dir, verbose, files, generate_html
        )
        # If specialized source succeeds, return immediately
        if success:
            return success, base_dir
        # If specialized source fails, fallback to generic scraping
        logger.info(
            "Specialized source failed, falling back to generic scraping"
        )

    # Try to determine the source from the URL using our configuration
    source = detect_source(url)

    if output_dir != ".":
        base_dir = os.path.abspath(output_dir)
    else:
        # Determine the project root directory (one level up from
        # Application directory)
        application_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(application_dir)
        
        # Create output directory for single articles
        from datetime import datetime
        formatted_date = datetime.now().strftime("%d-%m-%Y")
        
        capcats_dir = os.path.join(project_root, "Capcats")

        # For predefined configurations, create direct folder structure
        # in Capcats folder
        if source:
            # Get display name from registry
            registry = get_source_registry()
            config = registry.get_source_config(source)
            source_name = config.display_name if config else source
            logger.info(
                f"We have an optimization for {source_name}"
            )

            # Create folder: source_DD-MM-YYYY in Capcats directory
            from core.utils import get_source_folder_name
            source_folder_name = (
                f"{get_source_folder_name(source)}_{formatted_date}"
            )
            base_dir = os.path.join(capcats_dir, source_folder_name)
        else:
            # For unknown sources, use generic Capcats folder
            # Extract title from URL for folder naming
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            url_path = parsed_url.path.rstrip("/")
            url_title = (
                url_path.split("/")[-1] if url_path
                else parsed_url.netloc
            )

            # Sanitize title for folder name
            from core.utils import sanitize_filename
            safe_title = sanitize_filename(
                url_title, max_length=100
            )

            # Capcats are single articles - use title directly without
            # date prefix. Apply title case for better readability
            capcat_folder_name = safe_title.title()
            base_dir = os.path.join(capcats_dir, capcat_folder_name)

    # Don't create folder yet - let fetcher create it after skip check passes

    # Use appropriate fetching function based on detected source
    success = False
    use_generic = not source  # Start with generic if no source detected

    try:
        if source and not use_generic:
            # Use the modular source factory for config-driven sources
            from sources.base.factory import get_modular_source_factory

            factory = get_modular_source_factory()
            modular_source = factory.create_source(source)

            if modular_source:
                # Use config-driven source (NewsSourceAdapter interface)
                (success, article_path,
                 folder_path) = modular_source.fetch_article_content(
                    title=f"Article from {url}",
                    url=url,
                    index=1,
                    base_folder=base_dir,
                    progress_callback=None
                )
            else:
                # Try legacy config system
                try:
                    from core.unified_source_processor import (
                        get_unified_processor
                    )
                    from core.source_configs import get_source_config

                    processor = get_unified_processor()
                    source_config = get_source_config(source)
                    success = processor._process_single_article(
                        source,
                        source_config,
                        (1, f"Article from {url}", url, None),
                        base_dir,
                        files,
                        None,
                    )
                except ValueError:
                    # Source detected but no config - use generic
                    logger.info(
                        f"Source {source} detected but not configured, "
                        f"using generic scraper"
                    )
                    use_generic = True

        if not source or use_generic:
            # Generic fetching for unknown sources
            from core.article_fetcher import ArticleFetcher
            from core.session_pool import get_global_session

            # Create simple concrete implementation for generic articles
            class GenericArticleFetcher(ArticleFetcher):
                def should_skip_url(
                    self, url: str, title: str
                ) -> bool:
                    """Never skip URLs for generic fetching."""
                    return False

            session = get_global_session("generic")
            fetcher = GenericArticleFetcher(
                session, download_files=files
            )
            success, returned_title, content_path = fetcher.fetch_article_content(
                f"Article from {url}", url, 1, base_dir, None
            )

            # Check if this was a skip (success=True but no content)
            if success and returned_title is None and content_path is None:
                # User skipped - return None for base_dir to signal skip
                return True, None

    except Exception as e:
        logger.error(f"Failed to process single article: {e}")
        success = False

    if not success:
        logger.warning(
            "Failed to fetch article content, but folder structure created"
        )
    return success, base_dir


def run_app(argv: Optional[List[str]] = None):
    """Main application logic."""
    # Setup graceful shutdown
    shutdown_handler = GracefulShutdown()

    try:
        # Parse arguments
        config_dict = parse_arguments(argv)

        # Handle list and config commands (already handled in CLI)
        if config_dict["action"] in ["list", "config"]:
            return

        setup_logging(
            level=config_dict.get("log_level", "INFO"),
            log_file=config_dict.get("log_file"),
            verbose=config_dict.get("verbose", False),
            quiet=config_dict.get("quiet", False),
        )
        logger = get_logger(__name__)
        config = get_config()

        # Handle different actions
        if config_dict["action"] == "single":
            url = config_dict["url"]
            output_dir = config_dict["output"]
            download_media = config_dict["media"]
            generate_html = config_dict.get("html", False)
            update_mode = config_dict.get("update", False)

            # Handle update mode
            if update_mode:
                from core.update_manager import get_update_manager
                from core.article_fetcher import set_global_update_mode

                # Set global update mode flag for all ArticleFetchers
                set_global_update_mode(True)

                update_manager = get_update_manager()

                if not update_manager.check_and_handle_update(
                    "single", url=url
                ):
                    logger.info("Update cancelled by user")
                    set_global_update_mode(False)  # Reset flag
                    return

            # Don't show "Scraping single article" message for PDF files
            # Progress bar will show immediately during download
            if not url.lower().endswith('.pdf'):
                logger.info(f"Scraping single article: {url}")

            # Initialize to avoid NameError if exception occurs
            base_dir = None
            try:
                success, base_dir = scrape_single_article(
                    url,
                    output_dir,
                    verbose=config_dict.get("verbose", False),
                    files=download_media,
                    generate_html=generate_html,
                    update_mode=update_mode,
                )

                if success:
                    # Check if this was a user skip (success but no base_dir)
                    if base_dir is None:
                        # User skipped - exit cleanly with success
                        logger.info("Operation completed (user skip)")
                        sys.exit(0)

                    # Display output location using base_dir
                    # Convert absolute path to relative for display
                    application_dir = os.path.dirname(
                        os.path.abspath(__file__)
                    )
                    project_root = os.path.dirname(application_dir)
                    rel_path = os.path.relpath(base_dir, project_root)
                    output_location = f"../{rel_path}/"

                    # Check if this is a Capcats single article
                    is_capcats = "Capcats" in base_dir.split(os.sep)

                    # Generate HTML if requested
                    if generate_html:
                        try:
                            # Use base_dir directly for HTML processing
                            html_target_dir = base_dir

                            logger.info("Generating HTML web view...")
                            # Single command always creates only article.html (no index)
                            launch_web_view(html_target_dir, is_single_article=True)

                            # Find article.html path (single articles always link to article.html)
                            import glob
                            article_html_pattern = os.path.join(
                                base_dir, "**/html/article.html"
                            )
                            article_html_files = glob.glob(
                                article_html_pattern, recursive=True
                            )
                            if article_html_files:
                                article_rel_path = os.path.relpath(
                                    article_html_files[0], project_root
                                )
                                final_output_location = f"../{article_rel_path}"
                            else:
                                # Fallback to base directory
                                final_output_location = output_location

                            logger.info(
                                f"You can find your files in "
                                f"{final_output_location}"
                            )

                            # Skip parent directory index regeneration for single command
                            # Single articles are standalone - no need to regenerate
                            # parent index which may contain many unrelated articles
                            # This prevents the confusing "processing 85 items" message
                            logger.debug(
                                "Skipping parent directory index regeneration "
                                "for single article (standalone mode)"
                            )
                        except Exception as html_error:
                            logger.warning(
                                f"HTML generation failed: {html_error}"
                            )
                    else:
                        # No HTML generation - just show markdown folder
                        logger.info(
                            f"You can find your files in {output_location}"
                        )
                else:
                    # Exit with error code if scraping failed
                    sys.exit(1)

                # Reset global update mode flag after successful completion
                if update_mode:
                    from core.article_fetcher import set_global_update_mode
                    set_global_update_mode(False)

                sys.exit(0)

            except Exception as e:
                logger.error(f"Single article processing failed: {e}")
                # Reset global update mode flag on error
                if config_dict.get("update", False):
                    from core.article_fetcher import set_global_update_mode
                    set_global_update_mode(False)
                sys.exit(1)

        elif config_dict["action"] in ["fetch", "bundle"]:
            sources = config_dict["sources"]
            count = config_dict["count"]
            output_dir = config_dict["output"]
            download_media = config_dict["media"]
            generate_html = config_dict.get("html", False)
            bundle_name = config_dict.get("bundle_name")
            update_mode = config_dict.get("update", False)

            # Handle update mode
            if update_mode:
                from core.update_manager import get_update_manager
                from core.article_fetcher import set_global_update_mode

                # Set global update mode flag for all ArticleFetchers
                set_global_update_mode(True)

                update_manager = get_update_manager()

                if config_dict["action"] == "bundle":
                    if not update_manager.check_and_handle_update(
                        "bundle", bundle_name=bundle_name
                    ):
                        logger.info("Update cancelled by user")
                        set_global_update_mode(False)  # Reset flag
                        return
                else:  # fetch
                    if not update_manager.check_and_handle_update(
                        "fetch", sources=sources
                    ):
                        logger.info("Update cancelled by user")
                        set_global_update_mode(False)  # Reset flag
                        return

            try:
                # Check if this is --all flag (sequential bundle proc)
                if (bundle_name and
                        bundle_name.startswith("all-bundles-ordered")):
                    logger.info(
                        f"Processing all bundles in order: "
                        f"{', '.join(sources)}"
                    )

                    # Process each bundle sequentially
                    from cli import get_available_bundles

                    bundles = get_available_bundles()

                    # sources contains bundle names for --all
                    for bundle_name_single in sources:
                        if (bundle_name_single in bundles and
                                bundles[bundle_name_single]):
                            bundle_sources = (
                                bundles[bundle_name_single]
                            )
                            logger.info(
                                f"Processing bundle "
                                f"'{bundle_name_single}': "
                                f"{', '.join(bundle_sources)}"
                            )

                            # Create args-like object for backward
                            # compatibility
                            class Args:
                                def __init__(self, config_dict):
                                    self.count = config_dict.get("count", 30)
                                    self.quiet = config_dict.get(
                                        "quiet", False
                                    )
                                    self.verbose = config_dict.get(
                                        "verbose", False
                                    )
                                    self.media = config_dict.get(
                                        "media", False
                                    )

                            args = Args(config_dict)
                            result = process_sources(
                                bundle_sources,
                                args,
                                config,
                                logger,
                                generate_html,
                                output_dir,
                            )

                            # Log bundle summary
                            if result['failed']:
                                logger.warning(
                                    f"Bundle '{bundle_name_single}' "
                                    f"completed with "
                                    f"{len(result['successful'])}/"
                                    f"{result['total']} sources successful"
                                )
                            else:
                                logger.info(
                                    f"Completed bundle "
                                    f"'{bundle_name_single}' - all "
                                    f"{result['total']} sources successful"
                                )

                    logger.info("All bundles processing completed")
                else:
                    # Regular processing (single bundle or fetch)
                    if bundle_name:
                        logger.info(
                            f"Fetching articles from bundle "
                            f"'{bundle_name}': {', '.join(sources)}"
                        )
                    else:
                        logger.info(
                            f"Fetching articles from sources: "
                            f"{', '.join(sources)}"
                        )

                    # Create args-like object for backward
                    # compatibility
                    class Args:
                        def __init__(self, config_dict):
                            self.count = config_dict.get("count", 30)
                            self.quiet = config_dict.get("quiet", False)
                            self.verbose = config_dict.get("verbose", False)
                            self.media = config_dict.get("media", False)

                    args = Args(config_dict)
                    result = process_sources(
                        sources, args, config, logger,
                        generate_html, output_dir
                    )

                    # Display processing summary (only in verbose mode)
                    if result['failed']:
                        # Show detailed summary only with --verbose
                        if getattr(args, 'verbose', False):
                            logger.warning("\nProcessing Summary:")
                            logger.warning(
                                f"  Total sources: {result['total']}"
                            )
                            logger.warning(
                                f"  Successful: {len(result['successful'])}"
                            )
                            logger.warning(f"  Failed: {len(result['failed'])}")

                            if result['successful']:
                                logger.info(
                                    f"\nSuccessful sources: "
                                    f"{', '.join(result['successful'])}"
                                )

                            logger.error("\nFailed sources:")
                            for source, error in result['failed']:
                                # Truncate error message for readability
                                short_error = error.split('\n')[0][:100]
                                logger.error(f"  - {source}: {short_error}")

                        # Only exit with error if ALL sources failed
                        if not result['successful']:
                            # Simple message for user (no verbose output)
                            if not getattr(args, 'verbose', False):
                                print(f"\nCapcat Info: No articles fetched - all sources unavailable\n")
                            else:
                                logger.error(
                                    "\nAll sources failed to process."
                                )
                            sys.exit(1)
                        else:
                            if getattr(args, 'verbose', False):
                                logger.info(
                                    f"\nContinuing with "
                                    f"{len(result['successful'])} "
                                    f"successful source(s)"
                                )
                    else:
                        logger.info(
                            f"\nAll {result['total']} source(s) "
                            f"processed successfully"
                        )

                # Display output location
                from datetime import datetime

                formatted_date = datetime.now().strftime("%d-%m-%Y")

                # Use actual output_dir from args, not hardcoded path
                if output_dir == ".":
                    # Default behavior: use ../News/
                    output_location = f"../News/news_{formatted_date}/"
                else:
                    # Custom output directory specified
                    output_location = os.path.abspath(output_dir)
                    if not output_location.endswith('/'):
                        output_location += '/'

                final_output_location = output_location
                if generate_html:
                    final_output_location = os.path.join(
                        output_location, "index.html"
                    )

                logger.info(
                    f"You can find your files in {final_output_location}"
                )

                # Generate HTML if requested
                if generate_html:
                    try:
                        # Convert relative path to absolute for HTML processing
                        if output_location.startswith("../"):
                            project_root = os.path.dirname(
                                os.path.dirname(os.path.abspath(__file__))
                            )
                            html_target_dir = os.path.join(
                                project_root, output_location[3:]
                            )  # Remove '../'
                        else:
                            html_target_dir = output_location

                        logger.info("Generating HTML web view...")
                        launch_web_view(html_target_dir)
                    except Exception as html_error:
                        logger.warning(f"HTML generation failed: {html_error}")

                # Reset global update mode flag after successful completion
                if update_mode:
                    from core.article_fetcher import set_global_update_mode
                    set_global_update_mode(False)
                
                sys.exit(0)

            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
                # Reset global update mode flag on error
                if config_dict.get("update", False):
                    from core.article_fetcher import set_global_update_mode
                    set_global_update_mode(False)
                sys.exit(1)

        elif config_dict["action"] == "list":
            from cli import handle_list_command

            handle_list_command(config_dict)

        elif config_dict["action"] == "config":
            from cli import handle_config_command

            handle_config_command(config_dict, logger)

        elif config_dict["action"] == "catch":
            from core.interactive import start_interactive_mode
            start_interactive_mode()

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except CapcatError as e:
        logger.error(e.user_message)
        if hasattr(e, "technical_details") and config_dict.get(
            "verbose", False
        ):
            logger.debug(f"Technical details: {e.technical_details}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if config_dict.get("verbose", False):
            import traceback

            logger.debug(traceback.format_exc())
        sys.exit(1)


def main() -> None:
    """Main entry point for the optimized Capcat application.

    Parses command-line arguments and delegates to run_app for execution.
    Handles single article scraping, batch processing, and interactive mode.
    """
    run_app(sys.argv[1:])

if __name__ == "__main__":
    main()
