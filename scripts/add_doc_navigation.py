#!/usr/bin/env python3
"""
Add chapter navigation links to documentation HTML files.
Inserts navigation directly into HTML for better SEO and non-JS support.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional


# Navigation mapping: defines logical reading order for documentation
NAVIGATION_MAP = {
    # Main documentation flow (beginner to advanced)
    'quick-start.html': {'next': {'url': 'configuration.html', 'title': 'Configuration'}},
    'configuration.html': {'next': {'url': 'interactive-mode.html', 'title': 'Interactive Mode'}},
    'interactive-mode.html': {'next': {'url': 'source-management-menu.html', 'title': 'Source Management'}},
    'source-management-menu.html': {'next': {'url': 'source-development.html', 'title': 'Source Development'}},
    'source-development.html': {'next': {'url': 'architecture.html', 'title': 'Architecture Overview'}},
    'architecture.html': {'next': {'url': 'DIAGRAMS_INDEX.html', 'title': 'Architecture Diagrams'}},
    'DIAGRAMS_INDEX.html': {'next': {'url': 'api-reference.html', 'title': 'API Reference'}},
    'api-reference.html': {'next': {'url': 'testing.html', 'title': 'Testing Guide'}},
    'testing.html': {'next': {'url': 'deployment.html', 'title': 'Deployment Guide'}},
    'deployment.html': {'next': {'url': 'ethical-scraping.html', 'title': 'Ethical Scraping Guidelines'}},
    'ethical-scraping.html': {'next': {'url': 'dependencies.html', 'title': 'Dependency Management'}},
    'dependencies.html': {'next': {'url': 'dependency-management.html', 'title': 'Advanced Dependency Management'}},

    # User tutorials (numbered sequence)
    'tutorials/user/index.html': {'next': {'url': '01-getting-started.html', 'title': 'Tutorial 1: Getting Started'}},
    'tutorials/user/01-getting-started.html': {'next': {'url': '02-daily-workflow.html', 'title': 'Tutorial 2: Daily Workflow'}},
    'tutorials/user/02-daily-workflow.html': {'next': {'url': '03-interactive-mode.html', 'title': 'Tutorial 3: Interactive Mode'}},
    'tutorials/user/03-interactive-mode.html': {'next': {'url': '04-managing-sources.html', 'title': 'Tutorial 4: Managing Sources'}},
    'tutorials/user/04-managing-sources.html': {'next': {'url': '05-bundles.html', 'title': 'Tutorial 5: Working with Bundles'}},
    'tutorials/user/05-bundles.html': {'next': {'url': '06-customizing-output.html', 'title': 'Tutorial 6: Customizing Output'}},

    # Advanced tutorials (numbered sequence)
    'tutorials/01-cli-commands-exhaustive.html': {'next': {'url': '02-interactive-mode-exhaustive.html', 'title': 'Tutorial 2: Interactive Mode (Exhaustive)'}},
    'tutorials/02-interactive-mode-exhaustive.html': {'next': {'url': '03-configuration-exhaustive.html', 'title': 'Tutorial 3: Configuration (Exhaustive)'}},
    'tutorials/03-configuration-exhaustive.html': {'next': {'url': '04-source-system-exhaustive.html', 'title': 'Tutorial 4: Source System (Exhaustive)'}},
    'tutorials/04-source-system-exhaustive.html': {'next': {'url': '05-api-functions-exhaustive.html', 'title': 'Tutorial 5: API Functions (Exhaustive)'}},

    # Feature documentation
    'feature-add-source.html': {'next': {'url': 'feature-remove-source.html', 'title': 'Remove Source Feature'}},
    'feature-remove-source.html': {'next': {'url': 'remove-source-advanced-features.html', 'title': 'Advanced Remove Source Features'}},

    # Architecture deep dives
    'architecture/index.html': {'next': {'url': 'system.html', 'title': 'System Architecture'}},
    'architecture/system.html': {'next': {'url': 'components.html', 'title': 'Component Architecture'}},

    # Diagrams
    'diagrams/index.html': {'next': {'url': 'system_architecture.html', 'title': 'System Architecture Diagram'}},
    'diagrams/system_architecture.html': {'next': {'url': 'data_flow.html', 'title': 'Data Flow Diagram'}},
    'diagrams/data_flow.html': {'next': {'url': 'processing_pipeline.html', 'title': 'Processing Pipeline Diagram'}},
    'diagrams/processing_pipeline.html': {'next': {'url': 'source_system.html', 'title': 'Source System Diagram'}},
    'diagrams/source_system.html': {'next': {'url': 'class_diagrams.html', 'title': 'Class Diagrams'}},
    'diagrams/class_diagrams.html': {'next': {'url': 'deployment.html', 'title': 'Deployment Diagram'}},

    # Development guides
    'development/index.html': {'next': {'url': '01-architecture-logic.html', 'title': 'Architecture Logic'}},
    'development/01-architecture-logic.html': {'next': {'url': '02-team-onboarding.html', 'title': 'Team Onboarding'}},

    # Developer guides
    'developer/index.html': {'next': {'url': 'guide.html', 'title': 'Developer Guide'}},
}


def generate_navigation_html(next_url: str, next_title: str) -> str:
    """Generate the HTML for chapter navigation."""
    return f'''
<nav class="chapter-navigation" aria-label="Chapter navigation">
    <div class="next-chapter-content">
        <span class="next-chapter-label">Next Chapter</span>
        <span class="next-chapter-arrow" aria-hidden="true">→</span>
        <a href="{next_url}" class="next-chapter-link" rel="next">{next_title}</a>
    </div>
</nav>
'''


def get_relative_path(file_path: str) -> str:
    """Get the relative path from docs directory."""
    return file_path.replace('website/docs/', '')


def remove_existing_navigation(content: str) -> str:
    """Remove any existing chapter navigation from HTML."""
    # Remove navigation block with all its content
    pattern = r'<nav class="chapter-navigation"[^>]*>.*?</nav>\s*'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    return content


def add_navigation_to_file(file_path: Path, docs_dir: Path) -> bool:
    """Add navigation to a single HTML file."""
    try:
        # Get relative path from docs directory
        rel_path = str(file_path.relative_to(docs_dir))

        # Check if navigation is defined for this file
        if rel_path not in NAVIGATION_MAP:
            return False

        nav_info = NAVIGATION_MAP[rel_path].get('next')
        if not nav_info:
            return False

        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove any existing navigation
        content = remove_existing_navigation(content)

        # Generate navigation HTML
        nav_html = generate_navigation_html(nav_info['url'], nav_info['title'])

        # Find insertion point: before </div> that closes .doc-content
        # Look for the closing </div> before the footer
        pattern = r'(</div>\s*</div>\s*</div>\s*<!-- Footer -->)'

        if re.search(pattern, content):
            # Insert navigation before the closing divs
            content = re.sub(
                pattern,
                f'{nav_html}\\1',
                content,
                count=1
            )
        else:
            # Fallback: insert before closing body tag
            content = content.replace('</body>', f'{nav_html}\n</body>')

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Process all documentation HTML files."""
    # Get docs directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    docs_dir = project_dir / 'website' / 'docs'

    if not docs_dir.exists():
        print(f"Documentation directory not found: {docs_dir}")
        return

    # Find all HTML files recursively
    html_files = list(docs_dir.rglob('*.html'))

    print(f"Found {len(html_files)} HTML files in {docs_dir}")
    print(f"Processing files with navigation mappings...\n")

    processed = 0
    skipped = 0

    for html_file in html_files:
        rel_path = str(html_file.relative_to(docs_dir))

        if add_navigation_to_file(html_file, docs_dir):
            processed += 1
            print(f"✓ Added navigation to: {rel_path}")
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"Completed!")
    print(f"  Processed: {processed} files")
    print(f"  Skipped:   {skipped} files (no navigation defined)")
    print(f"  Total:     {len(html_files)} files")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
