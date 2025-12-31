#!/usr/bin/env python3
"""
Twitter/X.com specialized source implementation.
Twitter requires JavaScript and blocks automated access, so we create
placeholder articles with links to original posts.
"""

import os
import re
from typing import List, Optional, Tuple

from core.source_system.base_source import (
    Article,
    ArticleDiscoveryError,
    BaseSource,
)
from core.utils import sanitize_filename


class TwitterSource(BaseSource):
    """
    Twitter/X.com specialized source that creates placeholder articles.
    """

    @property
    def source_type(self) -> str:
        return "specialized"

    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        """Check if this source can handle the given URL."""
        twitter_patterns = [
            r"twitter\.com",
            r"x\.com",
        ]
        return any(
            re.search(pattern, url, re.IGNORECASE)
            for pattern in twitter_patterns
        )

    def discover_articles(self, count: int) -> List[Article]:
        """
        Twitter discovery not supported without API access.
        """
        raise ArticleDiscoveryError(
            "Twitter discovery not supported. Use single article mode with Twitter URLs.",
            self.config.name,
        )

    def fetch_article_content(
        self, article: Article, output_dir: str, progress_callback=None
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

            filename = os.path.join(output_dir, "article.md")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(article_content)

            self.logger.info(
                f"Created Twitter placeholder: '{display_title}'"
            )

            return True, display_title

        except Exception as e:
            self.logger.error(
                f"Failed to create Twitter placeholder for '{article.title}': {e}"
            )
            return False, None
