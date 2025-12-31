#!/usr/bin/env python3
"""
Media Configuration Manager for different news sources.
Provides source-specific configurations for media processing.
"""

from typing import Any, Dict


class MediaConfigManager:
    """
    Manages media processing configurations for different news sources.
    """

    @staticmethod
    def get_source_config(source_name: str) -> Dict[str, Any]:
        """
        Get media processing configuration for a specific source.

        Args:
            source_name: Name of the news source

        Returns:
            Dictionary with media processing configuration
        """
        configs = {
            "futurism": {
                "media_processing": {
                    "hero_image_selectors": [
                        ".featured-image img",
                        ".post-thumbnail img",
                        ".hero-image img",
                        ".entry-image img",
                    ],
                    "content_image_selectors": [
                        ".post-content img",
                        ".entry-content img",
                        ".article-content img",
                        "img",
                    ],
                    "url_patterns": {
                        "wordpress": ["/wp-content/uploads/", "/uploads/"],
                        "futurism_specific": [
                            "futurism.com/wp-content/uploads/"
                        ],
                    },
                    "skip_patterns": [
                        "data:",
                        "javascript:",
                        "mailto:",
                        "#",
                        ".svg",
                        "avatar",
                        "logo",
                        "icon",
                        "button",
                        "advertisement",
                        "ad-",
                        "ads-",
                    ],
                    "quality_thresholds": {
                        "min_width": 150,
                        "min_height": 150,
                        "min_file_size": 2048,
                    },
                }
            },
            "gizmodo": {
                "media_processing": {
                    "hero_image_selectors": [
                        ".featured-image img",
                        ".hero-image img",
                        ".post-header img",
                        ".article-header img",
                        ".entry-thumbnail img",
                    ],
                    "content_image_selectors": [
                        ".post-content img",
                        ".entry-content img",
                        ".article-content img",
                        ".content img",
                        "img",
                    ],
                    "url_patterns": {
                        "gizmodo": [
                            "gizmodo.com/wp-content/uploads/",
                            "i.gizmodo.com/",
                        ],
                        "wordpress": ["/wp-content/uploads/"],
                    },
                    "skip_patterns": [
                        "data:",
                        "javascript:",
                        "mailto:",
                        "#",
                        ".svg",
                        "avatar",
                        "logo",
                        "icon",
                        "button",
                        "advertisement",
                        "ad-",
                        "sponsored",
                    ],
                }
            },
            "ieee": {
                "media_processing": {
                    "hero_image_selectors": [
                        ".featured-image img",
                        ".article-image img",
                        ".hero-banner img",
                    ],
                    "url_patterns": {
                        "ieee": [
                            "spectrum.ieee.org/media/",
                            "spectrum.ieee.org/image/",
                        ],
                        "general": ["/media/", "/images/"],
                    },
                    "quality_thresholds": {
                        "min_width": 200,
                        "min_height": 150,
                        "min_file_size": 3072,
                    },
                }
            },
            "hn": {
                "media_processing": {
                    "content_image_selectors": [
                        "img",
                        ".post-content img",
                        ".article img",
                    ],
                    "url_patterns": {
                        "general": ["/images/", "/media/", "/static/"]
                    },
                    "skip_patterns": [
                        "data:",
                        "javascript:",
                        "mailto:",
                        "#",
                        ".svg",
                        "avatar",
                        "logo",
                        "icon",
                        "button",
                        "ycombinator.com",
                        "gravatar",
                    ],
                }
            },
            "bbc": {
                "media_processing": {
                    "hero_image_selectors": [
                        ".media-placeholder img",
                        ".lead-image img",
                        ".hero-image img",
                    ],
                    "url_patterns": {
                        "bbc": ["ichef.bbci.co.uk/", "bbc.co.uk/news/"],
                        "cdn": ["c.files.bbci.co.uk/"],
                    },
                    "quality_thresholds": {
                        "min_width": 300,
                        "min_height": 200,
                        "min_file_size": 5120,
                    },
                }
            },
            "cnn": {
                "media_processing": {
                    "hero_image_selectors": [
                        ".media__image img",
                        ".featured-image img",
                    ],
                    "url_patterns": {
                        "cnn": ["cdn.cnn.com/", "cnn.com/dam/"],
                        "turner": ["turner.com/"],
                    },
                }
            },
            "nature": {
                "media_processing": {
                    "hero_image_selectors": [
                        ".article-header__image img",
                        ".featured-image img",
                    ],
                    "url_patterns": {
                        "nature": ["nature.com/articles/", "media.nature.com/"]
                    },
                    "quality_thresholds": {
                        "min_width": 400,
                        "min_height": 300,
                        "min_file_size": 8192,
                    },
                }
            },
            "scientificamerican": {
                "media_processing": {
                    "hero_image_selectors": [
                        ".featured-image img",
                        ".article-image img",
                        ".hero-image img",
                    ],
                    "content_image_selectors": [
                        "img",
                        ".content img",
                        ".article-content img",
                    ],
                    "url_patterns": {
                        "static_images": [
                            "static.scientificamerican.com/dam/"
                        ],
                        "cdn": ["static.scientificamerican.com/"],
                    },
                    "quality_thresholds": {
                        "min_width": 150,
                        "min_height": 150,
                        "min_file_size": 2048,
                    },
                }
            },
        }

        # Return source-specific config or default
        return configs.get(
            source_name, MediaConfigManager._get_default_config()
        )

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default media processing configuration."""
        return {
            "media_processing": {
                "hero_image_selectors": [
                    ".featured-image img",
                    ".hero-image img",
                    ".post-thumbnail img",
                    ".entry-image img",
                    ".article-image img",
                    "img.featured",
                ],
                "content_image_selectors": [
                    "img",
                    ".content img",
                    ".post-content img",
                    ".entry-content img",
                    ".article-content img",
                    ".body img",
                ],
                "url_patterns": {
                    "wordpress": ["/wp-content/uploads/", "/uploads/"],
                    "cdn": ["cdn.", "media.", "static.", "assets."],
                    "images": ["/images/", "/img/", "/media/"],
                },
                "skip_patterns": [
                    "data:",
                    "javascript:",
                    "mailto:",
                    "#",
                    ".svg",
                    "avatar",
                    "logo",
                    "icon",
                    "button",
                ],
                "download_types": ["jpg", "jpeg", "png", "webp", "gif"],
                "quality_thresholds": {
                    "min_width": 100,
                    "min_height": 100,
                    "min_file_size": 1024,
                },
            }
        }

    @staticmethod
    def get_all_source_names() -> list:
        """Get list of all configured source names."""
        return [
            "futurism",
            "gizmodo",
            "ieee",
            "hn",
            "bbc",
            "cnn",
            "nature",
            "scientificamerican",
        ]
