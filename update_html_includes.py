#!/usr/bin/env python3
"""
Update all HTML files in docs/ to use includes system for header and footer.
"""

import re
from pathlib import Path

def update_html_file(file_path):
    """Update a single HTML file to use includes."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content

        # Replace <header> tag with placeholder
        header_pattern = r'<header class="site-header">.*?</header>'
        content = re.sub(header_pattern, '<div id="header-placeholder"></div>', content, flags=re.DOTALL)

        # Replace <footer> tag with placeholder
        footer_pattern = r'<footer class="site-footer">.*?</footer>'
        content = re.sub(footer_pattern, '<div id="footer-placeholder"></div>', content, flags=re.DOTALL)

        # Add includes-loader.js before </body> if not present
        if 'includes-loader.js' not in content and '</body>' in content:
            # Calculate relative path to js/ folder
            depth = len(file_path.relative_to(Path('docs')).parts) - 1
            js_path = '../' * depth + 'js/includes-loader.js'
            script_tag = f'    <script src="{js_path}"></script>\n  </body>'
            content = content.replace('</body>', script_tag)

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
        # Skip includes folder
        if 'includes' in html_file.parts:
            continue

        if update_html_file(html_file):
            updated += 1
            print(f"Updated: {html_file}")

    print(f"\nProcessed {len(html_files)} files")
    print(f"Updated {updated} files")

if __name__ == '__main__':
    main()
