#!/usr/bin/env python3
"""
Hacker News source implementation for the new source system.
Enhanced with comment functionality from V1 implementation.
"""

import os
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from core.article_fetcher import get_global_update_mode
from core.news_source_adapter import NewsSourceArticleFetcher
from core.source_system.base_source import (
    Article,
    ArticleDiscoveryError,
    BaseSource,
    ContentFetchError,
)


class HnSource(BaseSource):
    """
    Hacker News source implementation with comment support.
    """

    @property
    def source_type(self) -> str:
        return "custom"

    def discover_articles(self, count: int) -> List[Article]:
        """
        Discover articles from Hacker News with comment URLs.
        Supports pagination for fetching >30 articles.
        """
        import time

        try:
            self.logger.debug(
                f"Discovering articles for {self.config.name} (count: {count})"
            )

            articles = []
            page = 1
            max_pages = 10  # Limit to prevent infinite loops

            while len(articles) < count and page <= max_pages:
                # Construct page URL
                if page == 1:
                    page_url = self.config.base_url
                else:
                    # HN pagination: ?p=2, ?p=3, etc.
                    page_url = f"{self.config.base_url}?p={page}"
                    # Log pagination activity
                    self.logger.debug(f"Fetching page {page} from {page_url}")

                # Rate limiting: wait between page requests (except first page)
                if page > 1:
                    time.sleep(2.0)  # 2 second delay between pages

                response = self.session.get(
                    page_url, timeout=self.config.timeout
                )
                response.raise_for_status()

                # Ensure UTF-8 encoding
                response.encoding = 'utf-8'

                soup = BeautifulSoup(response.text, "html.parser")

                # Get article rows from Hacker News structure
                article_rows = soup.select("tr.athing")

                # If no articles found on this page, we've reached the end
                if not article_rows:
                    self.logger.debug(f"No more articles found on page {page}")
                    break

                for i, row in enumerate(article_rows):
                    if len(articles) >= count:
                        break

                    # Get title link
                    title_link = row.select_one(".titleline > a")
                    if not title_link:
                        continue

                    href = title_link.get("href", "")
                    title = title_link.get_text().strip() or "Untitled Article"

                    if not href:
                        continue

                    # Convert relative URLs to absolute
                    if href.startswith("/"):
                        href = "https://news.ycombinator.com" + href
                    elif href.startswith("item?id="):
                        # Handle HN discussion pages like "item?id=12345"
                        href = "https://news.ycombinator.com/" + href
                    elif not href.startswith(("http://", "https://")):
                        continue

                    # Get comment URL from the next row (meta row)
                    comment_url = None
                    article_id = row.get("id", "")
                    if article_id:
                        # Look for the meta row that follows this article
                        next_sibling = row.find_next_sibling("tr")
                        if next_sibling:
                            comment_link = next_sibling.select_one(
                                f'a[href*="item?id={article_id}"]'
                            )
                            if comment_link:
                                comment_href = comment_link.get("href", "")
                                if comment_href:
                                    if comment_href.startswith("/"):
                                        comment_url = (
                                            "https://news.ycombinator.com"
                                            + comment_href
                                        )
                                    elif comment_href.startswith("http"):
                                        comment_url = comment_href
                                    else:
                                        # Handle relative URLs like "item?id=12345"
                                        comment_url = (
                                            "https://news.ycombinator.com/"
                                            + comment_href
                                        )

                    article = Article(
                        title=title, url=href, comment_url=comment_url
                    )
                    articles.append(article)

                # Move to next page if we need more articles
                page += 1

            self.logger.info(
                f"Successfully discovered {len(articles)} articles for {self.config.name}"
            )
            return articles[:count]

        except Exception as e:
            raise ArticleDiscoveryError(
                f"Failed to discover articles: {e}", self.config.name
            )

    def fetch_article_content(
        self, article: Article, output_dir: str, progress_callback=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Fetch article content from Hacker News.
        Optimized to prevent conversion hangs.
        """
        try:
            self.logger.debug(f"Fetching content for article: {article.title}")

            # Skip HN discussion pages - only process external articles
            if article.url.startswith("https://news.ycombinator.com/item?id="):
                self.logger.debug(f"Skipping HN discussion page: {article.title}")
                return False, None

            # Use the standard NewsSourceArticleFetcher for content processing
            fetcher_config = {
                "name": self.config.display_name,  # Required by NewsSourceArticleFetcher
                "content_selectors": [
                    "article",
                    ".post-content",
                    ".article-content",
                    ".content",
                    "main",
                    ".main-content",
                    ".entry-content",
                    ".blog-post",
                    ".article-body",
                    "body",
                ],
                "skip_patterns": [
                    "/news",
                    "/newest",
                    "/threads",
                    "/front",
                    "/user?id=",
                    "hide?id=",
                    "news.ycombinator.com/news",
                    "news.ycombinator.com/newest",
                    "news.ycombinator.com/item",
                ],
            }

            fetcher = NewsSourceArticleFetcher(fetcher_config, self.session)

            # Set timeout to prevent hangs during conversion
            original_timeout = self.session.timeout if hasattr(self.session, 'timeout') else None
            self.session.timeout = 15  # 15 second timeout to prevent hangs

            try:
                # Fetch article content first (using proper method that includes PDF detection)
                success, title, folder_path = fetcher.fetch_article_content(
                    title=article.title,
                    url=article.url,
                    index=0,
                    base_folder=output_dir,
                    progress_callback=progress_callback,
                )
            finally:
                # Restore original timeout
                if original_timeout is not None:
                    self.session.timeout = original_timeout
                elif hasattr(self.session, 'timeout'):
                    delattr(self.session, 'timeout')

            # Fetch comments separately if article fetch was successful
            if success and article.comment_url and folder_path:
                try:
                    self.fetch_comments(
                        comment_url=article.comment_url,
                        article_title=title or article.title,
                        article_folder_path=folder_path,
                    )
                except Exception as e:
                    self.logger.debug(
                        f"Failed to fetch comments for {article.title}: {e}"
                    )
                    # Don't fail the entire article fetch if comments fail

            if success:
                return True, folder_path
            else:
                return False, None

        except Exception as e:
            raise ContentFetchError(
                f"Failed to fetch content for {article.url}: {e}",
                self.config.name,
            )

    def _validate_custom_config(self) -> List[str]:
        """
        Validate Hacker News-specific configuration.
        """
        errors = []

        # TODO: Add source-specific validation logic

        return errors

    def _should_skip_custom(self, url: str, title: str = "") -> bool:
        """
        Custom skip logic for Hacker News.
        """
        # TODO: Add source-specific skip logic
        return False

    def fetch_comments(
        self, comment_url: str, article_title: str, article_folder_path: str, html_mode: bool = False
    ) -> bool:
        """
        Fetch and save Hacker News comments using optimized streamlined processor.

        Args:
            comment_url: URL to the HN comments page
            article_title: Title of the article for logging
            article_folder_path: Specific folder path for this article
            html_mode: If True, generate HTML directly; if False, generate markdown

        Returns:
            bool: True if comments were successfully saved, False otherwise
        """
        # Validate inputs
        if not comment_url:
            self.logger.debug(f"No comment URL available for: {article_title}")
            return False

        if not article_folder_path or not os.path.exists(article_folder_path):
            self.logger.error(
                f"Invalid article folder path: {article_folder_path}"
            )
            return False

        try:
            # Network request with error handling
            self.logger.debug(f"Fetching comments from: {comment_url}")

            # Add cache-busting headers when in update mode to ensure fresh comments
            headers = {}
            if get_global_update_mode():
                headers.update({
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                })
                self.logger.debug("Using cache-busting headers for comment update")

            response = self.session.get(
                comment_url, timeout=self.config.timeout, headers=headers
            )
            response.raise_for_status()

        except requests.exceptions.Timeout:
            self.logger.warning(
                f"Timeout fetching comments for {article_title} - skipping comments"
            )
            return False
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                self.logger.warning(
                    f"Access forbidden for comments {comment_url} - anti-bot protection detected"
                )
            elif e.response.status_code == 404:
                self.logger.warning(
                    f"Comments not found for {article_title} - may have been deleted"
                )
            else:
                self.logger.warning(
                    f"HTTP error {e.response.status_code} fetching comments for {article_title}"
                )
            return False
        except requests.exceptions.ConnectionError:
            self.logger.warning(
                f"Connection error fetching comments for {article_title} - network may be unavailable"
            )
            return False
        except requests.exceptions.RequestException as e:
            self.logger.warning(
                f"Request error fetching comments for {article_title}: {e}"
            )
            return False

        try:
            # Use optimized streamlined comment processor
            from core.streamlined_comment_processor import create_optimized_comment_processor

            # Ensure UTF-8 encoding
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, "html.parser")

            # Create optimized processor with unlimited comments
            processor = create_optimized_comment_processor(max_comments=None)

            # Generate content based on mode (HTML or Markdown)
            if html_mode:
                # Generate HTML directly - skip markdown conversion
                content = processor.process_hacker_news_comments_html_optimized(
                    soup, article_title, comment_url
                )
                filename = os.path.join(article_folder_path, "html", "comments.html")
                # Ensure html directory exists
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            else:
                # Generate markdown (default behavior)
                content = processor.process_hacker_news_comments_optimized(
                    soup, article_title, comment_url
                )
                filename = os.path.join(article_folder_path, "comments.md")

            # Get metrics for logging
            metrics = processor.get_performance_metrics()
            self.logger.info(
                f"Processed {metrics['comments_processed']} comments with {metrics['links_processed']} links for: {article_title}"
            )

            # File I/O operations with error handling
            try:
                # In update mode, always overwrite. In normal mode, always write (new files).
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)

                format_type = "HTML" if html_mode else "markdown"
                self.logger.info(
                    f"Successfully saved {metrics['comments_processed']} comments as {format_type} for: {article_title}"
                )
                return True

            except (PermissionError, OSError, UnicodeEncodeError) as file_error:
                self.logger.error(
                    f"File I/O error writing comments for {article_title}: {file_error}"
                )
                return False

        except Exception as processing_error:
            self.logger.error(
                f"Comment processing error for {comment_url}: {processing_error}"
            )
            return False
