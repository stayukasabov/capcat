"""Single article fetch command."""
from __future__ import annotations

import os
from typing import Optional, Tuple

try:
    from capcat.core.source_config_mirror import SourceConfigMirror
    MIRROR_AVAILABLE = True
except ImportError:
    SourceConfigMirror = None  # type: ignore[assignment,misc]
    MIRROR_AVAILABLE = False


def _rename_to_dated(article_folder: str, date_str: str) -> str:
    """Rename article_folder to '<date_str>-<name>' in its parent directory.

    Idempotent: returns the original path unchanged if it already starts
    with ``date_str + '-'``.

    Args:
        article_folder: Absolute path to the article folder to rename.
        date_str: Date prefix in DD-MM-YYYY format.

    Returns:
        Absolute path to the (possibly renamed) folder.
    """
    from pathlib import Path

    folder = Path(article_folder)
    if folder.name.startswith(date_str + "-"):
        return article_folder
    new_path = folder.parent / f"{date_str}-{folder.name}"
    folder.rename(new_path)
    return str(new_path)


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
    from capcat.core.source_system.source_registry import get_source_registry

    logger = get_logger(__name__)
    source_match = get_source_registry().get_source_for_url(url)
    if not source_match:
        logger.error(f"No specialized source available for URL: {url}")
        return False, None

    source_instance, source_id = source_match

    if output_dir == ".":
        from capcat.core.config import get_capcats_dir
        capcats_dir = str(get_capcats_dir())
    else:
        capcats_dir = output_dir

    os.makedirs(capcats_dir, exist_ok=True)

    formatted_date = datetime.now().strftime("%d-%m-%Y")

    logger.info(f"Processing {source_id.title()} article with paywall detection...")

    try:
        from capcat.core.source_system.base_source import Article

        # Empty title - source will extract actual title during fetch
        article = Article(title="", url=url)
        success, folder_path = source_instance.fetch_article_content(
            article, capcats_dir, progress_callback=None
        )

        if success and folder_path:
            folder_path = _rename_to_dated(folder_path, formatted_date)
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

            logger.info(f"Output location: {folder_path}")
            return True, folder_path
        else:
            logger.error(f"Failed to fetch {source_id.title()} content")
            return False, capcats_dir

    except Exception as e:
        logger.error(f"Error processing {source_id.title()} article: {e}")
        return False, capcats_dir


def scrape_single_article(
    url: str,
    output_dir: str,
    verbose: bool = False,
    files: bool = False,
    pdfs: bool = False,
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
        files: Download all media files (audio, video, documents).
        pdfs: Download PDF files (--pdfs flag).
        generate_html: Generate HTML version of article.
        update_mode: Update existing article instead of creating new.

    Returns:
        Tuple of (success, output_directory_path).
    """
    from datetime import datetime

    from capcat.core.config import find_project_root
    from capcat.core.logging_config import get_logger
    from capcat.core.source_config import detect_source
    from capcat.core.source_system.source_registry import get_source_registry, reset_source_registry
    from capcat.core.tui_context import is_tui_active

    logger = get_logger(__name__)

    # Ensure userspace source files are up to date before URL routing.
    # Without this, an outdated Config/sources/active/custom/twitter/source.py
    # (e.g. with old substring-match logic) overrides the installed fixed version.
    if MIRROR_AVAILABLE:
        try:
            project_root = find_project_root()
            mirror = SourceConfigMirror(project_root, tui_mode=is_tui_active())
            if not mirror.is_mirrored():
                mirror.run_first_mirror()
            else:
                mirror.check_for_upgrades()
            reset_source_registry()
        except Exception:
            pass

    if get_source_registry().can_handle_url(url):
        logger.info(f"Attempting specialized source for URL: {url}")
        success, base_dir = _scrape_with_specialized_source(
            url, output_dir, verbose, files, generate_html
        )
        if success:
            return success, base_dir
        logger.info("Specialized source failed, falling back to generic scraping")

    source = detect_source(url)

    if output_dir != ".":
        parent_dir = os.path.abspath(output_dir)
    else:
        from capcat.core.config import get_capcats_dir
        parent_dir = str(get_capcats_dir())

    os.makedirs(parent_dir, exist_ok=True)
    formatted_date = datetime.now().strftime("%d-%m-%Y")

    success = False
    base_dir = parent_dir  # Will be updated to dated article folder if fetch succeeds

    try:
        # Try known source optimization first
        if source:
            from capcat.core.source_system.source_factory import get_source_factory
            from capcat.core.source_system.base_source import Article

            factory = get_source_factory()
            if source in factory.get_available_sources():
                registry = get_source_registry()
                config = registry.get_source_config(source)
                source_name = config.display_name if config else source
                logger.info(f"We have an optimization for {source_name}")

                source_obj = factory.create_source(source)
                article = Article(title=f"Article from {url}", url=url)
                # BaseSource.fetch_article_content returns (bool, Optional[str]) - 2-tuple
                success, article_folder = source_obj.fetch_article_content(article, parent_dir, None)
                if success and article_folder:
                    base_dir = _rename_to_dated(article_folder, formatted_date)
                else:
                    base_dir = parent_dir
            else:
                logger.info(
                    f"Source {source} not found in registry, using generic scraper"
                )
                source = None  # Fall back to generic path

        # Generic fallback when no known source or known source failed
        if not source:
            from capcat.core.article_fetcher import ArticleFetcher
            from capcat.core.session_pool import get_global_session

            class GenericArticleFetcher(ArticleFetcher):
                """ArticleFetcher subclass that never skips any URL.

                Used as the generic fallback when no registered source
                matches the requested URL.
                """

                def should_skip_url(self, url: str, title: str) -> bool:
                    """Always return False - no URL is skipped in generic mode.

                    Args:
                        url: The article URL being evaluated.
                        title: The article title being evaluated.

                    Returns:
                        Always ``False``.
                    """
                    return False

            session = get_global_session("generic")
            fetcher = GenericArticleFetcher(session, download_files=files, download_pdfs=pdfs)
            # ArticleFetcher.fetch_article_content returns (success, title, folder_path)
            success, _, article_folder = fetcher.fetch_article_content(
                f"Article from {url}", url, 1, parent_dir, None
            )
            if success and article_folder:
                base_dir = _rename_to_dated(article_folder, formatted_date)
            else:
                base_dir = parent_dir

    except Exception as e:
        logger.error(f"Failed to process single article: {e}")
        success = False

    if not success:
        logger.warning("Failed to fetch article content, but folder structure created")
        return success, base_dir

    if generate_html:
        try:
            from capcat.core.html_post_processor import HTMLPostProcessor
            processor = HTMLPostProcessor()
            processor.process_directory_tree(
                base_dir,
                incremental=False,
                is_single_article=True,
            )
            logger.info(f"Generated HTML in: {base_dir}")
        except Exception as e:
            logger.warning(f"Failed to generate HTML: {e}")

    return success, base_dir
