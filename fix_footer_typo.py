#!/usr/bin/env python3
"""
Fix typo in footer: edngineering → engineering
"""

from pathlib import Path

def process_file(file_path):
    """Fix typo edngineering to engineering."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Fix the typo
    content = content.replace('edngineering', 'engineering')
    content = content.replace('Edngineering', 'Engineering')

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    website_dir = Path('website')
    html_files = list(website_dir.rglob('*.html'))

    modified = 0
    for file_path in html_files:
        if process_file(file_path):
            print(f"Modified: {file_path.relative_to(website_dir)}")
            modified += 1

    print(f"\nTotal modified: {modified}/{len(html_files)}")

if __name__ == '__main__':
    main()
