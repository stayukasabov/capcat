#!/usr/bin/env python3
"""Fix ASCII formatting in HTML tutorial files."""

import os
import re
from pathlib import Path

def fix_ascii_in_html(html_content):
    """Convert div blocks containing ASCII art to pre blocks."""

    # Fix the main Capcat logo + menu (the big one with ____  and menu options)
    html_content = re.sub(
        r'<div>\s*(       ____.*?Use arrow keys[^\)]*\))\s*</div>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    # Fix bundle selection menu with all options listed
    html_content = re.sub(
        r'<div>\s*(  Select a news bundle.*?Use arrow keys[^\)]*\))\s*</div>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    # Fix example interaction blocks (multi-line with  "  " starting spaces and arrow/checkboxes)
    html_content = re.sub(
        r'<div>\s*(  .*?(?:▶|Select|Generate HTML|SUMMARY).*?\n(?:  .*?\n)+.*?)\s*</div>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    # Fix SUMMARY blocks with dashes
    html_content = re.sub(
        r'<div>\s*(-{10,}\s*\n\s*SUMMARY.*?\n.*?-{10,}.*?)</div>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    # Fix processing output blocks [N/M]
    html_content = re.sub(
        r'<div>\s*(Processing .*?bundle.*?\n.*?\[\d+/\d+\].*?)</div>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    # Fix error/success output blocks
    html_content = re.sub(
        r'<div>\s*((?:Error|✓|✗).*?Press Enter.*?)</div>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    # Fix directory tree structures (with ../News or ../Capcats and tree chars)
    html_content = re.sub(
        r'<div>(\.\./(?:News|Capcats)(?:/[^\n]+)?\n(?:.*?[│├└─].*?\n)+.*?)</div>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    # Fix simple directory structures without tree chars
    html_content = re.sub(
        r'<div>(\.\./(?:News|Capcats)/[^\n]+\n(?:├──|│|└──).*?)</div>',
        r'<pre>\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    # Fix flow diagrams (simple text with arrows)
    html_content = re.sub(
        r'<code>((?:Select|Enter|Choose).*?→.*?→.*?)</code>',
        r'<pre>\1</pre>',
        html_content
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
        content = fix_ascii_in_html(content)

        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Updated ASCII formatting")
        else:
            print(f"  - No changes needed")

if __name__ == '__main__':
    base_dir = 'HTML-Tutorials'
    print("Fixing ASCII formatting in HTML tutorial files...\n")
    process_html_files(base_dir)
    print("\n✓ All files processed")
