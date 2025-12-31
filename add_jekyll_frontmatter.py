#!/usr/bin/env python3
"""
Add Jekyll front matter to all HTML files so Jekyll processes them.
"""

from pathlib import Path

def add_frontmatter(file_path):
    """Add minimal front matter to HTML file if not present."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Skip if already has front matter
        if content.startswith('---'):
            return False

        # Add minimal front matter at the beginning
        frontmatter = '---\n---\n'
        new_content = frontmatter + content

        file_path.write_text(new_content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    docs_dir = Path('docs')
    html_files = list(docs_dir.rglob('*.html'))

    print(f"Found {len(html_files)} HTML files")

    updated = 0
    for html_file in html_files:
        # Skip _includes folder
        if '_includes' in html_file.parts:
            continue

        if add_frontmatter(html_file):
            updated += 1
            print(f"Updated: {html_file}")

    print(f"\nProcessed {len(html_files)} files")
    print(f"Added front matter to {updated} files")

if __name__ == '__main__':
    main()
