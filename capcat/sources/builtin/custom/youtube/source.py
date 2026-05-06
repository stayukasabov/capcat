#!/usr/bin/env python3
"""
YouTube specialized source implementation.
YouTube content is video-based and cannot be meaningfully archived as text,
so we create placeholder articles with links to original videos.
"""

import os
import re
from typing import List, Optional, Tuple

import yt_dlp

from capcat.core.source_system.base_source import (
    Article,
    ArticleDiscoveryError,
    BaseSource,
)
from capcat.core.storage_manager import article_md_filename


class YouTubeSource(BaseSource):
    """
    YouTube specialized source that creates placeholder articles.
    """

    @property
    def source_type(self) -> str:
        return "custom"

    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        """Check if this source can handle the given URL."""
        youtube_patterns = [
            r"youtube\.com",
            r"youtu\.be",
            r"m\.youtube\.com",
        ]
        return any(
            re.search(pattern, url, re.IGNORECASE)
            for pattern in youtube_patterns
        )

    def discover_articles(self, count: int) -> List[Article]:
        """
        YouTube discovery not supported without API access.
        """
        raise ArticleDiscoveryError(
            "YouTube discovery not supported. Use single article mode with YouTube URLs.",
            self.config.name,
        )

    def _extract_video_title(self, url: str) -> Optional[str]:
        """
        Extract video title from YouTube using yt-dlp.

        Args:
            url: YouTube video URL

        Returns:
            Video title or None if extraction fails
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'skip_download': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and 'title' in info:
                    return info['title'].strip()

            return None

        except Exception as e:
            self.logger.warning(f"Failed to extract YouTube title from {url}: {e}")
            return None

    def _fetch_oembed_title(self, url: str) -> Optional[str]:
        """
        Fetch video title from YouTube oEmbed API (no API key required).

        Args:
            url: YouTube video URL

        Returns:
            Video title or None if fetch fails
        """
        try:
            import json
            oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
            response = self.session.get(oembed_url, timeout=10)
            response.raise_for_status()
            data = json.loads(response.text)
            title = data.get("title", "").strip()
            return title if title else None
        except Exception as e:
            self.logger.debug(f"oEmbed title fetch failed for {url}: {e}")
            return None

    def fetch_article_content(
        self, article: Article, output_dir: str, progress_callback=None,
        download_files: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        Create placeholder article with actual video title.
        """
        try:
            # Load template from config
            template = self.config.template if hasattr(self.config, 'template') else {}
            body_text = template.get("body", "Visit the original link.")
            source_label = template.get("source_label", "Source URL")

            # Try to extract actual video title - yt-dlp → oEmbed → article.title → placeholder
            video_title = (
                self._extract_video_title(article.url)
                or self._fetch_oembed_title(article.url)
                or (article.title.strip() if article.title and article.title.strip() else None)
                or template.get("title", "YouTube Video")
            )
            display_title = video_title
            self.logger.info(f"Using YouTube title: '{display_title}'")

            # Create subdirectory for article (matches regular source structure)
            from capcat.core.utils import sanitize_filename
            safe_title = sanitize_filename(display_title)
            article_folder = os.path.join(output_dir, safe_title)
            os.makedirs(article_folder, exist_ok=True)

            # Build article content
            article_content = f"# {display_title}\n\n"
            article_content += f"**{source_label}:** [{article.url}]({article.url})\n\n"
            article_content += "---\n\n"
            article_content += f"{body_text}\n"

            filename = os.path.join(article_folder, article_md_filename(display_title))
            with open(filename, "w", encoding="utf-8") as f:
                f.write(article_content)

            self.logger.info(
                f"Created YouTube placeholder: '{display_title}'"
            )

            return True, article_folder

        except Exception as e:
            self.logger.error(
                f"Failed to create YouTube placeholder for '{article.title}': {e}"
            )
            return False, None
