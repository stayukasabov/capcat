# Markdown to HTML Documentation System - Product Requirements Document

**Project:** Capcat Documentation Automation
**Document Type:** PRD - Documentation Build System
**Version:** 1.0
**Date:** December 19, 2025
**Status:** Pending - Start After Main Capcat Development Tasks Complete
**Priority:** Medium

---

## Executive Summary

Implement an automated system to maintain documentation in Markdown (source of truth) while auto-generating HTML for GitHub Pages deployment. This eliminates duplicate content maintenance and ensures documentation stays synchronized.

**Goal:** Write once in Markdown, deploy as styled HTML automatically.

**Timeline:** 2-4 hours implementation
**Prerequisites:** Pandoc installed, existing website design system

---

## Problem Statement

**Current State:**
- Documentation exists in both Markdown (`docs/`) and HTML (`website/docs/`)
- Requires manual synchronization between formats
- Risk of documentation drift and outdated content
- Double maintenance burden

**Desired State:**
- Markdown files are the single source of truth
- HTML is auto-generated from Markdown
- Preserves existing custom design system
- One-command build and deployment

---

## Strategic Options Analysis

### **Option 1: Auto-Generate HTML from Markdown (RECOMMENDED)**

Keep Markdown as source of truth, auto-generate HTML for GitHub Pages.

#### Option 1A: MkDocs (Python-based)

**Implementation:**
```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Directory structure
capcat/
├── docs/                    # Markdown source (source of truth)
│   ├── index.md
│   ├── quick-start.md
│   ├── architecture.md
│   └── tutorials/
├── mkdocs.yml              # Configuration
└── site/                   # Auto-generated HTML
    └── ...
```

**Configuration `mkdocs.yml`:**
```yaml
site_name: Capcat Documentation
site_url: https://yourusername.github.io/capcat/
theme:
  name: material
  custom_dir: website/

nav:
  - Home: index.md
  - Quick Start: quick-start.md
  - Architecture: architecture.md
  - Tutorials:
      - Getting Started: tutorials/01-getting-started.md
      - Daily Workflow: tutorials/02-daily-workflow.md

extra_css:
  - css/design-system.css
  - css/main.css

site_dir: website
```

**Build & Deploy:**
```bash
mkdocs build          # Generate HTML
mkdocs serve          # Preview locally
mkdocs gh-deploy      # Deploy to GitHub Pages
```

**Pros:**
- ✓ Python-based (matches your stack)
- ✓ Live preview with auto-reload
- ✓ Built-in search functionality
- ✓ Can use custom CSS
- ✓ One-command deployment

**Cons:**
- ✗ May require adapting existing HTML structure
- ✗ Theme system learning curve
- ✗ Less control over exact HTML output

---

#### Option 1B: Jekyll (GitHub Pages Native)

**Implementation:**
```bash
# Directory structure
capcat/
├── docs/                    # Markdown source
├── _layouts/               # HTML templates
│   └── default.html
├── _includes/             # Reusable components
│   ├── header.html
│   └── footer.html
├── css/
└── _config.yml
```

**Configuration `_config.yml`:**
```yaml
title: Capcat Documentation
baseurl: "/capcat"
markdown: kramdown
theme: null

collections:
  docs:
    output: true
    permalink: /:collection/:path/
```

**Layout Template `_layouts/default.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ page.title }} - Capcat</title>
    <link rel="stylesheet" href="{{ site.baseurl }}/css/design-system.css">
    <link rel="stylesheet" href="{{ site.baseurl }}/css/main.css">
</head>
<body>
    {% include header.html %}

    <div class="doc-container">
        <div class="container">
            <div class="doc-content">
                {{ content }}
            </div>
        </div>
    </div>

    {% include footer.html %}
</body>
</html>
```

**Markdown Example:**
```markdown
---
layout: default
title: Quick Start
---

# Quick Start

Get started with Capcat...
```

**Pros:**
- ✓ Native GitHub Pages support (zero config deployment)
- ✓ No build step needed locally
- ✓ Can reuse existing HTML/CSS exactly
- ✓ Free hosting

**Cons:**
- ✗ Ruby-based (not Python)
- ✗ Liquid templating syntax to learn
- ✗ Limited local preview options

---

#### Option 1C: Sphinx (Python Docs Standard)

**Implementation:**
```bash
pip install sphinx sphinx-rtd-theme

sphinx-quickstart docs

# Configure docs/conf.py
html_theme = 'alabaster'
html_static_path = ['../website/css']
html_css_files = ['design-system.css', 'main.css']
```

