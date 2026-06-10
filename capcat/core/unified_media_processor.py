#!/usr/bin/env python3
"""
Unified Media Processor Integration Layer.
Clean, DRY interface using modular ImageProcessor.
"""

import os
import re

import requests
import yaml

from .config import get_config
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
            if not (get_config().processing.download_images or media_enabled):
                return content

            # Load source configuration
            source_config = UnifiedMediaProcessor._load_source_config(
                source_name
            )

            # Process images using modular ImageProcessor
            cfg = get_config().processing
            image_processor = get_image_processor(session)

            # Per-source max_image_size_mb overrides global default
            img_cfg = source_config.get("image_processing", {})
            per_source_mb = img_cfg.get("max_image_size_mb")
            if per_source_mb is not None:
                max_image_bytes = int(per_source_mb) * 1024 * 1024
            else:
                max_image_bytes = cfg.max_image_size_bytes

            # Phase 1: Download images already referenced inline in markdown.
            # This handles sources (Guardian, BBC) where content selectors
            # capture images that produce ![alt](url) during conversion.
            # These URLs may differ from what image_processing selectors
            # find on the full page, so we download them directly first.
            content = UnifiedMediaProcessor._download_inline_images(
                content, article_folder, session, img_cfg, max_image_bytes
            )

            # Phase 2: Discover and download additional images from the full
            # page HTML using image_processing selectors. This catches images
            # that are outside the content selector scope.
            url_mapping = image_processor.process_article_images(
                html_content, source_config, url, article_folder,
                article_url=url,
                min_pixel_dimension=cfg.min_image_dimensions,
                max_image_bytes=max_image_bytes,
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
    def _download_inline_images(
        content: str,
        article_folder: str,
        session: requests.Session,
        img_cfg: dict,
        max_image_bytes: int,
    ) -> str:
        """Download images already referenced inline in markdown content.

        Scans for ![alt](url) patterns, downloads each remote image, and
        replaces the URL with a local path. This ensures images captured by
        content selectors (e.g. Guardian, BBC) are downloaded even when
        image_processing selectors find different URLs on the full page.
        """
        logger = get_logger(__name__)
        # Match ![alt](url) and ![alt](url "title") separately so the
        # title portion is excluded from the captured URL.
        inline_pattern = re.compile(
            r'!\[([^\]]*)\]\((https?://[^\s"]+)(?:\s+"[^"]*")?\)'
        )
        matches = inline_pattern.findall(content)
        if not matches:
            return content

        from .downloader import download_file

        downloaded = 0

        for alt_text, img_url in matches:
            # Skip URLs that are already local
            if img_url.startswith(("images/", "files/", "./")):
                continue

            try:
                local_path = download_file(
                    img_url, article_folder, "image", False
                )
                if local_path:
                    content = content.replace(img_url, local_path)
                    downloaded += 1
            except Exception as exc:
                logger.debug(f"Inline image download failed {img_url}: {exc}")

        if downloaded:
            logger.debug(
                f"Downloaded {downloaded} inline images from markdown content"
            )
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
        try:
            from capcat.core.config import find_project_root
            project_root = find_project_root()
        except Exception:
            project_root = None

        def _resolve(relative: str) -> str:
            if project_root:
                return str(project_root / "Config" / relative)
            return relative

        # Check custom sources first
        config_path = _resolve(
            f"sources/active/custom/{source_name}/config.yaml"
        )

        if not os.path.exists(config_path):
            # Check config-driven sources
            config_path = _resolve(
                f"sources/active/config_driven/configs/{source_name}.yaml"
            )

        if not os.path.exists(config_path):
            return {}

        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
