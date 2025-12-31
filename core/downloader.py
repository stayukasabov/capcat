#!/usr/bin/env python3
"""
Media downloader for Capcat.
Handles downloading of images, documents, audio, and video files.
"""

import os
from typing import Optional
from urllib.parse import urlparse

import requests

from .config import get_config
from .exceptions import FileSystemError, NetworkError
from .logging_config import get_logger
from .retry import fast_media_retry, network_retry

# Create a session for connection pooling
config = get_config()
session = requests.Session()
session.headers.update({"User-Agent": config.network.user_agent})

# Configure session for better performance
session.mount(
    "http://",
    requests.adapters.HTTPAdapter(
        pool_connections=config.network.pool_connections,
        pool_maxsize=config.network.pool_maxsize,
    ),
)
session.mount(
    "https://",
    requests.adapters.HTTPAdapter(
        pool_connections=config.network.pool_connections,
        pool_maxsize=config.network.pool_maxsize,
    ),
)


def is_document_url(url: str) -> bool:
    """Check if a URL points to a document file using file extension only (fast)."""
    # Skip data URLs and other non-network URLs
    if (
        url.startswith("data:")
        or url.startswith("javascript:")
        or url.startswith("mailto:")
    ):
        return False

    try:
        parsed_url = urlparse(url)
        # Check file extension (case insensitive) - fast local check only
        path_lower = parsed_url.path.lower()
        # Don't treat HTML files as documents to download
        if path_lower.endswith((".html", ".htm")):
            return False
        return path_lower.endswith(
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
        )
    except Exception:
        return False