**Pros:**
- ✓ Standard for Python projects
- ✓ Excellent API documentation support
- ✓ Advanced cross-referencing
- ✓ Built-in search

**Cons:**
- ✗ reStructuredText by default (not Markdown)
- ✗ More complex setup
- ✗ Overkill for simple documentation

---

### **Option 2: Keep Both Separate + Add Links**

Maintain both independently, link between them.

**Implementation:**
```
capcat/
├── docs/           # Markdown (for developers)
├── website/        # HTML (for GitHub Pages)
└── README.md
```

**Add cross-links:**
```html
<!-- In HTML -->
<p>📝 <a href="https://github.com/user/capcat/blob/main/docs/quick-start.md">
    View Markdown source
</a></p>
```

```markdown
<!-- In Markdown -->
> 🌐 [View on website](https://user.github.io/capcat/docs/quick-start.html)
```

**Pros:**
- ✓ Zero setup
- ✓ Keep existing HTML as-is
- ✓ Simple to understand

**Cons:**
- ✗ Duplicate content maintenance
- ✗ Risk of documentation drift
- ✗ Manual synchronization required

---

### **Option 3: Pandoc with Custom Templates (RECOMMENDED)**

Write in Markdown, convert to HTML using Pandoc with custom templates.

**Implementation:**
```bash
# Install Pandoc
brew install pandoc  # macOS
apt install pandoc   # Linux
```

**Directory Structure:**
```
capcat/
├── docs/                           # Markdown source (source of truth)
│   ├── quick-start.md
│   ├── architecture.md
│   └── tutorials/
├── website/                        # Generated HTML
│   ├── docs/
│   │   ├── quick-start.html
│   │   └── architecture.html
│   ├── templates/
│   │   └── doc-template.html     # Pandoc template
│   └── css/
└── scripts/
    └── build_docs.py               # Build automation
```

**Pandoc Template `website/templates/doc-template.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title$ - Capcat Documentation</title>
    <link rel="stylesheet" href="/capcat/css/design-system.css">
    <link rel="stylesheet" href="/capcat/css/main.css">
</head>
<body>
    <!-- Header -->
    <header class="site-header">
        <div class="container">
            <nav class="main-nav">
                <div class="logo">
                    <a href="/capcat/index.html">
                        <!-- Logo SVG -->
                    </a>
                </div>
                <ul class="nav-links">
                    <li><a href="/capcat/index.html#features">Features</a></li>
                    <li><a href="/capcat/index.html#how-it-works">How It Works</a></li>
                    <li><a href="/capcat/index.html#tutorials">Tutorials</a></li>
                    <li><a href="https://github.com/user/capcat" class="btn-primary">GitHub</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <!-- Main Content -->
    <div class="doc-container">
        <div class="container">
            <div class="doc-content">
                <!-- Breadcrumbs -->
                <nav class="nav-breadcrumb">
                    <a href="/capcat/index.html">Home</a> /
                    <a href="/capcat/docs/index.html">Documentation</a> /
                    $title$
                </nav>

                <!-- Content from Markdown -->
                $body$

                <!-- Edit on GitHub Link -->
                <hr>
                <p class="text-center">
                    <a href="https://github.com/user/capcat/edit/main/docs/$sourcefile$">
                        ✏️ Edit this page on GitHub
                    </a>
                </p>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-logo">
                    <!-- Footer content -->
                </div>
            </div>
            <div class="footer-credit">
                <p>&copy; 2025 Capcat. Made with ❤️ for news archiving.</p>
            </div>
        </div>
    </footer>

    <!-- Back to Top Button -->
    <button id="backToTopBtn" title="Back to top">↑</button>
    <script src="/capcat/js/main.js"></script>
</body>
</html>
```

