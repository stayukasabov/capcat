#!/usr/bin/env python3
"""
Media processing component for Capcat.

Separates media discovery, download, and embedding operations from the
ArticleFetcher class to improve maintainability and testability.
"""

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional, Dict, Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .config import get_config
from .downloader import download_file
from .logging_config import get_logger


class MediaProcessor:
    """
    Handles all media processing responsibilities: discovery, download, and embedding.
    """
    
    def __init__(self, session: requests.Session, download_files: bool = False):
        """
        Initialize the media processor.
        
        Args:
            session: HTTP session for making requests
            download_files: Whether to download all media types (not just images)
        """
        self.session = session
        self.download_files = download_files
        self.logger = get_logger("MediaProcessor")
        
    def process_media(self, 
                     soup: BeautifulSoup, 
                     base_url: str, 
                     article_folder_path: str) -> str:
        """
        Process all media in the content and return updated markdown content.
        
        Args:
            soup: Parsed HTML soup object
            base_url: Base URL for resolving relative links
            article_folder_path: Path to save downloaded media files
            
        Returns:
            Updated markdown content with media references
        """
        # Extract all media links first to analyze them
        all_media_links = self._extract_media_links(soup, base_url)
        
        # Process links intelligently to minimize network requests
        processed_links = self._process_media_links(
            all_media_links, article_folder_path
        )
        
        # Update the markdown content with local paths
        markdown_content = str(soup)
        for original_url, local_path in processed_links.items():
            if local_path:
                markdown_content = self._replace_media_reference(
                    markdown_content, original_url, local_path
                )
        
        return markdown_content
    
    def _extract_media_links(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str, str]]:
        """
        Extract all media links from the soup object.
        
        Returns:
            List of tuples (link_type, url, alt_text)
        """
        all_links = []
        
        # Get image links from HTML soup
        img_tags = soup.find_all("img")
        self.logger.debug(f"Found {len(img_tags)} img tags in soup")

        for img in img_tags:
            img_src = img.get("src")
            if not img_src:
                # Try to get lazy-loaded images if src is not available
                img_src = img.get("data-src", "")
            if not img_src:
                img_src = img.get("data-lazy", "")

            # Skip data URLs and other non-network URLs
            if img_src and not (
                img_src.startswith("data:")
                or img_src.startswith("javascript:")
                or img_src.startswith("mailto:")
            ):
                if img_src.startswith("//"):
                    # Protocol-relative URL - use same protocol as base URL
                    base_parsed = urlparse(base_url)
                    img_src = f"{base_parsed.scheme}:{img_src}"
                elif img_src.startswith("/"):
                    img_src = urljoin(base_url, img_src)
                elif img_src.startswith(("http://", "https://")):
                    pass  # Already absolute
                else:
                    img_src = urljoin(base_url, img_src)

                all_links.append(("image", img_src, img.get("alt", "image")))

        # Get document links
        link_tags = soup.find_all("a", href=True)
        for link in link_tags:
            href = link.get("href")
            if href and not (
                href.startswith("javascript:")
                or href.startswith("mailto:")
                or href.startswith("#")
                or href.startswith("data:")
            ):
                # Convert relative URLs to absolute
                if href.startswith("//"):
                    # Protocol-relative URL - use same protocol as base URL
                    base_parsed = urlparse(base_url)
                    href = f"{base_parsed.scheme}:{href}"
                elif href.startswith("/"):
                    href = urljoin(base_url, href)
                elif not href.startswith(("http://", "https://")):
                    # Skip relative paths that don't start with /
                    continue

                # Check if this link points to an image - if so, classify as image, not document
                href_lower = href.lower()
                if href_lower.endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".tiff",
                        ".tif",
                        ".webp",
                        ".svg",
                        ".ico",
                    )
                ):
                    # This is an image link, add it as image type
                    all_links.append(("image", href, link.get_text().strip() or "image"))
                else:
                    # This is a regular document link
                    all_links.append(
                        (
                            "document",
                            href,
                            link.get_text().strip() or "document",
                        )
                    )

        # Get video and audio links
        video_tags = soup.find_all("video")
        for video in video_tags:
            video_src = video.get("src")
            if video_src:
                if video_src.startswith("//"):
                    # Protocol-relative URL - use same protocol as base URL
                    base_parsed = urlparse(base_url)
                    video_src = f"{base_parsed.scheme}:{video_src}"
                elif video_src.startswith("/"):
                    video_src = urljoin(base_url, video_src)
                elif not video_src.startswith(("http://", "https://")):
                    continue
                all_links.append(("video", video_src, "video"))

            # Check source elements within video tags
            source_elements = video.find_all("source")
            for source in source_elements:
                src = source.get("src")
                if src:
                    if src.startswith("//"):
                        # Protocol-relative URL - use same protocol as base URL
                        base_parsed = urlparse(base_url)
                        src = f"{base_parsed.scheme}:{src}"
                    elif src.startswith("/"):
                        src = urljoin(base_url, src)
                    elif not src.startswith(("http://", "https://")):
                        continue
                    all_links.append(("video", src, "video"))

        audio_tags = soup.find_all("audio")
        for audio in audio_tags:
            audio_src = audio.get("src")
            if audio_src:
                if audio_src.startswith("//"):
                    # Protocol-relative URL - use same protocol as base URL
                    base_parsed = urlparse(base_url)
                    audio_src = f"{base_parsed.scheme}:{audio_src}"
                elif audio_src.startswith("/"):
                    audio_src = urljoin(base_url, audio_src)
                elif not audio_src.startswith(("http://", "https://")):
                    continue
                all_links.append(("audio", audio_src, "audio"))

            # Check source elements within audio tags
            source_elements = audio.find_all("source")
            for source in source_elements:
                src = source.get("src")
                if src:
                    if src.startswith("//"):
                        # Protocol-relative URL - use same protocol as base URL
                        base_parsed = urlparse(base_url)
                        src = f"{base_parsed.scheme}:{src}"
                    elif src.startswith("/"):
                        src = urljoin(base_url, src)
                    elif not src.startswith(("http://", "https://")):
                        continue
                    all_links.append(("audio", src, "audio"))

        # Filter links based on type and extension
        filtered_links = self._filter_media_links(all_links)
        
        self.logger.info(
            f"Found {len(all_links)} total media links, {len(filtered_links)} passed filtering"
        )
        
        return filtered_links
    
    def _filter_media_links(self, all_links: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
        """
        Filter media links based on type and extension.
        
        Args:
            all_links: List of (link_type, url, alt_text) tuples
            
        Returns:
            Filtered list of media links
        """
        filtered_links = []
        for link_type, url, alt_text in all_links:
            parsed_url = urlparse(url)
            path_lower = parsed_url.path.lower()

            # Quick extension-based filtering
            if link_type == "image":
                if path_lower.endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".tiff",
                        ".tif",
                        ".webp",
                        ".svg",
                        ".ico",
                    )
                ):
                    filtered_links.append((link_type, url, alt_text))
                # Also include links that look like they might be images based on common patterns
                elif any(
                    pattern in path_lower
                    for pattern in ["image", "img", "photo", "pic"]
                ):
                    filtered_links.append((link_type, url, alt_text))
            elif link_type == "document" and self.download_files:
                # Only process documents if download_files flag is set
                # Exclude HTML files - they should be processed as web pages, not downloaded as documents
                if path_lower.endswith(
                    (
                        ".pdf",
                        ".doc",
                        ".docx",
                        ".xls",
                        ".xlsx",
                        ".ppt",
                        ".pptx",
                        ".txt",
                        ".rtf",
                        ".odt",
                        ".ods",
                        ".odp",
                    )
                ):
                    filtered_links.append((link_type, url, alt_text))
                # Include common document patterns but exclude HTML-related patterns
                elif any(
                    pattern in path_lower
                    for pattern in [
                        "document",
                        "doc",
                        "pdf",
                        "download",
                        "xls",
                        "ppt",
                    ]
                ):
                    # Make sure it's not an HTML file
                    if not path_lower.endswith((".html", ".htm")):
                        filtered_links.append((link_type, url, alt_text))
            elif link_type == "audio" and self.download_files:
                # Only process audio if download_files flag is set
                if path_lower.endswith(
                    (
                        ".mp3",
                        ".wav",
                        ".ogg",
                        ".flac",
                        ".aac",
                        ".m4a",
                        ".wma",
                        ".opus",
                    )
                ):
                    filtered_links.append((link_type, url, alt_text))
                # Include common audio patterns
                elif any(
                    pattern in path_lower
                    for pattern in ["audio", "sound", "mp3", "wav"]
                ):
                    filtered_links.append((link_type, url, alt_text))
            elif link_type == "video" and self.download_files:
                # Only process video if download_files flag is set
                if path_lower.endswith(
                    (
                        ".mp4",
                        ".avi",
                        ".mkv",
                        ".mov",
                        ".wmv",
                        ".flv",
                        ".webm",
                        ".m4v",
                        ".3gp",
                    )
                ):
                    filtered_links.append((link_type, url, alt_text))
                # Include common video patterns
                elif any(
                    pattern in path_lower
                    for pattern in ["video", "movie", "mp4", "mov"]
                ):
                    filtered_links.append((link_type, url, alt_text))
            else:
                # For unknown types, do quick filtering for common media extensions
                # Only include images by default, other media types require download_files flag
                if path_lower.endswith((".jpg", ".jpeg", ".png", ".gif")):
                    filtered_links.append((link_type, url, alt_text))
                elif self.download_files and path_lower.endswith(
                    (".pdf", ".mp3", ".mp4", ".wav", ".mov")
                ):
                    filtered_links.append((link_type, url, alt_text))

        return filtered_links
    
    def _process_media_links(
        self,
        media_links: List[Tuple[str, str, str]],
        article_folder_path: str,
    ) -> Dict[str, str]:
        """
        Process media links with concurrent downloading.
        
        Args:
            media_links: List of (link_type, url, alt_text) tuples
            article_folder_path: Path to save downloaded files
            
        Returns:
            Dictionary mapping original URLs to local file paths
        """
        config = get_config()
        max_workers = (
            min(config.processing.max_workers, len(media_links))
            if media_links
            else 1
        )
        
        processed_results = {}
        
        # Track downloaded URLs to avoid duplicates
        download_cache = {}  # url -> local_path

        def process_single_media(link_info):
            link_type, url, alt_text = link_info

            # Check cache first to avoid duplicate downloads
            if url in download_cache:
                cached_local_path = download_cache[url]
                self.logger.debug(f"Using cached download for {url}: {cached_local_path}")
                return link_type, url, alt_text, cached_local_path, True

            try:
                # Use the existing download functions but with better error handling
                local_path = download_file(
                    url, article_folder_path, link_type, self.download_files
                )
                if local_path:
                    # Cache the successful download
                    download_cache[url] = local_path
                    return link_type, url, alt_text, local_path, True
                else:
                    return link_type, url, alt_text, None, False
            except Exception as e:
                self.logger.debug(f"Skipped {link_type} download for {url}: {e}")
                return link_type, url, alt_text, None, False

        # Process media with concurrency
        if media_links:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_link = {
                    executor.submit(process_single_media, link_info): link_info
                    for link_info in media_links
                }

                for future in as_completed(future_to_link):
                    link_info = future_to_link[future]
                    try:
                        link_type, url, alt_text, local_path, success = future.result()
                        if success and local_path:
                            processed_results[url] = local_path
                        else:
                            # Clean up broken media references when download fails
                            processed_results[url] = None
                    except Exception as e:
                        self.logger.debug(f"Error processing media {link_info}: {e}")
                        processed_results[url] = None

        return processed_results
    
    def create_markdown_link_replacement(
        self,
        markdown_content: str,
        original_url: str,
        local_path: str,
        fallback_text: str,
        is_image: bool = False
    ) -> str:
        """
        Replace markdown link/image references with local paths.

        Consolidates URL replacement logic. Handles both image and link
        syntax with proper escaping to prevent f-string syntax errors.

        Args:
            markdown_content: Markdown text to process
            original_url: URL to replace (will be escaped for regex)
            local_path: Local file path to use instead
            fallback_text: Text to use if link text is empty
            is_image: True for image syntax (!![]()), False for link syntax ([])

        Returns:
            Updated markdown content with replaced URLs

        Example:
            >>> content = "![](http://example.com/img.jpg)"
            >>> result = processor.create_markdown_link_replacement(
            ...     content, "http://example.com/img.jpg",
            ...     "images/img.jpg", "image", is_image=True
            ... )
            >>> print(result)
            ![image](images/img.jpg)
        """
        import re

        escaped_url = re.escape(original_url)
        prefix = "!" if is_image else ""

        # Strategy 1: Replace [text](url) or ![text](url) with proper escaping
        pattern = rf"{prefix}\[([^\]]*)\]\({escaped_url}\)"

        def replacement_func(match):
            """Create replacement text with fallback for empty groups."""
            link_text = match.group(1) if match.group(1) else fallback_text
            return f"{prefix}[{link_text}]({local_path})"

        markdown_content = re.sub(pattern, replacement_func, markdown_content)

        # Strategy 2: Direct URL replacement in parentheses
        markdown_content = markdown_content.replace(
            f"]({original_url})", f"]({local_path})"
        )

        # Strategy 3: Replace any remaining instances
        markdown_content = markdown_content.replace(original_url, local_path)

        return markdown_content

    def _replace_media_reference(
        self, markdown_content: str, original_url: str, local_path: str
    ) -> str:
        """
        Replace a media reference in markdown content.

        Args:
            markdown_content: Original markdown content
            original_url: The original media URL
            local_path: Path to the downloaded local file

        Returns:
            Updated markdown content
        """
        if not local_path:
            return markdown_content

        # Try as image first, then as regular link
        # This handles most cases where we don't know the exact type
        markdown_content = self.create_markdown_link_replacement(
            markdown_content, original_url, local_path, "image", is_image=True
        )

        # Also handle non-image links (documents, etc.)
        markdown_content = self.create_markdown_link_replacement(
            markdown_content, original_url, local_path, "document", is_image=False
        )

        return markdown_content

    def is_pdf_url(self, url: str) -> bool:
        """
        Check if a URL points specifically to a PDF file.

        Args:
            url: URL to check

        Returns:
            True if URL points to a PDF file, False otherwise

        Example:
            >>> processor.is_pdf_url("https://example.com/doc.pdf")
            True
            >>> processor.is_pdf_url("https://example.com/page.html")
            False
        """
        try:
            parsed_url = urlparse(url)
            if parsed_url.path:
                return parsed_url.path.lower().endswith(".pdf")
        except Exception:
            pass
        return False

    def cleanup_empty_images_folder(self, article_folder_path: str) -> None:
        """
        Remove empty images folder if no images were downloaded.

        Args:
            article_folder_path: Path to article folder

        Example:
            >>> processor.cleanup_empty_images_folder("/path/to/article")
            # Removes /path/to/article/images if empty
        """
        images_folder = os.path.join(article_folder_path, "images")
        if os.path.exists(images_folder):
            # Check if folder is empty
            if not os.listdir(images_folder):
                try:
                    os.rmdir(images_folder)
                    self.logger.debug(
                        f"Removed empty images folder: {images_folder}"
                    )
                except OSError as e:
                    self.logger.debug(f"Could not remove images folder: {e}")

    def should_skip_image(
        self, img_tag, img_src: str, ui_patterns: dict
    ) -> bool:
        """
        Determine if an image should be skipped based on UI element patterns.

        Filters out:
        - UI icons (logos, avatars, buttons)
        - Tracking pixels (1x1, analytics)
        - Social media badges
        - Advertisement placeholders

        Args:
            img_tag: BeautifulSoup img tag
            img_src: Image source URL
            ui_patterns: Dictionary of patterns to match against
                - class_patterns: CSS class names to skip
                - id_patterns: Element ID patterns to skip
                - alt_patterns: Alt text patterns to skip
                - src_patterns: URL patterns to skip

        Returns:
            True if image should be skipped (is likely a UI element)

        Example:
            >>> ui_patterns = {
            ...     "class_patterns": ["icon", "logo"],
            ...     "id_patterns": ["avatar"],
            ...     "alt_patterns": ["badge"],
            ...     "src_patterns": ["pixel"]
            ... }
            >>> processor.should_skip_image(img_tag, "logo.png", ui_patterns)
            True
        """
        # Check class attributes
        img_classes = img_tag.get("class", [])
        if isinstance(img_classes, list):
            img_classes = " ".join(img_classes).lower()
        else:
            img_classes = str(img_classes).lower()

        for pattern in ui_patterns["class_patterns"]:
            if pattern in img_classes:
                return True

        # Check id attribute
        img_id = str(img_tag.get("id", "")).lower()
        for pattern in ui_patterns["id_patterns"]:
            if pattern in img_id:
                return True

        # Check alt text
        alt_text = str(img_tag.get("alt", "")).lower()
        for pattern in ui_patterns["alt_patterns"]:
            if pattern in alt_text:
                return True

        # Check src URL for common UI image names
        src_lower = img_src.lower()
        for pattern in ui_patterns["src_patterns"]:
            if pattern in src_lower:
                return True

        # Check if image is very likely a tracking pixel or beacon
        if any(
            term in src_lower
            for term in ["pixel", "beacon", "track", "analytics", "1x1"]
        ):
            return True

        return False

    def cleanup_failed_media_reference(
        self, markdown_content: str, url: str, link_type: str, alt_text: str
    ) -> str:
        """
        Clean up markdown references to failed media downloads.

        Replaces failed media links with informative text indicating
        the media is unavailable.

        Args:
            markdown_content: Markdown text to clean
            url: Failed media URL
            link_type: Type of media (image, document, audio, video)
            alt_text: Alternative text for the media

        Returns:
            Cleaned markdown with unavailable notice

        Example:
            >>> content = "![Image](http://fail.com/img.jpg)"
            >>> result = processor.cleanup_failed_media_reference(
            ...     content, "http://fail.com/img.jpg", "image", "Photo"
            ... )
            >>> print(result)
            [Photo](http://fail.com/img.jpg) *(image unavailable)*
        """
        import re

        # Create fallback text
        if link_type == "image":
            # For images, convert to regular link with note
            fallback = f"[{alt_text}]({url}) *({link_type} unavailable)*"

            # Remove image syntax variations
            escaped_url = re.escape(url)
            patterns = [
                rf"!\[([^\]]*)\]\({escaped_url}\)",
                rf"\[([^\]]*)\]\({escaped_url}\)",
            ]

            for pattern in patterns:
                markdown_content = re.sub(
                    pattern,
                    lambda m: f"[{m.group(1)}]({url}) *({link_type} unavailable)*",
                    markdown_content,
                )
        else:
            # For documents/audio/video, add unavailable note
            escaped_url = re.escape(url)
            pattern = rf"\[([^\]]*)\]\({escaped_url}\)"
            markdown_content = re.sub(
                pattern,
                lambda m: f"[{m.group(1)}]({url}) *({link_type} unavailable)*",
                markdown_content,
            )

        return markdown_content
    def parse_srcset(self, srcset: str) -> str:
        """
        Parse srcset attribute and return the highest resolution image URL.

        Args:
            srcset: HTML srcset attribute value

        Returns:
            URL of highest resolution image

        Example:
            >>> srcset = "img.jpg 1x, img@2x.jpg 2x, img@3x.jpg 3x"
            >>> processor.parse_srcset(srcset)
            'img@3x.jpg'
        """
        if not srcset:
            return ""

        # Split by comma and parse each source
        sources = []
        for source in srcset.split(","):
            source = source.strip()
            if " " in source:
                url, descriptor = source.rsplit(" ", 1)
                url = url.strip()
                descriptor = descriptor.strip()

                # Extract width from descriptor (e.g., "1536w" -> 1536)
                if descriptor.endswith("w"):
                    try:
                        width = int(descriptor[:-1])
                        sources.append((width, url))
                    except ValueError:
                        continue
                # Handle pixel density (e.g., "2x" -> 2)
                elif descriptor.endswith("x"):
                    try:
                        density = float(descriptor[:-1])
                        # Convert density to pseudo-width for comparison
                        sources.append((int(density * 1000), url))
                    except ValueError:
                        continue

        # Return the URL with the highest width, or first URL if no width descriptors
        if sources:
            sources.sort(key=lambda x: x[0], reverse=True)  # Sort by width descending
            return sources[0][1]

        # Fallback: return first URL from srcset
        first_source = srcset.split(",")[0].strip()
        return first_source.split(" ")[0] if " " in first_source else first_source

    def remove_image_from_markdown(
        self, markdown_content: str, image_src: str
    ) -> str:
        """
        Remove image references from markdown content when download fails.

        Args:
            markdown_content: Markdown text to process
            image_src: Image source URL to remove

        Returns:
            Markdown with image references removed

        Example:
            >>> content = "Text\\n![Image](http://example.com/img.jpg)\\nMore"
            >>> result = processor.remove_image_from_markdown(
            ...     content, "http://example.com/img.jpg"
            ... )
            >>> "![Image]" not in result
            True
        """
        import re

        # Escape special regex characters in the image source
        escaped_src = re.escape(image_src)

        # Pattern 1: Remove standard markdown image syntax ![alt](src) and ![alt](src "title")
        pattern1 = rf"!\[[^\]]*\]\({escaped_src}(?:\s+\"[^\"]*\")?\)"
        markdown_content = re.sub(pattern1, "", markdown_content)

        # Pattern 2: Remove link syntax that might reference an image [text](src)
        # Only remove if the link text suggests it's an image (contains image-related keywords)
        pattern2 = rf"\[([^\]]*)\]\({escaped_src}\)"

        def replace_if_image_link(match):
            link_text = match.group(1)  # Get the text between brackets
            image_keywords = [
                "image",
                "img",
                "avatar",
                "photo",
                "picture",
                "icon",
                "logo",
            ]
            if any(
                keyword.lower() in link_text.lower() for keyword in image_keywords
            ):
                return ""  # Remove the entire link
            # Keep non-image links but remove broken URL
            return f"[{link_text}]()"

        markdown_content = re.sub(pattern2, replace_if_image_link, markdown_content)

        # Pattern 3: Only remove direct references to the URL if it looks like an image URL
        if any(
            ext in image_src.lower()
            for ext in [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".webp",
                ".svg",
                "_next/image",
            ]
        ):
            markdown_content = markdown_content.replace(image_src, "")

        # Clean up any empty image references that might be left
        markdown_content = re.sub(r"!\[\]\(\)", "", markdown_content)
        markdown_content = re.sub(r"\[\]\(\)", "", markdown_content)

        # Clean up multiple consecutive newlines that might result from removals
        markdown_content = re.sub(r"\n\s*\n\s*\n+", "\n\n", markdown_content)

        return markdown_content

    def process_document_links(
        self,
        soup: BeautifulSoup,
        markdown_content: str,
        article_folder_path: str,
        base_url: str,
    ) -> str:
        """
        Process and download document files linked in the content.

        Args:
            soup: BeautifulSoup parsed HTML
            markdown_content: Markdown content to update
            article_folder_path: Path to save downloaded documents
            base_url: Base URL for resolving relative links

        Returns:
            Updated markdown content with local document paths

        Example:
            >>> # Downloads PDFs and updates markdown links
            >>> updated_md = processor.process_document_links(
            ...     soup, markdown, "/path/to/article", "https://example.com"
            ... )
        """
        from .downloader import download_file, is_document_url

        # Find all anchor tags with href attributes
        link_tags = soup.find_all("a", href=True)

        for link in link_tags:
            href = link.get("href")
            if href:
                # Skip obviously invalid URLs
                if (
                    href.startswith("javascript:")
                    or href.startswith("mailto:")
                    or href.startswith("#")
                    or href.startswith("data:")
                ):
                    continue

                # Convert relative URLs to absolute
                original_href = href  # Keep the original for replacement
                if href.startswith("/"):
                    href = urljoin(base_url, href)
                elif not href.startswith(("http://", "https://")):
                    # Skip relative paths that don't start with /
                    continue

                # Check if this is a document link (only download if --files flag is set)
                try:
                    if is_document_url(href) and self.download_files:
                        # Download the document
                        local_path = download_file(
                            href,
                            article_folder_path,
                            "document",
                            self.download_files,
                        )
                        if local_path:
                            # Replace the link reference in markdown
                            link_text = link.get_text().strip()
                            if not link_text:
                                link_text = "document"

                            # Replace document link references with local path
                            markdown_content = self.create_markdown_link_replacement(
                                markdown_content,
                                original_href,
                                local_path,
                                link_text,
                                is_image=False,
                            )
                except Exception as e:
                    self.logger.debug(
                        f"Could not process document link {href}: {e}"
                    )
                    continue

        return markdown_content
