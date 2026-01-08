#!/usr/bin/env python3
"""
Convert Markdown Tables to Centered HTML Tables

Scans all markdown files in website/docs/ directory and converts
markdown tables to centered HTML tables with proper styling.

Usage:
    python scripts/convert_md_tables_to_html.py [--dry-run]
"""

import re
import os
from pathlib import Path
from typing import List, Tuple


class MarkdownTableConverter:
    """Convert markdown tables to centered HTML tables."""

    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.stats = {
            "files_scanned": 0,
            "files_modified": 0,
            "tables_converted": 0
        }

    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in docs directory."""
        return list(self.docs_dir.rglob("*.md"))

    def detect_markdown_table(self, content: str) -> List[Tuple[int, int, str]]:
        """
        Detect markdown tables in content.

        Returns:
            List of tuples (start_line, end_line, table_text)
        """
        tables = []
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Check if line contains pipe characters (potential table)
            if '|' in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()

                # Check if next line is separator (|---|---| or |-------------|-------------|)
                if re.match(r'^\|?[-|]+\|?[-|]+\|?$', next_line):
                    # Found a table, collect all rows
                    start_line = i
                    table_lines = [lines[i]]
                    i += 1

                    # Add separator row
                    table_lines.append(lines[i])
                    i += 1

                    # Collect remaining table rows
                    while i < len(lines) and '|' in lines[i]:
                        table_lines.append(lines[i])
                        i += 1

                    end_line = i - 1
                    table_text = '\n'.join(table_lines)
                    tables.append((start_line, end_line, table_text))
                    continue

            i += 1

        return tables

    def parse_markdown_table(self, table_text: str) -> Tuple[List[str], List[List[str]]]:
        """
        Parse markdown table into headers and rows.

        Args:
            table_text: Raw markdown table text

        Returns:
            Tuple of (headers, rows)
        """
        lines = [line.strip() for line in table_text.split('\n') if line.strip()]

        # Parse header
        header_line = lines[0]
        headers = [cell.strip() for cell in header_line.split('|') if cell.strip()]

        # Skip separator line (lines[1])

        # Parse data rows
        rows = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                rows.append(cells)

        return headers, rows

    def convert_to_html_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """
        Convert parsed table to centered HTML table.

        Args:
            headers: List of header cells
            rows: List of row data (each row is a list of cells)

        Returns:
            HTML table string with center alignment
        """
        html_parts = []
        html_parts.append('<div class="table-container">')
        html_parts.append('<table class="centered-table">')

        # Add header
        html_parts.append('  <thead>')
        html_parts.append('    <tr>')
        for header in headers:
            html_parts.append(f'      <th>{self._escape_html(header)}</th>')
        html_parts.append('    </tr>')
        html_parts.append('  </thead>')

        # Add body
        html_parts.append('  <tbody>')
        for row in rows:
            html_parts.append('    <tr>')
            for cell in row:
                html_parts.append(f'      <td>{self._escape_html(cell)}</td>')
            html_parts.append('    </tr>')
        html_parts.append('  </tbody>')

        html_parts.append('</table>')
        html_parts.append('</div>')

        return '\n'.join(html_parts)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters but preserve code formatting."""
        # Handle code blocks with backticks
        if '`' in text:
            text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

        return text

    def convert_file(self, file_path: Path, dry_run: bool = False) -> int:
        """
        Convert markdown tables in a single file.

        Args:
            file_path: Path to markdown file
            dry_run: If True, only report changes without modifying

        Returns:
            Number of tables converted
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return 0

        tables = self.detect_markdown_table(content)

        if not tables:
            return 0

        # Convert tables from end to start to preserve line numbers
        converted_content = content
        lines = content.split('\n')
        tables_converted = 0

        for start_line, end_line, table_text in reversed(tables):
            try:
                headers, rows = self.parse_markdown_table(table_text)
                html_table = self.convert_to_html_table(headers, rows)

                # Replace markdown table with HTML table
                lines_before = lines[:start_line]
                lines_after = lines[end_line + 1:]
                lines = lines_before + [html_table] + lines_after

                tables_converted += 1
                print(f"  ✓ Converted table at line {start_line + 1}")

            except Exception as e:
                print(f"  ✗ Error converting table at line {start_line + 1}: {e}")

        if tables_converted > 0:
            converted_content = '\n'.join(lines)

            if not dry_run:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(converted_content)
                    print(f"  ✓ Saved changes to {file_path}")
                except Exception as e:
                    print(f"  ✗ Error writing {file_path}: {e}")
                    return 0
            else:
                print(f"  [DRY RUN] Would save changes to {file_path}")

        return tables_converted

    def convert_all(self, dry_run: bool = False) -> None:
        """
        Convert all markdown tables in docs directory.

        Args:
            dry_run: If True, only report changes without modifying
        """
        md_files = self.find_markdown_files()

        print(f"\nScanning {len(md_files)} markdown files in {self.docs_dir}/\n")

        for md_file in md_files:
            self.stats["files_scanned"] += 1
            relative_path = md_file.relative_to(self.docs_dir.parent)

            print(f"Processing: {relative_path}")
            tables_converted = self.convert_file(md_file, dry_run)

            if tables_converted > 0:
                self.stats["files_modified"] += 1
                self.stats["tables_converted"] += tables_converted
            else:
                print(f"  No tables found")
            print()

        self.print_summary(dry_run)

    def print_summary(self, dry_run: bool = False) -> None:
        """Print conversion summary."""
        print("=" * 60)
        print("CONVERSION SUMMARY")
        print("=" * 60)
        print(f"Files scanned:    {self.stats['files_scanned']}")
        print(f"Files modified:   {self.stats['files_modified']}")
        print(f"Tables converted: {self.stats['tables_converted']}")

        if dry_run:
            print("\n[DRY RUN] No files were actually modified.")
        print()


def add_css_styles() -> None:
    """Add centered table styles to main.css if not already present."""
    css_file = Path("website/css/main.css")

    table_styles = """
