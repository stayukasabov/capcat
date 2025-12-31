#!/usr/bin/env python3
"""
Medium.com specialized source implementation with paywall detection.
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


class MediumSource(BaseSource):
    """
    Medium.com specialized source with paywall detection and optimal formatting.
    """

    @property
    def source_type(self) -> str:
        return "specialized"

    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        """Check if this source can handle the given URL."""
        # More specific patterns to avoid conflicts with Substack
        medium_patterns = [
            r"medium\.com",
            r"[^/]+\.medium\.com",
            r"/@[^/]+",  # Medium profile URLs
        ]

        # Only match Medium URLs, not Substack
        if ".substack.com" in url.lower():
            return False

        return any(
            re.search(pattern, url, re.IGNORECASE)
            for pattern in medium_patterns
        )

    def discover_articles(self, count: int) -> List[Article]:
        """
        Medium doesn't have a reliable public feed, so this is not implemented.
        Use single article mode with Medium URLs instead.
        """
        raise ArticleDiscoveryError(
            "Medium discovery not supported. Use single article mode with Medium URLs.",
            self.config.name,
        )

    def fetch_article_content(
        self, article: Article, output_dir: str, progress_callback=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Fetch article content from Medium with paywall detection.
        """
        try:
            self.logger.debug(f"Fetching Medium content for: {article.title}")

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

            # Use optimized Medium-specific configuration
            fetcher_config = {
                "name": self.config.display_name,
                "content_selectors": [
                    "article",
                    '[data-testid="storyContent"]',
                    ".postArticle-content",
                    ".section-content",
                    ".p-name",
                    "main",
                    ".post-content",
                ],
                "title_selectors": [
                    'h1[data-testid="storyTitle"]',
                    ".p-name",
                    ".postArticle-title",
                    "h1",
                    ".story-title",
                ],
                "author_selectors": [
                    '[data-testid="authorName"]',
                    ".p-author",
                    ".postMetaInline-authorLockup a",
                    ".author-name",
                    '[rel="author"]',
                ],
                "date_selectors": [
                    '[data-testid="storyPublishDate"]',
                    ".dt-published",
                    "time",
                    ".post-date",
                ],
                "image_selectors": [
                    "figure img",
                    ".medium-image",
                    'img[src*="medium.com"]',
                    ".story-image img",
                    "img",
                ],
                "skip_patterns": [
                    "/sign-in",
                    "/membership",
                    "/subscribe",
                    "/upgrade",
                    "paywall",
                    "premium-content",
                ],
                "paywall_indicators": [
                    "paywall",
                    "member-only",
                    "subscription-required",
                    "premium-content",
                    "upgrade-to-continue",
                    "sign-in-to-continue",
                ],
            }

            fetcher = NewsSourceArticleFetcher(fetcher_config, self.session)

            # Use direct fetching to avoid URL transformation issues
            success, folder_path = self._fetch_medium_content_direct(
                article, output_dir
            )

            if success:
                # Post-process for Medium-specific optimizations
                self._optimize_medium_content(folder_path)
                return True, folder_path
            else:
                return False, None

        except Exception as e:
            raise ContentFetchError(
                f"Failed to fetch Medium content for {article.url}: {e}",
                self.config.name,
            )

    def _fetch_medium_content_direct(
        self, article: Article, output_dir: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Fetch Medium content directly without URL transformation.
        """
        try:
            response = self.session.get(article.url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_selectors = [
                'h1[data-testid="storyTitle"]',
                ".p-name",
                ".postArticle-title",
                "h1",
                "title",
            ]
            title = article.title
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break

            # Create article folder and images subfolder
            safe_title = re.sub(
                r'[<>:"/\\|?*]', "_", title or "Medium Article"
            )
            article_folder = os.path.join(output_dir, safe_title)
            os.makedirs(article_folder, exist_ok=True)

            images_folder = os.path.join(article_folder, "images")
            os.makedirs(images_folder, exist_ok=True)

            # Extract content first
            content_selectors = [
                "article",
                '[data-testid="storyContent"]',
                ".postArticle-content",
                ".section-content",
                ".p-name",
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

            # Use UnifiedMediaProcessor - following established architecture
            processed_content = UnifiedMediaProcessor.process_article_media(
                content=content,
                html_content=response.text,
                url=article.url,
                article_folder=article_folder,
                source_name="medium",
                session=self.session,
                page_title=title
            )

            # Extract metadata
            author_selectors = [
                '[data-testid="authorName"]',
                ".p-author",
                ".postMetaInline-authorLockup a",
                ".author-name",
                '[rel="author"]',
            ]
            author = ""
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    break

            date_selectors = [
                '[data-testid="storyPublishDate"]',
                ".dt-published",
                "time",
                ".post-date",
            ]
            date = ""
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date = date_elem.get("datetime") or date_elem.get_text(
                        strip=True
                    )
                    break

            # Save article content with processed media references
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

            self.logger.info(f"Successfully fetched Medium content: {title}")
            return True, article_folder

        except Exception as e:
            self.logger.error(f"Failed to fetch Medium content directly: {e}")
            return False, None

    # Custom image downloading methods removed - now using UnifiedMediaProcessor

    def _is_paywalled(self, url: str) -> str:
        """
        Check if the Medium article is behind a paywall.
        Returns: 'hard' for subscription required, 'soft' for overlay, 'none' for free
        """
        try:
            # Quick HEAD request to check for paywall redirects
            response = self.session.head(url, timeout=10, allow_redirects=True)

            # Check for hard paywall redirects
            if "sign-in" in response.url or "membership" in response.url:
                return "hard"

            # Get content to analyze paywall type
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Hard paywall indicators (content actually restricted)
            hard_paywall_indicators = [
                "member-only",
                "subscription required",
                "premium content",
                "member preview",
                "subscribers only",
                "paid subscribers",
            ]

            # Soft paywall indicators (overlay but content available)
            soft_paywall_indicators = [
                "sign in to continue",
                "become a member",
                "unlock this story",
                "upgrade to continue",
            ]

            content_lower = response.text.lower()

            # Check if full content is available first
            content_selectors = [
                "article",
                '[data-testid="storyContent"]',
                ".postArticle-content",
            ]
            full_content_available = False
            content_length = 0

            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text().strip()
                    content_length = len(content_text)
                    if content_length > 1000:  # Substantial content
                        full_content_available = True
                        break

            self.logger.debug(
                f"Content length found: {content_length}, Full content available: {full_content_available}"
            )

            # If substantial content is available, check for hard paywall indicators more carefully
            if full_content_available:
                # Only treat as hard paywall if content is actually truncated with paywall message
                paywall_truncation_indicators = [
                    "this story is published in",
                    "member-only story",
                    "become a member to unlock",
                    "sign up to unlock this story",
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
                r'[<>:"/\\|?*]', "_", article.title or "Medium Article"
            )
            article_folder = os.path.join(output_dir, safe_title)
            os.makedirs(article_folder, exist_ok=True)

            images_folder = os.path.join(article_folder, "images")
            os.makedirs(images_folder, exist_ok=True)

            # Create limited content file
            content = self._create_paywall_content(
                article, preview_content, soup
            )

            # Use UnifiedMediaProcessor for paywall content images - following established architecture
            processed_content = UnifiedMediaProcessor.process_article_media(
                content=content,
                html_content=response.text,
                url=article.url,
                article_folder=article_folder,
                source_name="medium",
                session=self.session,
                page_title=article.title
            )

            # Save processed content with unified media references
            article_file = os.path.join(article_folder, "article.md")
            with open(article_file, "w", encoding="utf-8") as f:
                f.write(processed_content)

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
            ".postArticle-content p",
            '[data-testid="storyContent"] p',
            ".story-content p",
            ".post-preview",
            ".excerpt",
            "p",
        ]

        preview_text = []
        for selector in preview_selectors:
            elements = soup.select(selector)
            for elem in elements[:3]:  # Limit to first 3 paragraphs
                text = elem.get_text().strip()
                if len(text) > 50:  # Only substantial paragraphs
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

        content = f"# {title}\n\n"

        if author:
            content += f"**Author:** {author}\n"
        if date:
            content += f"**Date:** {date}\n"

        content += f"**Source:** [Medium Article]({article.url})\n\n"
        content += "---\n\n"
        content += "**⚠️ PAYWALL NOTICE**\n\n"
        content += "This article is behind a paywall. Only preview content is available.\n\n"
        content += "**Preview Content:**\n\n"

        if preview_content:
            content += preview_content + "\n\n"
        else:
            content += "*No preview content available.*\n\n"

        content += f"**Read full article:** [{article.url}]({article.url})\n\n"
        content += "---\n\n"
        content += "*Note: Capcat respects paywall restrictions and only archives publicly available content.*"

        return content

    # Custom preview image downloading removed - now using UnifiedMediaProcessor

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from Medium page."""
        selectors = [
            'h1[data-testid="storyTitle"]',
            ".p-name",
            ".postArticle-title",
            "h1",
            "title",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()

        return "Medium Article"

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from Medium page."""
        selectors = [
            '[data-testid="authorName"]',
            ".p-author",
            ".postMetaInline-authorLockup a",
            ".author-name",
            '[rel="author"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()

        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date from Medium page."""
        selectors = [
            '[data-testid="storyPublishDate"]',
            ".dt-published",
            "time",
            ".post-date",
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

    def _optimize_medium_content(self, folder_path: str) -> None:
        """
        Apply Medium-specific content optimizations.
        """
        try:
            article_file = os.path.join(folder_path, "article.md")
            if not os.path.exists(article_file):
                return

            with open(article_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Medium-specific optimizations
            optimized_content = self._apply_medium_formatting(content)

            with open(article_file, "w", encoding="utf-8") as f:
                f.write(optimized_content)

        except Exception as e:
            self.logger.debug(f"Error optimizing Medium content: {e}")

    def _apply_medium_formatting(self, content: str) -> str:
        """Apply Medium-specific formatting improvements."""

        # Fix Medium-specific formatting issues
        content = re.sub(
            r"\n{3,}", "\n\n", content
        )  # Remove excessive line breaks
        content = re.sub(
            r"^\*\*\*$", "---", content, flags=re.MULTILINE
        )  # Fix dividers

        # Improve quote formatting
        content = re.sub(r"^> (.+)", r"> *\1*", content, flags=re.MULTILINE)

        # Clean up image captions
        content = re.sub(
            r"!\[([^\]]*)\]\(([^)]+)\)\s*\n\s*\*([^*]+)\*",
            r"![\1](\2)\n*\3*",
            content,
        )

        return content

    def _validate_custom_config(self) -> List[str]:
        """Validate Medium-specific configuration."""
        errors = []
        # Add Medium-specific validation if needed
        return errors

    def _should_skip_custom(self, url: str, title: str = "") -> bool:
        """Custom skip logic for Medium URLs."""
        skip_patterns = ["/sign-in", "/membership", "/subscribe", "/upgrade"]
        return any(pattern in url for pattern in skip_patterns)
