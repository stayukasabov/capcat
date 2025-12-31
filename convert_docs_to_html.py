#!/usr/bin/env python3
"""
Convert Markdown documentation to clean HTML with minimal styling.
Only applies styling to code blocks, ASCII art, and Mermaid diagrams.
"""

import os
import re
from pathlib import Path
import html

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import HtmlFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

def create_basic_html_template():
    """Create a clean HTML template with minimal styling."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}

        /* Code styling */
        code {{
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 0.9em;
        }}

        pre {{
            background-color: #f8f8f8;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 0.85em;
            line-height: 1.45;
        }}

        pre code {{
            background: none;
            padding: 0;
            border-radius: 0;
        }}

        /* ASCII Art and Mermaid styling */
        .ascii-art, .mermaid {{
            background-color: #f6f8fa;
            border: 1px solid #d1d5da;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            white-space: pre;
            line-height: 1.2;
            position: relative;
        }}

        /* Mermaid container wrapper */
        .mermaid-container {{
            position: relative;
            margin: 20px 0;
        }}

        /* Copy button for Mermaid diagrams */
        .mermaid-copy-btn {{
            position: absolute;
            top: 8px;
            right: 8px;
            background-color: #0366d6;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 12px;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 10;
        }}

        .mermaid-container:hover .mermaid-copy-btn {{
            opacity: 1;
        }}

        .mermaid-copy-btn:hover {{
            background-color: #0256c7;
        }}

        .mermaid-copy-btn.copied {{
            background-color: #22863a;
        }}

        /* Navigation styling */
        .nav-breadcrumb {{
            margin-bottom: 20px;
            padding: 10px 0;
            border-bottom: 1px solid #e1e4e8;
        }}

        .nav-breadcrumb a {{
            color: #0366d6;
            text-decoration: none;
        }}

        .nav-breadcrumb a:hover {{
            text-decoration: underline;
        }}

        /* Table styling */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}

        th, td {{
            border: 1px solid #d1d5da;
            padding: 8px 12px;
            text-align: left;
        }}

        th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}

        /* Link styling */
        a {{
            color: #0366d6;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        /* Blockquote styling */
        blockquote {{
            border-left: 4px solid #d1d5da;
            padding-left: 16px;
            margin-left: 0;
            color: #6a737d;
        }}

        /* List styling */
        ul, ol {{
            padding-left: 30px;
        }}

        li {{
            margin: 4px 0;
        }}

        /* Header styling */
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}

        h1 {{
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 10px;
        }}

        h2 {{
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 8px;
        }}
    </style>
</head>
<body>
{navigation}
{content}

<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{ startOnLoad: true }});

  // Add copy buttons to Mermaid diagrams after rendering
  document.addEventListener('DOMContentLoaded', function() {{
    const mermaidDivs = document.querySelectorAll('.mermaid');

    mermaidDivs.forEach(function(mermaidDiv) {{
      // Get the original Mermaid source code
      const mermaidSource = mermaidDiv.textContent;

      // Create container wrapper
      const container = document.createElement('div');
      container.className = 'mermaid-container';

      // Create copy button
      const copyBtn = document.createElement('button');
      copyBtn.className = 'mermaid-copy-btn';
      copyBtn.textContent = 'Copy Mermaid Code';
      copyBtn.setAttribute('title', 'Copy diagram code for Draw.io, Mermaid Live, etc.');

      copyBtn.addEventListener('click', function() {{
        navigator.clipboard.writeText(mermaidSource).then(function() {{
          copyBtn.textContent = 'Copied!';
          copyBtn.classList.add('copied');

          setTimeout(function() {{
            copyBtn.textContent = 'Copy Mermaid Code';
            copyBtn.classList.remove('copied');
          }}, 2000);
        }});
      }});

      // Wrap the mermaid div in container and add button
      mermaidDiv.parentNode.insertBefore(container, mermaidDiv);
      container.appendChild(mermaidDiv);
      container.appendChild(copyBtn);
    }});
  }});
</script>
</body>
</html>"""

