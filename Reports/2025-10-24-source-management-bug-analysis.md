# Source Management Bug Analysis and Fix Plan
**Date:** October 24, 2025
**Status:** Analysis Complete - Awaiting Approval

## Executive Summary

Analysis of the `capcat catch` menu source management functionality (add, remove, configure) reveals:
- **Add Source**: Working correctly
- **Remove Source**: Config deletion works, but leaves orphaned output directories
- **List Sources**: Working correctly after removal (registry properly refreshed)
- **HTML Generation**: Shows orphaned source directories from previous fetches

**Root Cause:** Source removal deletes configuration but not output directories, causing HTML generator to list deleted sources.

---

## Bug Identification

### Bug 1: Orphaned Output Directories After Source Removal

**Severity:** MEDIUM
**Component:** `core/source_system/remove_source_command.py`, `core/html_generator.py`

**Description:**
When a source is removed via `capcat catch` menu or `./capcat remove-source`:
1. Config file deleted: `sources/active/config_driven/configs/<source>.yml` ✓
2. Bundle references removed: `sources/active/bundles.yml` updated ✓
3. Registry refreshed: `reset_source_registry()` called ✓
4. **Output directories NOT deleted**: `../News/news_*/Source_*/` remain ✗

**Impact:**
- HTML index generation lists deleted sources (because it scans filesystem)
- Users see outdated/deleted sources in generated HTML archives
- Confusion about which sources are actually active
- Disk space wasted on orphaned output directories

**Evidence:**
```python
# From core/html_generator.py:973-983
for item in sorted(path.iterdir(), key=sort_items):  # ← Scans actual directories
    if item.is_dir():
        if (item / "article.md").exists():
            source_id = extract_source_id(item.name)  # ← Tries to map to source
            category = find_category(source_id)  # ← Fails for deleted sources
            # Directory is listed with "Unknown" or fallback category
```

