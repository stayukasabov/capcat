#!/usr/bin/env python3
"""
Fix navigation links in all docs HTML files to match root index.html
"""

import os
import re
from pathlib import Path

def calculate_relative_path(html_file_path, website_root):
    """Calculate relative path from HTML file to website root"""
    html_dir = os.path.dirname(html_file_path)
    rel_path = os.path.relpath(website_root, html_dir)
    rel_path = rel_path.replace(os.sep, '/')
    if rel_path == '.':
        return '.'
    return rel_path

def fix_nav_links(file_path, website_root):
    """Fix navigation links in a single HTML file"""
    print(f"Processing: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        rel_path = calculate_relative_path(file_path, website_root)

        # Find and replace the nav-links section
        old_nav_pattern = r'(<ul class="nav-links">)(.*?)(</ul>)'

        new_nav_links = f'''<ul class="nav-links">
                    <li><a href="{rel_path}/index.html#features" title="View Capcat features">Features</a></li>
                    <li><a href="{rel_path}/index.html#how-it-works" title="Learn how Capcat works">How It Works</a></li>
                    <li><a href="{rel_path}/index.html#tutorials" title="Browse Capcat tutorials">Tutorials</a></li>
                    <li><a href="https://substack.com/@yourusername/capcat-case-study" target="_blank" rel="noopener" title="Read the case study (opens in new window)">Case Study</a></li>
                    <li><a href="https://github.com/yourusername/capcat" class="btn-primary" title="Get started with Capcat on GitHub (opens in new window)" target="_blank" rel="noopener">Get Started</a></li>
                </ul>'''

        # Replace the nav links section
        content = re.sub(
            old_nav_pattern,
            new_nav_links,
            content,
            flags=re.DOTALL
        )

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ Navigation links updated")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    website_root = script_dir
    docs_dir = os.path.join(website_root, 'docs')

    if not os.path.exists(docs_dir):
        print(f"Error: docs directory not found at {docs_dir}")
        return

    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    print(f"Found {len(html_files)} HTML files\n")
    print("="*60)

    success_count = 0
    for html_file in html_files:
        if fix_nav_links(html_file, website_root):
            success_count += 1
        print()

    print("="*60)
    print(f"Successfully updated {success_count}/{len(html_files)} files")
    print("="*60)

if __name__ == '__main__':
    main()
