#!/usr/bin/env python3
"""
Replace "Exhaustive" with "Comprehensive" in all website files.
"""

import re
from pathlib import Path


def replace_exhaustive(content: str) -> tuple[str, int]:
    """
    Replace "Exhaustive" with "Comprehensive" in content.

    Args:
        content: File content string

    Returns:
        Tuple of (updated_content, number_of_replacements)
    """
    pattern = r'Exhaustive'
    replacement = 'Comprehensive'

    updated_content = re.sub(pattern, replacement, content)

    # Count replacements
    count = len(re.findall(pattern, content))

    return updated_content, count


def process_file(file_path: Path) -> bool:
    """
    Process a single file to replace text.

    Args:
        file_path: Path to file

    Returns:
        True if file was modified, False otherwise
    """
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update text
        updated_content, count = replace_exhaustive(content)

        # Only write if changes were made
        if count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Process all files in website/ directory."""
    # Get website directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    website_dir = project_dir / 'website'

    if not website_dir.exists():
        print(f"Website directory not found: {website_dir}")
        return

    # Find all files recursively (all text-based files)
    all_files = []
    # Include HTML, CSS, JS, MD files
    for ext in ['*.html', '*.css', '*.js', '*.md']:
        all_files.extend(list(website_dir.rglob(ext)))

    print(f"Found {len(all_files)} files in {website_dir}")
    print(f"Replacing 'Exhaustive' with 'Comprehensive'...\n")

    modified = 0
    skipped = 0

    for file_path in all_files:
        rel_path = file_path.relative_to(website_dir)

        if process_file(file_path):
            modified += 1
            print(f"✓ Updated: {rel_path}")
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"Completed!")
    print(f"  Modified: {modified} files")
    print(f"  Skipped:  {skipped} files (no changes needed)")
    print(f"  Total:    {len(all_files)} files")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
