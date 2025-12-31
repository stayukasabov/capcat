# Repository Cleanup Analysis

## Files/Directories That Should NOT Be Public

### 1. Backup Directories (~66.7MB)
**HIGH PRIORITY - Remove from git and ignore**

- `website/` (43MB) - Old duplicate of docs/, no longer needed
- `docs/docs_backup_20251128_164515/` (4.7MB)
- `docs/hybrid_utility_refactor/` (19MB)
- `website/docs_backup_20251128_164515/`
- `website/hybrid_utility_refactor/`

**Impact:** 760+ files tracked in git unnecessarily

### 2. Backup Files (684 files)
**HIGH PRIORITY - Remove from git**

- `*.backup` files (684 instances)
  - All in docs/docs/ subdirectories
  - Old HTML snapshots before changes
  - Example: `docs/docs/architecture.html.backup`

### 3. Log Files
**Currently in root directory**

- `debug.log` (665KB)
- `docs_regeneration.log`
- `docs_regeneration_foss.log`

**Note:** Already in .gitignore but exist in working directory

### 4. System Files
**Should be ignored**

- `__pycache__/` directory (exists in root)
- `.DS_Store` files (macOS metadata)
- `.pytest_cache/` directory
- `.capcat.py.swp` (vim swap file)

### 5. One-Off Utility Scripts
**Consider removing (not core functionality)**

These appear to be temporary fix scripts:
- `add_jekyll_frontmatter.py`
- `convert_docs_to_html.py`
- `convert_to_markdown.py`
- `delete_h4_colon.py`
- `fix_ascii_formatting.py`
- `fix_colon_formatting.py`
- `fix_ethical_scraping_links.py`
- `fix_footer_typo.py`
- `fix_mismatched_tags.py`
- `fix_sources_in_docs.py`
- `remove_br_tags.py`
- `remove_hr_tags.py`
- `replace_h4_with_h3.py`
- `replace_strong_tags.py`
- `replace_strong_with_h4.py`

**Keep these build scripts:**
- `build_site.py` - Active build script
- `fix_breadcrumbs.py` - Active build script
- `run_capcat.py` - Active wrapper

### 6. Test Files in Root
**Move to tests/ directory or remove**

- `test_colon_formatting.py`
- `test_css_cascade.py`
- `test_design_system.py`
- `test_guardian_source.py`
- `test_h4_replacement.py`
- `test_ieee_dates.py`
- `test_mitnews_*.py` (multiple)
- `test_pdf_article_handling.py`
- `test_refactored_components.py`
- `test_retry_skip_manual.py`

### 7. Mysterious Files
**Unknown purpose - investigate**

- `eyJidWNrZXQiOiAiYXNzZXRzLmluZm9xLmNvbSIsImtleSI6ICJ3ZWIvaGVhZGVyL2NvbmZlcmVuY2VzLzIwMjYvUUNvbi1Mb25kb24tMjAyNi10b3AuanBnIiwiZWRpdHMiOiB7ImpwZWciOiB7ICJxdWFsaXR5Ijo4MH19fQ==`
  - Base64-encoded filename - likely test/temporary data

## Summary Statistics

- **Total backup files in git:** 684 .backup files
- **Total backup directory files:** 760+ files
- **Total wasted space:** ~67MB in backups alone
- **One-off scripts:** ~15 temporary fix scripts
- **Test files in wrong location:** ~10 files

## Recommended Actions

1. **Remove from git history:** backup directories, .backup files
2. **Update .gitignore:** Add patterns for backup files
3. **Clean working directory:** Delete log files, system files
4. **Organize:** Move test files to tests/ directory
5. **Archive:** Move one-off scripts to scripts/legacy/ or delete
