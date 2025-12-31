#!/usr/bin/env python3
"""
Fix breadcrumbs: Remove 'user' from breadcrumb navigation.
Changes "Documentation Home / tutorials / user" to "Documentation Home / tutorials /"
"""

from pathlib import Path
import re

def fix_breadcrumbs():
    """Remove 'user' from breadcrumb navigation in all HTML files."""

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

            # Pattern: breadcrumb ending with " / user</div>"
            # Replace with just "</div>" to remove the " / user" part
            pattern = r'(<div class="nav-breadcrumb">.*?) / user</div>'
            content = re.sub(pattern, r'\1</div>', content, flags=re.DOTALL)

            if content != original:
                html_file.write_text(content, encoding='utf-8')
                updated += 1
                print(f"Updated: {html_file}")

        except Exception as e:
            print(f"Error processing {html_file}: {e}")

    print(f"\nUpdated {updated} files")
    print("Breadcrumbs fixed successfully")

if __name__ == '__main__':
    fix_breadcrumbs()