**Build Script `scripts/build_docs.py`:**
```python
#!/usr/bin/env python3
"""
Convert Markdown documentation to HTML using Pandoc.
Preserves custom website design and structure.
"""

import subprocess
import sys
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
WEBSITE_DOCS_DIR = PROJECT_ROOT / "website" / "docs"
TEMPLATE = PROJECT_ROOT / "website" / "templates" / "doc-template.html"

def ensure_pandoc():
    """Check if Pandoc is installed."""
    try:
        subprocess.run(["pandoc", "--version"],
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Pandoc not found. Install it first:")
        print("  macOS: brew install pandoc")
        print("  Linux: apt install pandoc")
        print("  Windows: https://pandoc.org/installing.html")
        sys.exit(1)

def convert_markdown_to_html(md_file: Path) -> Path:
    """Convert a single Markdown file to HTML."""
    # Calculate relative path structure
    relative_path = md_file.relative_to(DOCS_DIR)
    output_file = WEBSITE_DOCS_DIR / relative_path.with_suffix(".html")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Extract title from Markdown (first h1)
    title = "Capcat Documentation"
    with open(md_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                title = line[2:].strip()
                break

    # Pandoc conversion command
    cmd = [
        "pandoc",
        str(md_file),
        "--from", "markdown+smart",
        "--to", "html5",
        "--standalone",
        "--template", str(TEMPLATE),
        "--metadata", f"title={title}",
        "--metadata", f"sourcefile={relative_path}",
        "--css", "/capcat/css/design-system.css",
        "--css", "/capcat/css/main.css",
        "--toc",  # Table of contents
        "--toc-depth", "3",
        "--output", str(output_file),
    ]

    print(f"Converting: {relative_path}")
    subprocess.run(cmd, check=True)

    return output_file

def build_all_docs():
    """Convert all Markdown files to HTML."""
    ensure_pandoc()

    print("\n" + "="*60)
    print("Building Documentation")
    print("="*60 + "\n")

    # Ensure output directory exists
    WEBSITE_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Find all markdown files
    md_files = list(DOCS_DIR.rglob("*.md"))

    # Exclude README.md if it exists
    md_files = [f for f in md_files if f.name != "README.md"]

    if not md_files:
        print("No Markdown files found in docs/")
        return

    print(f"Found {len(md_files)} Markdown files\n")

    # Convert each file
    converted_files = []
    for md_file in sorted(md_files):
        try:
            output = convert_markdown_to_html(md_file)
            converted_files.append(output)
        except subprocess.CalledProcessError as e:
            print(f"Error converting {md_file}: {e}")
            sys.exit(1)

    print("\n" + "="*60)
    print(f"✓ Successfully converted {len(converted_files)} files")
    print("="*60)
    print(f"\nOutput directory: {WEBSITE_DOCS_DIR}")
    print("\nNext steps:")
    print("  1. Preview: python3 -m http.server 8000 --directory website")
    print("  2. Deploy: git add . && git commit -m 'Update docs' && git push")
    print()

if __name__ == "__main__":
    build_all_docs()
```

**Usage:**
```bash
# Build documentation
python3 scripts/build_docs.py

# Preview locally
cd website
python3 -m http.server 8000

# Deploy to GitHub Pages
git add .
git commit -m "Update documentation"
git push origin main
```

**Pros:**
- ✓ Full control over HTML output
- ✓ Uses existing custom design exactly
- ✓ Markdown source of truth
- ✓ Python-based automation
- ✓ One-command build
- ✓ No external dependencies beyond Pandoc
- ✓ Can customize template per section

**Cons:**
- ✗ Requires Pandoc installation
- ✗ Manual build step before deployment
- ✗ Generated HTML files in git repo

---

### **Option 4: GitHub Pages + README Links (Simplest)**

Point to existing HTML, add prominent links to Markdown sources.

**Implementation:**
Add to `website/index.html`:
```html
<section class="section">
    <div class="container">
        <h2>Documentation</h2>
        <div class="dual-mode-grid">
            <div class="mode-comparison">
                <h3>📖 Read Documentation</h3>
                <ul>
                    <li><a href="docs/quick-start.html">Quick Start</a></li>
                    <li><a href="docs/architecture.html">Architecture</a></li>
                </ul>
            </div>

            <div class="mode-comparison">
                <h3>✏️ Contribute</h3>
                <p>Edit documentation on GitHub:</p>
                <ul>
                    <li><a href="https://github.com/user/capcat/blob/main/docs/quick-start.md">Quick Start (Markdown)</a></li>
                    <li><a href="https://github.com/user/capcat/tree/main/docs">All Docs</a></li>
                </ul>
            </div>
        </div>
    </div>
</section>
```

**Pros:**
- ✓ Zero setup
- ✓ Immediate implementation

**Cons:**
- ✗ Manual sync required
- ✗ Duplicate maintenance

---

## Recommended Solution: **Option 3 - Pandoc with Custom Templates**

### Why This is Best for Capcat:

1. **Full Design Control**
   - Uses your existing `design-system.css` and `main.css` exactly
   - No theme customization needed
   - Maintains brand consistency

2. **Markdown Source of Truth**
   - All docs in `/docs` as Markdown
   - Easy to edit, review, and version control
   - GitHub renders Markdown beautifully

3. **Python Integration**
   - Build script in Python (matches your stack)
   - Easy to extend and customize
   - Can integrate with other build processes

4. **Simple Workflow**
   - Edit Markdown
   - Run `python3 scripts/build_docs.py`
   - Deploy

