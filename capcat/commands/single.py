"""Single article fetch command."""
from __future__ import annotations

import os
from typing import Optional, Tuple
from urllib.parse import urlparse


def _scrape_with_specialized_source(
    url: str,
    output_dir: str,
    verbose: bool = False,
    files: bool = False,
    generate_html: bool = False,
) -> Tuple[bool, Optional[str]]:
    """Handle article scraping with specialized sources (Medium, Substack, etc.)."""
    from datetime import datetime

    from capcat.core.logging_config import get_logger
    from capcat.core.specialized_source_manager import get_specialized_source_manager

    logger = get_logger(__name__)
    specialized_manager = get_specialized_source_manager()

    source_result = specialized_manager.get_source_for_url(url)
    if not source_result:
        logger.error(f"No specialized source available for URL: {url}")
        return False, None

    source_instance, source_id = source_result

    if output_dir == ".":
        from capcat.core.config import get_capcats_dir
        capcats_dir = str(get_capcats_dir())
    else:
        capcats_dir = output_dir

    os.makedirs(capcats_dir, exist_ok=True)

    formatted_date = datetime.now().strftime("%d-%m-%Y")
    source_folder = f"{source_id.title()}_{formatted_date}"
    final_output_dir = os.path.join(capcats_dir, source_folder)
    os.makedirs(final_output_dir, exist_ok=True)

    logger.info(f"Processing {source_id.title()} article with paywall detection...")

    try:
        from capcat.core.source_system.base_source import Article

        article = Article(title="", url=url)
        success, folder_path = source_instance.fetch_article_content(
            article, final_output_dir, progress_callback=None
        )

        if success:
            logger.info(
                f"Successfully saved {source_id.title()} content to: {folder_path}"
            )
            if generate_html:
                try:
                    from capcat.core.html_post_processor import HTMLPostProcessor

                    processor = HTMLPostProcessor()
                    processor.process_directory_tree(
                        folder_path,
                        incremental=False,
                        is_single_article=True,
                    )
                    logger.info(f"Generated HTML for {source_id.title()} article")
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
        url: Article URL to scrape.
        output_dir: Base directory for output (uses project Capcats/ if ".").
        verbose: Enable verbose logging output.
        files: Download all media files (PDFs, audio, video).
        generate_html: Generate HTML version of article.
        update_mode: Update existing article instead of creating new.

    Returns:
        Tuple of (success, output_directory_path).
    """
    from datetime import datetime

    from capcat.core.logging_config import get_logger
    from capcat.core.source_config import detect_source
    from capcat.core.source_system.source_registry import get_source_registry
    from capcat.core.specialized_source_manager import get_specialized_source_manager

    logger = get_logger(__name__)

    specialized_manager = get_specialized_source_manager()
    if specialized_manager.can_handle_url(url):
        logger.info(f"Attempting specialized source for URL: {url}")
        success, base_dir = _scrape_with_specialized_source(
            url, output_dir, verbose, files, generate_html
        )
        if success:
            return success, base_dir
        logger.info("Specialized source failed, falling back to generic scraping")

    source = detect_source(url)

    if output_dir != ".":
        base_dir = os.path.abspath(output_dir)
    else:
        from capcat.core.config import get_capcats_dir
        capcats_dir = str(get_capcats_dir())
        formatted_date = datetime.now().strftime("%d-%m-%Y")

        if source:
            registry = get_source_registry()
            config = registry.get_source_config(source)
            source_name = config.display_name if config else source
            logger.info(f"We have an optimization for {source_name}")

            from capcat.core.utils import get_source_folder_name
            source_folder_name = f"{get_source_folder_name(source)}_{formatted_date}"
            base_dir = os.path.join(capcats_dir, source_folder_name)
        else:
            parsed_url = urlparse(url)
            url_path = parsed_url.path.rstrip("/")
            url_title = url_path.split("/")[-1] if url_path else parsed_url.netloc

            from capcat.core.utils import sanitize_filename
            safe_title = sanitize_filename(url_title, max_length=100)
            base_dir = os.path.join(capcats_dir, safe_title.title())

    success = False
    use_generic = not source

    try:
        if source and not use_generic:
            from capcat.sources.base.factory import get_modular_source_factory

            factory = get_modular_source_factory()
            modular_source = factory.create_source(source)

            if modular_source:
                (success, _article_path, _folder_path) = modular_source.fetch_article_content(
                    title=f"Article from {url}",
                    url=url,
                    index=1,
                    base_folder=base_dir,
                    progress_callback=None,
                )
            else:
                try:
                    from capcat.core.unified_source_processor import get_unified_processor
                    from capcat.core.source_configs import get_source_config

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
                    logger.info(
                        f"Source {source} detected but not configured, "
                        "using generic scraper"
                    )
                    use_generic = True

        if not source or use_generic:
            from capcat.core.article_fetcher import ArticleFetcher
            from capcat.core.session_pool import get_global_session

            class GenericArticleFetcher(ArticleFetcher):
                """ArticleFetcher subclass that never skips any URL.

                Used as the generic fallback when no registered source
                matches the requested URL.
                """

                def should_skip_url(self, url: str, title: str) -> bool:
                    """Always return False — no URL is skipped in generic mode.

                    Args:
                        url: The article URL being evaluated.
                        title: The article title being evaluated.

                    Returns:
                        Always ``False``.
                    """
                    return False

            session = get_global_session("generic")
            fetcher = GenericArticleFetcher(session, download_files=files)
            success, returned_title, content_path = fetcher.fetch_article_content(
                f"Article from {url}", url, 1, base_dir, None
            )

            if success and returned_title is None and content_path is None:
                return True, None

    except Exception as e:
        logger.error(f"Failed to process single article: {e}")
        success = False

    if not success:
        logger.warning("Failed to fetch article content, but folder structure created")
    return success, base_dir
