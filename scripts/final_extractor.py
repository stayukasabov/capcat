#!/usr/bin/env python3
"""
This script intelligently extracts meaningful text content from HTML files, 
chunks it, and creates markdown files with placeholders for summaries.
"""

import os
import re
from pathlib import Path

def get_meaningful_text(html):
    """Extract meaningful text from an HTML string using a scoring system."""
    # 1. Remove noise tags
    html = re.sub(r'<script[^>]*>.*?<\/script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?<\/style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<header[^>]*>.*?<\/header>', '', html, flags=re.DOTALL)
    html = re.sub(r'<footer[^>]*>.*?<\/footer>', '', html, flags=re.DOTALL)
    html = re.sub(r'<nav[^>]*>.*?<\/nav>', '', html, flags=re.DOTALL)
    html = re.sub(r'<aside[^>]*>.*?<\/aside>', '', html, flags=re.DOTALL)

    # 2. Extract text from promising tags
    text_blocks = []
    for tag in ['p', 'h1', 'h2', 'h3', 'li', 'blockquote']:
        for match in re.finditer(r'<' + tag + r'[^>]*>(.*?)<\/' + tag + r'>', html, re.DOTALL):
            text_blocks.append(match.group(1))

    # 3. Score and filter the text blocks
    meaningful_text = []
    for block in text_blocks:
        text = strip_html_tags(block).strip()
        if not text:
            continue

        score = 0
        # Score based on length
        if len(text) > 100:
            score += 1
        # Score based on punctuation
        if '.' in text or ',' in text:
            score += 1
        # Penalize for code-like patterns
        if '{' in text or '}' in text or ';' in text:
            score -= 1

        if score > 1:
            meaningful_text.append(text)

    return "\n".join(meaningful_text)

def strip_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def main():
    """Main function"""
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

        meaningful_content = get_meaningful_text(content)
        if not meaningful_content:
            print(f"  No meaningful content found in {html_file.name}. Skipping.")
            continue

        # Chunk the text
        chunk_size = 4000
        chunks = [meaningful_content[i:i+chunk_size] for i in range(0, len(meaningful_content), chunk_size)]

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
