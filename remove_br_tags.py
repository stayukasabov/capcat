#!/usr/bin/env python3
"""
Remove all <br> tags from HTML files.

Removes: <br>, <br/>, <br />
"""

import re
from pathlib import Path

def process_file(file_path):
    """Remove all <br> tags from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Remove all variations of <br> tags
    content = re.sub(r'<br\s*/?>', '', content, flags=re.IGNORECASE)

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
