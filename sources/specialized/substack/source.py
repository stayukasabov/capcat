#!/usr/bin/env python3
"""
Substack.com specialized source implementation with paywall detection.
Optimized for best formatting and guaranteed local image embedding.
"""

import os
import re
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from core.news_source_adapter import NewsSourceArticleFetcher
from core.source_system.base_source import (
    Article,
    ArticleDiscoveryError,
    BaseSource,
    ContentFetchError,
)
from core.unified_media_processor import UnifiedMediaProcessor


class SubstackSource(BaseSource):
    """
    Substack.com specialized source with paywall detection and optimal formatting.
    """

    @property
    def source_type(self) -> str:
        return "specialized"

    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        """Check if this source can handle the given URL."""
        substack_patterns = [
            r"\.substack\.com",
            r"substack\.com",
            r"/p/[^/]+",  # Substack post URLs
            r"/archive",  # Substack archive URLs
        ]
        return any(
            re.search(pattern, url, re.IGNORECASE)
            for pattern in substack_patterns
        )

    def discover_articles(self, count: int) -> List[Article]:
        """
        Substack discovery through RSS feeds when available.
        """
        try:
            # Extract substack domain from base_url
            if (
                not hasattr(self.config, "base_url")
                or not self.config.base_url
            ):
                raise ArticleDiscoveryError(
                    "No base URL configured for Substack discovery",
                    self.config.name,
                )

            # Try to get RSS feed
            rss_url = f"{self.config.base_url.rstrip('/')}/feed"

            self.logger.debug(f"Attempting RSS discovery from: {rss_url}")

            response = self.session.get(rss_url, timeout=self.config.timeout)
            response.raise_for_status()

            articles = []
            soup = BeautifulSoup(response.content, "xml")

            items = soup.find_all("item")[:count]

            for item in items:
                title_elem = item.find("title")
                link_elem = item.find("link")

                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get_text().strip()

                    article = Article(title=title, url=url)
                    articles.append(article)

            self.logger.info(
                f"Successfully discovered {len(articles)} Substack articles"
            )
            return articles

        except Exception as e:
            raise ArticleDiscoveryError(
                f"Failed to discover Substack articles: {e}", self.config.name
            )

    def fetch_article_content(
        self, article: Article, output_dir: str, progress_callback=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Fetch article content from Substack with paywall detection.
        """
        try:
            self.logger.debug(
                f"Fetching Substack content for: {article.title}"
            )

            # Check for paywall type
            paywall_type = self._is_paywalled(article.url)

            if paywall_type == "hard":
                # Hard paywall - only extract preview content
                return self._handle_paywalled_content(article, output_dir)
            elif paywall_type == "soft":
                # Soft paywall - fetch full content but note the overlay
                self.logger.info(
                    "Soft paywall detected - fetching full content"
                )
            # paywall_type == 'none' - free content, proceed normally

            # Use optimized Substack-specific configuration
            fetcher_config = {
                "name": self.config.display_name,
                "content_selectors": [
                    ".post-content",
                    ".available-content",
                    '[class*="post-content"]',
                    ".body",
                    "article",
                    ".prose",
                    "main",
                    ".single-post",
                ],
                "title_selectors": [
                    ".post-title",
                    "h1.post-title",
                    ".single-post-title",
                    "h1",
                    ".entry-title",
                ],
                "author_selectors": [
                    ".author-name",
                    ".byline-names",
                    ".author",
                    '[rel="author"]',
                    ".post-author",
                ],
                "date_selectors": [
                    ".post-date",
                    "time",
                    ".published-date",
                    ".post-meta time",
                ],
                "image_selectors": [
                    ".post-content img",
                    ".available-content img",
                    "figure img",
                    'img[src*="substack"]',
                    "img",
                ],
                "skip_patterns": [
                    "/subscribe",
                    "/account/login",
                    "/sign-in",
                    "paywall",
                    "subscriber-only",
                ],
                "paywall_indicators": [
                    "paywall",
                    "subscriber-only",
                    "paid-subscription",
                    "premium-content",
                    "subscribe-to-continue",
                    "login-to-continue",
                ],
            }

            fetcher = NewsSourceArticleFetcher(fetcher_config, self.session)

            # Use direct fetching to avoid URL transformation issues
            success, folder_path = self._fetch_substack_content_direct(
                article, output_dir
            )

            if success:
                # Post-process for Substack-specific optimizations
                self._optimize_substack_content(folder_path)
                return True, folder_path
            else:
                return False, None

        except Exception as e:
            raise ContentFetchError(
                f"Failed to fetch Substack content for {article.url}: {e}",
                self.config.name,
            )

    def _fetch_substack_content_direct(
        self, article: Article, output_dir: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Fetch Substack content directly without URL transformation.
        """
        try:
            response = self.session.get(article.url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_selectors = [
                ".post-title",
                "h1.post-title",
                ".single-post-title",
                "h1",
                ".entry-title",
            ]
            title = article.title
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break

            # Create article folder and images subfolder
            safe_title = re.sub(
                r'[<>:"/\\|?*]', "_", title or "Substack Article"
            )
            article_folder = os.path.join(output_dir, safe_title)
            os.makedirs(article_folder, exist_ok=True)

            images_folder = os.path.join(article_folder, "images")
            os.makedirs(images_folder, exist_ok=True)

            # Use unified media processor - following established architecture
            # No custom image downloading - use the unified system

            # Extract content
            content_selectors = [
                ".post-content",
                ".available-content",
                '[class*="post-content"]',
                ".body",
                "article",
                ".prose",
                "main",
            ]
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Convert to markdown first
                    from markdownify import markdownify

                    content = markdownify(
                        str(content_elem), heading_style="ATX"
                    )
                    break

            # Extract metadata
            author_selectors = [
                ".author-name",
                ".byline-names",
                ".author",
                '[rel="author"]',
                ".post-author",
            ]
            author = ""
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    break

            date_selectors = [
                ".post-date",
                "time",
                ".published-date",
                ".post-meta time",
            ]
            date = ""
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date = date_elem.get("datetime") or date_elem.get_text(
                        strip=True
                    )
                    break

            # Apply unified media processing - following established architecture
            processed_content = UnifiedMediaProcessor.process_article_media(
                content=content,
                html_content=response.text,
                url=article.url,
                article_folder=article_folder,
                source_name="substack",
                session=self.session,
                page_title=title
            )

            # Save article content with processed media
            article_file = os.path.join(article_folder, "article.md")
            with open(article_file, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                if author:
                    f.write(f"**Author:** {author}\n")
                if date:
                    f.write(f"**Date:** {date}\n")
                f.write(f"**Source:** [{title}]({article.url})\n\n")
                f.write("---\n\n")
                f.write(processed_content)

            self.logger.info(f"Successfully fetched Substack content: {title}")
            return True, article_folder

        except Exception as e:
            self.logger.error(
                f"Failed to fetch Substack content directly: {e}"
            )
            return False, None

    def _is_paywalled(self, url: str) -> str:
        """
        Check if the Substack article is behind a paywall.
        Returns: 'hard' for subscription required, 'soft' for overlay, 'none' for free
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Hard paywall indicators (content actually restricted)
            hard_paywall_indicators = [
                "subscriber-only",
                "paid subscribers only",
                "subscriber exclusive",
                "premium content",
                "subscribers only",
            ]

            # Soft paywall indicators (overlay but content available)
            soft_paywall_indicators = [
                "subscribe to continue",
                "login to continue",
                "upgrade to paid",
                "become a paid subscriber",
            ]

            content_lower = response.text.lower()

            # Check if full content is available first
            content_selectors = [
                ".post-content",
                ".available-content",
                "article",
                ".prose",
            ]
            full_content_available = False
            content_length = 0

            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text().strip()
                    content_length = len(content_text)
                    if (
                        content_length > 1000
                    ):  # Substantial content (increased threshold)
                        full_content_available = True
                        break

            self.logger.debug(
                f"Content length found: {content_length}, Full content available: {full_content_available}"
            )

            # If substantial content is available, check for hard paywall indicators more carefully
            if full_content_available:
                # Only treat as hard paywall if content is actually truncated with paywall message
                paywall_truncation_indicators = [
                    "this post is for paid subscribers",
                    "subscribe to read the full story",
                    "become a paid subscriber to unlock",
                    "upgrade to paid to continue reading",
                ]

                for indicator in paywall_truncation_indicators:
                    if indicator in content_lower:
                        self.logger.info(
                            f"Hard paywall detected for {url}: {indicator}"
                        )
                        return "hard"

                # If content is available but has subscription prompts, treat as soft paywall
                for indicator in hard_paywall_indicators:
                    if indicator in content_lower:
                        self.logger.info(
                            f"Soft paywall detected for {url}: {indicator} (content accessible)"
                        )
                        return "soft"

                # No paywall indicators with full content = free article
                self.logger.info(f"Free content detected for {url}")
                return "none"
            else:
                # Limited content + paywall indicators = hard paywall
                for indicator in hard_paywall_indicators:
                    if indicator in content_lower:
                        self.logger.info(
                            f"Hard paywall detected for {url}: {indicator}"
                        )
                        return "hard"

            # Check for soft paywall
            for indicator in soft_paywall_indicators:
                if indicator in content_lower:
                    if full_content_available:
                        self.logger.info(
                            f"Soft paywall detected for {url}: {indicator} (content accessible)"
                        )
                        return "soft"
                    else:
                        self.logger.info(
                            f"Hard paywall detected for {url}: {indicator} (content restricted)"
                        )
                        return "hard"

            # Check for Substack-specific paywall classes
            soup = BeautifulSoup(response.text, "html.parser")
            paywall_selectors = [
                ".paywall",
                ".subscriber-only",
                ".paid-content",
                "[data-paywall]",
                ".premium-content",
            ]

            for selector in paywall_selectors:
                if soup.select_one(selector):
                    self.logger.info(f"Paywall element detected: {selector}")
                    return "hard"

            return "none"

        except Exception as e:
            self.logger.warning(
                f"Error checking paywall status for {url}: {e}"
            )
            return "none"

    def _handle_paywalled_content(
        self, article: Article, output_dir: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Handle paywalled content by extracting available preview text, metadata, and images.
        """
        try:
            response = self.session.get(article.url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract available preview content
            preview_content = self._extract_preview_content(soup)

            # Create article folder and images subfolder
            safe_title = re.sub(
                r'[<>:"/\\|?*]', "_", article.title or "Substack Article"
            )
            article_folder = os.path.join(output_dir, safe_title)
            os.makedirs(article_folder, exist_ok=True)

            images_folder = os.path.join(article_folder, "images")
            os.makedirs(images_folder, exist_ok=True)

            # Create limited content using unified media processing
            initial_content = self._create_paywall_content(
                article, preview_content, soup
            )

            # Process media using UnifiedMediaProcessor for consistent architecture
            content = UnifiedMediaProcessor.process_article_media(
                content=initial_content,
                html_content=str(soup),
                url=article.url,
                article_path=article_folder,
                media_config=self.media_downloader.config,
                session=self.session,
                logger=self.logger,
            )

            # Save content
            article_file = os.path.join(article_folder, "article.md")
            with open(article_file, "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.info(
                f"Saved paywall-limited content for: {article.title}"
            )
            return True, article_folder

        except Exception as e:
            self.logger.error(f"Failed to handle paywalled content: {e}")
            return False, None

    def _extract_preview_content(self, soup: BeautifulSoup) -> str:
        """Extract available preview content from paywalled article."""
        preview_selectors = [
            ".available-content p",
            ".post-content p",
            ".body p",
            ".prose p",
            ".preview-content p",
            "p",
        ]

        preview_text = []
        for selector in preview_selectors:
            elements = soup.select(selector)
            for elem in elements[:4]:  # Limit to first 4 paragraphs
                text = elem.get_text().strip()
                # Filter out navigation and subscription prompts
                if (
                    len(text) > 40
                    and "subscribe" not in text.lower()
                    and "paywall" not in text.lower()
                    and "sign up" not in text.lower()
                ):
                    preview_text.append(text)
            if preview_text:
                break

        return "\n\n".join(preview_text)




    def _create_paywall_content(
        self,
        article: Article,
        preview_content: str,
        soup: BeautifulSoup,
    ) -> str:
        """Create markdown content for paywalled articles."""

        # Extract metadata
        title = article.title or self._extract_title(soup)
        author = self._extract_author(soup)
        date = self._extract_date(soup)
        substack_name = self._extract_substack_name(article.url)

        content = f"# {title}\n\n"

        if substack_name:
            content += f"**Substack:** {substack_name}\n"
        if author:
            content += f"**Author:** {author}\n"
        if date:
            content += f"**Date:** {date}\n"

        content += f"**Source:** [Substack Article]({article.url})\n\n"
        content += "---\n\n"
        content += "**⚠️ PAYWALL NOTICE**\n\n"
        content += "This article requires a paid subscription. Only preview content is available.\n\n"
        content += "**Preview Content:**\n\n"

        if preview_content:
            content += preview_content + "\n\n"
        else:
            content += "*No preview content available.*\n\n"

        # Images will be processed by UnifiedMediaProcessor

        content += f"**Read full article:** [{article.url}]({article.url})\n\n"

        if substack_name:
            subscribe_url = f"https://{substack_name}.substack.com/subscribe"
            content += f"**Subscribe to {substack_name}:** [{subscribe_url}]({subscribe_url})\n\n"

        content += "---\n\n"
        content += "*Note: Capcat respects paywall restrictions and only archives publicly available content.*"

        return content

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from Substack page."""
        selectors = [
            ".post-title",
            "h1.post-title",
            ".single-post-title",
            "h1",
            "title",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()

        return "Substack Article"

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from Substack page."""
        selectors = [
            ".author-name",
            ".byline-names",
            ".author",
            '[rel="author"]',
            ".post-author",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()

        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date from Substack page."""
        selectors = [
            ".post-date",
            "time",
            ".published-date",
            ".post-meta time",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Try to get datetime attribute first
                date_str = (
                    element.get("datetime") or element.get_text().strip()
                )
                if date_str:
                    return date_str

        return None

    def _extract_substack_name(self, url: str) -> Optional[str]:
        """Extract Substack publication name from URL."""
        match = re.search(r"https?://([^.]+)\.substack\.com", url)
        if match:
            return match.group(1)
        return None

    def _optimize_substack_content(self, folder_path: str) -> None:
        """
        Apply Substack-specific content optimizations.
        """
        try:
            article_file = os.path.join(folder_path, "article.md")
            if not os.path.exists(article_file):
                return

            with open(article_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Substack-specific optimizations
            optimized_content = self._apply_substack_formatting(content)

            with open(article_file, "w", encoding="utf-8") as f:
                f.write(optimized_content)

        except Exception as e:
            self.logger.debug(f"Error optimizing Substack content: {e}")

    def _apply_substack_formatting(self, content: str) -> str:
        """Apply Substack-specific formatting improvements."""

        # Fix Substack-specific formatting issues
        content = re.sub(
            r"\n{3,}", "\n\n", content
        )  # Remove excessive line breaks

        # Improve blockquote formatting
        content = re.sub(r"^> (.+)", r"> *\1*", content, flags=re.MULTILINE)

        # Clean up subscription callouts
        content = re.sub(
            r"\*\*Subscribe.*?\*\*\n*", "", content, flags=re.IGNORECASE
        )

        # Fix image captions
        content = re.sub(
            r"!\[([^\]]*)\]\(([^)]+)\)\s*\n\s*\*([^*]+)\*",
            r"![\1](\2)\n*\3*",
            content,
        )

        # Remove common Substack footer patterns
        footer_patterns = [
            r"Thanks for reading.*?Subscribe for free.*?\n",
            r"Like this post\? Subscribe.*?\n",
            r"Share.*?\n.*?Subscribe.*?\n",
        ]

        for pattern in footer_patterns:
            content = re.sub(
                pattern, "", content, flags=re.IGNORECASE | re.DOTALL
            )

        return content

    def _validate_custom_config(self) -> List[str]:
        """Validate Substack-specific configuration."""
        errors = []
        # Add Substack-specific validation if needed
        return errors

    def _should_skip_custom(self, url: str, title: str = "") -> bool:
        """Custom skip logic for Substack URLs."""
        skip_patterns = ["/subscribe", "/account/login", "/sign-in"]
        return any(pattern in url for pattern in skip_patterns)
