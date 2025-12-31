#!/usr/bin/env python3
"""
Unified Article Processor - Universal entry point for all article processing.

All commands (single, fetch, bundle) route through this processor to ensure
consistent behavior across the application.
"""

import os
from typing import Callable, Optional, Tuple
import requests

from core.logging_config import get_logger
from core.specialized_source_manager import get_specialized_source_manager
from core.source_config import detect_source
from core.utils import sanitize_filename


class UnifiedArticleProcessor:
    """
    Universal article processing entry point.

    Provides consistent article fetching logic across all commands:
    - Single article mode
    - Fetch mode (multiple sources)
    - Bundle mode (predefined source groups)

    Processing Order:
    1. Check specialized sources (Twitter, YouTube, Medium, Substack)
    2. Check source-specific handlers (HN, BBC, etc.)
    3. Fall back to generic ArticleFetcher
    """

    def __init__(self):
        """Initialize processor with specialized source manager."""
        self.specialized_manager = get_specialized_source_manager()
        self.logger = get_logger(__name__)

    def process_article(
        self,
        url: str,
        title: str,
        index: int,
        base_folder: str,
        download_files: bool = False,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        update_mode: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Universal article processing with specialized source detection.

        Args:
            url: Article URL to process
            title: Article title (may be placeholder)
            index: Article index for folder numbering
            base_folder: Output directory path
            download_files: Whether to download media files
            progress_callback: Optional progress reporting callback
            update_mode: Re-check URL validity and update timestamp

        Returns:
            Tuple[bool, Optional[str], Optional[str]]:
            (success, article_title, article_folder_path)
        """

        # Step 1: Check specialized sources first
        if self.specialized_manager.can_handle_url(url):
            self.logger.info(f"Specialized source detected for URL: {url}")
            return self._process_with_specialized_source(
                url, title, base_folder, update_mode
            )

        # Step 2: Detect source-specific handler
        source = detect_source(url)
        if source:
            self.logger.debug(f"Source-specific handler detected: {source}")
            return self._process_with_source_handler(
                url, title, index, base_folder,
                download_files, progress_callback, source
            )

        # Step 3: Fall back to generic processing
        self.logger.debug(f"Using generic processing for URL: {url}")
        return self._process_with_generic_handler(
            url, title, index, base_folder,
            download_files, progress_callback
        )

    def _process_with_specialized_source(
        self,
        url: str,
        title: str,
        base_folder: str,
        update_mode: bool
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Handle specialized sources (Twitter, YouTube, Medium, Substack).

        Args:
            url: Article URL
            title: Article title
            base_folder: Output directory
            update_mode: Whether to re-check URL and update timestamp

        Returns:
            Tuple of (success, article_title, article_folder_path)
        """
        source_result = self.specialized_manager.get_source_for_url(url)

        if not source_result:
            self.logger.error(f"Specialized source detection failed for: {url}")
            return False, None, None

        source_instance, source_id = source_result

        # Create output directory for specialized content
        safe_title = sanitize_filename(title or source_id)
        article_folder = os.path.join(base_folder, safe_title)
        os.makedirs(article_folder, exist_ok=True)

        # Update mode: re-check URL validity and update timestamp
        if update_mode:
            if not self._check_url_validity(url):
                self._add_url_warning(article_folder, url)
                self.logger.warning(
                    f"URL invalid, preserved existing placeholder: {url}"
                )
                return True, title, article_folder

            self._update_timestamp(article_folder)
            self.logger.info(f"Updated timestamp for: {url}")

        # Create article object for specialized handler
        from core.source_system.base_source import Article
        article = Article(title=title or "", url=url)

        # Fetch content with specialized handler
        success, article_title = source_instance.fetch_article_content(
            article, article_folder, progress_callback=None
        )

        if success:
            self.logger.info(
                f"Specialized source '{source_id}' created placeholder: "
                f"{article_title}"
            )
            return True, article_title, article_folder

        self.logger.error(
            f"Specialized source '{source_id}' failed for: {url}"
        )
        return False, None, None

    def _process_with_source_handler(
        self,
        url: str,
        title: str,
        index: int,
        base_folder: str,
        download_files: bool,
        progress_callback: Optional[Callable],
        source: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Handle source-specific processing (HN, BBC, etc.).

        Delegates to existing source-specific implementations.

        Args:
            url: Article URL
            title: Article title
            index: Article index
            base_folder: Output directory
            download_files: Whether to download media
            progress_callback: Progress callback
            source: Source identifier (e.g., 'hn', 'bbc')

        Returns:
            Tuple of (success, article_title, article_folder_path)
        """
        # Import here to avoid circular dependencies
        try:
            from capcat import process_single_article

            return process_single_article(
                url=url,
                title=title,
                source=source,
                base_dir=base_folder,
                files=download_files,
                use_generic=False
            )
        except ImportError as e:
            self.logger.warning(f"Could not import process_single_article: {e}")
            # Fall back to generic if import fails
            return self._process_with_generic_handler(
                url, title, index, base_folder, download_files, progress_callback
            )

    def _process_with_generic_handler(
        self,
        url: str,
        title: str,
        index: int,
        base_folder: str,
        download_files: bool,
        progress_callback: Optional[Callable]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Handle generic article processing.

        Uses ArticleFetcher for unknown sources.

        Args:
            url: Article URL
            title: Article title
            index: Article index
            base_folder: Output directory
            download_files: Whether to download media
            progress_callback: Progress callback

        Returns:
            Tuple of (success, article_title, article_folder_path)
        """
        from core.article_fetcher import ArticleFetcher
        from core.session_pool import get_global_session

        # Create generic fetcher
        class GenericArticleFetcher(ArticleFetcher):
            def should_skip_url(self, url: str, title: str) -> bool:
                """Never skip URLs for generic fetching."""
                return False

        session = get_global_session("generic")
        fetcher = GenericArticleFetcher(
            session, download_files=download_files
        )

        return fetcher.fetch_article_content(
            title, url, index, base_folder, progress_callback
        )

    def _check_url_validity(self, url: str) -> bool:
        """
        Check if URL is still valid (HEAD request).

        Args:
            url: URL to check

        Returns:
            True if URL valid (status 200-399), False otherwise
        """
        try:
            response = requests.head(
                url,
                timeout=5,
                allow_redirects=True
            )
            is_valid = 200 <= response.status_code < 400

            self.logger.debug(
                f"URL validity check for {url}: {response.status_code} "
                f"({'valid' if is_valid else 'invalid'})"
            )

            return is_valid

        except requests.Timeout:
            self.logger.debug(f"URL validity check timeout for: {url}")
            return False
        except requests.RequestException as e:
            self.logger.debug(f"URL validity check failed for {url}: {e}")
            return False
        except Exception as e:
            self.logger.warning(
                f"Unexpected error in URL validity check for {url}: {e}"
            )
            return False

    def _update_timestamp(self, article_folder: str):
        """
        Update timestamp in article metadata.

        Args:
            article_folder: Path to article folder containing article.md
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        article_md = os.path.join(article_folder, "article.md")

        if os.path.exists(article_md):
            # Read existing content
            with open(article_md, "r", encoding="utf-8") as f:
                content = f.read()

            # Add/update timestamp footer
            timestamp_marker = "\n\n---\n\n**Last Updated:**"

            if timestamp_marker in content:
                # Update existing timestamp
                import re
                content = re.sub(
                    r"\*\*Last Updated:\*\* .*",
                    f"**Last Updated:** {timestamp}",
                    content
                )
            else:
                # Add new timestamp
                content += f"{timestamp_marker} {timestamp}\n"

            # Write updated content
            with open(article_md, "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.debug(f"Updated timestamp in: {article_md}")

    def _add_url_warning(self, article_folder: str, url: str):
        """
        Add warning about invalid URL to article.

        Args:
            article_folder: Path to article folder
            url: Invalid URL
        """
        article_md = os.path.join(article_folder, "article.md")

        if os.path.exists(article_md):
            with open(article_md, "a", encoding="utf-8") as f:
                f.write(
                    f"\n\n---\n\n"
                    f"**⚠️ Warning:** URL may be invalid or unreachable: {url}\n"
                )

            self.logger.debug(f"Added URL warning to: {article_md}")


# Global instance
_unified_processor = None


def get_unified_processor() -> UnifiedArticleProcessor:
    """Get the global unified article processor instance."""
    global _unified_processor
    if _unified_processor is None:
        _unified_processor = UnifiedArticleProcessor()
    return _unified_processor
