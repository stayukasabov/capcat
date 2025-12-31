#!/usr/bin/env python3
"""Fix mismatched pre/div tags in HTML files."""

import re
from pathlib import Path

def fix_mismatched_tags(html_content):
    """Fix tags where <pre> opens but </div> closes or vice versa."""

    # Fix <pre> opening with </div> closing
    html_content = re.sub(
        r'<pre>([^<]+(?:[│├└─])[^<]+)</div>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    # Fix <div> opening with </pre> closing
    html_content = re.sub(
        r'<div>([^<]+(?:[│├└─])[^<]+)</pre>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    # General fix: if content has directory tree chars, use pre not div
    html_content = re.sub(
        r'<div>(\.\./(?:News|Capcats)/[^\n]+\n[^<]*[│├└─][^<]*)</div>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    return html_content

def process_html_files(base_dir):
    """Process all HTML files in the directory."""
    html_files = list(Path(base_dir).rglob('*.html'))

    print(f"Found {len(html_files)} HTML files to process")

    for html_file in html_files:
        print(f"\nProcessing: {html_file}")

        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        content = fix_mismatched_tags(content)

        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Fixed mismatched tags")
        else:
            print(f"  - No mismatched tags found")

if __name__ == '__main__':
    base_dir = 'HTML-Tutorials'
    print("Fixing mismatched pre/div tags...\n")
    process_html_files(base_dir)
    print("\n✓ All files processed")