**Test Results:**
- Registry refresh: ✓ Working (verified with test script)
- CLI source listing: ✓ Working (deleted sources don't appear)
- Interactive menu listing: ✓ Working (deleted sources don't appear)
- HTML generation: ✗ FAILED (orphaned directories still listed)

---

### Bug 2: Source Addition Test Functionality

**Severity:** LOW (if working correctly, needs verification)
**Component:** `cli.py:add_source()`, `core/source_system/add_source_command.py`

**Status:** NOT TESTED YET
**Reason:** Requires RSS feed introspection and user interaction

**Requirements for Testing:**
1. Valid RSS feed URL
2. Interactive prompts for source ID, display name, category
3. Optional bundle assignment
4. Optional test fetch

---

### Bug 3: Source Configuration Functionality

**Severity:** LOW (if working correctly, needs verification)
**Component:** `core/interactive.py:_handle_generate_config()`

**Status:** NOT TESTED YET
**Reason:** Launches external script requiring user interaction

**Requirements for Testing:**
1. Script path: `scripts/generate_source_config.py`
2. Interactive wizard for complex source configuration
3. Python source generation for custom sources

---

## Detailed Analysis

### Source Removal Flow (Current Implementation)

```
User selects source(s) to remove
    ↓
EnhancedRemoveCommand.execute_with_options()
    ├─ Get available sources from registry ✓
    ├─ User selects sources via checkbox ✓
    ├─ Show removal summary ✓
    ├─ Confirm removal ✓
    ├─ Create backup (optional) ✓
    │  └─ Backup: config files + bundles.yml
    ├─ RemoveSourceCommand._remove_sources()
    │  ├─ BundleManager.remove_source_from_all_bundles() ✓
    │  │  └─ Update bundles.yml
    │  └─ FileSystemConfigRemover.remove_config_file() ✓
    │      └─ Delete YAML file
    ├─ RemoveSourceCommand._refresh_registry() ✓
    │  └─ reset_source_registry()
    └─ Show success message ✓

⚠️ MISSING STEP: Clean up output directories
```

### HTML Generation Flow (Current Behavior)

```
HTMLPostProcessor.process_directory_tree()
    ├─ _process_article_files() (incremental)
    ├─ _generate_directory_indices()
    └─ _create_main_index()
        └─ HTMLGenerator.generate_directory_index()
            └─ _generate_directory_listing()
                ├─ Get source registry ✓
                │  └─ registry.get_available_sources()
                ├─ Build category mapping from configs ✓
                ├─ SCAN FILESYSTEM ⚠️
                │  └─ for item in path.iterdir():  # ← Lists all directories
                ├─ Extract source_id from folder name
                │  └─ If source deleted: source_id = None
                └─ Display directory with:
                    └─ If source_id found: Use category from config ✓
                    └─ If source_id None: Show with "Unknown" or fallback ✗
```

**Problem:** HTML generator discovers directories by scanning filesystem, not querying registry.

---

## Fix Plan

### Fix 1: Add Output Directory Cleanup to Source Removal

**Priority:** HIGH
**Complexity:** MEDIUM
**Risk:** MEDIUM (potential data loss if not careful)

**Implementation:**

**Option A: Prompt User for Output Directory Cleanup (Recommended)**
```python
# In EnhancedRemoveCommand._execute_enhanced_removal()

# After source selection, before removal:
1. Scan for output directories matching selected sources
   - Search in ../News/news_*/
   - Match by source display name pattern (e.g., "Hacker_News_")
   - Match by source ID pattern (e.g., "hn_")

2. Show user what will be deleted:
   - Config files (already shown)
   - Bundle references (already shown)
   - Output directories (NEW):
     - Count directories found
     - Total size (MB/GB)
     - Date range of archives

3. Add prompt:
   "Also delete output archives for these sources? (Y/n)"
   - Default: Yes (recommended for clean removal)
   - No: Keep archives (for historical reference)

4. If Yes:
   - Include output directories in backup
   - Delete output directories
   - Show summary: "Deleted 15 archive directories (2.3 GB)"
```

**Option B: Automatic Cleanup with Flag (Alternative)**
```python
# Add --keep-archives flag to removal command

./capcat remove-source               # Deletes archives (default)
./capcat remove-source --keep-archives  # Keeps archives

# In EnhancedRemoveCommand:
- Always scan for output directories
- Delete if --keep-archives not specified
- Always backup before deletion
```

**Option C: Separate Cleanup Command (Low Priority)**
```python
# New command for orphaned directory cleanup

./capcat cleanup-archives             # Find and remove orphaned directories
./capcat cleanup-archives --dry-run  # Show what would be deleted
```

**Recommendation:** Implement **Option A** (user prompt) as primary fix, plus **Option C** (cleanup command) as utility.

---

### Fix 2: Improve HTML Generator Orphan Handling

**Priority:** MEDIUM
**Complexity:** LOW
**Risk:** LOW

**Implementation:**

**Change:** Filter out directories for non-existent sources

```python
# In HTMLGenerator._generate_directory_listing()

for item in sorted(path.iterdir(), key=sort_items):
    if item.is_dir():
        if (item / "article.md").exists():
            source_id = extract_source_id(item.name)

            # NEW: Check if source still exists in registry
            if source_id and source_id not in all_source_ids:
                self.logger.debug(
                    f"Skipping orphaned directory for deleted source: {item.name}"
                )
                continue  # Skip this directory

            # Rest of processing...
```

**Benefits:**
- HTML generator silently ignores orphaned directories
- No breaking changes
- Backward compatible

---

### Fix 3: Add Registry Verification to Interactive Menu

**Priority:** LOW
**Complexity:** LOW
**Risk:** NONE

**Implementation:**

**Enhancement:** Show source count after operations

```python
# In core/interactive.py:_handle_remove_source()

# After removal completes:
def _handle_remove_source():
    # ... existing removal code ...

    # NEW: Show updated source count
    from cli import get_available_sources
    sources = get_available_sources()
    print(f"\n✓ Removal complete")
    print(f"  Active sources: {len(sources)}")

    input("\nPress Enter to continue...")
```

---

## Testing Plan

### Test 1: Source Removal with Output Cleanup

**Steps:**
1. Fetch articles from test source: `./capcat fetch test_source --count 3 --html`
2. Verify output created: `../News/news_*/Test_Source_*/`
3. Remove source: Interactive menu → Remove Sources → Select test_source
4. Verify prompt for output cleanup appears
5. Accept cleanup (Yes)
6. Verify:
   - Config deleted: `sources/active/config_driven/configs/test_source.yml` ✓
   - Output deleted: `../News/news_*/Test_Source_*/` ✓
   - Registry updated: `./capcat list sources` (no test_source) ✓
   - HTML clean: Generate HTML, no test_source listed ✓
   - Backup created: `.capcat_backups/removal_*/` contains all files ✓

### Test 2: Source Removal WITHOUT Output Cleanup

**Steps:**
1. Fetch articles from test source
2. Remove source, decline output cleanup (No)
3. Verify:
   - Config deleted ✓
   - Output kept: Directories still exist ✓
   - HTML generation: Orphaned directory NOT listed (Filter working) ✓

### Test 3: Orphan Cleanup Command

**Steps:**
1. Manually delete source config (simulate old deletion)
2. Run: `./capcat cleanup-archives --dry-run`
3. Verify: Lists orphaned directories
4. Run: `./capcat cleanup-archives`
5. Verify: Orphaned directories deleted

### Test 4: Source Addition

**Steps:**
1. Interactive menu → Add New Source from RSS Feed
2. Enter test RSS URL: `https://example.com/feed`
3. Complete prompts (source ID, display name, category)
4. Verify:
   - Config created: `sources/active/config_driven/configs/<id>.yml` ✓
   - Source appears in listings ✓
   - Optional: Added to bundle ✓
   - Optional: Test fetch successful ✓

### Test 5: Registry Refresh in Interactive Session

**Steps:**
1. Start: `./capcat catch`
2. List sources (note count)
3. Add new source
4. List sources again (count increased)
5. Remove source
6. List sources again (count decreased)
7. Verify: All listings reflect current state ✓

---

## Implementation Priority

### Phase 1: Critical Fixes (Implement First)
1. **Fix 1A**: Add output directory cleanup to removal command
   - User prompt for archive deletion
   - Include in backup
   - Show cleanup summary

2. **Fix 2**: Filter orphaned directories in HTML generator
   - Skip directories for deleted sources
   - Log skipped directories

3. **Test**: Comprehensive removal testing
   - With cleanup
   - Without cleanup
   - HTML generation verification

### Phase 2: Enhancements (Implement Second)
1. **Fix 1C**: Orphan cleanup utility command
   - `./capcat cleanup-archives`
   - Dry-run mode
   - Interactive confirmation

2. **Fix 3**: Interactive menu enhancements
   - Show source counts after operations
   - Better feedback messages

3. **Test**: Addition and configuration testing
   - Source addition flow
   - Config generation
   - Registry refresh verification

---

## Code Changes Required

### File 1: `core/source_system/enhanced_remove_command.py`

**Location:** `_execute_enhanced_removal()` method

**Add:**
1. New method: `_scan_output_directories(source_info_list) -> List[Path]`
   - Search `../News/news_*/` for matching directories
   - Return list of Path objects

2. New method: `_prompt_output_cleanup(directories) -> bool`
   - Show directory count and total size
   - Prompt user: "Also delete output archives? (Y/n)"
   - Return True if yes

3. New method: `_delete_output_directories(directories, backup_metadata)`
   - Include directories in backup
   - Delete directories
   - Show summary

4. Modify: `_execute_enhanced_removal()`
   - After source selection, call `_scan_output_directories()`
   - Call `_prompt_output_cleanup()`
   - If yes, call `_delete_output_directories()`

**Estimated Lines:** ~150 new lines

---

### File 2: `core/html_generator.py`

**Location:** `_generate_directory_listing()` method (line 973)

**Modify:**
```python
# Before: for item in sorted(path.iterdir(), key=sort_items):
# After:
for item in sorted(path.iterdir(), key=sort_items):
    if item.is_dir():
        if (item / "article.md").exists():
            source_id = extract_source_id(item.name)

            # NEW: Skip orphaned directories
            if source_id and source_id not in all_source_ids:
                self.logger.debug(
                    f"Skipping orphaned directory: {item.name} (source '{source_id}' no longer exists)"
                )
                continue

            # Existing processing continues...
```

**Estimated Lines:** ~5 new lines

---

### File 3: `core/interactive.py`

**Location:** `_handle_remove_source()` method (line 228)

**Modify:**
```python
# After: enhanced_command.execute_with_options(options)

# NEW: Show updated source count
from cli import get_available_sources
sources = get_available_sources()
print(f"\n✓ Removal complete. Active sources: {len(sources)}")

input("\nPress Enter to continue...")
```

**Estimated Lines:** ~5 new lines

---

### File 4 (New): `core/source_system/archive_cleanup.py`

**Purpose:** Utility for cleaning orphaned output directories

**Contents:**
1. `class ArchiveCleanup`
   - `scan_orphaned_directories() -> List[Path]`
   - `calculate_size(directories) -> int`
   - `prompt_cleanup() -> bool`
   - `cleanup_directories(dry_run=False)`

2. CLI integration in `cli.py`:
   - New command: `cleanup-archives`
   - Flags: `--dry-run`, `--force`

**Estimated Lines:** ~200 new lines

---

## Risk Assessment

### Risks

**Risk 1: Data Loss**
- **Severity:** HIGH
- **Mitigation:** Always create backup before deletion
- **Mitigation:** User confirmation required
- **Mitigation:** Show exactly what will be deleted

**Risk 2: Incorrect Directory Matching**
- **Severity:** MEDIUM
- **Mitigation:** Use same logic as `extract_source_id()` in HTML generator
- **Mitigation:** Test with various naming patterns
- **Mitigation:** Dry-run mode to preview

**Risk 3: Backup Size**
- **Severity:** LOW
- **Mitigation:** Implement backup size limits
- **Mitigation:** Cleanup old backups automatically
- **Mitigation:** Warn user if backup > 1GB

### Safety Measures

1. **Always backup before deletion**
   - Config files
   - Bundle file
   - Output directories (if cleaned)

2. **User confirmation required**
   - Show summary of what will be deleted
   - Require explicit confirmation
   - Support --force flag for automation

3. **Comprehensive logging**
   - Log all deletion operations
   - Track deleted paths
   - Include in removal metadata

4. **Restore capability**
   - Existing undo functionality (`--undo <backup_id>`)
   - Extend to restore output directories
   - Test restore process

---

## Success Criteria

### Must Have
1. ✓ Source removal deletes config file
2. ✓ Source removal updates bundles.yml
3. ✓ Registry refreshes after removal
4. ✓ Deleted sources don't appear in CLI listing
5. ✓ Deleted sources don't appear in interactive menu
6. ✓ **NEW:** User prompted for output directory cleanup
7. ✓ **NEW:** HTML generator doesn't list orphaned directories

### Should Have
1. ✓ Backup includes output directories
2. ✓ Cleanup shows size and count
3. ✓ Dry-run mode for safety
4. ✓ Orphan cleanup utility command
5. ✓ Interactive menu shows source count

### Nice to Have
1. Source addition fully tested
2. Config generation fully tested
3. Automated test suite
4. Performance metrics (cleanup speed)

---

## Next Steps

1. **Get User Approval** for fix plan
2. **Implement Phase 1** (critical fixes)
3. **Test thoroughly** with various scenarios
4. **Implement Phase 2** (enhancements)
5. **Document** all changes
6. **Create** user-facing changelog

---

## Questions for User

1. **Output Directory Cleanup Preference:**
   - Should cleanup be default? (Recommend: Yes)
   - Or should it require explicit flag?

2. **Backup Size Concerns:**
   - Is there a size limit for backups?
   - Should we compress backups?

3. **Orphan Detection:**
   - Should we scan for orphans on startup?
   - Should we prompt user to clean them?

4. **Archive Retention:**
   - Do you want to keep ANY old archives?
   - Or prefer complete cleanup?

---

**Report Status:** COMPLETE
**Awaiting:** User approval to proceed with implementation
**Recommendation:** Proceed with Phase 1 implementation
