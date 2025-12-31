#!/usr/bin/env python3
"""
Remove internal development files from git tracking.
These files should not be in the public repository.
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a shell command and print status."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}", file=sys.stderr)
    return result.returncode == 0

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     REMOVE DEVELOPMENT FILES FROM PUBLIC REPOSITORY         ║
╚══════════════════════════════════════════════════════════════╝

Files to remove from git tracking:
- Reports/ (session documentation)
- tests/ (unit tests - optional, currently keeping)
- docs-markdown/ (markdown source, redundant with docs/)
- metrics/ (development metrics)
- CLAUDE.md (AI project instructions)
- *ANALYSIS.md, *SUMMARY.md, *REPORT.md files
- One-off build scripts (cleanup_repo.py, fix_*.py, etc.)
- Test scripts in root (test_*.py, TEST_*.sh)

These remain in working directory for local development.
    """)

    response = input("\nProceed? [y/N]: ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    # 1. Remove development directories
    print("\n\nPHASE 1: Development Directories")

    dev_dirs = [
        'Reports',
        'docs-markdown',
        'metrics'
    ]

    for dir_name in dev_dirs:
        run_command(
            f'git rm -r --cached "{dir_name}" 2>/dev/null || echo "Not tracked: {dir_name}"',
            f"Remove {dir_name}/ from git"
        )

    # 2. Remove development documentation
    print("\n\nPHASE 2: Development Documentation")

    run_command(
        'git ls-files | grep -E "(CLAUDE\\.md|CLEANUP_ANALYSIS\\.md|.*ANALYSIS\\.md|.*SUMMARY\\.md|.*REPORT\\.md|.*COMPLETE\\.md)" | xargs -r git rm --cached',
        "Remove development docs"
    )

    # 3. Remove one-off build scripts
    print("\n\nPHASE 3: One-Off Build Scripts")

    scripts = [
        'cleanup_repo.py',
        'add_jekyll_frontmatter.py',
        'update_includes.py',
        'convert_docs_to_html.py',
        'convert_to_markdown.py',
        'delete_h4_colon.py',
        'fix_colon_formatting.py',
        'fix_ethical_scraping_links.py',
        'fix_footer_typo.py',
        'fix_mismatched_tags.py',
        'fix_sources_in_docs.py',
        'fix_ascii_formatting.py',
        'remove_br_tags.py',
        'remove_hr_tags.py',
        'replace_h4_with_h3.py',
        'replace_strong_tags.py',
        'replace_strong_with_h4.py'
    ]

    for script in scripts:
        run_command(
            f'git rm --cached "{script}" 2>/dev/null || echo "Not tracked: {script}"',
            f"Remove {script}"
        )

    # 4. Remove test scripts from root
    print("\n\nPHASE 4: Test Scripts in Root")

    run_command(
        'git ls-files | grep -E "^test_.*\\.py$|^TEST_.*\\.(sh|md)$" | xargs -r git rm --cached',
        "Remove test scripts from root"
    )

    # 5. Optional: Remove tests directory (commented out by default)
    # print("\n\nPHASE 5: Tests Directory (Optional)")
    # run_command('git rm -r --cached tests/', "Remove tests/ from git")

    # 6. Show status
    print("\n\nFINAL STATUS:")
    run_command('git status --short | head -50', "Git status")

    print(f"""

╔══════════════════════════════════════════════════════════════╗
║                    CLEANUP COMPLETE                          ║
╚══════════════════════════════════════════════════════════════╝

Next steps:

1. Review changes:
   git status

2. Commit:
   git commit -m "Remove development artifacts from public repository"

3. Push:
   git push origin main

4. Files remain in working directory for local development.
   Updated .gitignore prevents re-adding them.

Note: tests/ directory is KEPT by default (standard for open source).
      To make tests private, uncomment tests/ in .gitignore and re-run.
    """)

if __name__ == '__main__':
    main()
