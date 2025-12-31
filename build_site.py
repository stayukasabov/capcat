#!/usr/bin/env python3
"""
Build script: Replace Jekyll includes with actual HTML content.
This creates a static site without needing Jekyll processing.
"""

from pathlib import Path
import re

def build_site():
    """Replace {% include %} directives and old HTML with actual content."""

    # Read include files
    header_html = Path('docs/_includes/header.html').read_text(encoding='utf-8')
    footer_html = Path('docs/_includes/footer.html').read_text(encoding='utf-8')

    # Find all HTML files
    html_files = list(Path('docs').rglob('*.html'))

    updated = 0
    for html_file in html_files:
        # Skip includes folder
        if '_includes' in html_file.parts:
            continue

        try:
            content = html_file.read_text(encoding='utf-8')
            original = content

            # First, replace old header HTML with Jekyll include syntax
            # Pattern: <!-- Header --> followed by <header...>...</header>
            header_pattern = r'<!-- Header -->\s*<header class="site-header">.*?</header>\s*'
            content = re.sub(header_pattern, '{% include header.html %}\n\n', content, flags=re.DOTALL)

            # Replace old footer HTML with Jekyll include syntax
            # Pattern: <footer class="site-footer">...</footer>
            footer_pattern = r'<footer class="site-footer">.*?</footer>\s*'
            content = re.sub(footer_pattern, '{% include footer.html %}\n', content, flags=re.DOTALL)

            # Now replace Jekyll includes with actual HTML
            content = content.replace('{% include header.html %}', header_html)
            content = content.replace('{% include footer.html %}', footer_html)

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
