# Git Repository Initialization - Product Requirements Document

**Project:** Capcat News Archiving System
**Document Type:** PRD - Git Repository Setup
**Version:** 1.0
**Date:** December 31, 2025
**Status:** Ready for Implementation

---

## Executive Summary

Initialize Git repository for Capcat project to enable version control, GitHub collaboration, and deployment (GitHub Pages, releases). Current state: No git repository. Goal: Fully configured git repo with GitHub remote, .gitignore, and initial commit.

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated (✓ verified: stayukasabov)
- HTTPS protocol configured (✓ verified)
- Local codebase at: `/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application`

**Timeline:** 30-45 minutes

---

## 1. Current State Analysis

**Repository Status:**
- No `.git` directory detected
- No version control history
- No GitHub remote configured
- Codebase ready for v2.0.0 release (v1.x had limited functionality)

**Impact of No Git:**
- Cannot create version tags
- Cannot create GitHub releases
- Cannot deploy to GitHub Pages
- No collaboration workflow
- No change history tracking

**GitHub CLI Status:**
```
✓ Authenticated: stayukasabov
✓ Protocol: HTTPS
✓ Scopes: gist, read:org, repo, workflow
```

---

## 2. Repository Structure Decision

### Option A: Single Repository (Recommended)

**Structure:**
```
capcat/
├── .git/
├── .gitignore
├── README.md
├── CHANGELOG.md
├── LICENSE
├── requirements.txt
├── capcat.py
├── cli.py
├── core/
├── sources/
├── htmlgen/
├── themes/
├── website/          # GitHub Pages source
├── docs/             # Markdown documentation
├── scripts/
└── tests/
```

**GitHub Repository Name:** `capcat`

**Advantages:**
- Single source of truth
- Unified issue tracking
- Simple contribution workflow
- Website deploys from `/website` folder

**GitHub Pages URL:** `https://stayukasabov.github.io/capcat/`

### Option B: Separate Repositories

**Not Recommended** - Adds complexity, splits history

---

## 3. .gitignore Configuration

**Critical Exclusions:**

### Python
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
*.log
```

### Output Directories
```gitignore
# Capcat Output (parent directories)
../News/
../Capcats/
```

**Issue:** Parent directories not in repo, use absolute paths:

```gitignore
# Capcat Output (absolute paths)
/Volumes/DRIVE\ B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat\ copy/News/
/Volumes/DRIVE\ B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat\ copy/Capcats/
```

**Better Approach:** Exclude by pattern in repo root:

```gitignore
# Output directories (if accidentally moved to repo)
news_*/
cc_*/
```

### IDE & System
```gitignore
# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store
.AppleDouble
.LSOverride
._*

# Thumbnails
Thumbs.db
```

### Sensitive Data
```gitignore
# Sensitive
capcat.yml
*.env
.env.*
credentials.json
secrets/
config/local.yml
```

### Temporary Files
```gitignore
# Temporary
*.tmp
*.bak
*_backup
*_old
test-diagnose-*.md
```

**Complete .gitignore:** See Section 10

---

## 4. Initial Commit Strategy

### Commit Sequence

**Commit 1: Infrastructure**
```bash
git add .gitignore README.md LICENSE requirements.txt
git commit -m "Initial commit: Project infrastructure"
```

**Commit 2: Core System**
```bash
git add capcat.py cli.py run_capcat.py capcat
git add core/ sources/
git commit -m "Add core application and source system"
```

**Commit 3: HTML Generation**
```bash
git add htmlgen/ themes/
git commit -m "Add HTML generation system"
```

**Commit 4: Documentation**
```bash
git add docs/ CLAUDE.md
git commit -m "Add documentation"
```

**Commit 5: Website**
```bash
git add website/
git commit -m "Add documentation website for GitHub Pages"
```

**Commit 6: Tests & Scripts**
```bash
git add tests/ scripts/
git commit -m "Add test suite and utility scripts"
```

**Commit 7: Reports (Optional)**
```bash
git add Reports/
git commit -m "Add development reports and sprint documentation"
```

### Alternative: Single Initial Commit

```bash
git add .
git commit -m "Initial commit: Capcat v1.0.0 - News archiving system with 17+ sources"
```

**Recommendation:** Single commit for v1.0.0 release (clean history start)

---

## 5. GitHub Repository Creation

### Method 1: GitHub CLI (Recommended)

```bash
cd "/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application"