def is_audio_url(url: str) -> bool:
    """Check if a URL points to an audio file using file extension only (fast)."""
    try:
        parsed_url = urlparse(url)
        # Check file extension (case insensitive) - fast local check only
        path_lower = parsed_url.path.lower()
        return path_lower.endswith(
            (".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".wma", ".opus")
        )
    except Exception:
        return False


def is_video_url(url: str) -> bool:
    """Check if a URL points to a video file using file extension only (fast)."""
    try:
        parsed_url = urlparse(url)
        # Check file extension (case insensitive) - fast local check only
        path_lower = parsed_url.path.lower()
        return path_lower.endswith(
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
        )
    except Exception:
        return False


def is_image_url(url: str) -> bool:
    """Check if a URL points to an image file using file extension only (fast)."""
    # Skip data URLs and other non-network URLs
    if (
        url.startswith("data:")
        or url.startswith("javascript:")
        or url.startswith("mailto:")
    ):
        return False

    try:
        parsed_url = urlparse(url)
        # Check file extension (case insensitive) - fast local check only
        path_lower = parsed_url.path.lower()
        image_extensions = (
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
            ".jpe",
            ".jfif",
        )
        return path_lower.endswith(image_extensions)
    except Exception:
        return False


@fast_media_retry
def download_file(
    file_url: str,
    folder_path: str,
    file_type: str,
    media_enabled: bool = False,
) -> Optional[str]:
    """Download a file (image, document, audio, or video) and save it to the appropriate folder.

    Args:
        file_url: URL of the file to download
        folder_path: Path to the article folder
        file_type: Type of file ('image', 'audio', 'video', 'document')
        media_enabled: Whether --media flag is enabled (affects size limits)
    """
    logger = get_logger(__name__)
    try:
        # Determine the appropriate folder path (but don't create it yet)
        if file_type == "image":
            files_folder = os.path.join(folder_path, "images")
        elif file_type == "audio":
            files_folder = os.path.join(folder_path, "audio")
        elif file_type == "video":
            files_folder = os.path.join(folder_path, "video")
        else:  # document types like PDF, DOC, etc.
            files_folder = os.path.join(folder_path, "files")

        # Make a single HEAD request to check size and content-type
        response = None
        content_length = None
        content_type = None

        head_response = None
        try:
            head_response = session.head(
                file_url, timeout=config.network.head_request_timeout
            )
            head_response.raise_for_status()
            content_length = head_response.headers.get("content-length")
            content_type = head_response.headers.get(
                "content-type", ""
            ).lower()

            # Check if content type suggests this should be skipped (e.g., HTML)
            if "text/html" in content_type:
                logger.debug(f"Skipping HTML content for {file_url}")
                return None

            # Apply size limits
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)

                if file_type == "image" and not media_enabled:
                    max_size_mb = (
                        3  # 3MB limit for images when --media flag is NOT used
                    )
                    if size_mb > max_size_mb:
                        logger.debug(
                            f"Skipping large image: {file_url} ({size_mb:.1f}MB)"
                        )
                        return None
                else:
                    max_size_mb = 20  # 20MB limit for all other cases
                    if size_mb > max_size_mb:
                        logger.info(
                            f"Skipping {file_type} download: {file_url} is {size_mb:.1f}MB (exceeds {max_size_mb}MB limit)"
                        )
                        return None
        except Exception as e:
            logger.debug(
                f"HEAD request failed for {file_url}: {e}, proceeding with download"
            )
            # Continue with download if HEAD fails
        finally:
            if head_response:
                head_response.close()

        # Now do the actual download
        try:
            response = session.get(
                file_url,
                timeout=config.network.media_download_timeout,
                stream=True,
            )
            response.raise_for_status()

            # If we didn't get content-type from HEAD, get it from GET response
            if not content_type:
                content_type = response.headers.get("content-type", "").lower()
                # Final check for HTML content
                if "text/html" in content_type:
                    logger.debug(f"Skipping HTML content for {file_url}")
                    response.close()
                    return None

        except requests.exceptions.RequestException as e:
            logger.debug(
                f"Could not download {file_type} from {file_url}: {e}"
            )
            raise NetworkError(file_url, e)

        # Get filename from URL or create one
        parsed_url = urlparse(file_url)
        filename = os.path.basename(parsed_url.path)

        # Handle URL-encoded filenames (e.g., Substack URLs that contain encoded URLs)
        if filename and "%" in filename:
            try:
                from urllib.parse import unquote

                decoded_filename = unquote(filename)
                # If the decoded filename looks like a URL, extract the actual filename
                if decoded_filename.startswith(("http://", "https://")):
                    decoded_parsed = urlparse(decoded_filename)
                    actual_filename = os.path.basename(decoded_parsed.path)
                    if actual_filename and "." in actual_filename:
                        filename = actual_filename
                        logger.debug(
                            f"Extracted clean filename '{filename}' from URL-encoded path"
                        )
                elif "." in decoded_filename:
                    filename = decoded_filename
            except Exception as e:
                logger.debug(f"Failed to decode URL-encoded filename: {e}")
                # Continue with original filename

        # Prevent HTML files from being downloaded as documents
        if filename and filename.lower().endswith((".html", ".htm")):
            logger.debug(f"Skipping HTML file download for {file_url}")
            return None

        # If no filename in URL, create one based on content type (already retrieved)
        if not filename or "." not in filename:
            if not content_type:
                content_type = response.headers.get("content-type", "")

            if file_type == "image":
                if "jpeg" in content_type or "jpg" in content_type:
                    filename = "image_1.jpg"
                elif "png" in content_type:
                    filename = "image_1.png"
                elif "gif" in content_type:
                    filename = "image_1.gif"
                else:
                    filename = "image_1.jpg"
            elif file_type == "audio":
                if "mpeg" in content_type or "mp3" in content_type:
                    filename = f"audio_{1}.mp3"
                elif "wav" in content_type:
                    filename = f"audio_{1}.wav"
                elif "ogg" in content_type:
                    filename = f"audio_{1}.ogg"
                elif "flac" in content_type:
                    filename = f"audio_{1}.flac"
                else:
                    filename = f"audio_{1}.mp3"
            elif file_type == "video":
                if "mp4" in content_type:
                    filename = f"video_{1}.mp4"
                elif "avi" in content_type:
                    filename = f"video_{1}.avi"
                elif "quicktime" in content_type:
                    filename = f"video_{1}.mov"
                elif "webm" in content_type:
                    filename = f"video_{1}.webm"
                else:
                    filename = f"video_{1}.mp4"
            else:  # document
                if "pdf" in content_type:
                    filename = f"document_{1}.pdf"
                elif "msword" in content_type:
                    filename = f"document_{1}.doc"
                elif "officedocument" in content_type:
                    if "word" in content_type:
                        filename = f"document_{1}.docx"
                    elif "excel" in content_type:
                        filename = f"document_{1}.xlsx"
                    elif "presentation" in content_type:
                        filename = f"document_{1}.pptx"
                    else:
                        filename = f"document_{1}.docx"  # default to docx
                elif "rtf" in content_type:
                    filename = f"document_{1}.rtf"
                elif "text/plain" in content_type:
                    filename = f"document_{1}.txt"
                elif "text/html" in content_type:
                    # HTML files should not be downloaded as documents
                    # This should not happen, but if it does, we should skip them
                    logger.debug(
                        f"Skipping HTML file download for {file_url} with content type {content_type}"
                    )
                    return None
                elif "opendocument" in content_type:
                    if "text" in content_type:
                        filename = f"document_{1}.odt"
                    elif "spreadsheet" in content_type:
                        filename = f"document_{1}.ods"
                    elif "presentation" in content_type:
                        filename = f"document_{1}.odp"
                    else:
                        filename = f"document_{1}.odt"  # default to odt
                else:
                    filename = f"document_{1}.bin"

        # Create the folder only now that we have validated content to save
        try:
            os.makedirs(files_folder, exist_ok=True)
        except OSError as e:
            raise FileSystemError("create directory", files_folder, e)

        # Ensure unique filename (now that folder exists)
        base_name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(files_folder, filename)):
            filename = f"{base_name}_{counter}{ext}"
            counter += 1

        # If the file has no extension, try to determine it from content type (already retrieved)
        if not ext and content_type:
            content_type_clean = content_type.split(";")[0].strip()
            extension_map = {
                "application/pdf": ".pdf",
                "application/msword": ".doc",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
                "application/vnd.ms-excel": ".xls",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
                "application/vnd.ms-powerpoint": ".ppt",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
                "text/plain": ".txt",
                # HTML files should not be downloaded as documents
                # 'text/html': '.html',  # Removed this line
                "text/rtf": ".rtf",
                "application/rtf": ".rtf",
                "application/vnd.oasis.opendocument.text": ".odt",
                "application/vnd.oasis.opendocument.spreadsheet": ".ods",
                "application/vnd.oasis.opendocument.presentation": ".odp",
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "image/gif": ".gif",
                "image/bmp": ".bmp",
                "image/tiff": ".tiff",
                "image/webp": ".webp",
                "audio/mpeg": ".mp3",
                "audio/wav": ".wav",
                "audio/ogg": ".ogg",
                "video/mp4": ".mp4",
                "video/avi": ".avi",
                "video/quicktime": ".mov",
                "video/webm": ".webm",
            }
            if content_type_clean in extension_map:
                filename = base_name + extension_map[content_type_clean]
                ext = extension_map[content_type_clean]

        # Save the file using streaming to handle large files
        file_path = os.path.join(files_folder, filename)
        try:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.debug(f"Successfully downloaded {file_type}: {filename}")
        except OSError as e:
            raise FileSystemError("write file", file_path, e)
        finally:
            response.close()  # Ensure connection is closed

        # Return the relative path for markdown linking
        if file_type == "image":
            return os.path.join("images", filename)
        elif file_type == "audio":
            return os.path.join("audio", filename)
        elif file_type == "video":
            return os.path.join("video", filename)
        else:
            return os.path.join("files", filename)

    except (NetworkError, FileSystemError):
        # These are already logged by the retry decorator
        raise
    except Exception as e:
        logger.debug(f"Could not download {file_type} from {file_url}: {e}")
        raise
