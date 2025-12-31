#!/usr/bin/env python3
"""
Apply design system CSS variables to Mermaid diagram styling in diagrams/*.html files.
Uses Capcat design system colors, fonts, and spacing.
"""

import re
from pathlib import Path


def get_mermaid_styling() -> str:
    """Generate Mermaid styling using design system hex colors."""
    return """  mermaid.initialize({
    startOnLoad: true,
    theme: 'base',
    themeVariables: {
      // Primary colors from design system (Capcat orange palette)
      primaryColor: '#FFD4B7',           // --orange-200
      primaryTextColor: '#201419',       // --ink
      primaryBorderColor: '#F1540E',     // --orange-500 / --accent-primary

      // Line and edge colors
      lineColor: '#58444c',              // --ink-medium

      // Secondary colors
      secondaryColor: '#FFEADB',         // --orange-100
      tertiaryColor: '#f9f8ed',          // --accent-cream-primary

      // Text colors
      textColor: '#201419',              // --ink
      mainBkg: '#FAF8EE',                // --cream

      // Node styling
      nodeBorder: '#F1540E',             // --accent-primary
      clusterBkg: '#faf2e7',             // --accent-cream-light
      clusterBorder: '#D44400',          // --orange-600 / --accent-hover

      // Font
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      fontSize: '16px'
    },
    flowchart: {
      nodeSpacing: 50,
      rankSpacing: 50,
      padding: 15,
      useMaxWidth: true,
      htmlLabels: true,
      curve: 'basis'
    }
  });"""


def update_mermaid_initialization(content: str) -> tuple[str, bool]:
    """
    Replace mermaid.initialize with design system version.

    Args:
        content: HTML file content

    Returns:
        Tuple of (updated_content, was_modified)
    """
    # Pattern to match existing mermaid.initialize (any version)
    pattern = r'mermaid\.initialize\(\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\}\s*\);'

    if not re.search(pattern, content, re.DOTALL):
        return content, False

    # Replace with new styling
    new_styling = get_mermaid_styling()
    updated_content = re.sub(pattern, new_styling, content, flags=re.DOTALL)

    return updated_content, True


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

        # Update mermaid initialization
        updated_content, was_modified = update_mermaid_initialization(content)

        # Only write if changes were made
        if was_modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Process all diagram HTML files."""
    # Get docs directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    docs_dir = project_dir / 'website' / 'docs'

    if not docs_dir.exists():
        print(f"Docs directory not found: {docs_dir}")
        return

    # Find all HTML files with mermaid.initialize recursively
    all_html_files = list(docs_dir.rglob('*.html'))

    # Filter only files that contain mermaid
    html_files = []
    for file in all_html_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                if 'mermaid.initialize' in f.read():
                    html_files.append(file)
        except Exception:
            continue

    print(f"Found {len(html_files)} HTML files with Mermaid diagrams in {docs_dir}")
    print(f"Applying design system styling to Mermaid diagrams...\n")

    modified = 0
    skipped = 0

    for html_file in html_files:
        rel_path = html_file.relative_to(docs_dir)

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
