#!/usr/bin/env python3
"""
Script to remove all <hr> tags from HTML files in website/docs/ directory.
This script follows clean code principles with proper error handling and logging.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hr_removal.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HRTagRemover:
    """Clean, focused class responsible for removing HR tags from HTML files."""

    def __init__(self, docs_directory: str = "website/docs"):
        """
        Initialize the HR tag remover.

        Args:
            docs_directory: Path to the docs directory to process
        """
        self.docs_directory = Path(docs_directory)
        self.files_processed = 0
        self.total_hr_tags_removed = 0

    def find_html_files(self) -> List[Path]:
        """
        Find all HTML files in the docs directory recursively.

        Returns:
            List of Path objects for HTML files
        """
        html_files = []
        try:
            html_files = list(self.docs_directory.rglob("*.html"))
            logger.info(f"Found {len(html_files)} HTML files in {self.docs_directory}")
        except Exception as e:
            logger.error(f"Error finding HTML files: {e}")

        return html_files

    def remove_hr_tags_from_content(self, content: str) -> Tuple[str, int]:
        """
        Remove all <hr> tags from HTML content.

        Args:
            content: HTML content as string

        Returns:
            Tuple of (cleaned_content, number_of_tags_removed)
        """
        # Pattern to match <hr> tags (with optional attributes and self-closing variants)
        hr_pattern = r'<hr[^>]*/?>'

        # Count tags before removal
        tags_found = len(re.findall(hr_pattern, content, re.IGNORECASE))

        # Remove the tags
        cleaned_content = re.sub(hr_pattern, '', content, flags=re.IGNORECASE)

        return cleaned_content, tags_found

    def process_file(self, file_path: Path) -> bool:
        """
        Process a single HTML file to remove HR tags.

        Args:
            file_path: Path to the HTML file

        Returns:
            True if file was successfully processed, False otherwise
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                original_content = file.read()

            # Remove HR tags
            cleaned_content, tags_removed = self.remove_hr_tags_from_content(original_content)

            if tags_removed > 0:
                # Write the cleaned content back
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(cleaned_content)

                logger.info(f"Removed {tags_removed} <hr> tags from {file_path}")
                self.total_hr_tags_removed += tags_removed
            else:
                logger.debug(f"No <hr> tags found in {file_path}")

            self.files_processed += 1
            return True

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False

    def run(self) -> None:
        """
        Main method to execute the HR tag removal process.
        """
        logger.info("Starting HR tag removal process...")

        # Verify docs directory exists
        if not self.docs_directory.exists():
            logger.error(f"Directory {self.docs_directory} does not exist!")
            sys.exit(1)

        # Find all HTML files
        html_files = self.find_html_files()

        if not html_files:
            logger.warning("No HTML files found to process")
            return

        # Process each file
        successful_files = 0
        for file_path in html_files:
            if self.process_file(file_path):
                successful_files += 1

        # Report results
        self.report_results(len(html_files), successful_files)

    def report_results(self, total_files: int, successful_files: int) -> None:
        """
        Report the final results of the HR tag removal process.

        Args:
            total_files: Total number of files found
            successful_files: Number of files successfully processed
        """
        logger.info("=" * 60)
        logger.info("HR TAG REMOVAL COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total HTML files found: {total_files}")
        logger.info(f"Files successfully processed: {successful_files}")
        logger.info(f"Files with errors: {total_files - successful_files}")
        logger.info(f"Total <hr> tags removed: {self.total_hr_tags_removed}")

        if successful_files == total_files:
            logger.info("✅ All files processed successfully!")
        else:
            logger.warning(f"⚠️  {total_files - successful_files} files had errors")


def main():
    """Main entry point for the script."""
    try:
        remover = HRTagRemover()
        remover.run()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()