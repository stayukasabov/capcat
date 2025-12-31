#!/usr/bin/env python3
"""
Fix ethical-scraping.html links to use correct relative paths based on file location.
"""

import os
import re
from pathlib import Path

WEBSITE_ROOT = Path("/Users/xpro/SynologyDrive/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application/website")

# Files containing ethical-scraping links (from grep results)
files_with_links = [
    "index.html",
    "docs/architecture/system.html",
    "docs/development/diagrams/01-system-architecture.html",
    "docs/development/diagrams/02-onboarding-journey.html",
    "docs/diagrams/class_diagrams.html",
    "docs/diagrams/data_flow.html",
    "docs/diagrams/deployment.html",
    "docs/diagrams/processing_pipeline.html",
    "docs/diagrams/source_system.html",
    "docs/diagrams/system_architecture.html",
    "docs/Process-flow.html",
    "docs/README.html",
    "docs/ethical-scraping.html",
    "docs/api/capcat/capcat.html",
    "docs/api/capcat/index.html",
    "docs/api/capcat/README.html",
    "docs/api/cli/cli.html",
    "docs/api/cli/index.html",
    "docs/api/cli/README.html",
    "docs/api/convert_docs_to_html/convert_docs_to_html.html",
]

def calculate_relative_path(file_path: str) -> str:
    """
    Calculate the correct relative path to docs/ethical-scraping.html
    based on the file's location.

    Args:
        file_path: Relative path from website root (e.g., "docs/api/core/index.html")

    Returns:
        Correct relative path to ethical-scraping.html
    """
    # Get directory depth of the file
    file_dir = os.path.dirname(file_path)

    if not file_dir or file_dir == ".":
        # File is in website/ root
        return "docs/ethical-scraping.html"

    # Count directory depth
    depth = len(file_dir.split("/"))

    # If file is in docs/ directly
    if file_dir == "docs":
        return "ethical-scraping.html"

    # If file is in a subdirectory of docs/
    if file_dir.startswith("docs/"):
        # Go up to docs/ level
        levels_up = depth - 1  # -1 because "docs" is the first level
        return "../" * levels_up + "ethical-scraping.html"

    # Shouldn't happen, but fallback
    return "docs/ethical-scraping.html"


def update_file(file_path: Path, correct_path: str) -> tuple[bool, str, str]:
    """
    Update ethical-scraping links in a file.

    Returns:
        (changed, old_pattern, new_pattern)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match ethical-scraping links in footer
    # Captures various possible paths
    pattern = r'href="([^"]*ethical-scraping\.html)"'

    matches = re.findall(pattern, content)
    if not matches:
        return False, "", correct_path

    old_path = matches[0] if matches else ""

    # Replace all occurrences with correct path
    new_content = re.sub(pattern, f'href="{correct_path}"', content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, old_path, correct_path

    return False, old_path, correct_path


def main():
    """Update all files with correct relative paths."""
    print("Fixing ethical-scraping.html links...\n")

    updated_files = []
    patterns_found = {}

    # Find ALL html files in website directory
    all_html_files = []
    for root, dirs, files in os.walk(WEBSITE_ROOT):
        for file in files:
            if file.endswith('.html'):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(WEBSITE_ROOT)
                all_html_files.append(str(rel_path))

    print(f"Found {len(all_html_files)} HTML files total\n")

    for rel_path in all_html_files:
        file_path = WEBSITE_ROOT / rel_path

        if not file_path.exists():
            print(f"Warning: File not found: {file_path}")
            continue

        # Calculate correct relative path
        correct_path = calculate_relative_path(rel_path)

        # Update file
        changed, old_path, new_path = update_file(file_path, correct_path)

        if changed:
            updated_files.append(rel_path)
            if old_path not in patterns_found:
                patterns_found[old_path] = []
            patterns_found[old_path].append(rel_path)
            print(f"✓ Updated: {rel_path}")
            print(f"  {old_path} → {new_path}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal files updated: {len(updated_files)}")

    if patterns_found:
        print(f"\nIncorrect link patterns found:")
        for old_pattern, files in sorted(patterns_found.items()):
            print(f"\n  '{old_pattern}' found in {len(files)} file(s):")
            for f in files[:5]:  # Show first 5
                print(f"    - {f}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")

    print("\n✓ All ethical-scraping links now use correct relative paths")

    # Verification
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)

    verification_samples = [
        ("index.html", "docs/ethical-scraping.html"),
        ("docs/source-development.html", "ethical-scraping.html"),
        ("docs/developer/guide.html", "../ethical-scraping.html"),
        ("docs/api/capcat/capcat.html", "../../ethical-scraping.html"),
        ("docs/development/diagrams/01-system-architecture.html", "../../ethical-scraping.html"),
    ]

    print("\nSample verification:")
    for file_rel, expected_path in verification_samples:
        file_path = WEBSITE_ROOT / file_rel
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            match = re.search(r'href="([^"]*ethical-scraping\.html)"', content)
            if match:
                actual_path = match.group(1)
                status = "✓" if actual_path == expected_path else "✗"
                print(f"{status} {file_rel}")
                print(f"  Expected: {expected_path}")
                print(f"  Actual:   {actual_path}")
            else:
                print(f"- {file_rel} (no ethical-scraping link found)")


if __name__ == "__main__":
    main()
