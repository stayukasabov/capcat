#!/usr/bin/env python3
"""
H4 to H3 Tag Replacement Script
--------------------------------
Replaces all <h4> tags with <h3> tags in HTML files within website/docs/

Requirements Analysis:
1. Only replace h4 tags with h3 tags - no new content
2. Preserve all attributes (class, id, style, etc.)
3. Handle both opening and closing tags
4. Process all HTML files in website/docs/ recursively
5. Maintain exact formatting and content

Edge Cases Handled:
- Tags with attributes: <h4 class="foo" id="bar">
- Self-closing or malformed tags (though rare for h4)
- Tags spanning multiple lines
- Nested content within h4 tags
- Mixed case tags (HTML is case-insensitive)

Implementation Strategy:
- Use regex for precise tag replacement (faster than HTML parser for simple replacements)
- Process files in-place with backup option
- Track all changes for verification
- Dry-run mode for safety

Trade-offs:
1. Regex vs HTML Parser:
   - Regex: Faster, simpler, preserves exact formatting
   - Parser: More robust for malformed HTML, but may reformat
   - Choice: Regex (preserves formatting, sufficient for well-formed HTML)

2. In-place vs New Files:
   - In-place: Simpler, saves space
   - New files: Safer, allows comparison
   - Choice: In-place with backup option
"""

import re
import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import argparse
import shutil


class H4ToH3Replacer:
    """Handles replacement of h4 tags with h3 tags in HTML files."""

    # Regex patterns for h4 tags
    # Pattern explanation:
    # <h4          - Opening tag start
    # ((?:\s+[^>]*)?  - Optional attributes (captured in group 1)
    # >            - Tag end
    # Case-insensitive flag handles <H4>, <h4>, etc.
    OPENING_TAG_PATTERN = re.compile(r'<h4((?:\s+[^>]*)?)>', re.IGNORECASE)
    CLOSING_TAG_PATTERN = re.compile(r'</h4>', re.IGNORECASE)

    def __init__(self, base_dir: str, dry_run: bool = False, backup: bool = True):
        """
        Initialize the replacer.

        Args:
            base_dir: Base directory to search for HTML files
            dry_run: If True, only report changes without modifying files
            backup: If True, create backup files before modification
        """
        self.base_dir = Path(base_dir)
        self.dry_run = dry_run
        self.backup = backup
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'h4_opening_tags_replaced': 0,
            'h4_closing_tags_replaced': 0,
            'errors': []
        }

    def find_html_files(self) -> List[Path]:
        """
        Recursively find all HTML files in the base directory.

        Returns:
            List of Path objects for HTML files
        """
        html_files = []
        for ext in ['*.html', '*.htm']:
            html_files.extend(self.base_dir.rglob(ext))
        return sorted(html_files)

    def replace_tags_in_content(self, content: str) -> Tuple[str, int, int]:
        """
        Replace h4 tags with h3 tags in the given content.

        Args:
            content: HTML content as string

        Returns:
            Tuple of (modified_content, opening_tags_count, closing_tags_count)
        """
        # Replace opening tags <h4 ...> with <h3 ...>
        modified_content, opening_count = self.OPENING_TAG_PATTERN.subn(r'<h3\1>', content)

        # Replace closing tags </h4> with </h3>
        modified_content, closing_count = self.CLOSING_TAG_PATTERN.subn(r'</h3>', modified_content)

        return modified_content, opening_count, closing_count

    def process_file(self, file_path: Path) -> bool:
        """
        Process a single HTML file.

        Args:
            file_path: Path to the HTML file

        Returns:
            True if file was modified, False otherwise
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Replace tags
            modified_content, opening_count, closing_count = self.replace_tags_in_content(original_content)

            # Check if any changes were made
            if modified_content == original_content:
                return False

            # Update statistics
            self.stats['h4_opening_tags_replaced'] += opening_count
            self.stats['h4_closing_tags_replaced'] += closing_count

            if self.dry_run:
                print(f"  [DRY RUN] Would replace {opening_count} opening and {closing_count} closing h4 tags")
                return True

            # Create backup if requested
            if self.backup:
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                shutil.copy2(file_path, backup_path)
                print(f"  Created backup: {backup_path.name}")

            # Write modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)

            print(f"  Replaced {opening_count} opening and {closing_count} closing h4 tags")
            return True

        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"  ERROR: {error_msg}", file=sys.stderr)
            return False

    def run(self) -> Dict:
        """
        Run the replacement process on all HTML files.

        Returns:
            Dictionary containing processing statistics
        """
        print(f"\nSearching for HTML files in: {self.base_dir}")
        html_files = self.find_html_files()

        if not html_files:
            print("No HTML files found.")
            return self.stats

        print(f"Found {len(html_files)} HTML files\n")

        if self.dry_run:
            print("=" * 60)
            print("DRY RUN MODE - No files will be modified")
            print("=" * 60 + "\n")

        for file_path in html_files:
            self.stats['files_processed'] += 1
            print(f"Processing: {file_path.relative_to(self.base_dir)}")

            if self.process_file(file_path):
                self.stats['files_modified'] += 1
            else:
                print("  No h4 tags found")

        return self.stats

    def print_summary(self):
        """Print summary of the replacement process."""
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Files processed:       {self.stats['files_processed']}")
        print(f"Files modified:        {self.stats['files_modified']}")
        print(f"H4 opening tags:       {self.stats['h4_opening_tags_replaced']}")
        print(f"H4 closing tags:       {self.stats['h4_closing_tags_replaced']}")

        if self.stats['errors']:
            print(f"\nErrors encountered:    {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"  - {error}")

        if self.dry_run:
            print("\nDRY RUN - No files were actually modified")
        elif self.backup:
            print("\nBackup files created with .backup extension")

        print("=" * 60)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Replace all h4 tags with h3 tags in HTML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be changed
  python replace_h4_with_h3.py --dry-run

  # Replace tags with backups
  python replace_h4_with_h3.py

  # Replace tags without backups
  python replace_h4_with_h3.py --no-backup

  # Process a different directory
  python replace_h4_with_h3.py --dir /path/to/docs
        """
    )

    parser.add_argument(
        '--dir',
        type=str,
        default='website/docs',
        help='Directory to process (default: website/docs)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )

    args = parser.parse_args()

    # Validate directory
    base_dir = Path(args.dir)
    if not base_dir.exists():
        print(f"Error: Directory '{base_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    if not base_dir.is_dir():
        print(f"Error: '{base_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    # Run replacement
    replacer = H4ToH3Replacer(
        base_dir=str(base_dir),
        dry_run=args.dry_run,
        backup=not args.no_backup
    )

    replacer.run()
    replacer.print_summary()

    # Exit with error code if there were errors
    sys.exit(1 if replacer.stats['errors'] else 0)


if __name__ == '__main__':
    main()
