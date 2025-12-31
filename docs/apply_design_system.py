#!/usr/bin/env python3
"""
Apply design system CSS and JS to all HTML files in the docs folder.
Removes inline <style> tags and adds links to design-system.css, main.css, and main.js
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

def calculate_relative_path(html_file_path, website_root):
    """Calculate relative path from HTML file to website root"""
    html_dir = os.path.dirname(html_file_path)
    rel_path = os.path.relpath(website_root, html_dir)
    # Normalize path separators to forward slashes for URLs
    rel_path = rel_path.replace(os.sep, '/')
    # Ensure it ends without a trailing slash
    if rel_path == '.':
        return '.'
    return rel_path

def process_html_file(file_path, website_root):
    """Process a single HTML file to add design system links"""
    print(f"Processing: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Find the <head> tag
        head = soup.find('head')
        if not head:
            print(f"  ⚠ No <head> tag found, skipping")
            return False

        # Calculate relative path to website root
        rel_path = calculate_relative_path(file_path, website_root)

        # Remove existing <style> tags
        style_tags = soup.find_all('style')
        if style_tags:
            print(f"  - Removing {len(style_tags)} <style> tag(s)")
            for style in style_tags:
                style.decompose()

        # Check if design system links already exist
        existing_links = [link.get('href', '') for link in soup.find_all('link', {'rel': 'stylesheet'})]
        has_design_system = any('design-system.css' in href for href in existing_links)
        has_main_css = any('main.css' in href for href in existing_links)

        if not has_design_system:
            # Add design-system.css link
            design_link = soup.new_tag('link', rel='stylesheet', href=f'{rel_path}/css/design-system.css')
            head.append(design_link)
            print(f"  + Added design-system.css")
        else:
            print(f"  ✓ design-system.css already linked")

        if not has_main_css:
            # Add main.css link
            main_link = soup.new_tag('link', rel='stylesheet', href=f'{rel_path}/css/main.css')
            head.append(main_link)
            print(f"  + Added main.css")
        else:
            print(f"  ✓ main.css already linked")

        # Check if main.js already exists
        existing_scripts = [script.get('src', '') for script in soup.find_all('script')]
        has_main_js = any('main.js' in src for src in existing_scripts)

        if not has_main_js:
            # Add main.js before closing </body>
            body = soup.find('body')
            if body:
                script_tag = soup.new_tag('script', src=f'{rel_path}/js/main.js')
                body.append(script_tag)
                print(f"  + Added main.js")
            else:
                print(f"  ⚠ No <body> tag found, couldn't add main.js")
        else:
            print(f"  ✓ main.js already linked")

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        print(f"  ✓ Successfully updated")
        return True

    except Exception as e:
        print(f"  ✗ Error processing file: {e}")
        return False

def main():
    # Get the website root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    website_root = script_dir
    docs_dir = os.path.join(website_root, 'docs')

    if not os.path.exists(docs_dir):
        print(f"Error: docs directory not found at {docs_dir}")
        return

    # Find all HTML files in docs directory
    html_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    print(f"Found {len(html_files)} HTML files in docs folder\n")

    # Process each file
    success_count = 0
    for html_file in html_files:
        if process_html_file(html_file, website_root):
            success_count += 1
        print()  # Blank line between files

    print(f"\n{'='*60}")
    print(f"Processed {success_count}/{len(html_files)} files successfully")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
