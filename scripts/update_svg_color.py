#!/usr/bin/env python3
"""
Update SVG fill color in all documentation HTML files.
Changes fill:rgb(234,94,52) to fill:rgb(255,83,31) in SVG elements.
"""

import re
from pathlib import Path


def update_svg_color(content: str) -> tuple[str, int]:
    """
    Update SVG fill color in HTML content.

    Args:
        content: HTML content string

    Returns:
        Tuple of (updated_content, number_of_replacements)
    """
    # Pattern to match the old color in SVG fill attribute
    pattern = r'style="fill:rgb\(255,86,14\)'
    replacement = 'style="fill:rgb(241,84,14)'

    updated_content = re.sub(pattern, replacement, content)

    # Count replacements
    count = len(re.findall(pattern, content))

    return updated_content, count


def process_html_file(file_path: Path) -> bool:
    """
    Process a single HTML file to update SVG colors.

    Args:
        file_path: Path to HTML file

    Returns:
        True if file was modified, False otherwise
    """
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update colors
        updated_content, count = update_svg_color(content)

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
    """Process all HTML files in website/docs directory."""
    # Get docs directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    docs_dir = project_dir / 'website' / 'docs'

    if not docs_dir.exists():
        print(f"Documentation directory not found: {docs_dir}")
        return

    # Find all HTML files recursively
    html_files = list(docs_dir.rglob('*.html'))

    print(f"Found {len(html_files)} HTML files in {docs_dir}")
    print(f"Updating SVG colors from rgb(255,83,46) to rgb(255,86,14)...\n")

    modified = 0
    skipped = 0

    for html_file in html_files:
        rel_path = html_file.relative_to(docs_dir)

        if process_html_file(html_file):
            modified += 1
            print(f"✓ Updated: {rel_path}")
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"Completed!")
    print(f"  Modified: {modified} files")
    print(f"  Skipped:  {skipped} files (no changes needed)")
    print(f"  Total:    {len(html_files)} files")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