# Create repository
gh repo create capcat \
  --public \
  --description "Personal news archiving utility: 12 sources to Markdown + media. Plugin-based architecture." \
  --source=. \
  --remote=origin \
  --push
```

**Flags Explained:**
- `--public`: Public repository (required for free GitHub Pages)
- `--description`: Repository description
- `--source=.`: Use current directory
- `--remote=origin`: Set remote name
- `--push`: Push initial commit immediately

### Method 2: Manual GitHub Creation

1. Visit https://github.com/new
2. Repository name: `capcat`
3. Description: "News archiving system: 17+ sources to Markdown + media"
4. Public repository
5. No README, .gitignore, or LICENSE (already in codebase)
6. Create repository

```bash
git remote add origin https://github.com/stayukasabov/capcat.git
git branch -M main
git push -u origin main
```

---

## 6. Branch Strategy

### Initial Setup

**Default Branch:** `main`

**Reasoning:**
- Industry standard (GitHub default)
- Better than `master` (inclusive terminology)
- Simpler than `develop` for single-maintainer project

### Future Branch Strategy

**For Solo Development:**
```
main (stable, deployable)
```

**For Collaborative Development:**
```
main (production)
├── develop (integration)
├── feature/* (new features)
├── bugfix/* (bug fixes)
└── hotfix/* (urgent production fixes)
```

**Recommendation:** Start simple with `main` only, add branches if contributors join.

---

## 7. Pre-Commit Checklist

**Before `git init`:**

1. **Verify Working Directory**
   ```bash
   pwd
   # Expected: /Volumes/DRIVE B/SYNCA/.../Application
   ls capcat.py
   # Expected: capcat.py exists
   ```

2. **Review Sensitive Files**
   ```bash
   find . -name "*.env" -o -name "*secret*" -o -name "*password*" -o -name "credentials.json"
   ```
   Ensure none contain real credentials.

3. **Check Output Directories**
   ```bash
   ls ../News/ ../Capcats/ 2>/dev/null
   ```
   Verify output is OUTSIDE Application/ directory.

4. **Audit Large Files**
   ```bash
   find . -type f -size +10M
   ```
   Remove or .gitignore large binary files.

5. **Test Backup Naming**
   ```bash
   find . -name "*_backup" -o -name "*_old" -o -name "*_fixed"
   ```
   Clean up backup files per CLAUDE.md versioning rules.

6. **Virtual Environment Check**
   ```bash
   ls venv/
   ```
   Ensure venv/ will be in .gitignore.

---

## 8. Step-by-Step Initialization

### Phase 1: Prepare (5-10 minutes)

```bash
# Navigate to project
cd "/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application"

# Verify location
pwd
ls capcat.py

# Check for existing git
ls -la .git
# Expected: No such file or directory (good)
```

### Phase 2: Create .gitignore (2 minutes)

```bash
# Create .gitignore (content in Section 10)
# Use Write tool or:
cat > .gitignore << 'EOF'
[Content from Section 10]
EOF

# Verify
cat .gitignore
```

### Phase 3: Initialize Git (1 minute)

```bash
# Initialize repository
git init

# Verify
ls -la .git
# Expected: .git/ directory exists

# Set default branch to main
git branch -M main

# Configure user (if not global)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Verify config
git config --list | grep user
```

### Phase 4: Stage Files (2 minutes)

```bash
# Check status
git status

# Stage all files
git add .

# Verify staged files
git status

# Review what will be committed
git diff --cached --stat
```

### Phase 5: Initial Commit (1 minute)

```bash
# Create initial commit
git commit -m "Initial commit: Capcat v2.0.0 - Personal news archiving utility

Version 2.0 - Complete rewrite with enhanced architecture.

Features:
- 12 news sources (HN, BBC, Nature, IEEE, Guardian, MIT News, etc.)
- Plugin-based architecture (config-driven + custom sources)
- Unified article processor (Dec 2025)
- Specialized source handlers (Twitter, YouTube, Medium, Substack)
- HTML generation with themes
- Interactive mode and CLI
- Bundle system (tech, techpro, news, science, ai, sports)
- Privacy compliance (username anonymization)
- Media handling (images always, video/audio/docs with --media flag)
- Fallback image detection system
- Documentation website (website/) integrated with GitHub Pages

Tech Stack:
- Python 3.8+
- Requests, BeautifulSoup4, lxml, Pillow
- YAML configuration
- Session pooling
- PEP 8 compliant"

# Verify commit
git log --oneline
git show --stat
```

### Phase 6: Create GitHub Repository (5 minutes)

**Option A: Using gh CLI (Recommended)**

```bash
# Create and push in one command
gh repo create capcat \
  --public \
  --description "Personal news archiving utility: 12 sources to Markdown + media. Plugin-based architecture." \
  --source=. \
  --remote=origin \
  --push

# Verify
gh repo view
git remote -v
```

**Option B: Manual**

```bash
# Create repository on GitHub first (via web UI)
# Then:
git remote add origin https://github.com/stayukasabov/capcat.git
git push -u origin main

# Verify
git remote -v
```

### Phase 7: Verify GitHub (3 minutes)

```bash
# Check remote
git remote -v
# Expected: origin https://github.com/stayukasabov/capcat.git

# Check branch tracking
git branch -vv
# Expected: * main [origin/main]

# View on GitHub
gh repo view --web
```

---

## 9. Post-Initialization Tasks

### Configure Repository Settings

**Via GitHub Web:**
1. Navigate to https://github.com/stayukasabov/capcat/settings
2. **General:**
   - Features: Enable Issues, Disable Wikis (using /docs instead)
   - Pull Requests: Require PR reviews for collaborators (future)
3. **Branches:**
   - Default branch: `main` (already set)
   - Branch protection rules (optional for solo dev):
     - Require pull request reviews: No (solo dev)
     - Require status checks: No (no CI yet)
4. **Pages:**
   - DO NOT configure yet (Phase 3 of main plan)

**Via gh CLI:**
```bash
# Enable issues
gh repo edit --enable-issues

# Disable wikis
gh repo edit --enable-wiki=false

# Add topics
gh repo edit --add-topic python,news,archiving,web-scraping,markdown
```

### Create README Badge

Update README.md with badges:

```markdown
# Capcat

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Personal news archiving utility: 12 sources to Markdown + media.

**[Documentation Website](https://stayukasabov.github.io/capcat/)**
```

### Add LICENSE

**Recommendation:** MIT License (permissive, standard for tools)

```bash
# Create LICENSE file
gh repo edit --license=mit
```

Or create manually with year and copyright holder.

### Create Branch Protection (Optional)

**For Solo Development:** Skip initially

**For Future Collaborators:**
```bash
# Protect main branch
gh api repos/stayukasabov/capcat/branches/main/protection \
  -X PUT \
  -F required_status_checks=null \
  -F enforce_admins=false \
  -F required_pull_request_reviews=null \
  -F restrictions=null
```

---

## 10. Complete .gitignore Template

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual Environment
venv/
env/
ENV/
.venv/

# Distribution / Packaging
build/
dist/
*.egg-info/
.eggs/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# Logs
*.log
capcat.log
*.log.*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject

# macOS
.DS_Store
.AppleDouble
.LSOverride
._*

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Sensitive Data
capcat.yml
*.env
.env.*
credentials.json
secrets/
config/local.yml
api_keys.txt

# Temporary Files
*.tmp
*.bak
*_backup
*_old
*_fixed
test-diagnose-*.md
temp/
tmp/

# Output Directories (if accidentally in repo)
news_*/
cc_*/

