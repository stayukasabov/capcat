#!/usr/bin/env python3
"""
Replace 'menus' with 'menu' in text under Mermaid diagrams in diagrams/*.html files.
"""

import re
from pathlib import Path


def replace_menus_after_diagram(content: str) -> tuple[str, int]:
    """
    Replace 'menus' with 'menu' in content after Mermaid diagrams.

    Args:
        content: HTML file content

    Returns:
        Tuple of (updated_content, number_of_replacements)
    """
    # Replace all instances of 'menus' with 'menu'
    updated_content = re.sub(r'\bmenus\b', 'menu', content, flags=re.IGNORECASE)

    # Count replacements (case-insensitive)
    count = len(re.findall(r'\bmenus\b', content, re.IGNORECASE))

    return updated_content, count


def process_diagram_file(file_path: Path) -> bool:
    """
    Process a single diagram HTML file.

    Args:
        file_path: Path to HTML file

    Returns:
        True if file was modified, False otherwise
    """
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace menus with menu
        updated_content, count = replace_menus_after_diagram(content)

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
    """Process all diagram HTML files."""
    # Get diagrams directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    diagrams_dir = project_dir / 'website' / 'docs' / 'diagrams'

    if not diagrams_dir.exists():
        print(f"Diagrams directory not found: {diagrams_dir}")
        return

    # Find all HTML files
    html_files = list(diagrams_dir.glob('*.html'))

    print(f"Found {len(html_files)} HTML files in {diagrams_dir}")
    print(f"Replacing 'menus' with 'menu'...\n")

    modified = 0
    skipped = 0

    for html_file in html_files:
        rel_path = html_file.relative_to(diagrams_dir)

        if process_diagram_file(html_file):
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
