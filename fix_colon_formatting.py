#!/usr/bin/env python3
"""
fix_colon_formatting.py

Removes leading colons from HTML lines in website/docs/ directory.
Targets pattern: lines starting with `:` (optionally preceded by whitespace).

Pattern: `: content` → `content` (preserving indentation)

Usage:
    python3 fix_colon_formatting.py --dry-run  # Preview changes
    python3 fix_colon_formatting.py            # Apply changes
    python3 fix_colon_formatting.py --no-backup  # Apply without backup
"""

import re
import os
import shutil
import argparse
from pathlib import Path
from typing import Tuple, List


class ColonFormattingFixer:
    """Removes leading colons from HTML lines while preserving structure."""

    # Pattern: optional whitespace, colon, optional space, capture rest
    PATTERN = re.compile(r'^(\s*):\s*(.*)$')

    def __init__(self, dry_run: bool = True, create_backup: bool = True):
        """
        Initialize fixer.

        Args:
            dry_run: Preview changes without modifying files
            create_backup: Create .bak files before modification
        """
        self.dry_run = dry_run
        self.create_backup = create_backup
        self.stats = {
            'files_scanned': 0,
            'files_modified': 0,
            'lines_changed': 0,
            'backups_created': 0
        }

    def fix_line(self, line: str) -> Tuple[str, bool]:
        """
        Fix a single line by removing leading colon.

        Args:
            line: Input line

        Returns:
            (fixed_line, was_modified)
        """
        match = self.PATTERN.match(line)
        if match:
            indent = match.group(1)
            content = match.group(2)
            # Preserve indentation + content
            return f"{indent}{content}\n" if line.endswith('\n') else f"{indent}{content}", True
        return line, False

    def fix_file(self, filepath: Path) -> int:
        """
        Fix all lines in a file.

        Args:
            filepath: Path to HTML file

        Returns:
            Number of lines modified
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return 0

        modified_lines = []
        changes_count = 0

        for line in lines:
            fixed_line, was_modified = self.fix_line(line)
            modified_lines.append(fixed_line)
            if was_modified:
                changes_count += 1

        if changes_count > 0:
            if self.dry_run:
                print(f"\n[DRY RUN] Would modify {filepath}")
                print(f"  Lines to change: {changes_count}")
                # Show first few changes
                for i, (orig, fixed) in enumerate(zip(lines, modified_lines)):
                    if orig != fixed:
                        print(f"  Line {i+1}:")
                        print(f"    Before: {orig.rstrip()}")
                        print(f"    After:  {fixed.rstrip()}")
                        if i >= 2:  # Show max 3 examples
                            if changes_count > 3:
                                print(f"  ... and {changes_count - 3} more changes")
                            break
            else:
                # Create backup
                if self.create_backup:
                    backup_path = filepath.with_suffix(filepath.suffix + '.bak')
                    shutil.copy2(filepath, backup_path)
                    self.stats['backups_created'] += 1
                    print(f"Created backup: {backup_path}")

                # Write modified content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(modified_lines)

                print(f"Modified {filepath}: {changes_count} lines changed")

            self.stats['files_modified'] += 1
            self.stats['lines_changed'] += changes_count

        return changes_count

    def process_directory(self, directory: Path) -> None:
        """
        Process all HTML files in directory recursively.

        Args:
            directory: Root directory to scan
        """
        if not directory.exists():
            print(f"Error: Directory {directory} does not exist")
            return

        html_files = list(directory.rglob('*.html'))

        if not html_files:
            print(f"No HTML files found in {directory}")
            return

        print(f"Found {len(html_files)} HTML files to scan")
        if self.dry_run:
            print("\n=== DRY RUN MODE - No files will be modified ===\n")

        for filepath in html_files:
            self.stats['files_scanned'] += 1
            self.fix_file(filepath)

    def print_summary(self) -> None:
        """Print statistics summary."""
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(f"Files scanned:     {self.stats['files_scanned']}")
        print(f"Files modified:    {self.stats['files_modified']}")
        print(f"Lines changed:     {self.stats['lines_changed']}")
        if self.create_backup and not self.dry_run:
            print(f"Backups created:   {self.stats['backups_created']}")
        print("="*50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fix leading colon formatting in HTML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 fix_colon_formatting.py --dry-run     # Preview changes
  python3 fix_colon_formatting.py               # Apply with backups
  python3 fix_colon_formatting.py --no-backup   # Apply without backups
  python3 fix_colon_formatting.py --dir ../other/path  # Custom directory
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create .bak files'
    )

    parser.add_argument(
        '--dir',
        type=str,
        default='website/docs',
        help='Directory to process (default: website/docs)'
    )

    args = parser.parse_args()

    # Determine paths
    script_dir = Path(__file__).parent
    target_dir = script_dir / args.dir

    # Initialize fixer
    fixer = ColonFormattingFixer(
        dry_run=args.dry_run,
        create_backup=not args.no_backup
    )

    # Process directory
    fixer.process_directory(target_dir)

    # Print summary
    fixer.print_summary()

    if args.dry_run and fixer.stats['files_modified'] > 0:
        print("\nRun without --dry-run to apply changes")


if __name__ == '__main__':
    main()
