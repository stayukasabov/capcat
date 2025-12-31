#!/usr/bin/env python3
"""
Base NewsSourceAdapter class to eliminate code duplication across source modules.
Provides a configuration-driven approach for news source scraping.
"""

import json
import os
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from core.article_fetcher import ArticleFetcher
from core.config import get_config
from core.downloader import (
    download_file,
    is_audio_url,
    is_document_url,
    is_image_url,
    is_video_url,
)
from core.formatter import html_to_markdown
from core.logging_config import get_logger
from core.session_pool import get_global_session
from core.unified_media_processor import UnifiedMediaProcessor
from core.utils import sanitize_filename


class NewsSourceAdapter(ABC):
    """
    Base class for news source adapters.
    Eliminates code duplication by providing common functionality.
    """

    def __init__(self, source_config: Dict[str, Any]):
        """Initialize with source-specific configuration."""
        self.config = get_config()
        self.source_config = source_config
        self.logger = get_logger(f"{__name__}.{source_config['name']}")

        # Use global session pool for optimal resource management
        self.session = get_global_session(
            source_config["name"].lower().replace(" ", "_")
        )

        # Create article fetcher instance
        self.article_fetcher = self._create_article_fetcher()

    def _create_article_fetcher(self) -> "NewsSourceArticleFetcher":
        """Create source-specific article fetcher."""
        return NewsSourceArticleFetcher(self.source_config, self.session)

    def scrape_articles(
        self, count: int = 30
    ) -> List[Tuple[str, str, Optional[str]]]:
        """
        Scrape articles from the news source with comprehensive error handling.

        Args:
            count: Number of articles to scrape

        Returns:
            List of tuples containing (title, url, comment_url) for each article

        Error Handling:
            - Network timeouts and connection errors
            - HTTP status errors (403, 404, 500, etc.)
            - HTML parsing errors
            - Graceful degradation for missing elements
        """
        self.logger.info(
            f"Scraping top {count} articles from {self.source_config['name']}..."
        )

        # Validate inputs
        if count <= 0:
            self.logger.warning(
                f"Invalid count {count} requested - using default of 10"
            )
            count = 10
        elif count > 100:
            self.logger.warning(
                f"Large count {count} requested - limiting to 100 for performance"
            )
            count = 100

        try:
            # Network request with specific error handling
            self.logger.debug(
                f"Fetching from: {self.source_config['base_url']}"
            )
            response = self.session.get(
                self.source_config["base_url"],
                timeout=self.config.network.connect_timeout,
            )
            response.raise_for_status()

            # Ensure UTF-8 encoding to prevent Unicode corruption
            response.encoding = 'utf-8'

        except requests.exceptions.Timeout:
            self.logger.warning(
                f"Timeout fetching {self.source_config['name']} homepage - site may be slow"
            )
            return []
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                self.logger.warning(
                    f"Access forbidden to {self.source_config['name']} - anti-bot protection detected"
                )
            elif e.response.status_code == 404:
                self.logger.error(
                    f"{self.source_config['name']} homepage not found - URL may have changed"
                )
            elif e.response.status_code >= 500:
                self.logger.warning(
                    f"{self.source_config['name']} server error ({e.response.status_code}) - temporary issue"
                )
            else:
                self.logger.warning(
                    f"HTTP error {e.response.status_code} accessing {self.source_config['name']}"
                )
            return []
        except requests.exceptions.ConnectionError:
            self.logger.warning(
                f"Connection error accessing {self.source_config['name']} - network may be unavailable"
            )
            return []
        except requests.exceptions.RequestException as e:
            self.logger.warning(
                f"Request error accessing {self.source_config['name']}: {e}"
            )
            return []

        try:
            # HTML parsing with error handling
            soup = BeautifulSoup(response.text, "html.parser")
            articles = []
            processed_urls = set()

            # Validate that we have selectors configured
            if not self.source_config.get("article_selectors"):
                self.logger.error(
                    f"No article selectors configured for {self.source_config['name']}"
                )
                return []

            # Use configured selectors to find articles
            for selector in self.source_config["article_selectors"]:
                try:
                    elements = soup.select(selector)
                    self.logger.debug(
                        f"Found {len(elements)} elements with selector: {selector}"
                    )

                    for element in elements:
                        if len(articles) >= count:
                            break

                        article = self._extract_article_from_element(
                            element, processed_urls
                        )
                        if article:
                            articles.append(article)
                            processed_urls.add(
                                article[1]
                            )  # Add URL to processed set

                    if len(articles) >= count:
                        break

                except Exception as selector_error:
                    self.logger.debug(
                        f"Selector '{selector}' failed: {selector_error}"
                    )
                    continue

            if not articles:
                self.logger.warning(
                    f"No articles found on {self.source_config['name']} - selectors may need updating"
                )
            else:
                self.logger.info(
                    f"Successfully extracted {len(articles)} articles from {self.source_config['name']}"
                )

            return articles[:count]

        except Exception as parsing_error:
            self.logger.error(
                f"HTML parsing error for {self.source_config['name']}: {parsing_error}"
            )
            return []

    def _extract_article_from_element(
        self, element, processed_urls: set
    ) -> Optional[Tuple[str, str, Optional[str]]]:
        """Extract article information from HTML element."""
        try:
            # Find the link element
            link_elem = element if element.name == "a" else element.find("a")
            if not link_elem or not link_elem.get("href"):
                return None

            url = urljoin(
                self.source_config["base_url"], link_elem.get("href")
            )

            # Skip if already processed
            if url in processed_urls:
                return None

            # Skip unwanted URLs
            if self._should_skip_url(url):
                return None

            # Extract title
            title = self._extract_title(element, link_elem)
            if not title or len(title.strip()) < 10:
                return None

            # Extract comment URL if the source has comments
            comment_url = None
            if self.source_config.get("has_comments", False):
                comment_url = self._extract_comment_url(element)

            self.logger.debug(
                f"Found article: {title[:50]}... (comments: {'yes' if comment_url else 'no'})"
            )
            return (title, url, comment_url)

        except Exception as e:
            self.logger.debug(f"Error extracting article from element: {e}")
            return None

    def _extract_title(self, element, link_elem) -> str:
        """Extract article title from element."""
        # Try different methods to get the title
        title_methods = [
            lambda: link_elem.get_text(strip=True),
            lambda: element.get_text(strip=True),
            lambda: link_elem.get("title", "").strip(),
            lambda: element.get("aria-label", "").strip(),
        ]

        for method in title_methods:
            try:
                title = method()
                if title and len(title.strip()) > 5:
                    return title.strip()
            except:
                continue

        return "Untitled Article"

    def _extract_comment_url(self, element) -> Optional[str]:
        """Extract comment URL from the article element for sources with comments."""
        try:
            # Get the configured comments selector
            comments_selector = self.source_config.get("comments_selector")
            if not comments_selector:
                return None

            # For HN, we need to look for the subline that contains this article
            # The element is the titleline, so we need to find the corresponding subline
            if self.source_config["name"] == "Hacker News":
                # Find the parent container that has both titleline and subline
                article_row = element.find_parent("tr")
                if article_row:
                    # Look for the next row which should contain the subline
                    next_row = article_row.find_next_sibling("tr")
                    if next_row and next_row.select_one(".subline"):
                        subline = next_row.select_one(".subline")
                        comment_links = subline.select('a[href*="item?id="]')

                        # Find the comment link (usually has "comment" text or is a timestamp)
                        for link in comment_links:
                            href = link.get("href", "")
                            text = link.get_text().lower()

                            # Skip user links
                            if "user?id=" in href:
                                continue

                            # Look for comment indicators or timestamps
                            if (
                                "comment" in text
                                or ("hour" in text and "ago" in text)
                                or ("minute" in text and "ago" in text)
                                or ("day" in text and "ago" in text)
                            ):
                                return urljoin(
                                    self.source_config["base_url"], href
                                )

            # For Lobsters and other sources, use the general approach
            elif self.source_config["name"] == "Lobsters":
                # Find the story container that contains this article link
                story_container = element.find_parent(
                    ".story"
                ) or element.find_parent("li")
                if story_container:
                    comment_links = story_container.select('a[href*="/s/"]')
                    for link in comment_links:
                        href = link.get("href", "")
                        text = link.get_text().lower()

                        # Look for comment indicators
                        if "comment" in text or "discuss" in text:
                            return urljoin(
                                self.source_config["base_url"], href
                            )

            # Fallback: use the configured selector to search around the element
            parent_container = element.find_parent(
                ["tr", "div", "li", "article"]
            )
            if parent_container:
                comment_element = parent_container.select_one(
                    comments_selector
                )
                if comment_element:
                    href = comment_element.get("href", "")
                    if href:
                        return urljoin(self.source_config["base_url"], href)

            return None

        except Exception as e:
            self.logger.debug(f"Error extracting comment URL: {e}")
            return None

    def _should_skip_url(self, url: str) -> bool:
        """Check if URL should be skipped based on configuration."""
        # Skip patterns from configuration
        for pattern in self.source_config.get("skip_patterns", []):
            if pattern in url:
                return True

        # Skip only clearly non-content URLs (keep binary files for proper handling by article fetcher)
        skip_extensions = [".zip", ".tar", ".gz", ".exe", ".dmg", ".iso"]
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return True

        return False

    def fetch_article_content(
        self,
        title: str,
        url: str,
        index: int,
        base_folder: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Tuple[bool, str, str]:
        """Fetch article content using the article fetcher."""
        return self.article_fetcher.fetch_article_content(
            title, url, index, base_folder, progress_callback
        )

    def process_article(
        self,
        title: str,
        url: str,
        index: int,
        base_folder: str,
        comment_url: str = None,
        download_files: bool = False,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bool:
        """
        Process a single article - unified interface for the optimized system.

        Args:
            title: Article title
            url: Article URL
            index: Article index number
            base_folder: Base directory to save article
            comment_url: Optional comment URL for sources with comments
            download_files: Whether to download media files
            progress_callback: Optional callback for progress updates (progress, stage_description)

        Returns:
            bool: True if article was processed successfully
        """
        try:
            # Set the download_files flag on the article fetcher before processing
            self.article_fetcher.set_download_files(download_files)

            success, article_path, folder_path = (
                self.article_fetcher.fetch_article_content(
                    title,
                    url,
                    index,
                    base_folder,
                    progress_callback,
                )
            )

            # Process comments if available and article was successful
            if (
                success
                and comment_url
                and self.source_config.get("has_comments", False)
            ):
                self._process_comments(
                    comment_url, title, index, base_folder, folder_path
                )

            # Note: Media downloading is handled within fetch_article_content based on global config
            # The download_files parameter is available for future enhancement

            return success

        except Exception as e:
            self.logger.error(f"Failed to process article '{title}': {e}")
            return False

    def _process_comments(
        self,
        comment_url: str,
        title: str,
        index: int,
        base_folder: str,
        article_folder_path: str,
    ) -> bool:
        """
        Process comments for an article by delegating to source-specific implementation.

        Args:
            comment_url: URL to fetch comments from
            title: Article title
            index: Article index number
            base_folder: Base directory
            article_folder_path: Path to the article folder

        Returns:
            bool: True if comments were processed successfully
        """
        try:
            # Get source name from the configurabe source instance
            source_name = getattr(self, "source_name", None)

            # Import and call source-specific comment function
            if source_name == "hn":
                from sources.hn import fetch_comments

                return fetch_comments(
                    comment_url, title, index, base_folder, article_folder_path
                )
            elif source_name == "lb":
                from sources.lb import fetch_comments

                return fetch_comments(
                    comment_url, title, index, base_folder, article_folder_path
                )
            else:
                # For sources without specific comment implementations, create placeholder
                self._create_comment_placeholder(title, article_folder_path)
                return True

        except Exception as e:
            self.logger.debug(f"Failed to process comments for '{title}': {e}")
            return False

    def _create_comment_placeholder(
        self, title: str, article_folder_path: str
    ) -> None:
        """Create a placeholder comments.md file for sources without comment support."""
        import os

        comment_content = f"# Comments for: {title}\n\n"
        comment_content += f"Comments are not available for this source.\n\n"

        filename = os.path.join(article_folder_path, "comments.md")

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(comment_content)
        except Exception as e:
            self.logger.debug(f"Failed to create comment placeholder: {e}")


class NewsSourceArticleFetcher(ArticleFetcher):
    """
    Configurable article fetcher that works with any news source.
    """

    def __init__(
        self, source_config: Dict[str, Any], session: requests.Session
    ):
        super().__init__(session)
        self.source_config = source_config
        self.logger = get_logger(
            f"{__name__.replace('core.', '')}.{source_config['name']}"
        )

    def should_skip_url(self, url: str, title: str) -> bool:
        """Skip URLs based on source configuration."""
        # Skip patterns from configuration
        for pattern in self.source_config.get("skip_patterns", []):
            if pattern in url:
                return True

        # Skip only clearly non-content URLs (keep binary files for proper handling by article fetcher)
        skip_extensions = [".zip", ".tar", ".gz", ".exe", ".dmg", ".iso"]
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return True

        return False

    def _fetch_web_content(
        self,
        title: str,
        url: str,
        index: int,
        base_folder: str,
        progress_callback=None,
    ):
        """Override to extract content using configured selectors."""
        from .config import get_config

        config = get_config()

        # Report initial progress
        if progress_callback:
            progress_callback(0.0, "fetching")

        try:
            # Use source-specific timeout instead of global read_timeout
            source_timeout = self.source_config.get(
                "timeout", config.network.read_timeout
            )
            response = self.session.get(url, timeout=source_timeout)
            response.raise_for_status()

            # Ensure UTF-8 encoding to prevent Unicode corruption
            response.encoding = 'utf-8'
        except requests.exceptions.Timeout:
            self.logger.warning(f"Timeout fetching article content from {url}")
            return False, None, None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                self.logger.warning(
                    f"Access forbidden for article {url} - anti-bot protection detected"
                )
            elif e.response.status_code == 404:
                self.logger.warning(
                    f"Article not found at {url} - may have been deleted"
                )
            elif e.response.status_code == 429:
                self.logger.warning(
                    f"Rate limited accessing {url} - try reducing request frequency"
                )
            elif e.response.status_code >= 500:
                self.logger.warning(
                    f"Server error ({e.response.status_code}) fetching {url} - temporary issue"
                )
            else:
                self.logger.warning(
                    f"HTTP error {e.response.status_code} fetching {url}"
                )
            return False, None, None
        except requests.exceptions.ConnectionError:
            self.logger.warning(
                f"Connection error fetching {url} - network may be unavailable"
            )
            return False, None, None
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Request error fetching {url}: {e}")
            return False, None, None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}")
            return False, None, None

        # Report parsing progress
        if progress_callback:
            progress_callback(0.2, "parsing")

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
            progress_callback(0.3, "cleaning")

        # Extract content using configured selectors
        content_html = None
        for selector in self.source_config.get("content_selectors", []):
            try:
                content_elements = soup.select(selector)
                if content_elements:
                    # Combine all found content elements
                    content_html = ""
                    for element in content_elements:
                        content_html += str(element)
                    break
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed: {e}")
                continue

        # Fallback to article body if no selectors worked
        if not content_html:
            self.logger.debug(
                f"No content found with configured selectors, using fallback"
            )
            article_body = (
                soup.find("article")
                or soup.find("main")
                or soup.find("div", class_="content")
            )
            if article_body:
                content_html = str(article_body)
            else:
                # Last resort: use the entire cleaned soup
                content_html = str(soup)

        # Get page title (prefer meta title, fallback to h1, then provided title)
        page_title = title  # Default to provided title

        # Try to get a better title from the page
        if soup.title and soup.title.string:
            page_title = soup.title.string.strip()
        elif soup.find("h1"):
            h1 = soup.find("h1")
            if h1 and h1.get_text().strip():
                page_title = h1.get_text().strip()

        # Create individual folder for this article
        safe_title = sanitize_filename(page_title)

        # Handle potential duplicate folder names by appending a counter
        article_folder_name = self._get_unique_folder_name(
            base_folder, safe_title
        )
        article_folder_path = os.path.join(base_folder, article_folder_name)

        try:
            os.makedirs(article_folder_path, exist_ok=True)
        except PermissionError:
            self.logger.error(
                f"Permission denied creating directory {article_folder_path} - check folder permissions"
            )
            return False, None, None
        except OSError as e:
            self.logger.error(
                f"OS error creating directory {article_folder_path}: {e}"
            )
            return False, None, None
        except Exception as e:
            self.logger.error(
                f"Unexpected error creating directory {article_folder_path}: {e}"
            )
            return False, None, None

        # MANDATORY: Create images folder for ALL articles (regardless of --media flag)
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
            # Continue processing - images folder creation failure shouldn't stop article processing

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
                f.write(content_html)
            self.logger.debug(f"Saved raw HTML to: {raw_html_path}")
        except Exception as e:
            self.logger.debug(f"Could not save raw HTML: {e}")

        # Report conversion progress
        if progress_callback:
            progress_callback(0.5, "converting")

        # Convert HTML to Markdown using only the extracted content
        try:
            markdown_content = html_to_markdown(content_html, url)
        except Exception as e:
            self.logger.debug(
                f"Failed to convert HTML to Markdown for {url}: {e}"
            )
            return False, None, None

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

        # Remove "Read the full article:" links that appear in scraped content
        import re

        markdown_content = re.sub(
            r"\*\*Read the full article:\*\*\s*\[.*?\]\(.*?\)",
            "",
            markdown_content,
            flags=re.IGNORECASE,
        )
        markdown_content = re.sub(
            r"Read the full article:\s*\[.*?\]\(.*?\)",
            "",
            markdown_content,
            flags=re.IGNORECASE,
        )
        # Clean up any extra whitespace left behind
        markdown_content = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown_content)

        # Save preliminary content immediately (before media processing)
        article_content = f"# {page_title}\n\n"
        article_content += f"**Source URL:** [{url}]({url})\n\n"
        article_content += "---\n\n"
        article_content += markdown_content

        # Save the preliminary article
        filename = os.path.join(article_folder_path, "article.md")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(article_content)
        except PermissionError:
            self.logger.error(
                f"Permission denied writing article file {filename} - check folder permissions"
            )
            return False, None, None
        except OSError as e:
            self.logger.error(f"OS error writing article file {filename}: {e}")
            return False, None, None
        except UnicodeEncodeError as e:
            self.logger.error(
                f"Unicode encoding error writing article {filename}: {e}"
            )
            return False, None, None
        except Exception as e:
            self.logger.error(
                f"Unexpected error writing article file {filename}: {e}"
            )
            return False, None, None

        # Process and download embedded media using unified system
        try:
            # Use source_id from config if available (config-driven sources)
            # Otherwise fall back to URL domain parsing (custom sources)
            source_name = self.source_config.get("source_id")

            if not source_name:
                # Fallback: Extract source name from URL domain for custom sources
                from urllib.parse import urlparse

                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
                if "futurism.com" in domain:
                    source_name = "futurism"
                elif "gizmodo.com" in domain:
                    source_name = "gizmodo"
                elif "spectrum.ieee.org" in domain:
                    source_name = "ieee"
                elif "news.ycombinator.com" in domain:
                    source_name = "hn"
                elif "lobste.rs" in domain:
                    source_name = "lb"
                elif "bbc.co.uk" in domain or "bbc.com" in domain:
                    # Differentiate between BBC News and BBC Sport
                    if "/sport" in url:
                        source_name = "bbcsport"
                    else:
                        source_name = "bbc"
                elif "cnn.com" in domain:
                    source_name = "cnn"
                elif "nature.com" in domain:
                    source_name = "nature"
                elif "blog.research.google" in domain or "googleblog.com" in domain:
                    source_name = "googleai"
                elif "news.mit.edu" in domain:
                    source_name = "mitnews"
                elif "scientificamerican.com" in domain:
                    source_name = "scientificamerican"
                elif "theguardian.com" in domain:
                    source_name = "guardian"
                elif "infoq.com" in domain:
                    source_name = "iq"
                else:
                    source_name = "unknown"

            # Use unified media processor for consistent results across all sources
            self.logger.debug(
                f"Processing media for {source_name} using unified system"
            )
            updated_markdown = UnifiedMediaProcessor.process_article_media(
                content=article_content,
                html_content=response.text,
                url=url,
                article_folder=article_folder_path,
                source_name=source_name,
                session=self.session,
            )

            # Save the final content with processed media
            # The unified media processor already updated the content with local image paths
            with open(filename, "w", encoding="utf-8") as f:
                f.write(updated_markdown)

        except Exception as e:
            self.logger.error(
                f"Could not process embedded media for {url}: {e}"
            )
            # Continue with preliminary content - core article is already saved

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
            progress_callback(1.0, "complete")

        # Clean up empty images folder if no images were downloaded
        self._cleanup_empty_images_folder(article_folder_path)

        self.logger.info(f"Saved article: {page_title}")
        return True, filename, article_folder_path

    def _cleanup_empty_images_folder(self, article_folder_path: str) -> None:
        """Remove images folder if it exists but is empty."""
        images_folder = os.path.join(article_folder_path, "images")
        try:
            if os.path.exists(images_folder) and os.path.isdir(images_folder):
                # Check if folder is empty (no files)
                if not os.listdir(images_folder):
                    os.rmdir(images_folder)
                    self.logger.debug(
                        f"Removed empty images folder: {images_folder}"
                    )
        except Exception as e:
            self.logger.debug(
                f"Could not remove empty images folder {images_folder}: {e}"
            )

    def _fallback_image_detection(
        self,
        full_page_html: str,
        existing_images: set,
        article_folder_path: str,
        base_url: str,
    ):
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
            from urllib.parse import urljoin

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
                from core.downloader import download_file

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
            f"Fallback system downloaded {len(downloaded_images)} additional images"
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
