#!/usr/bin/env python3
"""
Config-driven source implementation.
Handles sources that are defined purely through configuration files.

Refactored for:
- Proper XML parsing with lxml (eliminates XMLParsedAsHTMLWarning)
- Strategy pattern for discovery methods (RSS vs HTML)
- Reduced cyclomatic complexity
- Single Responsibility Principle compliance
- Improved error handling
"""

from typing import List, Optional, Tuple

import requests

from ..news_source_adapter import NewsSourceArticleFetcher
from .base_source import (
    Article,
    ArticleDiscoveryError,
    BaseSource,
    ContentFetchError,
)
from .discovery_strategies import DiscoveryStrategyFactory


class ConfigDrivenSource(BaseSource):
    """
    Source implementation for config-driven sources.

    Uses configuration data to extract articles and content without
    requiring custom Python code. Delegates to strategy classes for
    different discovery methods (RSS, HTML).
    """

    @property
    def source_type(self) -> str:
        """Return the source type."""
        return "config_driven"

    def discover_articles(self, count: int) -> List[Article]:
        """
        Discover articles using configured discovery method.

        Supports both RSS and HTML scraping based on configuration.
        Uses Strategy pattern to delegate to appropriate discovery handler.

        Args:
            count: Maximum number of articles to discover

        Returns:
            List of Article objects

        Raises:
            ArticleDiscoveryError: If article discovery fails
        """
        start_time = self._start_performance_timing()

        try:
            self.logger.debug(
                f"Discovering articles for {self.config.name} (count: {count})"
            )

            # Get discovery configuration
            custom_config = self.config.custom_config
            discovery_config = custom_config.get("discovery", {})

            # Create appropriate strategy (pass full config for legacy support)
            strategy = DiscoveryStrategyFactory.create(
                discovery_config,
                legacy_config=custom_config
            )

            # Execute discovery
            articles = strategy.discover(
                count=count,
                config=custom_config,
                session=self.session,
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                logger=self.logger,
                should_skip_callback=self.should_skip_url
            )

            self.logger.debug(
                f"Successfully discovered {len(articles)} articles for {self.config.name}"
            )
            self._record_article_discovery(len(articles))
            self._end_performance_timing(start_time, True)

            return articles[:count]

        except ArticleDiscoveryError:
            # Re-raise with proper timing
            self._end_performance_timing(start_time, False, "DiscoveryError")
            raise
        except ValueError as e:
            # Strategy creation or validation error
            self._end_performance_timing(start_time, False, "ConfigError")
            raise ArticleDiscoveryError(
                f"Configuration error: {e}",
                self.config.name,
            )
        except requests.RequestException as e:
            self._end_performance_timing(start_time, False, "NetworkError")
            raise ArticleDiscoveryError(
                f"Network error while fetching articles: {e}",
                self.config.name,
            )
        except Exception as e:
            self._end_performance_timing(start_time, False, "UnknownError")
            raise ArticleDiscoveryError(
                f"Article discovery failed: {e}",
                self.config.name
            )

    def fetch_article_content(
        self, article: Article, output_dir: str, progress_callback=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Fetch article content using configured content selectors.

        Args:
            article: Article to fetch
            output_dir: Directory to save content
            progress_callback: Optional progress callback function

        Returns:
            Tuple of (success, article_path)

        Raises:
            ContentFetchError: If content fetching fails
        """
        try:
            self.logger.debug(f"Fetching content for article: {article.title}")

            # Prepare configuration for NewsSourceArticleFetcher
            fetcher_config = self._prepare_fetcher_config()
            fetcher = NewsSourceArticleFetcher(fetcher_config, self.session)

            # Fetch content
            success, title, folder_path = fetcher._fetch_web_content(
                title=article.title,
                url=article.url,
                index=0,
                base_folder=output_dir,
                progress_callback=progress_callback,
            )

            self._record_content_fetch(success)

            if success:
                return True, folder_path
            else:
                return False, None

        except Exception as e:
            self._record_content_fetch(False)
            raise ContentFetchError(
                f"Failed to fetch content for {article.url}: {e}",
                self.config.name,
            )

    def _prepare_fetcher_config(self) -> dict:
        """
        Prepare configuration for NewsSourceArticleFetcher.

        Returns:
            Configuration dictionary with required fields
        """
        fetcher_config = self.config.custom_config.copy()
        fetcher_config["name"] = self.config.display_name
        fetcher_config["source_id"] = self.config.custom_config.get(
            "source_id",
            self.config.name.lower()
        )
        return fetcher_config

    def _validate_custom_config(self) -> List[str]:
        """
        Validate config-driven source configuration.

        Returns:
            List of validation error messages
        """
        errors = []
        custom_config = self.config.custom_config

        # Check required fields
        if not custom_config.get("article_selectors"):
            errors.append("article_selectors is required")

        if not custom_config.get("content_selectors"):
            errors.append("content_selectors is required")

        # Validate selectors format
        article_selectors = custom_config.get("article_selectors", [])
        if not isinstance(article_selectors, list) or not article_selectors:
            errors.append("article_selectors must be a non-empty list")

        content_selectors = custom_config.get("content_selectors", [])
        if not isinstance(content_selectors, list) or not content_selectors:
            errors.append("content_selectors must be a non-empty list")

        # Validate skip_patterns if present
        skip_patterns = custom_config.get("skip_patterns", [])
        if skip_patterns and not isinstance(skip_patterns, list):
            errors.append("skip_patterns must be a list")

        return errors

    def _should_skip_custom(self, url: str, title: str = "") -> bool:
        """
        Custom skip logic for config-driven sources.

        Args:
            url: URL to check
            title: Optional article title

        Returns:
            True if URL should be skipped
        """
        skip_patterns = self.config.custom_config.get("skip_patterns", [])
        return any(pattern in url for pattern in skip_patterns)
