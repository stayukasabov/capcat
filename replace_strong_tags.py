#!/usr/bin/env python3
"""
Replace all <strong> tags with <h3> tags in HTML files.
"""

import os
import re
from pathlib import Path


def replace_strong_with_h3(file_path):
    """Replace <strong> tags with <h3> tags in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Count occurrences before replacement
        strong_open_count = content.count('<strong>')
        strong_close_count = content.count('</strong>')

        if strong_open_count == 0 and strong_close_count == 0:
            return 0, 0

        # Replace tags
        modified_content = content.replace('<strong>', '<h3>')
        modified_content = modified_content.replace('</strong>', '</h3>')

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        return strong_open_count, strong_close_count

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, 0


def main():
    """Process all HTML files in website/docs directory."""
    base_dir = Path(__file__).parent / 'website' / 'docs'

    if not base_dir.exists():
        print(f"Directory not found: {base_dir}")
        return

    print(f"Processing HTML files in: {base_dir}")
    print("-" * 60)

    total_files_processed = 0
    total_files_modified = 0
    total_strong_tags = 0

    # Find all HTML files recursively
    html_files = list(base_dir.rglob('*.html'))

    print(f"Found {len(html_files)} HTML files\n")

    for html_file in sorted(html_files):
        open_count, close_count = replace_strong_with_h3(html_file)
        total_files_processed += 1

        if open_count > 0 or close_count > 0:
            total_files_modified += 1
            total_strong_tags += open_count
            rel_path = html_file.relative_to(base_dir)
            print(f"✓ {rel_path}")
            print(f"  Replaced: {open_count} <strong> and {close_count} </strong> tags")

    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Total files processed: {total_files_processed}")
    print(f"  Files modified: {total_files_modified}")
    print(f"  Total <strong> tags replaced: {total_strong_tags}")
    print("=" * 60)


if __name__ == '__main__':
    main()
