#!/usr/bin/env python3
"""
Storage management component for Capcat.

Handles file system operations, folder creation, and content storage
independently from the main article fetching logic.
"""

import os
from pathlib import Path

from .config import get_config
from .logging_config import get_logger
from .utils import sanitize_filename

_logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level filename helpers — single source of truth for naming convention
# ---------------------------------------------------------------------------

def article_md_filename(title: str) -> str:
    """Return sanitized markdown filename for an article (e.g. 'My-Title.md').

    Truncation respects processing.max_filename_length from config.
    Spaces are replaced with hyphens.
    """
    max_len = get_config().processing.max_filename_length
    return sanitize_filename(title, max_length=max_len).replace(" ", "-") + ".md"


def comments_md_filename(title: str) -> str:
    """Return sanitized markdown filename for comments (e.g. 'My-Title-Comments.md').

    Truncation respects processing.max_filename_length from config.
    '-Comments.md' is appended after truncation.
    Spaces are replaced with hyphens.
    """
    max_len = get_config().processing.max_filename_length
    return sanitize_filename(title, max_length=max_len).replace(" ", "-") + "-Comments.md"


def find_article_md(folder: Path) -> "Path | None":
    """Return the article markdown path in folder, or None if absent.

    Non-recursive: only searches direct children of folder.
    Returns the first .md file whose stem does not end in '-Comments'.
    """
    return next(
        (
            p
            for p in folder.glob("*.md")
            if p.is_file() and not p.stem.endswith("-Comments")
        ),
        None,
    )


def find_comments_md(folder: Path) -> "Path | None":
    """Return the comments markdown path in folder, or None if absent."""
    return next((p for p in folder.glob("*-Comments.md") if p.is_file()), None)


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


def inject_frontmatter(md_path: str, metadata: dict) -> bool:
    """Prepend YAML frontmatter to a markdown file.

    Idempotent: if the file already starts with '---', returns True without
    modifying. Omits any key whose value is None. Returns False on any error
    without raising.
    """
    import yaml

    try:
        path = Path(md_path)
        if not path.is_file():
            _logger.warning(f"inject_frontmatter: file not found: {md_path}")
            return False

        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            _logger.debug(f"Frontmatter already present: {md_path}")
            return True

        clean = {k: v for k, v in metadata.items() if v is not None}
        fm = yaml.dump(clean, default_flow_style=False, allow_unicode=True,
                       sort_keys=False)
        path.write_text(f"---\n{fm}---\n\n{content}", encoding="utf-8")
        return True

    except Exception as e:
        _logger.warning(f"inject_frontmatter failed for {md_path}: {e}")
        return False


def update_frontmatter_pdfs(md_path: str, pdf_paths: list) -> bool:
    """Add or replace the 'pdfs' key in an existing YAML frontmatter block.

    Reads current frontmatter, sets pdfs to pdf_paths, writes back.
    No-ops (returns True) when pdf_paths is empty.
    Returns False if no frontmatter exists or on any error.
    """
    import yaml

    if not pdf_paths:
        return True

    try:
        path = Path(md_path)
        if not path.is_file():
            return False

        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return False

        end = content.find("\n---", 3)
        if end == -1:
            return False

        fm_text = content[3:end]
        body = content[end + 4:]

        metadata = yaml.safe_load(fm_text) or {}
        metadata["pdfs"] = pdf_paths

        fm_out = yaml.dump(metadata, default_flow_style=False, allow_unicode=True,
                           sort_keys=False)
        path.write_text(f"---\n{fm_out}---{body}", encoding="utf-8")
        return True

    except Exception as e:
        _logger.warning(f"update_frontmatter_pdfs failed for {md_path}: {e}")
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