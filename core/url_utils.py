#!/usr/bin/env python3
"""
URL validation and normalization utilities for Capcat.

Provides safe URL handling for user inputs and media processing.
Prevents common URL-related errors and security issues.
"""

from typing import Optional
from urllib.parse import urlparse, urljoin

from core.exceptions import ValidationError


class URLValidator:
    """URL validation utilities for user input and media processing.

    Validates URLs to ensure they use safe schemes and proper formatting.
    Prevents file:// and other potentially dangerous URL schemes.
    """

    ALLOWED_SCHEMES = ('http', 'https')
    BLOCKED_SCHEMES = ('file', 'ftp', 'data', 'javascript', 'mailto')

    @classmethod
    def validate_article_url(cls, url: str) -> bool:
        """Validate user-provided article URLs.

        Args:
            url: URL to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If URL is invalid or unsafe

        Example:
            >>> URLValidator.validate_article_url(
            ...     "https://example.com/article"
            ... )
            True
            >>> URLValidator.validate_article_url("file:///etc/passwd")
            Traceback (most recent call last):
            ...
            ValidationError: Only HTTP/HTTPS URLs supported
        """
        if not url or not isinstance(url, str):
            raise ValidationError(
                "url",
                str(url),
                "URL cannot be empty"
            )

        try:
            parsed = urlparse(url.strip())
        except Exception as e:
            raise ValidationError("url", url, f"Malformed URL: {e}")

        if not parsed.scheme:
            raise ValidationError(
                "url",
                url,
                "URL must include scheme (http/https)"
            )

        if parsed.scheme not in cls.ALLOWED_SCHEMES:
            raise ValidationError(
                "url",
                url,
                f"Only {'/'.join(cls.ALLOWED_SCHEMES)} URLs supported"
            )

        if not parsed.netloc:
            raise ValidationError(
                "url",
                url,
                "URL must include domain name"
            )

        return True

    @classmethod
    def normalize_url(cls, url: str, base_url: str) -> Optional[str]:
        """Normalize relative/protocol-relative URLs to absolute.

        Handles common URL patterns safely:
        - Protocol-relative: //example.com/image.jpg
        - Absolute path: /images/photo.jpg
        - Relative path: images/photo.jpg
        - Already absolute: https://example.com/img.jpg
        - Blocked: data:, javascript:, mailto:, file:

        Args:
            url: URL to normalize
            base_url: Base URL for resolution

        Returns:
            Normalized absolute URL, or None if blocked/invalid

        Example:
            >>> URLValidator.normalize_url(
            ...     "//cdn.com/img.jpg",
            ...     "https://example.com"
            ... )
            'https://cdn.com/img.jpg'
            >>> URLValidator.normalize_url(
            ...     "/images/photo.jpg",
            ...     "https://example.com"
            ... )
            'https://example.com/images/photo.jpg'
        """
        if not url or not isinstance(url, str):
            return None

        url = url.strip()

        # Block dangerous schemes
        for blocked in cls.BLOCKED_SCHEMES:
            if url.startswith(f"{blocked}:"):
                return None

        # Skip fragments and empty anchors
        if url.startswith('#') or url == '':
            return None

        try:
            if url.startswith('//'):
                # Protocol-relative URL
                parsed_base = urlparse(base_url)
                return f"{parsed_base.scheme}:{url}"
            elif url.startswith('/'):
                # Absolute path
                return urljoin(base_url, url)
            elif url.startswith(('http://', 'https://')):
                # Already absolute
                return url
            else:
                # Relative path
                return urljoin(base_url, url)
        except Exception:
            return None


class URLProcessor:
    """Centralized URL processing for media extraction.

    Handles batch processing of image and media URLs with normalization
    and deduplication.
    """

    def __init__(self, base_url: str):
        """Initialize with base URL for relative resolution.

        Args:
            base_url: Base URL for resolving relative URLs
        """
        self.base_url = base_url
        self.validator = URLValidator()

    def process_image_urls(
        self,
        image_elements: list,
        existing_images: set
    ) -> list:
        """Process image elements into normalized URL tuples.

        Args:
            image_elements: BeautifulSoup img elements
            existing_images: Set of already processed image URLs (modified)

        Returns:
            List of (type, normalized_url, alt_text) tuples

        Example:
            >>> processor = URLProcessor("https://example.com")
            >>> imgs = [{'src': '/photo.jpg', 'alt': 'Photo'}]
            >>> processor.process_image_urls(imgs, set())
            [('image', 'https://example.com/photo.jpg', 'Photo')]
        """
        processed_images = []

        for img in image_elements:
            img_src = img.get('src', '').strip()
            alt_text = img.get('alt', '').strip()

            if not img_src or img_src in existing_images:
                continue

            normalized_url = self.validator.normalize_url(
                img_src,
                self.base_url
            )
            if normalized_url:
                processed_images.append(
                    ("image", normalized_url, alt_text)
                )
                existing_images.add(img_src)

        return processed_images

    def process_media_urls(
        self,
        media_elements: list,
        existing_media: set
    ) -> list:
        """Process video/audio elements into normalized URL tuples.

        Args:
            media_elements: BeautifulSoup video/audio/source elements
            existing_media: Set of already processed media URLs (modified)

        Returns:
            List of (type, normalized_url, description) tuples

        Example:
            >>> processor = URLProcessor("https://example.com")
            >>> videos = [{'src': '/video.mp4', 'type': 'video/mp4'}]
            >>> processor.process_media_urls(videos, set())
            [('video', 'https://example.com/video.mp4', 'video/mp4')]
        """
        processed_media = []

        for media in media_elements:
            media_src = media.get('src', '').strip()
            media_type = media.get('type', '').strip()

            if not media_src or media_src in existing_media:
                continue

            normalized_url = self.validator.normalize_url(
                media_src,
                self.base_url
            )
            if normalized_url:
                processed_media.append(
                    ("media", normalized_url, media_type)
                )
                existing_media.add(media_src)

        return processed_media
