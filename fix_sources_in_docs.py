#!/usr/bin/env python3
"""Fix hardcoded outdated sources in documentation."""

import re
from pathlib import Path

# Real sources mapping
REAL_SOURCES = {
    'tech': 'ieee, mashable',
    'techpro': 'hn, lb, iq',
    'news': 'bbc, guardian',
    'science': 'nature, scientificamerican',
    'ai': 'mitnews',
    'sports': 'bbcsport'
}

FAKE_SOURCES = ['gizmodo', 'futurism', 'lesswrong', 'googleai', 'openai', 'cnn']

def fix_file(filepath):
    """Fix source mentions in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix bundle descriptions
    content = re.sub(
        r'\(Gizmodo, Futurism, IEEE\)',
        '(IEEE, Mashable)',
        content
    )
    
    content = re.sub(
        r'\(LessWrong, Google AI, OpenAI, MIT News\)',
        '(MIT News)',
        content
    )
    
    # Fix tech bundle command example
    content = re.sub(
        r'bundle tech\s+#.*gizmodo.*futurism.*',
        f'bundle tech          # {REAL_SOURCES["tech"]}',
        content
    )
    
    # Fix ai bundle command example  
    content = re.sub(
        r'bundle ai\s+#.*lesswrong.*',
        f'bundle ai            # {REAL_SOURCES["ai"]}',
        content
    )
    
    # Remove fake source listings
    for fake in FAKE_SOURCES:
        # Remove from bulleted lists
        content = re.sub(rf'^\s*[-*]\s*`{fake}`.*$\n', '', content, flags=re.MULTILINE)
        # Remove from comma-separated lists
        content = re.sub(rf'{fake},?\s*', '', content)
    
    # Fix techcrunch examples (keep as placeholder, mark as example)
    content = re.sub(
        r'(https?://techcrunch\.com/[^\s\)]+)',
        r'https://example.com/article',
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Fix key documentation files
docs_dir = Path('docs')
files_to_fix = [
    'README.md',
    'quick-start.md',
    'interactive-mode.md',
    'architecture.md',
    'source-development.md',
    'user_guides/beginners_guide.md',
    'user_guides/quick_start.md',
    'user_guides/semi_pro_guide.md',
    'user_guides/advanced_guide.md',
]

fixed_count = 0
for file_rel in files_to_fix:
    filepath = docs_dir / file_rel
    if filepath.exists():
        if fix_file(filepath):
            print(f"✓ Fixed: {file_rel}")
            fixed_count += 1
        else:
            print(f"- No changes: {file_rel}")

print(f"\n✓ Fixed {fixed_count} files")
