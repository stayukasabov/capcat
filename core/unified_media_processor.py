#!/usr/bin/env python3
"""
Unified Media Processor Integration Layer.
Clean, DRY interface using modular ImageProcessor.
"""

import os

import requests
import yaml

from .image_processor import get_image_processor
from .logging_config import get_logger


class UnifiedMediaProcessor:
    """
    Clean, DRY integration layer using modular ImageProcessor.
    """

    @staticmethod
    def process_article_media(
        content: str,
        html_content: str,
        url: str,
        article_folder: str,
        source_name: str,
        session: requests.Session,
        media_enabled: bool = False,
        page_title: str = "",
    ) -> str:
        """
        Process images using clean, modular architecture.

        Args:
            content: Markdown content of the article
            html_content: Original HTML content
            url: Source URL of the article
            article_folder: Path to article folder
            source_name: Name of the news source
            session: HTTP session for downloading

        Returns:
            Updated markdown content with local image references
        """
        logger = get_logger(__name__)

        try:
            # Load source configuration
            source_config = UnifiedMediaProcessor._load_source_config(
                source_name
            )

            # Process images using modular ImageProcessor
            image_processor = get_image_processor(session)
            url_mapping = image_processor.process_article_images(
                html_content, source_config, url, article_folder
            )

            # Process image embedding based on content structure
            if url_mapping:
                # First try URL replacement (for sources where markdown
                # has image refs)
                updated_content = image_processor.replace_image_urls(
                    content, url_mapping
                )

                # If no images embedded (config-driven), insert them
                if "![" not in updated_content and url_mapping:
                    logger.debug(
                        f"No image references in markdown, inserting "
                        f"{len(url_mapping)} images"
                    )
                    updated_content = (
                        UnifiedMediaProcessor
                        ._insert_images_into_markdown(
                            content, url_mapping
                        )
                    )

                content = updated_content
                logger.info(f"Media processing completed for {source_name}")
            else:
                logger.debug(f"No images processed for {source_name}")

            return content

        except Exception as e:
            logger.error(f"Media processing error: {e}")
            return content

    @staticmethod
    def _insert_images_into_markdown(content: str, url_mapping: dict) -> str:
        """
        Insert images into markdown content for config-driven sources.
        Adds images at the end of content in a dedicated section.
        """
        if not url_mapping:
            return content

        # Create images section
        images_section = "\n\n## Article Images\n\n"
        for i, (original_url, local_filename) in enumerate(
            url_mapping.items(), 1
        ):
            local_path = f"images/{local_filename}"
            images_section += f"![Image {i}]({local_path})\n\n"

        return content + images_section

    @staticmethod
    def _load_source_config(source_name: str) -> dict:
        """Load source configuration from YAML file."""
        # Check custom sources first
        config_path = (
            f"sources/active/custom/{source_name}/config.yaml"
        )

        if not os.path.exists(config_path):
            # Check config-driven sources
            config_path = (
                f"sources/active/config_driven/configs/"
                f"{source_name}.yaml"
            )

        if not os.path.exists(config_path):
            return {}

        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