# Documentation Backups
docs_backup_*/
website_backup_*/

# Test Outputs
test_output/
test_results/

# Coverage Reports
.coverage.*
coverage.xml

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre
.pyre/

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Compiled translations
*.mo
*.pot

# Django/Flask (if future web UI)
db.sqlite3
db.sqlite3-journal
instance/
.webassets-cache

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Cython
*.c
*.cpp
*.h

# Project Specific
# (Add Capcat-specific exclusions here)
```

---

## 11. Verification Checklist

**After Initialization:**

**✓ Local Git:**
- [ ] `.git/` directory exists
- [ ] `.gitignore` file created and comprehensive
- [ ] Initial commit created
- [ ] Default branch is `main`
- [ ] No uncommitted changes: `git status` clean

**✓ GitHub Remote:**
- [ ] Repository created: `gh repo view`
- [ ] Remote configured: `git remote -v`
- [ ] Initial commit pushed: `gh browse` shows files
- [ ] Repository is public
- [ ] Description accurate

**✓ Configuration:**
- [ ] User name/email set: `git config user.name`
- [ ] Branch tracking: `git branch -vv`
- [ ] Topics added (optional)
- [ ] Issues enabled

**✓ Security:**
- [ ] No sensitive files committed: `git log --all --full-history -- "*.env"`
- [ ] .gitignore includes sensitive patterns
- [ ] No large binaries: `git ls-files -s | awk '$4 > 1000000 {print $4, $5}'`

**✓ Documentation:**
- [ ] README.md accurate
- [ ] LICENSE file present
- [ ] CLAUDE.md committed

---

## 12. Troubleshooting

### Issue: "fatal: not a git repository"

**Cause:** Not in Application/ directory or `git init` not run

**Solution:**
```bash
cd "/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application"
git init
```

### Issue: "fatal: refusing to merge unrelated histories"

**Cause:** Created README on GitHub, conflicts with local

**Solution:**
```bash
git pull origin main --allow-unrelated-histories
# Resolve conflicts
git push origin main
```

### Issue: gh repo create fails with authentication error

**Cause:** Token missing `repo` scope

**Solution:**
```bash
gh auth refresh -s repo
gh repo create capcat [options]
```

### Issue: Accidentally committed sensitive file

**Solution:**
```bash
# Remove from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all

