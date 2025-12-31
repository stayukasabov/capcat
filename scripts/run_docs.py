#!/usr/bin/env python3
"""
Documentation Generation Runner

Convenient script to generate all documentation types.
"""

import os
import sys
import time
from pathlib import Path


def run_command(command, description):
    """Run a command and report status."""
    print(f"\n🔄 {description}...")
    start_time = time.time()

    result = os.system(command)
    duration = time.time() - start_time

    if result == 0:
        print(f"✅ {description} completed in {duration:.1f}s")
        return True
    else:
        print(f"❌ {description} failed after {duration:.1f}s")
        return False


def main():
    """Main documentation generation runner."""
    print("📚 Capcat Documentation Generator")
    print("=" * 50)

    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    print(f"Working directory: {project_root}")

    # Create docs directory if it doesn't exist
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)

    success_count = 0
    total_tasks = 0

    # Task 1: Generate API documentation
    total_tasks += 1
    if run_command("python3 scripts/doc_generator.py", "API documentation generation"):
        success_count += 1

    # Task 2: Generate architecture diagrams
    total_tasks += 1
    if run_command("python3 scripts/generate_diagrams.py", "Architecture diagrams generation"):
        success_count += 1

    # Summary
    print("\n📊 Documentation Generation Summary")
    print("=" * 50)
    print(f"Tasks completed: {success_count}/{total_tasks}")

    if success_count == total_tasks:
        print("🎉 All documentation generated successfully!")
        print(f"\n📁 Documentation available in: {docs_dir}")
        print("\n🚀 Quick start:")
        print(f"   - Open {docs_dir}/index.md for the main documentation index")
        print(f"   - Browse {docs_dir}/README.md for the project overview")
        print(f"   - Check {docs_dir}/api/ for detailed API documentation")
        print(f"   - View {docs_dir}/architecture/ for system design")
    else:
        failed_tasks = total_tasks - success_count
        print(f"⚠️ {failed_tasks} task(s) failed. Check the output above for details.")

    # Generate documentation manifest
    manifest_path = docs_dir / "manifest.txt"
    with open(manifest_path, 'w') as f:
        f.write(f"""Capcat Documentation Manifest
Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
Success rate: {success_count}/{total_tasks} tasks

Generated Documentation:
""")

        # List all generated files
        for doc_file in sorted(docs_dir.rglob("*.md")):
            relative_path = doc_file.relative_to(docs_dir)
            f.write(f"  - {relative_path}\n")

        f.write(f"\nTotal files: {len(list(docs_dir.rglob('*')))}\n")
        f.write(f"Documentation size: {get_directory_size(docs_dir):.1f} MB\n")

    print(f"\n📄 Documentation manifest created: {manifest_path}")

    return 0 if success_count == total_tasks else 1


def get_directory_size(directory):
    """Get directory size in MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                pass
    return total_size / (1024 * 1024)


if __name__ == "__main__":
    sys.exit(main())