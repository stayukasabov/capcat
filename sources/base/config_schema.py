#!/usr/bin/env python3
"""
Base configuration schema for news sources.
Provides standardized structure for source configuration.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SourceConfig:
    """
    Standardized configuration schema for news sources.
    """

    # Basic source information
    name: str
    source_id: str
    category: str
    base_url: str

    # Scraping configuration
    article_selectors: List[str] = field(default_factory=list)
    content_selectors: List[str] = field(default_factory=list)
    skip_patterns: List[str] = field(default_factory=list)

    # Optional selectors for specific sites
    title_selectors: Optional[List[str]] = None
    author_selectors: Optional[List[str]] = None
    date_selectors: Optional[List[str]] = None
    article_containers: Optional[str] = None
    link_selectors: Optional[List[str]] = None

    # Behavior configuration
    has_comments: bool = False
    comments_selector: Optional[str] = None
    timeout: int = 10
    rate_limit: float = 1.0

    # Optional URLs
    rss_url: Optional[str] = None

    # Custom processing
    custom_processor: Optional[str] = None
    module: Optional[str] = None
    scraping_function: Optional[str] = None

    # Additional configuration
    extra_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for compatibility."""
        result = {
            "name": self.name,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "rate_limit": self.rate_limit,
        }

        if self.article_selectors:
            result["article_selectors"] = self.article_selectors

        if self.content_selectors:
            result["content_selectors"] = self.content_selectors

        if self.skip_patterns:
            result["skip_patterns"] = self.skip_patterns

        if self.title_selectors:
            result["title_selectors"] = self.title_selectors

        if self.author_selectors:
            result["author_selectors"] = self.author_selectors

        if self.date_selectors:
            result["date_selectors"] = self.date_selectors

        if self.article_containers:
            result["article_containers"] = self.article_containers

        if self.link_selectors:
            result["link_selectors"] = self.link_selectors

        if self.has_comments:
            result["has_comments"] = self.has_comments

        if self.comments_selector:
            result["comments_selector"] = self.comments_selector

        if self.rss_url:
            result["rss_url"] = self.rss_url

        if self.module:
            result["module"] = self.module

        if self.scraping_function:
            result["scraping_function"] = self.scraping_function

        if self.custom_processor:
            result["custom_processor"] = self.custom_processor

        # Add extra configuration
        result.update(self.extra_config)

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any], source_id: str) -> "SourceConfig":
        """Create SourceConfig from dictionary (for legacy compatibility)."""
        return cls(
            name=data.get("name", source_id.title()),
            source_id=source_id,
            category=data.get("category", "unknown"),
            base_url=data["base_url"],
            article_selectors=data.get("article_selectors", []),
            content_selectors=data.get("content_selectors", []),
            skip_patterns=data.get("skip_patterns", []),
            title_selectors=data.get("title_selectors"),
            author_selectors=data.get("author_selectors"),
            date_selectors=data.get("date_selectors"),
            article_containers=data.get("article_containers"),
            link_selectors=data.get("link_selectors"),
            has_comments=data.get("has_comments", False),
            comments_selector=data.get("comments_selector"),
            timeout=data.get("timeout", 10),
            rate_limit=data.get("rate_limit", 1.0),
            rss_url=data.get("rss_url"),
            module=data.get("module"),
            scraping_function=data.get("scraping_function"),
            custom_processor=data.get("custom_processor"),
            extra_config={k: v for k, v in data.items() if k not in {
                "name", "base_url", "article_selectors", "content_selectors",
                "skip_patterns", "title_selectors", "author_selectors",
                "date_selectors", "article_containers", "link_selectors",
                "has_comments", "comments_selector", "timeout", "rate_limit",
                "rss_url", "module", "scraping_function", "custom_processor"
            }}
        )

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        if not self.name:
            errors.append("Source name is required")

        if not self.source_id:
            errors.append("Source ID is required")

        if not self.base_url:
            errors.append("Base URL is required")
        elif not self.base_url.startswith(("http://", "https://")):
            errors.append("Base URL must start with http:// or https://")

        if not self.article_selectors and not self.custom_processor:
            errors.append("Either article_selectors or custom_processor must be provided")

        if not self.content_selectors and not self.custom_processor:
            errors.append("Either content_selectors or custom_processor must be provided")

        if self.timeout <= 0:
            errors.append("Timeout must be positive")

        if self.rate_limit <= 0:
            errors.append("Rate limit must be positive")

        return errors