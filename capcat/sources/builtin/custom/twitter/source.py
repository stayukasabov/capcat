#!/usr/bin/env python3
"""
Twitter/X.com specialized source implementation.
Twitter requires JavaScript and blocks automated access, so we create
placeholder articles with links to original posts.
"""

import os
import re
from typing import List, Optional, Tuple

from capcat.core.source_system.base_source import (
    Article,
    ArticleDiscoveryError,
    BaseSource,
)
from capcat.core.storage_manager import article_md_filename
from capcat.core.utils import sanitize_filename


class TwitterSource(BaseSource):
    """
    Twitter/X.com specialized source that creates placeholder articles.
    """

    @property
    def source_type(self) -> str:
        return "custom"

    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        """Check if this source can handle the given URL."""
        from urllib.parse import urlparse
        try:
            netloc = urlparse(url).netloc.lower().split(':')[0]
            return (
                netloc == 'x.com' or netloc.endswith('.x.com') or
                netloc == 'twitter.com' or netloc.endswith('.twitter.com')
            )
        except Exception:
            return False

    def discover_articles(self, count: int) -> List[Article]:
        """
        Twitter discovery not supported without API access.
        """
        raise ArticleDiscoveryError(
            "Twitter discovery not supported. Use single article mode with Twitter URLs.",
            self.config.name,
        )

    def fetch_article_content(
        self, article: Article, output_dir: str, progress_callback=None,
        download_files: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        Create placeholder article using config-driven template.
        """
        try:
            # Load template from config
            template = self.config.template if hasattr(self.config, 'template') else {}

            display_title = template.get("title", "X.com post")
            body_text = template.get("body", "Visit the original publication.")
            source_label = template.get("source_label", "Source URL")

            # Build article content from template
            article_content = f"# {display_title}\n\n"
            article_content += f"**{source_label}:** [{article.url}]({article.url})\n\n"
            article_content += "---\n\n"
            article_content += f"{body_text}\n"

            article_folder = os.path.join(output_dir, sanitize_filename(display_title))
            os.makedirs(article_folder, exist_ok=True)

            filename = os.path.join(article_folder, article_md_filename(display_title))
            with open(filename, "w", encoding="utf-8") as f:
                f.write(article_content)

            self.logger.info(
                f"Created Twitter placeholder: '{display_title}'"
            )

            return True, article_folder

        except Exception as e:
            self.logger.error(
                f"Failed to create Twitter placeholder for '{article.title}': {e}"
            )
            return False, None
