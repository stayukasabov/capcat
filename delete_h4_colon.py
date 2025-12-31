#!/usr/bin/env python3
"""
Delete colon after </h4> tags.

Pattern: </h4>: → </h4>
"""

import re
from pathlib import Path

def process_file(file_path):
    """Remove colon after </h4> tags."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    # Remove : after </h4>
    content = content.replace('</h4>:', '</h4>')

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    docs_dir = Path('website/docs')
    html_files = list(docs_dir.rglob('*.html'))

    modified = 0
    for file_path in html_files:
        if process_file(file_path):
            print(f"Modified: {file_path.relative_to(docs_dir)}")
            modified += 1

    print(f"\nTotal modified: {modified}/{len(html_files)}")

if __name__ == '__main__':
    main()
