#!/usr/bin/env python3
"""
Repository cleanup script: Remove unnecessary files from git tracking.
This script removes backup files, backup directories, and other temporary files.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and print status."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}", file=sys.stderr)

    return result.returncode == 0

def main():
    """Main cleanup process."""

    print("""
╔══════════════════════════════════════════════════════════════╗
║           CAPCAT REPOSITORY CLEANUP SCRIPT                   ║
║                                                              ║
║  This will remove from git tracking:                        ║
║  - 684 .backup files                                        ║
║  - Backup directories (website/, docs_backup_*, etc.)       ║
║  - Log files                                                ║
║  - System files (__pycache__, .DS_Store, etc.)             ║
║                                                              ║
║  ~67MB will be cleaned from repository                      ║
╚══════════════════════════════════════════════════════════════╝
    """)

    response = input("\nProceed with cleanup? [y/N]: ")
    if response.lower() != 'y':
        print("Cleanup cancelled.")
        return

    # 1. Remove .backup files from git
    print("\n\n" + "="*60)
    print("PHASE 1: Removing .backup files from git tracking")
    print("="*60)

    run_command(
        'git ls-files | grep "\\.backup$" | xargs -r git rm --cached',
        "Remove .backup files from git index"
    )

    # 2. Remove backup directories from git
    print("\n\n" + "="*60)
    print("PHASE 2: Removing backup directories from git tracking")
    print("="*60)

    backup_dirs = [
        'website',
        'docs/docs_backup_20251128_164515',
        'docs/hybrid_utility_refactor'
    ]

    for dir_path in backup_dirs:
        if Path(dir_path).exists():
            run_command(
                f'git rm -r --cached "{dir_path}"',
                f"Remove {dir_path} from git tracking"
            )

    # 3. Remove system files from git
    print("\n\n" + "="*60)
    print("PHASE 3: Removing system files from git tracking")
    print("="*60)

    system_files = [
        '__pycache__',
        '.DS_Store',
        '.pytest_cache',
        'debug.log',
        'docs_regeneration.log',
        'docs_regeneration_foss.log'
    ]

    for file_path in system_files:
        if Path(file_path).exists():
            run_command(
                f'git rm -rf --cached "{file_path}" 2>/dev/null || true',
                f"Remove {file_path} from git tracking"
            )

    # 4. Show status
    print("\n\n" + "="*60)
    print("PHASE 4: Git status after cleanup")
    print("="*60)

    run_command('git status --short | head -50', "Show git status")

    # 5. Instructions
    print(f"""

╔══════════════════════════════════════════════════════════════╗
║                    CLEANUP COMPLETE                          ║
╚══════════════════════════════════════════════════════════════╝

Next steps:

1. Review changes:
   git status

2. Commit the cleanup:
   git commit -m "Clean up repository: remove backup files and directories"

3. Push to remote:
   git push origin main

4. (Optional) Clean working directory:
   # Remove .backup files from disk
   find . -name "*.backup" -type f -delete

   # Remove backup directories from disk
   rm -rf website/
   rm -rf docs/docs_backup_20251128_164515/
   rm -rf docs/hybrid_utility_refactor/

   # Remove log files
   rm -f *.log

5. The updated .gitignore will prevent these files from being added again.
    """)

if __name__ == '__main__':
    main()
