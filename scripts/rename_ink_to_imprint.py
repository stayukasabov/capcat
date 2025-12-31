#!/usr/bin/env python3
"""
Rename all instances of --cream to --paper in website/css/ files.
"""

import re
from pathlib import Path


def replace_cream_with_paper(content: str) -> tuple[str, int]:
    """
    Replace --cream with --paper in CSS content.

    Args:
        content: CSS file content

    Returns:
        Tuple of (updated_content, number_of_replacements)
    """
    # Pattern to match --cream with word boundaries
    # Matches: --cream, but NOT --accent-cream-primary, --accent-cream-light
    pattern = r'--cream\b'
    replacement = '--paper'

    updated_content = re.sub(pattern, replacement, content)

    # Count replacements
    count = len(re.findall(pattern, content))

    return updated_content, count


def process_css_file(file_path: Path) -> bool:
    """
    Process a single CSS file.

    Args:
        file_path: Path to CSS file

    Returns:
        True if file was modified, False otherwise
    """
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace --cream with --paper
        updated_content, count = replace_cream_with_paper(content)

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
    """Process all CSS files in website/css/ directory."""
    # Get css directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    css_dir = project_dir / 'website' / 'css'

    if not css_dir.exists():
        print(f"CSS directory not found: {css_dir}")
        return

    # Find all CSS files
    css_files = list(css_dir.glob('*.css'))

    print(f"Found {len(css_files)} CSS files in {css_dir}")
    print(f"Replacing '--cream' with '--paper'...\n")

    modified = 0
    skipped = 0

    for css_file in css_files:
        rel_path = css_file.relative_to(css_dir)

        if process_css_file(css_file):
            modified += 1
            print(f"✓ Updated: {rel_path}")
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"Completed!")
    print(f"  Modified: {modified} files")
    print(f"  Skipped:  {skipped} files (no changes needed)")
    print(f"  Total:    {len(css_files)} files")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
