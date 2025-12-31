#!/usr/bin/env python3
"""
Build script: Replace Jekyll includes with actual HTML content.
This creates a static site without needing Jekyll processing.
"""

from pathlib import Path
import re

def get_favicon_path(html_file, docs_root):
    """Calculate relative path to favicon based on file location."""
    # Get relative path from file to docs root
    try:
        rel_path = html_file.relative_to(docs_root)
        depth = len(rel_path.parts) - 1  # Subtract 1 for the file itself

        if depth == 0:
            # File is in docs/
            return 'icons/Capcat.ico'
        else:
            # File is in subdirectory
            return '../' * depth + 'icons/Capcat.ico'
    except ValueError:
        return 'icons/Capcat.ico'

def inject_favicon(content, favicon_path):
    """Inject favicon link into <head> if not already present."""
    # Check if favicon already exists
    if 'Capcat.ico' in content:
        return content

    favicon_link = f'    <link rel="icon" type="image/x-icon" href="{favicon_path}">'

    # Find </head> tag and inject before it
    head_pattern = r'(\s*)</head>'
    replacement = f'{favicon_link}\n\\1</head>'
    content = re.sub(head_pattern, replacement, content, count=1)

    return content

def build_site():
    """Replace {% include %} directives and old HTML with actual content."""

    # Read include files
    header_html = Path('docs/_includes/header.html').read_text(encoding='utf-8')
    footer_html = Path('docs/_includes/footer.html').read_text(encoding='utf-8')

    # Find all HTML files
    docs_root = Path('docs')
    html_files = list(docs_root.rglob('*.html'))

    updated = 0
    for html_file in html_files:
        # Skip includes folder
        if '_includes' in html_file.parts:
            continue

        try:
            content = html_file.read_text(encoding='utf-8')
            original = content

            # First, replace old header HTML with Jekyll include syntax
            # Pattern: <header class="site-header">...</header>
            header_pattern = r'<header class="site-header">.*?</header>\s*'
            content = re.sub(header_pattern, '{% include header.html %}\n\n', content, flags=re.DOTALL)

            # Replace old footer HTML with Jekyll include syntax
            # Pattern: <footer class="site-footer">...</footer>
            footer_pattern = r'<footer class="site-footer">.*?</footer>\s*'
            content = re.sub(footer_pattern, '{% include footer.html %}\n', content, flags=re.DOTALL)

            # Now replace Jekyll includes with actual HTML
            content = content.replace('{% include header.html %}', header_html)
            content = content.replace('{% include footer.html %}', footer_html)

            # Inject favicon
            favicon_path = get_favicon_path(html_file, docs_root)
            content = inject_favicon(content, favicon_path)

            # Remove front matter
            if content.startswith('---\n---\n'):
                content = content[8:]  # Remove "---\n---\n"

            if content != original:
                html_file.write_text(content, encoding='utf-8')
                updated += 1
                print(f"Updated: {html_file}")

        except Exception as e:
            print(f"Error processing {html_file}: {e}")

    print(f"\nUpdated {updated} files")
    print("Site built successfully - ready for deployment")

if __name__ == '__main__':
    build_site()
