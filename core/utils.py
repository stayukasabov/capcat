#!/usr/bin/env python3
"""
Core utilities for the Capcat application.
Handles file system operations, URL processing, and other shared functionalities.
"""

import os
import re
from urllib.parse import urlparse

from .config import get_config


def get_source_folder_name(source_code: str) -> str:
    """
    Convert source code to proper folder name format using display_name from source configurations.

    Args:
        source_code (str): Source code (e.g., 'hn', 'aljazeera', 'bbc')

    Returns:
        str: Proper folder name (e.g., 'Hacker-News', 'Al-Jazeera', 'BBC-News')
    """
    # Try to get display_name from source registry first
    try:
        from core.source_system.source_registry import get_source_registry
        registry = get_source_registry()
        config = registry.get_source_config(source_code)
        if config and hasattr(config, 'display_name'):
            # Use official display_name directly, sanitized for path usage
            return config.display_name.replace(' ', '_')
    except Exception:
        pass

    # Try legacy source configurations
    try:
        from .source_configs import SOURCE_CONFIGURATIONS
        if source_code in SOURCE_CONFIGURATIONS:
            config = SOURCE_CONFIGURATIONS[source_code]
            display_name = config.get("display_name") or config.get("name")
            if display_name:
                return display_name.replace(' ', '_')
    except ImportError:
        pass

    # Only use registered sources - no fallback mapping
    return source_code.title()


def sanitize_filename(title: str, max_length: int = None, intelligent_truncation: bool = True) -> str:
    """
    Sanitize a string to be used as a filename with intelligent title truncation.

    Args:
        title (str): The title to sanitize.
        max_length (int): Maximum length for the filename.
        intelligent_truncation (bool): Whether to use intelligent truncation for long titles.

    Returns:
        str: A sanitized filename string.
    """
    # First apply intelligent truncation if enabled and title is long
    if intelligent_truncation:
        if max_length is None:
            max_length = get_config().processing.max_filename_length
        if len(title) > max_length:
            title = truncate_title_intelligently(title, max_length)

    # Remove invalid characters for filenames and common special characters
    safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1F!@#$%^&()+=\[\]{}~`]', "", title)
    # Remove leading/trailing whitespace and dots
    safe_title = safe_title.strip(". ")

    # Final length check (fallback for edge cases)
    if max_length is None:
        max_length = get_config().processing.max_filename_length
    if len(safe_title) > max_length:
        safe_title = safe_title[:max_length].rstrip(". ")

    # If empty, use a default
    if not safe_title:
        safe_title = "untitled"
    return safe_title


def truncate_title_intelligently(title: str, max_length: int = 200) -> str:
    """
    Intelligently truncate article titles to a reasonable length for folder names and display.

    Preserves meaning by:
    - Removing redundant prefixes (GitHub - user/repo: actual title)
    - Truncating at word boundaries when possible
    - Removing URL references and redundant information
    - Keeping the most meaningful part of the title

    Args:
        title (str): The original title to truncate
        max_length (int): Maximum desired length (default: 200 characters for HTML cards)

    Returns:
        str: Intelligently truncated title

    Examples:
        >>> truncate_title_intelligently("GitHub - xyflow/xyflow: React Flow | Svelte Flow - Powerful open source libraries for building node-based UIs with React (https://reactflow.dev) or Svelte (https://svelteflow.dev). Ready out-of-the-box and infinitely customizable.")
        "Powerful open source libraries for building node-based UIs with React"

        >>> truncate_title_intelligently("A" * 100)
        "AAAA..." (100 chars unchanged with 200 default)

        >>> truncate_title_intelligently("A" * 100, max_length=80)
        "AAAA..." (truncated to 80 chars)
    """
    if not title or len(title) <= max_length:
        return title

    # Step 1: Remove common redundant patterns
    # Remove "GitHub - user/repo:" pattern
    title = re.sub(r'^GitHub\s*-\s*[^:]+:\s*', '', title)

    # Remove URL references in parentheses
    title = re.sub(r'\s*\([^)]*https?://[^)]*\)', '', title)

    # Remove standalone URLs
    title = re.sub(r'\s*https?://\S+', '', title)

    # Step 2: Clean up common separators and redundant information
    # Split on common separators and choose the most meaningful part
    separators = [' - ', ' | ', ' – ', ' — ', ': ']
    parts = [title]

    for sep in separators:
        if sep in title:
            parts = title.split(sep)
            break

    # Step 3: Choose the most meaningful part
    if len(parts) > 1:
        # Remove very short parts (likely site names or prefixes)
        meaningful_parts = [part.strip() for part in parts if len(part.strip()) > 15]

        if meaningful_parts:
            # Choose the longest meaningful part (usually contains most content)
            title = max(meaningful_parts, key=len)
        else:
            # If no meaningful parts, use the longest part
            title = max(parts, key=len).strip()

    # Step 2.5: Remove common redundant phrases and clean up
    # Remove "or [platform]" endings for software libraries
    title = re.sub(r'\s+or\s+\w+(?:\s+\([^)]*\))?\s*(?:Ready|Available|\..*)?$', '', title)
    # Remove ". Ready..." and similar trailing phrases
    title = re.sub(r'\.\s*Ready.*$', '', title)
    title = re.sub(r'\.\s*Available.*$', '', title)

    # Step 4: Truncate at word boundary if still too long
    if len(title) > max_length:
        # Try to truncate at sentence end first
        sentences = re.split(r'[.!?]\s+', title)
        if len(sentences) > 1 and len(sentences[0]) <= max_length:
            title = sentences[0]
        else:
            # Truncate at word boundary
            words = title.split()
            truncated_words = []
            current_length = 0

            for word in words:
                # Account for space between words
                word_length = len(word) + (1 if truncated_words else 0)
                if current_length + word_length <= max_length:
                    truncated_words.append(word)
                    current_length += word_length
                else:
                    break

            if truncated_words:
                title = ' '.join(truncated_words)
            else:
                # If even the first word is too long, hard truncate
                title = title[:max_length].rstrip()

    # Step 5: Clean up the result
    title = title.strip(' .-')

    # Ensure we don't return empty string
    if not title:
        title = "Article"

    return title


