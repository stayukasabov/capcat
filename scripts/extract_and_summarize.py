#!/usr/bin/env python3
"""
This script extracts text from HTML files in the AgentBrew folder, 
chunks it, and creates markdown files with placeholders for summaries.
"""

import os
import re
from pathlib import Path

def strip_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def main():
    """Main function"""
    # The user specified the AgentBrew folder, which is at the root of the project.
    # The script is in the scripts folder, so we need to go up one level.
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    research_dir = base_dir / 'Anthropic research for Capcat Presentation'
    summaries_dir = base_dir / 'summaries'
    summaries_dir.mkdir(exist_ok=True)

    print(f"Scanning for HTML files in: {research_dir}")

    html_files = list(research_dir.glob('*.html'))

    print(f"Found {len(html_files)} HTML files to process.")

    for html_file in html_files:
        print(f"Processing {html_file.name}...")
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        text_content = strip_html_tags(content)
        # Replace multiple newlines with a single one
        text_content = re.sub(r'\n+', '\n', text_content).strip()

        # Chunk the text
        chunk_size = 4000
        chunks = [text_content[i:i+chunk_size] for i in range(0, len(text_content), chunk_size)]

        for i, chunk in enumerate(chunks):
            md_file_name = f"{html_file.stem}_chunk_{i+1}.md"
            md_file_path = summaries_dir / md_file_name

            md_content = f"# Summary for {md_file_name}\n\n"
            md_content += f"**Original Text:**\n> {chunk}\n\n"
            md_content += f"**Summary:**\n> [TODO: Add summary here]"

            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"  Created summary placeholder: {md_file_path.name}")

    print("\nProcessing complete.")
    print(f"Summary placeholders created in: {summaries_dir}")

if __name__ == "__main__":
    main()
