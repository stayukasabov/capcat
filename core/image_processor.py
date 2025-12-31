#!/usr/bin/env python3
"""
Global Image Processor for Capcat.
Modular, DRY architecture with source-specific configurations.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from core.logging_config import get_logger
from core.utils import sanitize_filename
# from core.simple_protection import create_simple_protection  # Disabled - aggregator protection removed


class ImageProcessor:
    """
    Global image processing coordinator.
    Uses source-specific configurations for clean, modular processing.
    """

    def __init__(self, session: Optional[requests.Session] = None):
        self.logger = get_logger(__name__)
        self.session = session or requests.Session()
        # self.protection = create_simple_protection()  # Disabled - aggregator protection removed

    def process_article_images(
        self,
        html_content: str,
        source_config: dict,
        base_url: str,
        output_folder: str,
        page_title: str = "",
        media_enabled: bool = False,
    ) -> Dict[str, str]:
        """
        Process images for an article using source-specific configuration.
        Includes intelligent protection against aggregator sites.

        Args:
            html_content: Raw HTML content
            source_config: Source configuration with image processing rules
            base_url: Base URL for resolving relative links
            output_folder: Article output folder path
            page_title: Page title for classification
            media_enabled: Whether --media flag is enabled (affects limits)

        Returns:
            Dict mapping original URLs to local filenames
        """
        try:
            # Protection system disabled - process all content
            # Note: Aggregator protection removed to allow processing all URLs including Wikipedia
            self.logger.debug(f"Processing content from: {base_url}")

            # Extract image processing config
            img_config = source_config.get("image_processing", {})

            # Extract images from HTML using source selectors
            image_urls = self._extract_image_urls(
                html_content, img_config, base_url
            )

            if not image_urls:
                return {}

            # Apply max_images limit if configured
            max_images = img_config.get("max_images")
            if max_images and isinstance(max_images, int) and max_images > 0:
                self.logger.debug(
                    f"Limiting to first {max_images} images "
                    f"(found {len(image_urls)})"
                )
                image_urls = image_urls[:max_images]

            # Download images with per-image size checking
            min_image_size = img_config.get("min_image_size", 0)
            downloaded_images = self._download_images_with_checking(
                image_urls, output_folder, media_enabled, min_image_size
            )

            self.logger.info(f"Processed {len(downloaded_images)} images")
            return downloaded_images

        except Exception as e:
            self.logger.error(f"Image processing error: {e}")
            return {}

    def _extract_image_urls(
        self, html_content: str, img_config: dict, base_url: str
    ) -> List[str]:
        """Extract image URLs using source-specific selectors."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Get selectors from config
        selectors = img_config.get("selectors", ["img"])
        skip_selectors = img_config.get("skip_selectors", [])
        url_patterns = img_config.get("url_patterns", [])

        image_urls = []

        # Extract images using configured selectors
        for selector in selectors:
            images = soup.select(selector)

            for img in images:
                # Skip if matches skip selectors
                if self._should_skip_image(img, skip_selectors):
                    continue

                # Prioritize data-src for lazy-loaded images
                src = img.get("data-src") or img.get("src")
                if not src or not isinstance(src, str):
                    continue

                # Resolve relative URLs
                full_url = urljoin(base_url, src)

                # Apply URL transformations if configured
                url_transforms = img_config.get("url_transforms", [])
                for transform in url_transforms:
                    pattern = transform.get("pattern")
                    replacement = transform.get("replacement")
                    if pattern and replacement is not None:
                        full_url = re.sub(pattern, replacement, full_url)

                # Filter by URL patterns if specified
                if url_patterns and not self._matches_url_patterns(
                    full_url, url_patterns
                ):
                    continue

                if self._is_valid_image_url(
                    full_url, img_config.get("allow_extensionless", False)
                ):
                    image_urls.append(full_url)

        return list(set(image_urls))  # Remove duplicates

    def _should_skip_image(
        self, img_element, skip_selectors: List[str]
    ) -> bool:
        """Check if image should be skipped based on skip selectors."""
        for skip_selector in skip_selectors:
            # Parse selector: "parent img" -> check if img has parent matching "parent"
            # or ".class img" -> check if img has parent with class
            parts = skip_selector.split()

            if len(parts) == 2 and parts[1] == "img":
                # Pattern: ".parent-class img" or "div.class img"
                parent_selector = parts[0]

                # Try to find parent matching the selector
                if img_element.find_parent(class_=parent_selector.lstrip('.')):
                    return True

                # Also try tag-based matching for selectors like "nav img"
                if img_element.find_parent(parent_selector):
                    return True
            else:
                # Direct selector matching
                if img_element.find_parent(skip_selector):
                    return True

        return False

    def _matches_url_patterns(self, url: str, patterns: List[str]) -> bool:
        """Check if URL matches any of the specified patterns."""
        return any(pattern in url for pattern in patterns)

    def _is_valid_image_url(
        self, url: str, allow_extensionless: bool = False
    ) -> bool:
        """Validate image URL."""
        if not url or not url.startswith(("http://", "https://")):
            return False

        # Check for image extensions
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Allow extensionless URLs if configured
        if allow_extensionless:
            return True

        return any(
            path.endswith(ext)
            for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
        )

    def _download_images(
        self, image_urls: List[str], output_folder: str, max_total_size_mb: int = 20,
        allow_large_files: bool = False
    ) -> Dict[str, str]:
        """Download images with size limits and return URL to filename mapping."""
        images_dir = os.path.join(output_folder, "images")
        os.makedirs(images_dir, exist_ok=True)

        downloaded = {}
        image_counter = 1
        total_size_bytes = 0
        max_total_size_bytes = max_total_size_mb * 1024 * 1024

        for url in image_urls:
            try:
                # Check size before download if possible
                if total_size_bytes >= max_total_size_bytes:
                    self.logger.warning(
                        f"Stopping download: Size limit {max_total_size_mb}MB reached"
                    )
                    break

                filename, file_size = self._download_single_image_with_size_check(
                    url, images_dir, image_counter,
                    max_total_size_bytes - total_size_bytes, allow_large_files
                )

                if filename:
                    downloaded[url] = filename
                    total_size_bytes += file_size
                    image_counter += 1

                    self.logger.debug(
                        f"Downloaded {filename}: {file_size / 1024:.1f}KB "
                        f"(Total: {total_size_bytes / 1024 / 1024:.1f}MB)"
                    )

            except Exception as e:
                self.logger.debug(f"Failed to download {url}: {e}")

        if total_size_bytes > max_total_size_bytes * 0.8:  # Warn at 80%
            self.logger.warning(
                f"High image download volume: {total_size_bytes / 1024 / 1024:.1f}MB"
            )

        return downloaded

    def _download_images_with_checking(
        self, image_urls: List[str], output_folder: str, media_enabled: bool = False,
        min_image_size: int = 0
    ) -> Dict[str, str]:
        """Download images with simple per-image checking and optional size filtering."""
        images_dir = os.path.join(output_folder, "images")
        os.makedirs(images_dir, exist_ok=True)

        downloaded = {}
        image_counter = 1

        for url in image_urls:
            try:
                # Download with optional size filtering
                if min_image_size > 0:
                    filename = self._download_single_image_with_min_size(
                        url, images_dir, image_counter, min_image_size
                    )
                else:
                    filename = self._download_single_image_simple(
                        url, images_dir, image_counter
                    )

                if filename:
                    downloaded[url] = filename
                    image_counter += 1

            except Exception as e:
                self.logger.debug(f"Failed to download {url}: {e}")

        return downloaded

    def _has_explicit_source_config(self, source_config: Dict) -> bool:
        """Check if source has explicit configuration (not a generic/discovered source)."""
        # Sources with explicit configs have detailed image processing rules
        return bool(source_config.get("image_processing", {}).get("selectors", []))

    def _download_single_image_simple(
        self, url: str, images_dir: str, counter: int
    ) -> Optional[str]:
        """Download single image with simple error handling."""
        try:
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # Generate simple sequential filename
            extension = self._get_extension_from_url_or_content(
                url, response.headers.get("content-type")
            )
            filename = f"image-{counter}{extension}"
            filepath = os.path.join(images_dir, filename)

            # Write file
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.debug(f"Downloaded {filename}")
            return filename

        except Exception as e:
            self.logger.debug(f"Failed to download {url}: {e}")
            return None

    def _download_single_image_with_min_size(
        self, url: str, images_dir: str, counter: int, min_size: int
    ) -> Optional[str]:
        """Download single image with minimum size filtering."""
        try:
            # Check size via HEAD request first
            head_response = self.session.head(url, timeout=10)
            content_length = head_response.headers.get('content-length')

            if content_length:
                file_size = int(content_length)
                if file_size < min_size:
                    self.logger.debug(
                        f"Skipping {url}: {file_size} bytes < {min_size} bytes minimum"
                    )
                    return None

            # Proceed with download
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # Generate simple sequential filename
            extension = self._get_extension_from_url_or_content(
                url, response.headers.get("content-type")
            )
            filename = f"image-{counter}{extension}"
            filepath = os.path.join(images_dir, filename)

            # Write file and track size
            downloaded_size = 0
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)

            # Verify size after download if no content-length header
            if not content_length and downloaded_size < min_size:
                os.remove(filepath)
                self.logger.debug(
                    f"Removed {filename}: {downloaded_size} bytes < {min_size} bytes minimum"
                )
                return None

            self.logger.debug(f"Downloaded {filename} ({downloaded_size} bytes)")
            return filename

        except Exception as e:
            self.logger.debug(f"Failed to download {url}: {e}")
            return None

    def _download_single_image_with_size_check(
        self, url: str, images_dir: str, counter: int, remaining_bytes: int,
        allow_large_files: bool = False
    ) -> Tuple[Optional[str], int]:
        """Download single image with size checking and return (filename, size)."""
        try:
            # First, get headers to check file size
            head_response = self.session.head(url, timeout=10)
            content_length = head_response.headers.get('content-length')

            if content_length:
                file_size = int(content_length)
                if file_size > remaining_bytes:
                    self.logger.debug(
                        f"Skipping {url}: {file_size / 1024:.1f}KB exceeds remaining limit "
                        f"{remaining_bytes / 1024:.1f}KB"
                    )
                    return None, 0

                # Skip individual files over 5MB only if large files not explicitly allowed
                if not allow_large_files and file_size > 5 * 1024 * 1024:
                    self.logger.debug(f"Skipping large file: {url} ({file_size / 1024 / 1024:.1f}MB)")
                    return None, 0

            # Proceed with download
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # Generate simple sequential filename
            extension = self._get_extension_from_url_or_content(
                url, response.headers.get("content-type")
            )
            filename = f"image-{counter}{extension}"
            filepath = os.path.join(images_dir, filename)

            # Download with size tracking
            downloaded_size = 0
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    chunk_size = len(chunk)
                    if downloaded_size + chunk_size > remaining_bytes:
                        self.logger.debug(f"Truncating download for {url}: size limit reached")
                        break
                    f.write(chunk)
                    downloaded_size += chunk_size

            return filename, downloaded_size

        except Exception as e:
            self.logger.debug(f"Download failed for {url}: {e}")
            return None, 0

    def _download_single_image(
        self, url: str, images_dir: str, counter: int
    ) -> Optional[str]:
        """Download single image and return filename (legacy method)."""
        filename, _ = self._download_single_image_with_size_check(
            url, images_dir, counter, float('inf')
        )
        return filename

    def _generate_filename(self, url: str, content_type: Optional[str] = None) -> str:
        """Generate clean filename from URL."""
        parsed = urlparse(url)
        path = parsed.path

        # Extract filename from path
        if path and path != "/":
            filename = os.path.basename(path)

            # Remove query parameters from filename
            filename = filename.split("?")[0]

            # Ensure it has an extension
            if "." not in filename and content_type:
                ext = self._get_extension_from_content_type(content_type)
                if ext:
                    filename += ext

        else:
            # Generate filename from domain
            filename = f"{parsed.netloc.replace('.', '-')}-image"
            if content_type:
                ext = self._get_extension_from_content_type(content_type)
                if ext:
                    filename += ext
                else:
                    filename += ".jpg"  # Default
            else:
                filename += ".jpg"

        return sanitize_filename(filename)

    def _get_extension_from_content_type(
        self, content_type: str
    ) -> Optional[str]:
        """Get file extension from content type."""
        content_type_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/svg+xml": ".svg",
        }
        return content_type_map.get(content_type.lower()) if content_type else None

    def _get_extension_from_url_or_content(
        self, url: str, content_type: Optional[str] = None
    ) -> str:
        """Get file extension from URL or content type, defaulting to .jpg."""
        # Try to get extension from URL first
        parsed = urlparse(url)
        path = parsed.path.lower()

        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
            if path.endswith(ext):
                return ext

        # Try content type
        if content_type:
            ext = self._get_extension_from_content_type(content_type)
            if ext:
                return ext

        # Default to .jpg
        return ".jpg"

    @staticmethod
    def replace_image_urls(
        markdown_content: str, url_mapping: Dict[str, str]
    ) -> str:
        """
        Clean URL replacement in markdown content.
        DRY approach with systematic pattern matching.
        """
        if not url_mapping:
            return markdown_content

        updated_content = markdown_content

        for original_url, local_filename in url_mapping.items():
            local_path = f"images/{local_filename}"

            # Apply replacement strategies systematically
            updated_content = ImageProcessor._apply_url_patterns(
                updated_content, original_url, local_path
            )

        return updated_content

    @staticmethod
    def _apply_url_patterns(
        content: str, original_url: str, local_path: str
    ) -> str:
        """Apply systematic URL replacement patterns."""
        # Direct string replacement
        content = content.replace(original_url, local_path)

        # Markdown image pattern replacement
        parsed = urlparse(original_url)
        replacement = rf"![\1]({local_path})"

        patterns = [
            # Full URL with escaping
            rf"!\[([^\]]*)\]\({re.escape(original_url)}\)",
            # Base URL without query parameters
            rf'!\[([^\]]*)\]\({re.escape(f"{parsed.scheme}://{parsed.netloc}{parsed.path}")}[^)]*\)',
            # Filename-based matching
            (
                rf"!\[([^\]]*)\]\([^)]*{re.escape(os.path.basename(parsed.path))}[^)]*\)"
                if parsed.path
                else None
            ),
        ]

        for pattern in patterns:
            if pattern:
                content = re.sub(pattern, replacement, content)

        return content


def get_image_processor(session: Optional[requests.Session] = None) -> ImageProcessor:
    """Get ImageProcessor instance."""
    return ImageProcessor(session)