def create_output_directory(base_path: str, source_prefix: str) -> str:
    """
    Create the main output directory for a source with the current date (YYYY-MM-DD format).

    Args:
        base_path (str): The base directory path.
        source_prefix (str): The prefix for the source (e.g., 'hn', 'lb').

    Returns:
        str: The full path to the created directory.
    """
    from datetime import datetime

    current_date = datetime.now().strftime("%Y-%m-%d")
    folder_name = get_source_folder_name(source_prefix)
    dir_name = f"{folder_name}_{current_date}"
    full_path = os.path.join(base_path, dir_name)
    os.makedirs(full_path, exist_ok=True)
    return full_path


def create_output_directory_capcat(
    base_path: str, source_prefix: str
) -> str:
    """
    Create the main output directory for a source with the current date (DD-MM-YYYY format).

    Args:
        base_path (str): The base directory path.
        source_prefix (str): The prefix for the source (e.g., 'hn', 'lb').

    Returns:
        str: The full path to the created directory.
    """
    from datetime import datetime

    current_date = datetime.now().strftime("%d-%m-%Y")
    folder_name = get_source_folder_name(source_prefix)
    dir_name = f"{folder_name}_{current_date}"
    full_path = os.path.join(base_path, dir_name)
    os.makedirs(full_path, exist_ok=True)
    return full_path


def create_batch_output_directory(source_prefix: str) -> str:
    """
    Create the proper nested directory structure for batch processing (fetch/bundle commands).
    Creates: ../News/news_DD-MM-YYYY/source_DD-MM-YYYY/

    Args:
        source_prefix (str): The prefix for the source (e.g., 'hn', 'lb').

    Returns:
        str: The full path to the created source directory.
    """
    import os
    from datetime import datetime

    # Get current date in DD-MM-YYYY format
    current_date = datetime.now().strftime("%d-%m-%Y")

    # Determine project root (one level up from Application directory)
    application_dir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    project_root = os.path.dirname(application_dir)

    # Create News directory structure: ../News/News_DD-MM-YYYY/ (check for existing capitalized first)
    news_base_dir = os.path.join(project_root, "News")

    # Check if capitalized version exists first
    capitalized_news_date_dir = os.path.join(
        news_base_dir, f"News_{current_date}"
    )
    lowercase_news_date_dir = os.path.join(
        news_base_dir, f"news_{current_date}"
    )

    if os.path.exists(capitalized_news_date_dir):
        news_date_dir = capitalized_news_date_dir
    else:
        news_date_dir = capitalized_news_date_dir  # Use capitalized by default

    # Create the nested directory structure
    os.makedirs(news_date_dir, exist_ok=True)

    # Create source-specific directory within the date directory
    folder_name = get_source_folder_name(source_prefix)
    source_dir_name = f"{folder_name}_{current_date}"
    source_dir_path = os.path.join(news_date_dir, source_dir_name)
    os.makedirs(source_dir_path, exist_ok=True)

    return source_dir_path


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