/* ====================================
   CENTERED TABLES
   ================================== */

.table-container {
  display: flex;
  justify-content: center;
  margin: var(--space-lg) 0;
  overflow-x: auto;
  width: 100%;
}

.centered-table {
  border-collapse: collapse;
  margin: 0 auto;
  background-color: var(--card-bg);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  min-width: 300px;
  max-width: 100%;
}

.centered-table thead {
  background-color: var(--accent-primary);
  color: #ffffff;
}

.centered-table th {
  padding: var(--space-sm) var(--space-md);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  font-size: var(--text-base);
  border-bottom: 2px solid var(--border-color);
}

.centered-table td {
  padding: var(--space-sm) var(--space-md);
  border-bottom: 1px solid var(--border-color);
  font-size: var(--text-base);
}

.centered-table tbody tr:hover {
  background-color: var(--code-bg);
  transition: background-color var(--transition-fast);
}

.centered-table tbody tr:last-child td {
  border-bottom: none;
}

.centered-table code {
  background-color: var(--code-bg);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-family: var(--font-family-mono);
  font-size: 0.9em;
}

/* Responsive table */
@media (max-width: 768px) {
  .table-container {
    margin: var(--space-md) 0;
  }

  .centered-table {
    font-size: var(--text-small);
  }

  .centered-table th,
  .centered-table td {
    padding: var(--space-xs) var(--space-sm);
  }
}
"""

    try:
        if not css_file.exists():
            print(f"Warning: {css_file} not found")
            return

        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'CENTERED TABLES' in content:
            print(f"✓ Table styles already exist in {css_file}")
            return

        # Add styles at the end of the file
        with open(css_file, 'a', encoding='utf-8') as f:
            f.write(table_styles)

        print(f"✓ Added centered table styles to {css_file}")

    except Exception as e:
        print(f"✗ Error adding CSS styles: {e}")


def main():
    """Main execution function."""
    import sys

    dry_run = '--dry-run' in sys.argv

    print("\n" + "=" * 60)
    print("MARKDOWN TABLE TO HTML CONVERTER")
    print("=" * 60)

    if dry_run:
        print("\n[DRY RUN MODE] No files will be modified\n")

    # Add CSS styles first
    print("\nStep 1: Adding CSS styles...")
    add_css_styles()

    # Convert markdown tables
    print("\nStep 2: Converting markdown tables...")
    converter = MarkdownTableConverter(docs_dir="docs")
    converter.convert_all(dry_run=dry_run)


if __name__ == "__main__":
    main()
