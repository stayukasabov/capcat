#!/usr/bin/env python3
"""
Strong to H4 Tag Replacement Script

Replaces all <strong> tags with <h4> tags in HTML files within website/docs/ directory.
When multiple <strong> tags appear on the same line, each replacement is placed on a new line.

Key Features:
- Replaces <strong> → <h4> and </strong> → </h4>
- Inserts newlines before subsequent <strong> tags on the same line
- Preserves indentation and spacing
- Handles nested content and attributes
- Dry-run mode for safe testing
- Automatic backups
- Comprehensive statistics and reporting

Usage:
    python replace_strong_with_h4.py                    # Dry run (no changes)
    python replace_strong_with_h4.py --execute          # Execute replacement
    python replace_strong_with_h4.py --backup-dir ./my-backups  # Custom backup location
"""

import re
import os
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class ReplacementStats:
    """Statistics for replacement operations."""
    files_processed: int = 0
    files_modified: int = 0
    total_replacements: int = 0
    lines_with_multiple_tags: int = 0
    lines_modified: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class StrongToH4Replacer:
    """
    Handles replacement of <strong> tags with <h4> tags.

    Special handling for multiple tags on the same line:
    - Inserts newline before each subsequent <strong> tag (after the first)
    - Preserves indentation and spacing
    - Maintains exact content within tags
    """

    # Regex pattern to match <strong> opening tags (with or without attributes)
    STRONG_OPEN_PATTERN = re.compile(r'<strong\b([^>]*)>', re.IGNORECASE)

    # Regex pattern to match </strong> closing tags
    STRONG_CLOSE_PATTERN = re.compile(r'</strong>', re.IGNORECASE)

    # Pattern to detect multiple <strong> tags on the same line
    MULTIPLE_STRONG_PATTERN = re.compile(r'(<strong\b[^>]*>.*?</strong>).*(<strong\b[^>]*>)', re.IGNORECASE | re.DOTALL)

    def __init__(self, docs_dir: str = "website/docs"):
        """
        Initialize the replacer.

        Args:
            docs_dir: Directory containing HTML files to process
        """
        self.docs_dir = Path(docs_dir)
        self.stats = ReplacementStats()

    def process_line(self, line: str) -> Tuple[str, int, bool]:
        """
        Process a single line, replacing <strong> tags with <h4> tags.

        If multiple <strong> tags exist on the line, insert newlines before
        subsequent tags (but not the first).

        Args:
            line: The line to process

        Returns:
            Tuple of (modified_line, replacement_count, has_multiple_tags)
        """
        original_line = line
        replacement_count = 0
        has_multiple_tags = False

        # Count how many <strong> opening tags are on this line
        strong_count = len(self.STRONG_OPEN_PATTERN.findall(line))

        if strong_count == 0:
            return line, 0, False

        if strong_count > 1:
            has_multiple_tags = True
            line = self._handle_multiple_strong_tags(line)

        # Now replace all <strong> tags with <h4>
        modified_line, open_count = self.STRONG_OPEN_PATTERN.subn(r'<h4\1>', line)
        modified_line, close_count = self.STRONG_CLOSE_PATTERN.subn(r'</h4>', modified_line)

        replacement_count = open_count + close_count

        return modified_line, replacement_count, has_multiple_tags

    def _handle_multiple_strong_tags(self, line: str) -> str:
        """
        Handle lines with multiple <strong> tags by inserting newlines.

        Strategy:
        1. Find all <strong> tag positions
        2. Starting from the second tag, insert a newline before it
        3. Preserve indentation by extracting leading whitespace

        Args:
            line: Line with multiple <strong> tags

        Returns:
            Modified line with newlines inserted before subsequent tags
        """
        # Extract leading whitespace for indentation preservation
        leading_space = len(line) - len(line.lstrip())
        indent = line[:leading_space]

        # Find all <strong> opening tag positions
        positions = []
        for match in self.STRONG_OPEN_PATTERN.finditer(line):
            positions.append(match.start())

        if len(positions) <= 1:
            return line

        # Build the new line with newlines inserted before subsequent tags
        result_parts = []

        # Add the portion before the second tag (includes first tag and content)
        result_parts.append(line[:positions[1]])

        # Process each subsequent tag
        for i in range(1, len(positions)):
            # Insert newline and indentation before this tag
            result_parts.append('\n' + indent)

            # Determine where this segment ends
            if i + 1 < len(positions):
                # Not the last tag - add up to next tag
                result_parts.append(line[positions[i]:positions[i+1]])
            else:
                # Last tag - add remainder of line
                result_parts.append(line[positions[i]:])

        return ''.join(result_parts)

    def process_file(self, file_path: Path) -> Tuple[str, int, int, int]:
        """
        Process a single HTML file.

        Args:
            file_path: Path to the HTML file

        Returns:
            Tuple of (modified_content, total_replacements, modified_lines, multiple_tag_lines)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            self.stats.errors.append(f"Error reading {file_path}: {e}")
            return "", 0, 0, 0

        modified_lines = []
        total_replacements = 0
        modified_line_count = 0
        multiple_tag_line_count = 0

        for line in lines:
            modified_line, replacements, has_multiple = self.process_line(line)

            if replacements > 0:
                modified_line_count += 1
                total_replacements += replacements

            if has_multiple:
                multiple_tag_line_count += 1

            modified_lines.append(modified_line)

        modified_content = ''.join(modified_lines)
        return modified_content, total_replacements, modified_line_count, multiple_tag_line_count

    def create_backup(self, file_path: Path, backup_dir: Path) -> bool:
        """
        Create a backup of the file before modification.

        Args:
            file_path: Path to the file to backup
            backup_dir: Directory to store backups

        Returns:
            True if backup successful, False otherwise
        """
        try:
            # Create backup directory structure mirroring source
            relative_path = file_path.relative_to(self.docs_dir)
            backup_file = backup_dir / relative_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file to backup location
            shutil.copy2(file_path, backup_file)
            return True
        except Exception as e:
            self.stats.errors.append(f"Error backing up {file_path}: {e}")
            return False

    def process_directory(self, dry_run: bool = True, backup_dir: Path = None) -> ReplacementStats:
        """
        Process all HTML files in the docs directory.

        Args:
            dry_run: If True, only simulate changes without writing
            backup_dir: Directory for backups (if not dry run)

        Returns:
            ReplacementStats object with processing statistics
        """
        if not self.docs_dir.exists():
            self.stats.errors.append(f"Directory not found: {self.docs_dir}")
            return self.stats

        # Find all HTML files
        html_files = list(self.docs_dir.rglob("*.html"))

        if not html_files:
            self.stats.errors.append(f"No HTML files found in {self.docs_dir}")
            return self.stats

        print(f"{'[DRY RUN] ' if dry_run else ''}Processing {len(html_files)} HTML files...")

        for file_path in html_files:
            self.stats.files_processed += 1

            # Process the file
            modified_content, replacements, modified_lines, multiple_lines = self.process_file(file_path)

            if replacements == 0:
                continue

            self.stats.files_modified += 1
            self.stats.total_replacements += replacements
            self.stats.lines_modified += modified_lines
            self.stats.lines_with_multiple_tags += multiple_lines

            print(f"  {file_path.relative_to(self.docs_dir)}: {replacements} replacements, {multiple_lines} multi-tag lines")

            # Write changes if not dry run
            if not dry_run:
                # Create backup first
                if backup_dir:
                    if not self.create_backup(file_path, backup_dir):
                        self.stats.errors.append(f"Skipping {file_path} due to backup failure")
                        continue

                # Write modified content
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                except Exception as e:
                    self.stats.errors.append(f"Error writing {file_path}: {e}")

        return self.stats


def print_statistics(stats: ReplacementStats, dry_run: bool):
    """Print formatted statistics."""
    print("\n" + "=" * 70)
    print(f"{'DRY RUN ' if dry_run else ''}REPLACEMENT STATISTICS")
    print("=" * 70)
    print(f"Files processed:              {stats.files_processed}")
    print(f"Files modified:               {stats.files_modified}")
    print(f"Total replacements:           {stats.total_replacements}")
    print(f"Lines modified:               {stats.lines_modified}")
    print(f"Lines with multiple tags:     {stats.lines_with_multiple_tags}")

    if stats.errors:
        print(f"\nErrors encountered:           {len(stats.errors)}")
        for error in stats.errors:
            print(f"  - {error}")

    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Replace <strong> tags with <h4> tags in website/docs/ HTML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python replace_strong_with_h4.py                           # Dry run
  python replace_strong_with_h4.py --execute                 # Execute replacement
  python replace_strong_with_h4.py --execute --no-backup     # No backups
  python replace_strong_with_h4.py --backup-dir ./backups    # Custom backup location
        """
    )

    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the replacement (default is dry-run)'
    )

    parser.add_argument(
        '--docs-dir',
        type=str,
        default='website/docs',
        help='Directory containing HTML files (default: website/docs)'
    )

    parser.add_argument(
        '--backup-dir',
        type=str,
        help='Directory for backups (default: website/docs_backup_TIMESTAMP)'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backups (not recommended)'
    )

    args = parser.parse_args()

    # Determine backup directory
    backup_dir = None
    if args.execute and not args.no_backup:
        if args.backup_dir:
            backup_dir = Path(args.backup_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(f"website/docs_backup_{timestamp}")

        print(f"Backups will be stored in: {backup_dir}")

    # Create replacer and process
    replacer = StrongToH4Replacer(docs_dir=args.docs_dir)
    stats = replacer.process_directory(dry_run=not args.execute, backup_dir=backup_dir)

    # Print statistics
    print_statistics(stats, dry_run=not args.execute)

    # Exit with appropriate code
    if stats.errors:
        sys.exit(1)
    else:
        if not args.execute:
            print("\nThis was a DRY RUN. Use --execute to apply changes.")
        else:
            print("\nReplacement completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