# Rotate compromised credentials immediately
```

**Prevention:** Use .gitignore, audit before first push.

### Issue: Large file warning

**Cause:** File >50MB

**Solution:**
```bash
# Remove large file
git rm --cached large_file.bin
echo "large_file.bin" >> .gitignore
git commit -m "Remove large file"

# Or use Git LFS
git lfs install
git lfs track "*.bin"
git add .gitattributes
```

---

## 13. Success Criteria

**Repository Initialization Complete When:**

- ✓ Local git repository initialized
- ✓ .gitignore comprehensive and tested
- ✓ Initial commit created with clear message
- ✓ GitHub repository created (public)
- ✓ Remote origin configured
- ✓ Initial commit pushed successfully
- ✓ Repository visible at https://github.com/stayukasabov/capcat
- ✓ No sensitive data committed
- ✓ README.md accurate and displayed
- ✓ Issues enabled, wikis disabled
- ✓ Topics added for discoverability

---

## 14. Next Steps (Post-Initialization)

**Immediate (Phase 1 - Code Cleanup):**
1. Fix BUG-001 and BUG-002
2. Run comprehensive tests
3. Commit fixes to `main`

**Short-Term (Phase 2 - Release):**
4. Create v2.0.0 tag: `git tag -a v2.0.0 -m "Release v2.0.0"`
5. Push tag: `git push origin v2.0.0`
6. Create GitHub release: `gh release create v2.0.0`

**Medium-Term (Phase 3 - GitHub Pages):**
7. Configure GitHub Pages: Settings → Pages → Source: main, Folder: /website
8. Deploy documentation website
9. Update README with website link

**Long-Term:**
10. Set up GitHub Actions for automated testing
11. Add contributing guidelines (CONTRIBUTING.md)
12. Create issue templates
13. Consider pre-commit hooks for code quality

---

## 15. Command Summary

**Complete Initialization Sequence:**

```bash
# 1. Navigate
cd "/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application"

# 2. Create .gitignore (use content from Section 10)
# [Create .gitignore file]

# 3. Initialize git
git init
git branch -M main

# 4. Initial commit
git add .
git commit -m "Initial commit: Capcat v1.0.0 - News archiving system"

# 5. Create GitHub repo and push
gh repo create capcat \
  --public \
  --description "Personal news archiving utility: 12 sources to Markdown + media. Plugin-based architecture." \
  --source=. \
  --remote=origin \
  --push

# 6. Verify
gh repo view
git status

# 7. Add topics
gh repo edit --add-topic python,news,archiving,web-scraping,markdown

# 8. View on GitHub
gh repo view --web
```

**Total Time:** 15-20 minutes

---

## 16. Resources

**Git Documentation:**
- https://git-scm.com/doc
- https://git-scm.com/book/en/v2

**GitHub CLI:**
- https://cli.github.com/manual/
- `gh help repo create`

**GitHub Documentation:**
- https://docs.github.com/en/repositories

**Best Practices:**
- https://github.com/github/gitignore (gitignore templates)
- https://semver.org/ (semantic versioning)
- https://keepachangelog.com/ (changelog format)

---

## Conclusion

Git repository initialization is straightforward with GitHub CLI. The process takes 15-20 minutes and enables version control, collaboration, releases, and GitHub Pages deployment.

**Critical Success Factor:** Comprehensive .gitignore before first commit to prevent sensitive data exposure.

**Risk:** Low - Initialization is reversible (`rm -rf .git` to restart)

**Benefit:** Unlocks Phases 2 & 3 of main cleanup/release plan

---

**Document Owner:** Technical Lead
**Last Updated:** December 31, 2025
**Review Date:** After repository initialization
