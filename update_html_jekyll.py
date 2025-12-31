#!/usr/bin/env python3
"""
Update all HTML files in docs/ to use Jekyll includes for header and footer.
"""

import re
from pathlib import Path

def update_html_file(file_path):
    """Update a single HTML file to use Jekyll includes."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content

        # Replace placeholder divs with Jekyll includes
        content = content.replace('<div id="header-placeholder"></div>', '{% include header.html %}')
        content = content.replace('<div id="footer-placeholder"></div>', '{% include footer.html %}')

        # Remove includes-loader.js script tag
        content = re.sub(r'\s*<script src="[^"]*includes-loader\.js"></script>\n?', '', content)

        # Only write if changed
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
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

        if update_html_file(html_file):
            updated += 1
            print(f"Updated: {html_file}")

    print(f"\nProcessed {len(html_files)} files")
    print(f"Updated {updated} files")

if __name__ == '__main__':
    main()
