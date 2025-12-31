#!/usr/bin/env python3
"""
HTML Post-Processor for Capcat Archives
Handles post-processing HTML generation after article scraping is complete.
Creates directory indices, article pages, and manages the complete web view system.
"""

import os

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from core.config import get_config
from core.html_generator import HTMLGenerator
from core.logging_config import get_logger
import re


class HTMLPostProcessor:
    """
    Post-processing HTML generation system.
    Handles directory traversal, index generation, and browser launching.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.html_generator = HTMLGenerator()

    def process_directory_tree(self, root_path: str, incremental: bool = True, is_single_article: bool = False) -> str:
        """
        Process an entire directory tree and generate HTML files.

        Args:
            root_path: Root directory path to process
            incremental: If True, only process changed/missing articles
            is_single_article: If True, skip directory index creation (for single command)

        Returns:
            URL of the main index page or article.html for single articles
        """
        root_path = Path(root_path)

        if not root_path.exists():
            self.logger.error(f"Directory does not exist: {root_path}")
            return ""

        self.logger.info("Generating HTML files...")

        # Store is_single_article for use in article processing
        self._is_single_article_mode = is_single_article

        try:
            # Process article markdown files (incremental by default)
            self._process_article_files(root_path, incremental)

            # Generate all directory indices (skip for single articles)
            if not is_single_article:
                self._generate_directory_indices(root_path)

            # Create the main index.html
            # Skip for single articles (both Capcats and custom output with single command)
            main_index_path = root_path / "index.html"
            if not is_single_article and not self._is_capcats_single_article(root_path):
                self._create_main_index(root_path, main_index_path)

            # Return file:// URL for browser opening
            # For Capcats, return article.html path if index doesn't exist
            if main_index_path.exists():
                return main_index_path.as_uri()
            else:
                # Find the article HTML file
                article_html = list(root_path.rglob("**/html/article.html"))
                if article_html:
                    return article_html[0].as_uri()
                return ""

        except Exception as e:
            self.logger.error(f"Error processing directory tree: {e}")
            return ""

    def _process_article_files(self, root_path: Path, incremental: bool = True) -> None:
        """Process article.md and comments.md files with intelligent caching."""
        from core.progress import get_batch_progress
        import time

        # Collect article directories that need processing
        article_dirs = []
        current_time = time.time()

        for article_dir in root_path.rglob("**/*/"):
            if self._is_article_directory(article_dir):
                should_process = True

                if incremental:
                    should_process = self._should_process_article(article_dir)

                if should_process:
                    article_dirs.append(article_dir)

        if not article_dirs:
            if incremental:
                self.logger.info("No new articles to convert to HTML")
            return

        # Process with progress tracking
        with get_batch_progress(
            "Converting to HTML", len(article_dirs)
        ) as progress:
            for article_dir in article_dirs:
                try:
                    progress.update_item_progress(0.0, "processing")
                    self._process_article_directory(article_dir, progress)
                    progress.item_completed(True)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to process article directory {article_dir}: {e}"
                    )
                    progress.item_completed(False)

        self.logger.info(f"Processed {len(article_dirs)} article directories")

    def _should_process_article(self, article_dir: Path) -> bool:
        """
        Determine if article should be processed based on intelligent caching.

        Returns True if:
        - HTML files don't exist, OR
        - Source files are newer than HTML files
        """
        html_dir = article_dir / "html"
        article_html = html_dir / "article.html"

        # Always process if HTML doesn't exist
        if not article_html.exists():
            return True

        # Check modification times - only process if source is newer than HTML
        html_mtime = article_html.stat().st_mtime

        # Check article.md
        article_md = article_dir / "article.md"
        if article_md.exists():
            source_mtime = article_md.stat().st_mtime
            if source_mtime > html_mtime:
                return True

        # Check comments.md
        comments_md = article_dir / "comments.md"
        if comments_md.exists():
            comments_html = html_dir / "comments.html"
            if not comments_html.exists():
                return True
            source_mtime = comments_md.stat().st_mtime
            comments_html_mtime = comments_html.stat().st_mtime
            if source_mtime > comments_html_mtime:
                return True

        return False

    def _is_article_directory(self, directory: Path) -> bool:
        """Check if directory contains article content."""
        return (directory / "article.md").exists() or (
            directory / "comments.md"
        ).exists()

    def _get_source_config(self, article_dir: Path) -> Optional[Dict]:
        """Get source configuration if it has template metadata."""
        try:
            # Extract source name from directory path using comprehensive mapping
            source_dir_name = None

            # Define comprehensive source directory name mappings
            source_mappings = {
                # Tech sources
                ("Hacker-News", "HackerNews"): "hn",
                ("Lobsters",): "lb",
                ("InfoQ", "Infoq"): "iq",
                ("Futurism",): "futurism",
                # News sources
                ("BBC",): "bbc",
                ("CNN",): "cnn",
                ("Al-Jazeera", "AlJazeera"): "aljazeera",
                ("EuroNews", "Euronews"): "euronews",
                ("Straits-Times", "StraitsTimes"): "straitstimes",
                # Science sources
                ("Nature",): "nature",
                (
                    "Scientific-American",
                    "ScientificAmerican",
                ): "scientificamerican",
                ("MIT-Tech-Review", "MITTechReview"): "mittechreview",
                # Business sources
                ("Financial-Times", "FinancialTimes"): "financialtimes",
                # Aggregators
                ("Google-News", "GoogleNews"): "gn",
                ("NewsMap",): "newsmap",
                ("Upday",): "upday",
                # Tech blogs
                ("TechCrunch",): "techcrunch",
                ("Gizmodo",): "gizmodo",
                ("Mashable",): "mashable",
                ("Recode",): "recode",
                ("VentureBeat",): "venturebeat",
                ("CNET",): "cnet",
                # News outlets
                ("Reuters",): "reuters",
                ("The-Guardian", "TheGuardian"): "theguardian",
                ("NY-Times", "NYTimes"): "nytimes",
                ("Washington-Post", "WashingtonPost"): "washingtonpost",
                ("Bloomberg",): "bloomberg",
                ("AP",): "ap",
                ("Ars-Technica", "ArsTechnica"): "arstechnica",
                # AI/Rationality
                ("Lesswrong", "LessWrong"): "lesswrong",
            }

            # Search through directory path parts to find source
            for part in article_dir.parts:
                for source_patterns, source_name in source_mappings.items():
                    if any(
                        part.startswith(pattern) for pattern in source_patterns
                    ):
                        source_dir_name = source_name
                        break
                if source_dir_name:
                    break

            if not source_dir_name:
                return None

            # Look for source config with template metadata
            config_path = Path(
                f"sources/active/custom/{source_dir_name}/config.yaml"
            )
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    if "template" in config:
                        return config

            return None
        except Exception:
            return None

    def _process_article_directory(self, article_dir: Path, progress=None) -> None:
        """Process a single article directory to generate HTML files."""
        # Create html subfolder for HTML files
        html_dir = article_dir / "html"
        html_dir.mkdir(exist_ok=True)

        # Check if this source has template configuration
        source_config = self._get_source_config(article_dir)

        # Detect output mode and determine index filename
        output_mode = self._detect_output_mode(article_dir)
        index_filename = self._get_index_filename(output_mode)

        # Generate article.html from article.md
        article_md = article_dir / "article.md"
        if article_md.exists():
            if progress:
                progress.update_item_progress(0.3, "generating")

            breadcrumb = self._build_breadcrumb_path(article_dir)
            article_title = self._extract_title_from_markdown(article_md)

            # Use template-based generation (all sources now have templates)
            # Fallback to default if source_config not found
            if not source_config:
                source_config = {"template": {"variant": "article-no-comments"}}

            html_content = (
                self.html_generator.generate_article_html_from_template(
                    str(article_md),
                    article_title,
                    breadcrumb,
                    source_config,
                    html_subfolder=True,
                    index_filename=index_filename,
                    is_single_article=getattr(self, '_is_single_article_mode', False),
                )
            )

            article_html = html_dir / "article.html"
            self._write_html_file(article_html, html_content)

        # Generate comments.html from comments.md
        comments_md = article_dir / "comments.md"
        if comments_md.exists():
            if progress:
                progress.update_item_progress(0.7, "generating")

            breadcrumb = self._build_breadcrumb_path(article_dir)
            article_title = self._extract_title_from_markdown(article_md)
            comments_title = f"{article_title} - Comments"

            # Use template-based generation for comments
            # Fallback to default comments template if source_config not found
            if not source_config:
                source_config = {"template": {"variant": "comments-with-navigation"}}

            html_content = (
                self.html_generator.generate_article_html_from_template(
                    str(comments_md),
                    comments_title,
                    breadcrumb + ["Comments"],
                    source_config,
                    html_subfolder=True,
                    index_filename=index_filename,
                    is_single_article=getattr(self, '_is_single_article_mode', False),
                )
            )

            comments_html = html_dir / "comments.html"
            self._write_html_file(comments_html, html_content)

    def _generate_directory_indices(self, root_path: Path) -> None:
        """Generate index.html files for all directories."""
        # Process directories from bottom up (deepest first)
        directories = []
        for directory in root_path.rglob("**/"):
            if directory != root_path and self._should_have_index(directory):
                directories.append(directory)

        # Sort by depth (deepest first)
        directories.sort(key=lambda d: len(d.parts), reverse=True)

        for directory in directories:
            try:
                self._create_directory_index(directory)
            except Exception as e:
                self.logger.warning(
                    f"Failed to create index for {directory}: {e}"
                )

    def _should_have_index(self, directory: Path) -> bool:
        """Determine if directory should have an index.html file."""
        # Skip if it's an article directory (has article.md)
        if (directory / "article.md").exists():
            return False

        # Skip utility directories
        skip_dirs = {
            "images",
            "files",
            "audio",
            "video",
            "html",
            "__pycache__",
            ".git",
        }
        if directory.name in skip_dirs:
            return False

        # Check if directory has content that warrants an index
        has_subdirs = any(
            item.is_dir()
            for item in directory.iterdir()
            if not item.name.startswith(".")
        )
        has_articles = any(
            item.is_dir() and (item / "article.md").exists()
            for item in directory.iterdir()
        )

        return has_subdirs or has_articles

    def _create_directory_index(self, directory: Path) -> None:
        """Create news.html for a specific directory.

        Skip news.html for Capcats single article directories since they only
        contain one article and index.html is sufficient.
        """
        # Skip news.html for Capcats single article directories
        # These are direct children of Capcats/ and only contain one article
        if self._is_capcats_single_article(directory):
            return

        breadcrumb = self._build_breadcrumb_path(directory)
        title = self.html_generator._clean_title_for_display(directory.name)

        html_content = self.html_generator.generate_directory_index(
            str(directory), title, breadcrumb
        )

        news_path = directory / "news.html"
        self._write_html_file(news_path, html_content)

    def _is_capcats_single_article(self, directory: Path) -> bool:
        """
        Check if directory is a Capcats single article capture.

        Returns True if:
        - Parent directory is named "Capcats"
        - This indicates a single article capture, not a News archive

        Examples:
            Capcats/Sam-Altman-Article/ -> True (skip news.html)
            Capcats/InfoQ_26-10-2025/ -> True (skip news.html)
            News_26-10-2025/BBC_26-10-2025/ -> False (keep news.html)
        """
        parent = directory.parent
        return parent.name.lower() == "capcats"

    def _create_main_index(self, root_path: Path, index_path: Path) -> None:
        """Create the main index.html at the root level."""
        # Use a cleaner title format with proper date formatting
        # Convert News_11-09-2025 or news_11-09-2025 to "11 September 2025"
        date_part = (
            root_path.name.split("_")[-1]
            if "_" in root_path.name
            else root_path.name
        )

        # Parse date (DD-MM-YYYY format)
        if "-" in date_part and len(date_part.split("-")) == 3:
            day, month, year = date_part.split("-")
            months = [
                "",
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
            try:
                month_name = months[int(month)]
                formatted_date = f"{int(day)} {month_name} {year}"
            except (ValueError, IndexError):
                formatted_date = date_part.replace("-", "/")
        else:
            formatted_date = date_part.replace("-", "/")

        title = f"News Archive - {formatted_date}"
        breadcrumb = [formatted_date]

        html_content = self.html_generator.generate_directory_index(
            str(root_path), title, breadcrumb
        )

        self._write_html_file(index_path, html_content)

    def _build_breadcrumb_path(self, current_path: Path) -> List[str]:
        """Build breadcrumb navigation path for a given directory."""
        # Start from the archive root (e.g., news_DD-MM-YYYY)
        parts = []
        path = current_path

        # Walk up the path until we reach a recognizable root
        while path.parent != path:
            if self._is_archive_root(path):
                parts.append(path.name.replace("_", " "))
                break
            parts.append(path.name.replace("_", " "))
            path = path.parent

        # Reverse to get proper order (root -> current)
        parts.reverse()
        return parts if parts else [current_path.name]

    def _is_archive_root(self, path: Path) -> bool:
        """Check if path is an archive root directory."""
        name = path.name.lower()
        # Match patterns like news_DD-MM-YYYY, News_DD-MM-YYYY, Hacker-News_DD-MM-YYYY, sg_DD-MM-YYYY
        if name.startswith(("news_", "sg_")):
            return True

        # Check if it matches any source folder pattern (both old and new formats)
        from core.utils import get_source_folder_name

        # Get source codes dynamically from registry
        source_codes = []
        try:
            from core.config import get_source_registry
            registry = get_source_registry()
            source_codes = registry.list_available_sources()
        except Exception:
            # No fallback - only use registered sources
            source_codes = []

        for source_code in source_codes:
            # Check old format (hn_DD-MM-YYYY)
            if name.startswith(f"{source_code}_"):
                return True
            # Check new format (Hacker News DD-MM-YYYY)
            folder_name = get_source_folder_name(source_code)
            if name.startswith(f"{folder_name.lower()} "):
                return True

        return False

    def _detect_output_mode(self, path: Path) -> str:
        """
        Detect output mode based on directory structure.

        Args:
            path: Path to check (article directory or any path in the tree)

        Returns:
            'batch' for standard news archive structure
            'custom' for custom --output directories
        """
        # Walk up the directory tree looking for archive root patterns
        current = path
        while current.parent != current:
            if self._is_archive_root(current):
                return "batch"
            current = current.parent

        # No archive root found = custom output mode
        return "custom"

    def _get_index_filename(self, output_mode: str) -> str:
        """
        Get the appropriate index filename based on output mode.

        Args:
            output_mode: Either 'batch' or 'custom'

        Returns:
            'news.html' for batch mode
            'index.html' for custom mode or unknown modes
        """
        if output_mode == "batch":
            return "news.html"
        return "index.html"

    def _extract_title_from_markdown(self, markdown_path: Path) -> str:
        """
        Extract the article title from the markdown file's H1 heading.
        Falls back to using the folder name if no H1 is found.

        Args:
            markdown_path: Path to the markdown file

        Returns:
            The article title string
        """
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()

            # Match H1 heading (# Title)
            match = re.match(r'^#\s+(.+)$', first_line)
            if match:
                full_title = match.group(1).strip()

                # Handle duplicated titles (common pattern in markdown files)
                # Format: "Full Long Title Short Duplicate Title"
                # Strategy: Look for sequences of 2+ repeated words indicating duplication

                words = full_title.split()

                # If title is short (< 10 words), no duplication likely
                if len(words) < 10:
                    return full_title

                # Look for sequences of repeated words (minimum 2 words)
                # This avoids false positives from common words like "than", "the", etc.
                for i in range(len(words) - 3):  # Need at least 2 words to check
                    # Try matching 2-word sequences first
                    word1 = words[i]
                    word2 = words[i + 1]

                    # Skip if either word is too short
                    if len(word1) < 3 or len(word2) < 3:
                        continue

                    # Search for this 2-word sequence later in the title
                    for j in range(i + 2, len(words) - 1):
                        if words[j] == word1 and words[j + 1] == word2:
                            # Found a duplicate sequence - trim at this point
                            return ' '.join(words[:j])

                # No duplication detected, return full title
                return full_title
        except Exception as e:
            self.logger.debug(f"Could not extract title from {markdown_path}: {e}")

        # Fallback to folder name
        return markdown_path.parent.name.replace("_", " ")

    def _write_html_file(self, file_path: Path, content: str) -> None:
        """Write HTML content to file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Failed to write HTML file {file_path}: {e}")
            raise

    def launch_browser(self, index_url: str) -> bool:
        """
        Display URL for browser opening (platform-agnostic approach).

        Args:
            index_url: File URL to the main index

        Returns:
            True if URL was displayed successfully
        """
        if not index_url:
            self.logger.error("No valid index URL provided")
            return False

        try:
            self.logger.info(f"HTML archive available at: {index_url}")

            return True

        except Exception as e:
            self.logger.error(f"Error displaying browser URL: {e}")
            return False


def process_html_generation(directory_path: str, incremental: bool = True, is_single_article: bool = False) -> Optional[str]:
    """
    Convenience function to process HTML generation for a directory.

    Args:
        directory_path: Path to the directory to process
        incremental: If True, only process recently modified files (default: True)
        is_single_article: If True, skip directory index creation (for single command)

    Returns:
        URL of the generated index page or article.html, or None if failed
    """
    processor = HTMLPostProcessor()
    return processor.process_directory_tree(directory_path, incremental, is_single_article) or None


def launch_web_view(directory_path: str, incremental: bool = True, is_single_article: bool = False) -> bool:
    """
    Generate HTML files and display browser URL for a directory.

    Args:
        directory_path: Path to the directory to process
        incremental: If True, only process recently modified files (default: True)
        is_single_article: If True, skip directory index creation (for single command)

    Returns:
        True if successful, False otherwise
    """
    processor = HTMLPostProcessor()
    index_url = processor.process_directory_tree(directory_path, incremental, is_single_article)

    if index_url:
        return processor.launch_browser(index_url)

    return False
