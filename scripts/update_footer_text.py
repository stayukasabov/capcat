#!/usr/bin/env python3
"""
Update footer text in website HTML files.

Changes: "Design and context engineering by"
To: "Design, illustration and context engineering by"
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def should_skip_directory(dir_name: str) -> bool:
    """Check if directory should be skipped."""
    skip_patterns = [
        'docs_backup',
        '__pycache__',
        '.git',
        'node_modules',
    ]
    return any(pattern in dir_name for pattern in skip_patterns)


def should_skip_file(file_name: str) -> bool:
    """Check if file should be skipped."""
    return file_name.endswith('.backup') or file_name.startswith('.')


def update_footer_in_file(file_path: Path) -> Tuple[bool, int]:
    """
    Update footer text in a single HTML file.

    Returns:
        Tuple of (changed: bool, count: int) - whether file was modified and number of replacements
    """
    old_text = "Design and context engineering by"
    new_text = "Design, illustration and context engineering by"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Count occurrences
        count = content.count(old_text)

        if count == 0:
            return False, 0

        # Replace text
        new_content = content.replace(old_text, new_text)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, count

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0


def find_and_update_html_files(root_dir: Path) -> List[Tuple[Path, int]]:
    """
    Find all HTML files in directory tree and update footer text.

    Returns:
        List of (file_path, replacement_count) tuples for modified files
    """
    modified_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip certain directories
        dirnames[:] = [d for d in dirnames if not should_skip_directory(d)]

        for filename in filenames:
            # Only process HTML files
            if not filename.endswith('.html'):
                continue

            # Skip backup files
            if should_skip_file(filename):
                continue

            file_path = Path(dirpath) / filename
            changed, count = update_footer_in_file(file_path)

            if changed:
                modified_files.append((file_path, count))

    return modified_files


def main():
    """Main execution function."""
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Target directories
    target_dirs = [
        project_root / 'website',
    ]

    print("=" * 80)
    print("Footer Text Update Script")
    print("=" * 80)
    print(f"\nChanging:")
    print(f'  FROM: "Design and context engineering by"')
    print(f'  TO:   "Design, illustration and context engineering by"')
    print()

    total_modified = 0
    total_replacements = 0

    for target_dir in target_dirs:
        if not target_dir.exists():
            print(f"⚠️  Directory not found: {target_dir}")
            continue

        print(f"\n📁 Processing: {target_dir}")
        print("-" * 80)

        modified_files = find_and_update_html_files(target_dir)

        if modified_files:
            for file_path, count in modified_files:
                rel_path = file_path.relative_to(project_root)
                print(f"✓ {rel_path} ({count} replacement{'s' if count > 1 else ''})")
                total_modified += 1
                total_replacements += count
        else:
            print("  No files needed updating in this directory")

    print()
    print("=" * 80)
    print(f"Summary: Updated {total_modified} file{'s' if total_modified != 1 else ''}")
    print(f"         Total replacements: {total_replacements}")
    print("=" * 80)


if __name__ == "__main__":
    main()