def detect_ascii_art(content):
    """Detect ASCII art patterns in content."""
    ascii_patterns = [
        r'[│├└─]+',  # Box drawing characters
        r'[▶▼◀▲]+',  # Arrow characters
        r'[┌┐┘└─│┬┴┼]+',  # More box drawing
        r'[═║╔╗╚╝╬╠╣╦╩]+',  # Double line box drawing
        r'____+',  # Underscores (common in ASCII art)
    ]

    for pattern in ascii_patterns:
        if re.search(pattern, content):
            return True
    return False

def convert_markdown_to_html(markdown_content, title="Documentation"):
    """Convert markdown content to HTML with minimal styling."""

    # Extract code blocks BEFORE escaping HTML entities
    code_blocks = {}
    code_block_counter = [0]

    def extract_code_block(match):
        lang = match.group(1) if match.group(1) else ''
        code_content = match.group(2)

        # Store original unescaped content
        placeholder = f"___CODE_BLOCK_{code_block_counter[0]}___"
        code_blocks[placeholder] = (lang, code_content)
        code_block_counter[0] += 1
        return placeholder

    content = re.sub(r'```(\w+)?\n(.*?)```', extract_code_block, markdown_content, flags=re.DOTALL)

    # NOW escape HTML entities (but code blocks are safe as placeholders)
    content = html.escape(content)

    # Convert headers
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    content = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', content, flags=re.MULTILINE)
    content = re.sub(r'^###### (.+)$', r'<h6>\1</h6>', content, flags=re.MULTILINE)

    # Convert inline code BEFORE restoring code blocks
    # (inline code uses single backticks which won't be in placeholders)
    content = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', content)

    # Convert links - handle both [text](url) and [text](url "title")
    content = re.sub(r'\[([^\]]+)\]\(([^)]+?)(?:\s+"[^"]*")?\)', r'<a href="\2">\1</a>', content)

    # Convert bold and italic
    content = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*([^\*]+)\*', r'<em>\1</em>', content)

    # Convert lists
    # Unordered lists
    lines = content.split('\n')
    in_ul = False
    in_ol = False
    result_lines = []

    for line in lines:
        # Handle unordered lists
        if re.match(r'^\s*[-*+]\s+(.+)', line):
            match = re.match(r'^(\s*)[-*+]\s+(.+)', line)
            indent_level = len(match.group(1)) // 2

            if not in_ul:
                result_lines.append('<ul>')
                in_ul = True
            elif in_ol:
                result_lines.append('</ol>')
                in_ol = False
                result_lines.append('<ul>')
                in_ul = True

            result_lines.append(f'<li>{match.group(2)}</li>')

        # Handle ordered lists
        elif re.match(r'^\s*\d+\.\s+(.+)', line):
            match = re.match(r'^(\s*)\d+\.\s+(.+)', line)

            if not in_ol:
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                result_lines.append('<ol>')
                in_ol = True

            result_lines.append(f'<li>{match.group(2)}</li>')

        # Handle blockquotes
        elif line.startswith('>'):
            quote_text = line[1:].strip()
            result_lines.append(f'<blockquote>{quote_text}</blockquote>')

        # Handle horizontal rules
        elif re.match(r'^[-*]{3,}$', line.strip()):
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False
            result_lines.append('<hr>')

        # Regular text
        else:
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False

            # Check if line is a code block placeholder - don't wrap it
            if re.match(r'^___CODE_BLOCK_\d+___$', line.strip()):
                result_lines.append(line)
            # Convert empty lines to <br> and non-empty to <p>
            elif line.strip() == '':
                result_lines.append('<br>')
            elif not re.match(r'<[^>]+>', line):  # Don't wrap already converted HTML
                result_lines.append(f'<p>{line}</p>')
            else:
                result_lines.append(line)

    # Close any open lists
    if in_ul:
        result_lines.append('</ul>')
    if in_ol:
        result_lines.append('</ol>')

    content = '\n'.join(result_lines)

    # Clean up multiple <br> tags and empty <p> tags
    content = re.sub(r'<br>\s*<br>', '<br>', content)
    content = re.sub(r'<p>\s*</p>', '', content)
    content = re.sub(r'<p>\s*<br>\s*</p>', '<br>', content)

    # NOW restore code blocks (after all line processing)
    def restore_code_block(match):
        placeholder = match.group(0)
        if placeholder in code_blocks:
            lang, code_content = code_blocks[placeholder]

            # Check if it's ASCII art or Mermaid
            if lang.lower() in ['mermaid', 'ascii'] or detect_ascii_art(code_content):
                css_class = 'mermaid' if lang.lower() == 'mermaid' else 'ascii-art'
                # For Mermaid, keep content raw (unescaped)
                # For ASCII art, escape it
                if lang.lower() == 'mermaid':
                    return f'<div class="{css_class}">{code_content}</div>'
                else:
                    return f'<div class="{css_class}">{html.escape(code_content)}</div>'
            else:
                # Use Pygments for syntax highlighting if available
                if PYGMENTS_AVAILABLE and lang:
                    try:
                        lexer = get_lexer_by_name(lang, stripall=True)
                        formatter = HtmlFormatter(noclasses=False, cssclass='highlight')
                        highlighted = highlight(code_content, lexer, formatter)
                        return highlighted
                    except:
                        # Fallback to plain code block if Pygments fails
                        return f'<pre><code>{html.escape(code_content)}</code></pre>'
                else:
                    return f'<pre><code>{html.escape(code_content)}</code></pre>'
        return placeholder

    content = re.sub(r'___CODE_BLOCK_\d+___', restore_code_block, content)

    return content