5. **No Lock-in**
   - Pandoc is universal converter
   - Can switch to another system later
   - Standard Markdown format

---

## Implementation Plan

### Phase 1: Setup (30 minutes)

**Tasks:**
1. Install Pandoc
2. Create `website/templates/doc-template.html`
3. Create `scripts/build_docs.py`
4. Test with one existing doc

**Deliverables:**
- ✓ Pandoc installed
- ✓ Template created with existing design
- ✓ Build script functional
- ✓ One test doc converted successfully

---

### Phase 2: Migration (1 hour)

**Tasks:**
1. Convert existing HTML docs to Markdown (if not already done)
2. Organize in `/docs` directory structure
3. Build all docs with script
4. Verify all pages render correctly

**Directory Structure:**
```
docs/
├── index.md
├── quick-start.md
├── architecture.md
├── configuration.md
├── tutorials/
│   ├── 01-getting-started.md
│   ├── 02-daily-workflow.md
│   └── ...
├── api/
│   └── ...
└── development/
    └── ...
```

**Deliverables:**
- ✓ All docs in Markdown format
- ✓ Organized directory structure
- ✓ HTML generated successfully
- ✓ All links working

---

### Phase 3: Automation (30 minutes)

**Tasks:**
1. Add pre-commit hook to build docs
2. Add GitHub Actions workflow (optional)
3. Update README with build instructions
4. Test end-to-end workflow

**Pre-commit Hook `.git/hooks/pre-commit`:**
```bash
#!/bin/bash
# Auto-build docs before commit

if git diff --cached --name-only | grep -q "^docs/"; then
    echo "Building documentation..."
    python3 scripts/build_docs.py
    git add website/docs/
fi
```

**GitHub Actions `.github/workflows/build-docs.yml`:**
```yaml
name: Build Documentation

on:
  push:
    paths:
      - 'docs/**'
      - 'scripts/build_docs.py'
      - 'website/templates/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Pandoc
        run: sudo apt-get install -y pandoc

      - name: Build Documentation
        run: python3 scripts/build_docs.py

      - name: Commit Generated HTML
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add website/docs/
          git commit -m "Auto-build documentation [skip ci]" || echo "No changes"
          git push
```

**Deliverables:**
- ✓ Pre-commit hook configured
- ✓ GitHub Actions workflow (optional)
- ✓ Documentation updated
- ✓ Tested workflow

---

### Phase 4: Testing & Validation (30 minutes)

**Tasks:**
1. Visual regression testing (compare old vs new HTML)
2. Link validation (all internal links work)
3. Responsive testing (mobile, tablet, desktop)
4. Cross-browser testing

**Testing Checklist:**
- ✓ All pages render with correct styling
- ✓ Navigation works
- ✓ Breadcrumbs functional
- ✓ Images/icons load
- ✓ Code blocks formatted correctly
- ✓ Tables render properly
- ✓ Links work (internal and external)
- ✓ Mobile responsive
- ✓ Back to top button works

**Deliverables:**
- ✓ All tests passed
- ✓ Issues documented and resolved
- ✓ Ready for deployment

---

## File Structure After Implementation

```
capcat/
├── Application/
│   ├── capcat.py
│   ├── core/
│   └── sources/
├── docs/                               # ← Markdown source of truth
│   ├── index.md
│   ├── quick-start.md
│   ├── architecture.md
│   ├── tutorials/
│   │   ├── 01-getting-started.md
│   │   └── 02-daily-workflow.md
│   └── api/
├── website/                            # ← Generated HTML for GitHub Pages
│   ├── .nojekyll
│   ├── index.html                     # Landing page (manually maintained)
│   ├── docs/                          # ← Auto-generated from Markdown
│   │   ├── quick-start.html
│   │   ├── architecture.html
│   │   └── tutorials/
│   ├── templates/
│   │   └── doc-template.html         # Pandoc template
│   ├── css/
│   │   ├── design-system.css
│   │   └── main.css
│   ├── js/
│   └── fonts/
├── scripts/
│   └── build_docs.py                  # Documentation build script
├── .github/
│   └── workflows/
│       └── build-docs.yml             # Optional automation
├── README.md
├── GITHUB-PAGES-DEPLOYMENT-PRD.md
└── MARKDOWN-TO-HTML-DOCUMENTATION-PRD.md  # This document
```

---

## Success Criteria

Implementation is successful when:

**✓ Functionality:**
- Markdown files are source of truth
- One-command build generates all HTML
- All pages render with correct styling
- Navigation and links work correctly
- Mobile responsive layout maintained

