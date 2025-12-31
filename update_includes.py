#!/usr/bin/env python3
"""
Update script: Replace old header/footer HTML with new includes.
"""

from pathlib import Path
import re

def update_site():
    """Replace old header/footer HTML with Jekyll include syntax."""

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

            # Replace header section with include placeholder
            # Pattern: <!-- Header --> followed by <header...>...</header>
            header_pattern = r'<!-- Header -->\s*<header class="site-header">.*?</header>\s*'
            content = re.sub(header_pattern, '{% include header.html %}\n\n', content, flags=re.DOTALL)

            # Replace footer section with include placeholder
            # Pattern: <footer class="site-footer">...</footer>
            footer_pattern = r'<footer class="site-footer">.*?</footer>\s*'
            content = re.sub(footer_pattern, '{% include footer.html %}\n', content, flags=re.DOTALL)

            if content != original:
                html_file.write_text(content, encoding='utf-8')
                updated += 1
                print(f"Updated: {html_file}")

        except Exception as e:
            print(f"Error processing {html_file}: {e}")

    print(f"\nReplaced old HTML in {updated} files")
    print("Now running build_site.py to inject new includes...")

if __name__ == '__main__':
    update_site()

    # Now run the build script
    import subprocess
    subprocess.run(['python3', 'build_site.py'])