def create_navigation(file_path, base_path):
    """Create navigation breadcrumb for the file."""
    rel_path = os.path.relpath(file_path, base_path)
    parts = rel_path.split(os.sep)[:-1]  # Exclude filename

    nav_links = ['<a href="../index.html">Documentation Home</a>']

    current_path = ""
    for i, part in enumerate(parts):
        current_path = os.path.join(current_path, part)
        if i == len(parts) - 1:
            nav_links.append(part)
        else:
            # Calculate relative path to index
            nav_links.append(f'<a href="../{current_path}/index.html">{part}</a>')

    return '<div class="nav-breadcrumb">' + ' / '.join(nav_links) + '</div>'

def process_file(md_file_path, output_dir, docs_base_dir):
    """Process a single markdown file."""
    print(f"Processing: {md_file_path}")

    with open(md_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        markdown_content = f.read()

    # Get relative path structure
    rel_path = os.path.relpath(md_file_path, docs_base_dir)
    output_path = os.path.join(output_dir, rel_path).replace('.md', '.html')

    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Extract title from filename or first header
    title = os.path.basename(md_file_path).replace('.md', '').replace('_', ' ').replace('-', ' ').title()

    # Look for first header in content
    header_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
    if header_match:
        title = header_match.group(1)

    # Convert content
    html_content = convert_markdown_to_html(markdown_content, title)

    # Create navigation
    navigation = create_navigation(md_file_path, docs_base_dir)

    # Generate final HTML
    template = create_basic_html_template()
    final_html = template.format(
        title=title,
        navigation=navigation,
        content=html_content
    )

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    return output_path, title

def create_directory_index(dir_path, title):
    """Create an index.html file for a directory."""
    index_path = os.path.join(dir_path, 'index.html')

    # Get all HTML files in directory
    html_files = []
    for file in os.listdir(dir_path):
        if file.endswith('.html') and file != 'index.html':
            html_files.append(file)

    # Get all subdirectories
    subdirs = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            subdirs.append(item)

    content = f'<h1>{title}</h1>\n'

    # Special handling for root index (HTML-Docs directory)
    if dir_path.endswith('HTML-Docs'):
        content += '<ul>\n'
        # List main documentation areas
        content += '<li><a href="quick-start.html">Quick Start</a></li>\n'
        content += '<li><a href="tutorials/index.html">Tutorials</a></li>\n'
        content += '<li><a href="api-reference.html">API Reference</a></li>\n'
        content += '<li><a href="architecture.html">Architecture</a></li>\n'
        content += '<li><a href="DIAGRAMS_INDEX.html">Diagrams Index</a></li>\n'
        content += '<li><a href="interactive-mode.html">Interactive Mode</a></li>\n'
        content += '<li><a href="configuration.html">Configuration</a></li>\n'
        content += '<li><a href="source-development.html">Source Development</a></li>\n'
        content += '<li><a href="testing.html">Testing</a></li>\n'
        content += '<li><a href="deployment.html">Deployment</a></li>\n'
        content += '<li><a href="ethical-scraping.html">Ethical Scraping</a></li>\n'
        content += '<li><a href="dependencies.html">Dependencies</a></li>\n'
        content += '</ul>\n'
    # Special handling for tutorials directory
    elif 'tutorials' in dir_path:
        content += '<h2>Available Documentation</h2>\n<ul>\n'
        # Add user guides directly
        user_guides = [
            ('user/01-getting-started.html', 'Getting Started'),
            ('user/02-daily-workflow.html', 'Daily Workflow'),
            ('user/03-interactive-mode.html', 'Interactive Mode'),
            ('user/04-managing-sources.html', 'Managing Sources'),
            ('user/05-bundles.html', 'Bundles'),
            ('user/06-customizing-output.html', 'Customizing Output'),
        ]
        for href, name in user_guides:
            content += f'<li><a href="{href}">{name}</a></li>\n'

        # Add exhaustive references
        for html_file in sorted(html_files):
            if html_file.startswith('0') and 'exhaustive' in html_file:
                name = html_file.replace('.html', '').replace('-exhaustive', ' Reference').replace('01-cli-commands', 'CLI Commands').replace('02-interactive-mode', 'Interactive Mode').replace('03-configuration', 'Configuration').replace('04-source-system', 'Source System').replace('05-api-functions', 'API Functions')
                content += f'<li><a href="{html_file}">{name}</a></li>\n'

        # Add README files
        for html_file in sorted(html_files):
            if 'README' in html_file:
                content += f'<li><a href="{html_file}">Documentation Index</a></li>\n'
        content += '<li><a href="user/README.html">User Guides Index</a></li>\n'
        content += '</ul>\n'
    else:
        # Default behavior for other directories
        if subdirs:
            content += '<h2>Subdirectories</h2>\n<ul>\n'
            for subdir in sorted(subdirs):
                content += f'<li><a href="{subdir}/index.html">{subdir.replace("_", " ").title()}</a></li>\n'
            content += '</ul>\n'

        if html_files:
            content += '<h2>Documents</h2>\n<ul>\n'
            for html_file in sorted(html_files):
                name = html_file.replace('.html', '').replace('_', ' ').replace('-', ' ').title()
                content += f'<li><a href="{html_file}">{name}</a></li>\n'
            content += '</ul>\n'

    template = create_basic_html_template()

    # No navigation breadcrumb for root index
    nav = '' if dir_path.endswith('HTML-Docs') else '<div class="nav-breadcrumb"><a href="../index.html">Documentation Home</a></div>'

    html = template.format(
        title=title,
        navigation=nav,
        content=content
    )

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    """Main conversion function."""
    docs_dir = 'docs'
    output_dir = 'HTML-Docs'

    if not os.path.exists(docs_dir):
        print(f"Error: {docs_dir} directory not found")
        return

    print(f"Converting markdown files from {docs_dir} to {output_dir}")
    print(f"Found markdown files to process...")

    # Process all markdown files
    converted_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                try:
                    output_path, title = process_file(md_path, output_dir, docs_dir)
                    converted_files.append((output_path, title))
                except Exception as e:
                    print(f"Error processing {md_path}: {e}")

    print(f"\n✓ Converted {len(converted_files)} files")

    # Create directory indexes
    print("Creating directory indexes...")
    for root, dirs, files in os.walk(output_dir):
        if any(f.endswith('.html') for f in files) or dirs:
            rel_path = os.path.relpath(root, output_dir)
            if rel_path == '.':
                title = "Documentation"
            else:
                title = rel_path.replace(os.sep, ' / ').replace('_', ' ').title()

            create_directory_index(root, title)

    print("\n✓ Documentation conversion complete!")
    print(f"✓ Output directory: {output_dir}")
    print(f"✓ Main index: {output_dir}/index.html")

if __name__ == '__main__':
    main()