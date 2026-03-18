#!/usr/bin/env python3
"""
Storage management component for Capcat.

Handles file system operations, folder creation, and content storage
independently from the main article fetching logic.
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

from .logging_config import get_logger
from .utils import sanitize_filename

_logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level filename helpers — single source of truth for naming convention
# ---------------------------------------------------------------------------

def article_md_filename(title: str) -> str:
    """Return sanitized markdown filename for an article (e.g. 'My-Title.md').

    The base stem is truncated at 200 chars before adding the extension.
    Spaces are replaced with hyphens.
    """
    return sanitize_filename(title, max_length=200).replace(" ", "-") + ".md"


def comments_md_filename(title: str) -> str:
    """Return sanitized markdown filename for comments (e.g. 'My-Title-Comments.md').

    The base stem is truncated at 200 chars; '-Comments.md' is appended after truncation.
    Spaces are replaced with hyphens.
    """
    return sanitize_filename(title, max_length=200).replace(" ", "-") + "-Comments.md"


def find_article_md(folder: Path) -> "Path | None":
    """Return the article markdown path in folder, or None if absent.

    Non-recursive: only searches direct children of folder.
    Returns the first .md file whose stem does not end in '-Comments'.
    """
    return next(
        (p for p in folder.glob("*.md") if not p.stem.endswith("-Comments")),
        None,
    )


def find_comments_md(folder: Path) -> "Path | None":
    """Return the comments markdown path in folder, or None if absent."""
    return next(folder.glob("*-Comments.md"), None)


def inject_comments_wikilink(article_folder_path: str, comments_stem: str) -> bool:
    """Inject a → [[comments_stem|Comments]] wikilink at top and bottom of the article .md.

    Idempotent: if line 1 already starts with '→ [[', returns True without modifying.
    Returns False on any error without raising.
    Module-level function, not a StorageManager method.
    """
    try:
        article_path = find_article_md(Path(article_folder_path))
        if article_path is None:
            _logger.warning(f"No article .md found in: {article_folder_path}")
            return False

        content = article_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        if not lines:
            _logger.warning(f"Article file is empty: {article_path}")
            return False
        if lines[0].startswith("→ [["):
            _logger.debug(f"Wikilink already present: {article_path}")
            return True

        content = content.rstrip()
        wikilink = f"→ [[{comments_stem}|Comments]]"
        new_content = f"{wikilink}\n\n{content}\n\n{wikilink}\n"
        article_path.write_text(new_content, encoding="utf-8")
        return True

    except Exception as e:
        _logger.warning(f"Failed to inject wikilink into {article_folder_path}: {e}")
        return False


class StorageManager:
    """
    Manages all file system operations for article storage.
    """
    
    def __init__(self):
        self.logger = get_logger("StorageManager")
    
    def create_article_folder(self, base_folder: str, title: str) -> str:
        """
        Create a folder for storing an article's content.
        
        Args:
            base_folder: Base directory to create the article folder in
            title: Article title to use for folder name
            
        Returns:
            Path to the created article folder
        """
        safe_title = sanitize_filename(title)
        article_folder_name = self._get_unique_folder_name(base_folder, safe_title)
        article_folder_path = os.path.join(base_folder, article_folder_name)
        
        try:
            os.makedirs(article_folder_path, exist_ok=True)
            self.logger.debug(f"Created article folder: {article_folder_path}")
        except Exception as e:
            self.logger.error(f"Failed to create directory {article_folder_path}: {e}")
            raise
        
        # Create mandatory images folder for ALL articles
        images_folder = os.path.join(article_folder_path, "images")
        try:
            os.makedirs(images_folder, exist_ok=True)
            self.logger.debug(f"Created mandatory images folder: {images_folder}")
        except Exception as e:
            self.logger.debug(f"Failed to create images directory {images_folder}: {e}")
            # Continue processing - images folder creation failure shouldn't stop article processing
        
        return article_folder_path
    
    def save_article_content(self, article_folder_path: str, content: str, title: str) -> str:
        """
        Save article content to the article folder.

        Args:
            article_folder_path: Path to the article folder
            content: Content to save
            title: Article title used to generate the markdown filename

        Returns:
            Path to the saved content file
        """
        filename = os.path.join(article_folder_path, article_md_filename(title))
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.debug(f"Saved article content to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Failed to save article content to {filename}: {e}")
            raise
    
    def cleanup_empty_images_folder(self, article_folder_path: str) -> None:
        """
        Remove images folder if it exists but is empty.
        
        Args:
            article_folder_path: Path to the article folder
        """
        images_folder = os.path.join(article_folder_path, "images")
        try:
            if os.path.exists(images_folder) and os.path.isdir(images_folder):
                # Check if folder is empty (no files)
                if not os.listdir(images_folder):
                    os.rmdir(images_folder)
                    self.logger.debug(f"Removed empty images folder: {images_folder}")
        except Exception as e:
            self.logger.debug(f"Could not remove empty images folder {images_folder}: {e}")
    
    def _get_unique_folder_name(self, base_folder: str, base_title: str) -> str:
        """
        Get folder name - always returns base_title to allow overwrite.
        When user runs repeatedly, content is replaced instead of creating duplicates.
        """
        try:
            # ALWAYS use the original name (allow overwrite)
            # This prevents _2, _3 numbered folders when re-running fetch/bundle
            return base_title
        except Exception as e:
            self.logger.debug(f"Error getting folder name: {e}")
            return base_title