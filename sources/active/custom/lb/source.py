#!/usr/bin/env python3
"""
Lobsters source implementation for the new source system.
Enhanced with comment functionality from V1 implementation.
Uses RSS for article discovery to respect robots.txt.

Implements retry-and-skip logic for network resilience.
"""

import os
import time
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from core.article_fetcher import get_global_update_mode
from core.news_source_adapter import NewsSourceArticleFetcher
from core.network_resilience import (
    get_retry_executor,
    URLFallbackExecutor,
)
from core.source_system.base_source import (
    Article,
    ArticleDiscoveryError,
    BaseSource,
    ContentFetchError,
)


class LbSource(BaseSource):
    """
    Lobsters source implementation with comment support.
    """

    @property
    def source_type(self) -> str:
        return "custom"

    def discover_articles(self, count: int) -> List[Article]:
        """
        Discover articles from Lobsters RSS feed or HTML.
        Supports pagination for fetching >25 articles.

        Tries multiple URLs in order. Raises exception on failure
        so the main retry-skip logic can handle it.
        """
        # First try RSS with pagination
        try:
            articles = self._discover_with_rss_pagination(count)
            if articles and len(articles) >= min(count, 25):
                return articles[:count]
        except Exception as e:
            self.logger.debug(f"RSS pagination failed, trying HTML fallback: {e}")

        # Fallback to HTML pagination
        try:
            articles = self._discover_with_html_pagination(count)
            if articles:
                return articles[:count]
        except Exception as e:
            self.logger.debug(f"HTML pagination failed: {e}")

        # All methods failed - raise exception for main retry logic
        raise ArticleDiscoveryError(
            f"Failed to discover articles from all methods",
            source_name=self.config.name
        )

    def _discover_with_rss_pagination(self, count: int) -> List[Article]:
        """
        Discover articles using RSS with pagination support.
        """
        articles = []
        page = 1
        max_pages = 10

        # Enhanced headers to avoid blocking
        headers = {
            'User-Agent': 'Capcat/2.0 (Personal news archiver)',
            'Accept': 'application/rss+xml, application/xml, text/xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

        while len(articles) < count and page <= max_pages:
            # Lobsters RSS pagination
            if page == 1:
                url = "https://lobste.rs/newest.rss"
            else:
                url = f"https://lobste.rs/newest.rss?page={page}"
                self.logger.debug(f"Fetching RSS page {page} from {url}")

            # Rate limiting
            if page > 1:
                time.sleep(2.0)

            try:
                response = self.session.get(
                    url,
                    timeout=self.config.timeout,
                    headers=headers
                )

                if response.status_code in [500, 503, 429, 403]:
                    break

                response.raise_for_status()

                if not response.content or len(response.content) < 10:
                    break

                page_articles = self._parse_rss_content(response.content, count - len(articles))

                if not page_articles:
                    # No more articles available
                    break

                articles.extend(page_articles)
                page += 1

            except Exception as e:
                self.logger.debug(f"Error fetching RSS page {page}: {e}")
                break

        if articles:
            self.logger.info(
                f"Successfully discovered {len(articles)} articles via RSS pagination"
            )

        return articles

    def _discover_with_html_pagination(self, count: int) -> List[Article]:
        """
        Discover articles using HTML pagination as fallback.
        """
        articles = []
        page = 1
        max_pages = 10

        headers = {
            'User-Agent': 'Capcat/2.0 (Personal news archiver)',
            'Accept': 'text/html',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        while len(articles) < count and page <= max_pages:
            # Lobsters HTML pagination
            if page == 1:
                url = "https://lobste.rs/newest"
            else:
                url = f"https://lobste.rs/page/{page}"
                self.logger.debug(f"Fetching HTML page {page} from {url}")

            # Rate limiting
            if page > 1:
                time.sleep(2.0)

            try:
                response = self.session.get(
                    url,
                    timeout=self.config.timeout,
                    headers=headers
                )

                if response.status_code in [500, 503, 429, 403]:
                    break

                response.raise_for_status()

                if not response.content or len(response.content) < 10:
                    break

                page_articles = self._parse_html_fallback(response.content, count - len(articles))

                if not page_articles:
                    # No more articles available
                    break

                articles.extend(page_articles)
                page += 1

            except Exception as e:
                self.logger.debug(f"Error fetching HTML page {page}: {e}")
                break

        if articles:
            self.logger.info(
                f"Successfully discovered {len(articles)} articles via HTML pagination"
            )

        return articles

    def _parse_rss_content(self, content: bytes, count: int) -> List[Article]:
        """
        Parse RSS XML content and extract articles.

        Args:
            content: Raw RSS XML content
            count: Maximum number of articles to return

        Returns:
            List of Article objects

        Raises:
            ET.ParseError: If XML parsing fails
        """
        try:
            root = ET.fromstring(content)
            articles = []

            # Find all item elements in the RSS feed
            for item in root.findall(".//item"):
                if len(articles) >= count:
                    break

                try:
                    # Extract title
                    title_elem = item.find("title")
                    title = (
                        title_elem.text
                        if title_elem is not None and title_elem.text
                        else "Untitled Article"
                    )

                    # Extract URL (article link)
                    link_elem = item.find("link")
                    if link_elem is None or not link_elem.text:
                        self.logger.debug(f"Skipping RSS item with no link: {title}")
                        continue
                    url = link_elem.text.strip()

                    # Validate URL
                    if not url.startswith('http'):
                        self.logger.debug(f"Skipping RSS item with invalid URL: {url}")
                        continue

                    # Extract comment URL
                    comments_elem = item.find("comments")
                    comment_url = (
                        comments_elem.text.strip()
                        if comments_elem is not None and comments_elem.text
                        else None
                    )

                    article = Article(
                        title=title, url=url, comment_url=comment_url
                    )
                    articles.append(article)

                except Exception as e:
                    self.logger.debug(f"Error parsing RSS item: {e}")
                    continue

            return articles

        except ET.ParseError as e:
            self.logger.error(f"XML parsing failed: {e}")
            raise

    def _parse_html_fallback(self, content: bytes, count: int) -> List[Article]:
        """
        Fallback HTML parsing when RSS feeds are unavailable.

        Args:
            content: Raw HTML content from /newest page
            count: Maximum number of articles to return

        Returns:
            List of Article objects
        """
        try:
            soup = BeautifulSoup(content, 'html.parser')
            articles = []

            # Look for article links on the newest page
            # Lobsters typically uses <a class="u-url"> for article links
            article_links = soup.find_all('a', class_='u-url')

            if not article_links:
                # Fallback: look for any links that might be articles
                article_links = soup.find_all('a', href=True)
                article_links = [link for link in article_links
                               if link.get('href', '').startswith('http') and
                               'lobste.rs' not in link.get('href', '')]

            for link in article_links:
                if len(articles) >= count:
                    break

                try:
                    url = link.get('href', '').strip()
                    title = link.get_text(strip=True) or link.get('title', '').strip()

                    if not url or not title or not url.startswith('http'):
                        continue

                    # Try to find the corresponding discussion link
                    comment_url = None
                    parent = link.find_parent()
                    if parent:
                        discussion_link = parent.find('a', href=True)
                        if discussion_link and 'lobste.rs/s/' in discussion_link.get('href', ''):
                            comment_url = discussion_link.get('href')
                            if not comment_url.startswith('http'):
                                comment_url = f"https://lobste.rs{comment_url}"

                    article = Article(
                        title=title,
                        url=url,
                        comment_url=comment_url
                    )
                    articles.append(article)

                except Exception as e:
                    self.logger.debug(f"Error parsing HTML article link: {e}")
                    continue

            return articles

        except Exception as e:
            self.logger.error(f"HTML parsing failed: {e}")
            raise

    def fetch_article_content(
        self, article: Article, output_dir: str, progress_callback=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Fetch article content from Lobsters with enhanced error handling.
        """
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                self.logger.debug(
                    f"Fetching content for article: {article.title} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

                # Use the standard NewsSourceArticleFetcher for content processing
                fetcher_config = {
                    "name": self.config.display_name,
                    "content_selectors": [
                        ".story_content",
                        ".comment_tree",
                        ".comments",
                        "article",
                        ".post-content",
                        "body",
                    ],
                    "skip_patterns": [
                        "/u/",
                        "/login",
                        "/signup",
                        "/about",
                        "/privacy",
                        "/newest",
                        "/threads",
                        "lobste.rs/u/",
                        "lobste.rs/login",
                    ],
                }

                fetcher = NewsSourceArticleFetcher(fetcher_config, self.session)

                # Fetch article content first
                success, title, folder_path = fetcher.fetch_article_content(
                    title=article.title,
                    url=article.url,
                    index=0,
                    base_folder=output_dir,
                    progress_callback=progress_callback,
                )

                # Fetch comments separately if article fetch was successful
                if success and article.comment_url and folder_path:
                    try:
                        self.fetch_comments(
                            comment_url=article.comment_url,
                            article_title=title or article.title,
                            article_folder_path=folder_path,
                        )
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to fetch comments for {article.title}: {e}"
                        )
                        # Don't fail the entire article fetch if comments fail

                if success:
                    self.logger.info(f"Successfully fetched content for: {article.title}")
                    return True, folder_path
                else:
                    self.logger.warning(f"Content fetch failed for: {article.title}")
                    return False, None

            except requests.exceptions.Timeout as e:
                self.logger.warning(
                    f"Timeout fetching {article.url} (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    raise ContentFetchError(
                        f"Timeout fetching content after {max_retries} attempts: {e}",
                        self.config.name,
                    )

            except requests.exceptions.ConnectionError as e:
                self.logger.warning(
                    f"Connection error fetching {article.url} (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    raise ContentFetchError(
                        f"Connection error after {max_retries} attempts: {e}",
                        self.config.name,
                    )

            except Exception as e:
                self.logger.error(f"Unexpected error fetching {article.url}: {e}")
                raise ContentFetchError(
                    f"Failed to fetch content for {article.url}: {e}",
                    self.config.name,
                )

        # Should not reach here, but just in case
        return False, None

    def _validate_custom_config(self) -> List[str]:
        """
        Validate Lobsters-specific configuration.
        """
        errors = []

        # TODO: Add source-specific validation logic

        return errors

    def _should_skip_custom(self, url: str, title: str = "") -> bool:
        """
        Custom skip logic for Lobsters.
        """
        # Skip Lobsters internal pages
        skip_patterns = [
            'lobste.rs/u/',
            'lobste.rs/login',
            'lobste.rs/signup',
            'lobste.rs/about',
            'lobste.rs/privacy',
            'lobste.rs/newest',
            'lobste.rs/threads',
        ]

        for pattern in skip_patterns:
            if pattern in url.lower():
                self.logger.debug(f"Skipping internal Lobsters page: {url}")
                return True

        return False

    def check_service_health(self) -> dict:
        """
        Check the health status of Lobsters RSS and HTML endpoints.

        Returns:
            dict: Health status information including endpoint availability,
                  response times, and error conditions.
        """
        health_status = {
            "service_name": "Lobsters",
            "timestamp": time.time(),
            "endpoints": {},
            "overall_status": "unknown",
            "recommendations": []
        }

        endpoints_to_check = [
            ("RSS Feed", "https://lobste.rs/newest.rss"),
            ("Alternative RSS", "https://lobste.rs/rss"),
            ("HTML Fallback", "https://lobste.rs/newest"),
            ("Main Site", "https://lobste.rs/")
        ]

        available_endpoints = 0
        total_endpoints = len(endpoints_to_check)

        for name, url in endpoints_to_check:
            endpoint_status = {
                "url": url,
                "available": False,
                "status_code": None,
                "response_time": None,
                "error": None
            }

            try:
                start_time = time.time()
                headers = {
                    'User-Agent': 'Capcat/2.0 (Personal news archiver)',
                    'Accept': 'application/rss+xml, application/xml, text/xml, text/html',
                }

                response = self.session.get(
                    url,
                    timeout=10,
                    headers=headers
                )

                endpoint_status["status_code"] = response.status_code
                endpoint_status["response_time"] = round((time.time() - start_time) * 1000, 2)

                if response.status_code == 200:
                    endpoint_status["available"] = True
                    available_endpoints += 1

                    # Additional validation for RSS endpoints
                    if url.endswith('.rss') or url.endswith('/rss'):
                        try:
                            ET.fromstring(response.content)
                            endpoint_status["content_valid"] = True
                        except ET.ParseError:
                            endpoint_status["content_valid"] = False
                            endpoint_status["error"] = "Invalid XML content"

                elif response.status_code == 500:
                    endpoint_status["error"] = "Server error (500)"
                elif response.status_code == 503:
                    endpoint_status["error"] = "Service unavailable (503)"
                elif response.status_code == 429:
                    endpoint_status["error"] = "Rate limited (429)"
                elif response.status_code == 403:
                    endpoint_status["error"] = "Forbidden (403)"
                else:
                    endpoint_status["error"] = f"HTTP {response.status_code}"

            except requests.exceptions.Timeout:
                endpoint_status["error"] = "Timeout"
            except requests.exceptions.ConnectionError:
                endpoint_status["error"] = "Connection error"
            except Exception as e:
                endpoint_status["error"] = f"Unexpected error: {str(e)}"

            health_status["endpoints"][name] = endpoint_status

        # Determine overall status
        if available_endpoints == 0:
            health_status["overall_status"] = "critical"
            health_status["recommendations"].append(
                "All endpoints are unavailable. Lobsters service may be down."
            )
        elif available_endpoints < total_endpoints / 2:
            health_status["overall_status"] = "degraded"
            health_status["recommendations"].append(
                "Some endpoints are unavailable. Service is partially functional."
            )
        else:
            health_status["overall_status"] = "healthy"

        # Add specific recommendations
        if not health_status["endpoints"].get("RSS Feed", {}).get("available", False):
            if health_status["endpoints"].get("HTML Fallback", {}).get("available", False):
                health_status["recommendations"].append(
                    "RSS feed is down but HTML fallback is available."
                )
            else:
                health_status["recommendations"].append(
                    "Both RSS and HTML endpoints are unavailable."
                )

        return health_status

    def fetch_comments(
        self, comment_url: str, article_title: str, article_folder_path: str, html_mode: bool = False
    ) -> bool:
        """
        Fetch and save Lobsters comments for an article.

        Args:
            comment_url: URL to the Lobsters comments page
            article_title: Title of the article for logging
            article_folder_path: Specific folder path for this article
            html_mode: If True, generate HTML directly; if False, generate markdown

        Returns:
            bool: True if comments were successfully saved, False otherwise
        """
        try:
            if not comment_url:
                self.logger.debug(
                    f"No comment URL available for: {article_title}"
                )
                return False

            # Add cache-busting headers when in update mode to ensure fresh comments
            headers = {}
            if get_global_update_mode():
                headers.update({
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                })
                self.logger.debug("Using cache-busting headers for comment update")

            # Rate limiting and retry logic for 429 errors
            max_retries = self.config.custom_config.get('max_retries', 3) if self.config.custom_config else 3
            base_delay = self.config.custom_config.get('base_delay', 2.0) if self.config.custom_config else 2.0
            response = None

            for attempt in range(max_retries + 1):
                try:
                    # Apply rate limiting before request
                    time.sleep(self.config.rate_limit)

                    response = self.session.get(
                        comment_url, timeout=self.config.timeout, headers=headers
                    )
                    response.raise_for_status()

                    if attempt > 0:
                        self.logger.info(
                            f"Successfully fetched comments for {article_title} after {attempt} retry attempt(s)"
                        )
                    break  # Success, exit retry loop

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429 and attempt < max_retries:
                        # Exponential backoff: 2s, 4s, 8s
                        retry_delay = base_delay * (2 ** attempt)
                        self.logger.warning(
                            f"Rate limit (429) hit for {article_title}, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(retry_delay)
                        continue
                    elif e.response.status_code == 429:
                        self.logger.error(
                            f"Rate limit (429) exceeded for {article_title} after {max_retries} retry attempts"
                        )
                        raise
                    else:
                        raise  # Re-raise if not 429

            if response is None:
                self.logger.error(f"Failed to fetch comments for {article_title}: No response received")
                return False

            # Use optimized streamlined comment processor
            from core.streamlined_comment_processor import create_optimized_comment_processor

            soup = BeautifulSoup(response.text, "html.parser")

            # Create optimized processor with unlimited comments
            processor = create_optimized_comment_processor(max_comments=None)

            # Generate content based on mode (HTML or Markdown)
            if html_mode:
                # Generate HTML directly - skip markdown conversion
                content = processor.process_lobsters_comments_html_optimized(
                    soup, article_title, comment_url
                )
                filename = os.path.join(article_folder_path, "html", "comments.html")
                # Ensure html directory exists
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            else:
                # Generate markdown (default behavior)
                content = processor.process_lobsters_comments_optimized(
                    soup, article_title, comment_url
                )
                filename = os.path.join(article_folder_path, "comments.md")

            # Get metrics for logging
            metrics = processor.get_performance_metrics()
            self.logger.info(
                f"Processed {metrics['comments_processed']} comments with {metrics['links_processed']} links for: {article_title}"
            )

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            format_type = "HTML" if html_mode else "markdown"
            self.logger.info(
                f"Successfully saved {metrics['comments_processed']} comments as {format_type} for: {article_title}"
            )
            return True


        except Exception as e:
            self.logger.error(
                f"Failed to fetch comments for {article_title}: {str(e)}"
            )
            return False