**✓ Workflow:**
- Edit Markdown → Run build → Deploy
- Takes < 30 seconds to build all docs
- No manual HTML editing required
- Git history shows only Markdown changes

**✓ Quality:**
- Visual consistency with existing design
- No broken links
- Proper formatting (code blocks, tables, lists)
- Breadcrumb navigation works
- "Edit on GitHub" links functional

**✓ Maintainability:**
- Clear build process documentation
- Error handling in build script
- Easy for contributors to understand

---

## Rollback Plan

If implementation fails:

1. **Immediate Rollback:**
   - Keep existing HTML in `website/docs/`
   - Disable build script
   - Continue manual maintenance temporarily

2. **Identify Issues:**
   - Document what failed
   - Identify root cause
   - Determine if fixable or need different approach

3. **Alternative Approach:**
   - Try Option 1B (Jekyll) if Pandoc issues
   - Try Option 2 (separate + links) as fallback
   - Consult community for solutions

---

## Maintenance Plan

### Regular Tasks:

**When adding new documentation:**
1. Write in Markdown in `docs/`
2. Run `python3 scripts/build_docs.py`
3. Preview locally
4. Commit and push

**When updating existing docs:**
1. Edit Markdown file
2. Run build script
3. Verify changes in HTML
4. Commit and push

**Periodic Review:**
- Monthly: Check for broken links
- Quarterly: Update Pandoc version
- Annually: Review and update template

---

## Future Enhancements

**Phase 2 (Future):**
- Add search functionality (Algolia, Lunr.js)
- Syntax highlighting for code blocks
- Auto-generate table of contents
- Version selector (v1.0, v2.0, etc.)
- PDF export option
- Dark mode support

**Phase 3 (Future):**
- Multi-language support
- API documentation auto-generation
- Interactive examples
- Video tutorials integration
- Community contributions workflow

---

## Dependencies

**Required:**
- Pandoc (2.x or higher)
- Python 3.8+
- Git

**Optional:**
- GitHub Actions (for automation)
- Pre-commit hooks (for automatic builds)

---

## Resources

**Pandoc Documentation:**
- https://pandoc.org/MANUAL.html
- Templates: https://pandoc.org/MANUAL.html#templates

**Python Documentation:**
- subprocess: https://docs.python.org/3/library/subprocess.html
- pathlib: https://docs.python.org/3/library/pathlib.html

**Examples:**
- Pandoc templates: https://github.com/jgm/pandoc-templates
- GitHub Pages: https://docs.github.com/en/pages

---

## Cost Analysis

**Time Investment:**
- Initial setup: 2-4 hours
- Learning curve: 1-2 hours
- First-time conversion: 2-3 hours
- **Total:** 5-9 hours

**Ongoing Savings:**
- No duplicate maintenance: ~2 hours/week
- Faster doc updates: ~30 min/doc
- Reduced errors: ~1 hour/week

**Break-even:** After 2-3 weeks of active documentation work

---

## Risks & Mitigation

**Risk 1: Pandoc Installation Issues**
- **Mitigation:** Provide clear installation docs for all platforms
- **Fallback:** Use Docker container with Pandoc pre-installed

**Risk 2: Template Complexity**
- **Mitigation:** Start with simple template, iterate
- **Fallback:** Use default Pandoc template temporarily

**Risk 3: Build Script Failures**
- **Mitigation:** Add error handling and logging
- **Fallback:** Manual conversion command documented

**Risk 4: Design System Changes**
- **Mitigation:** Template references CSS files, not inline styles
- **Fallback:** Rebuild docs after CSS changes

---

## Decision Log

**Why Pandoc over MkDocs:**
- Full control over HTML output structure
- Can use existing design system without modification
- No theme customization required
- Simpler for non-Python contributors

**Why Pandoc over Jekyll:**
- Python-based build script (team familiarity)
- No Ruby dependency
- Can run builds locally without GitHub Pages
- More flexible template system

**Why not keep both formats:**
- Maintenance burden too high
- Risk of documentation drift
- Wastes developer time

---

## Next Steps (When Ready to Implement)

1. **Read this PRD thoroughly**
2. **Install Pandoc** on development machine
3. **Create template** using existing HTML structure
4. **Test with one doc** to verify concept
5. **Migrate all docs** if test successful
6. **Deploy to GitHub Pages**
7. **Document workflow** for team

---

## Approval & Sign-off

**Document Owner:** Technical Lead
**Stakeholders:** Development Team, Documentation Contributors
**Review Date:** After main Capcat development tasks complete
**Status:** Approved for future implementation

---

**Last Updated:** December 19, 2025
**Next Review:** When main development tasks are 80% complete
**Version:** 1.0
