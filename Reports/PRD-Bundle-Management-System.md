# Product Requirements Document: Bundle Management System
**Version:** 1.0
**Date:** October 24, 2025
**Status:** DRAFT
**Priority:** HIGH

---

## 1. Executive Summary

### 1.1 Problem Statement
Currently, bundle management in Capcat is limited to reading predefined bundles from `bundles.yml`. Users cannot create, modify, or delete bundles through the interactive menu. Source-to-bundle assignments are manual YAML edits, prone to errors and requiring technical knowledge.

### 1.2 Proposed Solution
Implement comprehensive CRUD (Create, Read, Update, Delete) operations for bundle management through the interactive menu system, allowing users to:
- Create new bundles with descriptions and default counts
- Edit existing bundle metadata
- Delete bundles
- Add/remove sources to/from bundles
- Move sources between bundles
- View bundle composition and statistics

### 1.3 Success Metrics
- Bundle creation time: < 30 seconds
- Zero YAML syntax errors from UI operations
- 100% bundle operation success rate
- User can manage all bundle operations without command-line YAML editing

---

## 2. Current State Analysis

### 2.1 Existing Infrastructure

**Bundle Storage:**
- Location: `sources/active/bundles.yml`
- Format: YAML with preserved comments
- Structure:
  ```yaml
  bundles:
    bundle_id:
      description: "Bundle description"
      sources: [source1, source2]
      default_count: 30
  ```

**Existing Code:**
- `BundleManager` class (80 lines) - Basic operations
- `get_available_bundles()` in cli.py - Read operations
- Bundle selection in interactive menu - Read-only

**Capabilities:**
- ✓ Load bundles from YAML
- ✓ Add source to bundle (programmatic)
- ✓ Remove source from all bundles (programmatic)
- ✓ Display bundles in menu (read-only)

**Limitations:**
- ✗ No UI for bundle creation
- ✗ No UI for bundle deletion
- ✗ No UI for bundle editing
- ✗ No UI for source assignment
- ✗ No validation of bundle operations
- ✗ No undo/backup for bundle changes
- ✗ No bundle metadata management

### 2.2 User Pain Points
1. **Manual YAML Editing Required:** Users must edit `bundles.yml` directly
2. **Syntax Errors:** Manual edits can break YAML syntax
3. **No Validation:** Invalid source IDs or bundle names not caught
4. **Cumbersome Workflow:** Requires text editor, file navigation, save, restart
5. **Error-Prone:** Easy to accidentally delete sources or corrupt structure
6. **No Discoverability:** Users don't know which sources exist

---

## 3. Requirements

### 3.1 Functional Requirements

#### FR-1: Bundle CRUD Operations

**FR-1.1: Create Bundle**
- User can create new bundle with unique ID
- Required fields: bundle_id, description
- Optional fields: default_count (default: 20)
- Validation: unique bundle ID, valid identifier format
- Auto-add to bundles.yml with proper formatting

**FR-1.2: Read Bundle**
- List all bundles with metadata
- View bundle details (sources, count, description)
- Show bundle statistics (source count, category distribution)
- Browse bundle contents interactively

**FR-1.3: Update Bundle**
- Rename bundle (change bundle_id)
- Edit description
- Change default_count
- Validation: prevent duplicate names, maintain integrity

**FR-1.4: Delete Bundle**
- Remove bundle from bundles.yml
- Confirmation prompt with bundle details
- Protected bundles: "all" cannot be deleted
- Backup before deletion

#### FR-2: Source-to-Bundle Management

**FR-2.1: Add Sources to Bundle**
- Select bundle
- Multi-select sources from available list
- Show current bundle composition
- Prevent duplicates
- Save to YAML

**FR-2.2: Remove Sources from Bundle**
- Select bundle
- Multi-select sources to remove
- Show remaining sources
- Confirmation prompt
- Save to YAML

**FR-2.3: Move Sources Between Bundles**
- Select source(s)
- Show current bundle memberships
- Select target bundle
- Option: remove from source bundle(s)
- Option: copy (keep in source) or move (remove from source)
- Save to YAML

**FR-2.4: Bulk Operations**
- Add all sources of a category to bundle
- Remove all sources of a category from bundle
- Copy entire bundle
- Merge bundles

#### FR-3: Bundle Validation

**FR-3.1: Pre-Save Validation**
- Bundle ID: lowercase, alphanumeric, underscores only
- Description: non-empty, max 200 chars
- Default count: integer, range 1-100
- Source IDs: exist in registry
- No circular dependencies

**FR-3.2: Integrity Checks**
- No orphaned bundle references
- All source IDs valid
- YAML syntax correct
- File permissions adequate

#### FR-4: User Interface

**FR-4.1: Interactive Menu Integration**
- New submenu: "Manage Bundles"
- Consistent with existing menu design
- Questionary-based UI
- Orange theme with ▶ pointer
- Clear navigation paths

**FR-4.2: Bundle Browser**
- List view: all bundles with descriptions
- Detail view: bundle composition
- Statistics: source count, categories
- Visual separators and formatting

**FR-4.3: Source Assignment UI**
- Multi-select checkboxes for sources
- Category grouping
- Current membership indicators
- Clear selection feedback

#### FR-5: Safety Features

**FR-5.1: Backup System**
- Auto-backup before modifications
- Backup location: `backups/bundles/`
- Timestamped backups
- Restore capability

**FR-5.2: Confirmation Prompts**
- Destructive operations require confirmation
- Show impact preview (what will change)
- Default: safe option (No for deletes)

**FR-5.3: Undo Capability**
- Restore from backup
- Show list of recent backups
- Preview backup contents

### 3.2 Non-Functional Requirements

#### NFR-1: Performance
- Bundle load time: < 100ms
- Save operation: < 200ms
- UI response time: < 50ms
- Handle up to 100 bundles
- Handle up to 50 sources per bundle

#### NFR-2: Reliability
- 100% YAML syntax preservation
- Zero data loss on operations
- Atomic file writes (temp file + rename)
- Error recovery from corrupted state

#### NFR-3: Usability
- Intuitive menu navigation
- Clear operation outcomes
- Helpful error messages
- Keyboard-only operation
- No external tool dependencies

#### NFR-4: Maintainability
- Clean architecture (protocols, DI)
- Comprehensive docstrings
- Unit test coverage > 90%
- Integration test coverage > 80%
- Logging all operations

---

## 4. User Stories

### 4.1 Priority 1 (Must Have)

**US-1: Create Bundle**
As a user, I want to create a new bundle so that I can group related sources together.

**Acceptance Criteria:**
- Interactive prompt for bundle ID, description, default_count
- Validation of inputs
- Bundle saved to bundles.yml
- Confirmation message shown
- Bundle immediately available in menu

**US-2: Delete Bundle**
As a user, I want to delete a bundle I no longer need so that my bundle list stays clean.

**Acceptance Criteria:**
- Select bundle from list
- Confirmation prompt with bundle details
- Bundle removed from bundles.yml
- Cannot delete "all" bundle
- Success message shown

**US-3: Add Sources to Bundle**
As a user, I want to add sources to a bundle so that I can customize bundle composition.

**Acceptance Criteria:**
- Select bundle
- Multi-select sources to add
- Only show sources not already in bundle
- Sources added to bundles.yml
- Confirmation message shown

**US-4: Remove Sources from Bundle**
As a user, I want to remove sources from a bundle so that I can refine bundle contents.

**Acceptance Criteria:**
- Select bundle
- Multi-select sources to remove
- Only show sources currently in bundle
- Sources removed from bundles.yml
- Confirmation message shown

**US-5: View Bundle Details**
As a user, I want to see what sources are in a bundle so that I understand its composition.

**Acceptance Criteria:**
- Select bundle from list
- Shows description, default_count, source list
- Sources grouped by category
- Statistics: total sources, categories
- Back to bundle list

### 4.2 Priority 2 (Should Have)

**US-6: Edit Bundle Metadata**
As a user, I want to edit bundle description and default_count so that I can keep metadata current.

**Acceptance Criteria:**
- Select bundle
- Edit description and/or default_count
- Cannot change bundle_id (creates new instead)
- Changes saved to bundles.yml
- Confirmation shown

**US-7: Move Source Between Bundles**
As a user, I want to move a source from one bundle to another so that I can reorganize efficiently.

**Acceptance Criteria:**
- Select source(s)
- Show current bundle memberships
- Select target bundle
- Option: copy or move
- Changes saved to bundles.yml
- Summary shown

**US-8: Copy Bundle**
As a user, I want to duplicate a bundle so that I can create variations easily.

**Acceptance Criteria:**
- Select bundle to copy
- Enter new bundle ID
- Optionally edit description
- New bundle created with same sources
- Confirmation shown

### 4.3 Priority 3 (Nice to Have)

**US-9: Bulk Category Operations**
As a user, I want to add all sources from a category to a bundle so that I can work efficiently.

**Acceptance Criteria:**
- Select bundle
- Select category (tech, news, science, etc.)
- Add all sources from category
- Changes saved
- Summary shown

**US-10: Bundle Statistics**
As a user, I want to see bundle statistics so that I understand my bundle landscape.

**Acceptance Criteria:**
- Overview screen showing all bundles
- Statistics: source counts, category distribution
- Largest/smallest bundles
- Source overlap analysis

---

## 5. Technical Architecture

### 5.1 Component Structure

```
core/source_system/bundle_management/
├── __init__.py
├── bundle_manager.py          # Extended CRUD operations
├── bundle_validator.py        # Validation logic
├── bundle_backup_manager.py   # Backup/restore
├── bundle_ui.py              # Questionary UI components
└── bundle_service.py         # Service layer (DI orchestration)
```

### 5.2 Class Design

#### BundleManager (Extended)
```python
class BundleManager:
    # Existing
    def add_source_to_bundle(source_id, bundle_name)
    def remove_source_from_all_bundles(source_id)

    # New
    def create_bundle(bundle_id, description, default_count=20)
    def delete_bundle(bundle_id)
    def update_bundle_metadata(bundle_id, description?, default_count?)
    def rename_bundle(old_id, new_id)
    def get_bundle_details(bundle_id) -> BundleInfo
    def list_bundles() -> List[BundleInfo]
    def copy_bundle(source_id, target_id)
    def merge_bundles(bundle_ids, target_id)
    def add_sources_to_bundle(bundle_id, source_ids)
    def remove_sources_from_bundle(bundle_id, source_ids)
    def move_source_between_bundles(source_id, from_bundle, to_bundle)
```

#### BundleValidator
```python
class BundleValidator:
    def validate_bundle_id(bundle_id) -> ValidationResult
    def validate_description(description) -> ValidationResult
    def validate_default_count(count) -> ValidationResult
    def validate_source_ids(source_ids) -> ValidationResult
    def check_bundle_exists(bundle_id) -> bool
    def check_bundle_unique(bundle_id) -> bool
    def check_sources_exist(source_ids) -> List[str]  # Missing IDs
```

#### BundleBackupManager
```python
class BundleBackupManager:
    def create_backup() -> BackupMetadata
    def list_backups() -> List[BackupMetadata]
    def restore_backup(backup_id) -> bool
    def cleanup_old_backups(keep_count=10)
```

#### BundleUI
```python
class BundleUI:
    def show_bundle_menu() -> BundleAction
    def prompt_create_bundle() -> BundleData
    def prompt_select_bundle(bundles) -> str
    def prompt_select_sources(sources, current=[]) -> List[str]
    def prompt_confirm_delete(bundle_info) -> bool
    def show_bundle_details(bundle_info)
    def show_success(message)
    def show_error(message)
```

#### BundleService
```python
class BundleService:
    def __init__(manager, validator, backup_manager, ui)
    def execute_create_bundle()
    def execute_delete_bundle()
    def execute_edit_bundle()
    def execute_add_sources()
    def execute_remove_sources()
    def execute_move_source()
    def execute_copy_bundle()
```

### 5.3 Data Models

```python
@dataclass
class BundleInfo:
    bundle_id: str
    description: str
    sources: List[str]
    default_count: int
    category_distribution: Dict[str, int]
    total_sources: int

@dataclass
class BundleData:
    bundle_id: str
    description: str
    default_count: int

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]

@dataclass
class BackupMetadata:
    backup_id: str
    timestamp: datetime
    file_path: Path
    bundle_count: int
```

### 5.4 Menu Integration

```
Main Menu
  └─> Manage Sources
        ├─> Add New Source
        ├─> Remove Sources
        ├─> List Sources
        ├─> Test Source
        └─> Manage Bundles  ← NEW
              ├─> Create New Bundle
              ├─> Edit Bundle
              ├─> Delete Bundle
              ├─> Add Sources to Bundle
              ├─> Remove Sources from Bundle
              ├─> Move Sources Between Bundles
              ├─> Copy Bundle
              ├─> View All Bundles
              └─> Back to Source Management
```

---

## 6. User Workflows

### 6.1 Create Bundle Flow

```
1. User selects "Manage Bundles" → "Create New Bundle"
2. System prompts for bundle ID
   - Input: Text field
   - Validation: lowercase, alphanumeric, underscores
   - Example: "my_custom_bundle"
3. System prompts for description
   - Input: Text field
   - Example: "My custom tech sources"
4. System prompts for default count (optional)
   - Input: Number
   - Default: 20
5. System shows summary and confirms
6. System creates bundle in bundles.yml
7. System shows success message
8. Bundle available immediately in menu
```

### 6.2 Add Sources to Bundle Flow

```
1. User selects "Manage Bundles" → "Add Sources to Bundle"
2. System shows list of bundles (interactive select)
3. User selects target bundle
4. System shows bundle details and current sources
5. System shows available sources (multi-select checkboxes)
   - Grouped by category
   - Excludes sources already in bundle
6. User selects sources to add
7. System shows summary of changes
8. User confirms
9. System updates bundles.yml
10. System shows success message with count
```

### 6.3 Move Source Between Bundles Flow

```
1. User selects "Manage Bundles" → "Move Sources Between Bundles"
2. System shows list of all sources (multi-select)
3. User selects source(s) to move
4. System shows current bundle memberships for selected sources
5. System prompts: Copy or Move?
   - Copy: Keep in source bundle(s)
   - Move: Remove from source bundle(s)
6. System shows list of target bundles
7. User selects target bundle
8. System shows summary of changes
9. User confirms
10. System updates bundles.yml
11. System shows success message with summary
```

---

## 7. Error Handling

### 7.1 User Input Errors

| Error | Validation | User Feedback |
|-------|-----------|---------------|
| Invalid bundle ID | Regex: `^[a-z0-9_]+$` | "Bundle ID must be lowercase letters, numbers, and underscores only" |
| Duplicate bundle ID | Check existing | "Bundle 'tech' already exists. Choose a different name." |
| Empty description | Length check | "Description cannot be empty" |
| Invalid default_count | Range 1-100 | "Default count must be between 1 and 100" |
| Non-existent source | Registry check | "Source 'invalid_id' not found in registry" |
| Empty bundle deletion | Source count check | "Cannot delete bundle: no sources to remove" |
| Protected bundle deletion | Hardcoded check | "Cannot delete 'all' bundle (system bundle)" |

### 7.2 System Errors

| Error | Cause | Recovery | User Message |
|-------|-------|----------|--------------|
| YAML parse error | Corrupted file | Restore from backup | "Bundle file corrupted. Restoring from backup..." |
| File permission error | Read-only | Prompt for sudo or path change | "Cannot write to bundles.yml. Check file permissions." |
| Disk full | No space | Abort, rollback | "Insufficient disk space. Operation cancelled." |
| Backup failure | Backup dir not writable | Continue without backup, warn | "Warning: Backup failed. Continue without backup? (not recommended)" |

---

## 8. Testing Strategy

### 8.1 Unit Tests

**BundleManager Tests:**
- Create bundle: valid inputs, duplicate ID, invalid ID format
- Delete bundle: existing, non-existing, protected bundle
- Update metadata: valid, invalid, non-existing bundle
- Add sources: valid, duplicate, non-existing sources
- Remove sources: valid, non-existing sources
- YAML preservation: comments, formatting maintained

**BundleValidator Tests:**
- Bundle ID: valid, invalid characters, too long, too short
- Description: valid, empty, too long
- Default count: valid, negative, zero, too large
- Source validation: all exist, some missing, all missing

**BundleBackupManager Tests:**
- Create backup: success, failure scenarios
- Restore backup: valid, corrupted, non-existing
- List backups: empty, multiple, sorted by date
- Cleanup: retention policy, disk space

### 8.2 Integration Tests

**End-to-End Workflows:**
- Create bundle → Add sources → Verify YAML → Load in CLI
- Delete bundle → Verify removed → Cannot load
- Edit bundle → Verify changes persisted
- Move sources → Verify source memberships updated
- Restore backup → Verify exact state restored

### 8.3 UI Tests

**Interactive Menu:**
- Navigation: all menu options reachable
- Selection: single and multi-select work
- Validation: errors shown in UI
- Confirmation: prompts appear for destructive ops
- Feedback: success/error messages display

---

## 9. Security Considerations

### 9.1 Input Sanitization
- Bundle IDs: alphanumeric + underscores only (prevent injection)
- Descriptions: max length, no control characters
- File paths: no path traversal (../)
- Source IDs: whitelist validation against registry

### 9.2 File Operations
- Atomic writes: write to temp file, then rename
- Permission checks: verify write access before operations
- Backup verification: checksums for backup integrity

### 9.3 Undo Protection
- All destructive operations create backup first
- Restore capability for last 10 operations
- Confirmation for irreversible actions

---

## 10. Performance Considerations

### 10.1 Optimization Strategies
- Lazy load: load bundle details only when viewing
- Cache: cache parsed YAML between operations in session
- Batch operations: group multiple source adds into single save
- Incremental saves: only write changed bundles

### 10.2 Performance Targets
- Bundle list load: < 50ms
- Bundle details load: < 100ms
- Add/remove source: < 200ms (including save)
- Create/delete bundle: < 300ms
- Multi-source operation: < 500ms

---

## 11. Dependencies

### 11.1 Existing Dependencies
- ruamel.yaml (YAML with comment preservation)
- questionary (interactive UI)
- pathlib (file operations)
- dataclasses (data models)

### 11.2 New Dependencies
None required (use existing)

---

## 12. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| YAML corruption | Low | High | Atomic writes, backups, validation |
| Data loss | Low | Critical | Automatic backups, confirmation prompts |
| User error | Medium | Medium | Clear UI, confirmations, undo capability |
| Performance degradation | Low | Low | Optimize file I/O, cache parsed data |
| Integration bugs | Medium | Medium | Comprehensive testing, staged rollout |
| UI confusion | Medium | Low | Clear labels, help text, examples |

---

## 13. Rollout Plan

### 13.1 Phase 1: Core CRUD (Week 1)
**Deliverables:**
- Extended BundleManager with create/delete/update
- BundleValidator implementation
- Unit tests for core operations

**Success Criteria:**
- All CRUD operations functional
- 100% test coverage for BundleManager
- YAML integrity maintained

### 13.2 Phase 2: Source Management (Week 2)
**Deliverables:**
- Add/remove sources to/from bundles
- Move sources between bundles
- Bulk operations

**Success Criteria:**
- Source operations work correctly
- Multi-select UI functional
- Integration tests pass

### 13.3 Phase 3: UI Integration (Week 3)
**Deliverables:**
- BundleUI component
- Integration with interactive menu
- User workflows implemented

**Success Criteria:**
- All menu options functional
- Consistent with existing UI design
- User testing feedback positive

### 13.4 Phase 4: Safety & Polish (Week 4)
**Deliverables:**
- Backup/restore system
- Enhanced validation and error messages
- Documentation and help text

**Success Criteria:**
- Backup/restore works reliably
- Clear error messages
- User documentation complete

---

## 14. Success Criteria

### 14.1 Functional Success
- ✓ Create, edit, delete bundles via UI
- ✓ Add, remove, move sources via UI
- ✓ No YAML syntax errors from UI operations
- ✓ All operations atomic and reversible
- ✓ Consistent UI design

### 14.2 Quality Success
- ✓ Unit test coverage > 90%
- ✓ Integration test coverage > 80%
- ✓ Zero data loss incidents
- ✓ Performance targets met
- ✓ User acceptance testing passed

### 14.3 User Success
- ✓ Bundle management time reduced by 80%
- ✓ Zero manual YAML editing required
- ✓ Positive user feedback (> 8/10 satisfaction)
- ✓ No support tickets for bundle corruption

---

## 15. Future Enhancements

### 15.1 Advanced Features (Post-MVP)
- Bundle templates (quick start bundles)
- Bundle sharing/export (JSON/YAML export)
- Bundle analytics (usage statistics)
- Bundle recommendations (suggest sources based on category)
- Bundle dependencies (bundle A includes bundle B)
- Dynamic bundles (auto-update based on rules)

### 15.2 Integration Opportunities
- CI/CD: validate bundles in pre-commit hooks
- Web UI: manage bundles via web interface
- API: REST API for programmatic bundle management
- Sync: sync bundles across multiple machines

---

## 16. Open Questions

1. **Bundle Naming Convention:** Enforce specific format or allow free-form?
   - **Recommendation:** lowercase_with_underscores, no spaces, max 30 chars

2. **Bundle Limits:** Maximum number of bundles? Maximum sources per bundle?
   - **Recommendation:** 100 bundles max, 50 sources per bundle max

3. **Protected Bundles:** Which bundles should be protected from deletion?
   - **Recommendation:** Only "all" bundle protected (system-managed)

4. **Source Membership:** Can source be in multiple bundles?
   - **Current:** Yes (confirmed by existing structure)
   - **Recommendation:** Keep current behavior

5. **Default Count Override:** Allow per-bundle override of default count?
   - **Current:** Yes (exists in YAML)
   - **Recommendation:** Keep, allow editing via UI

---

## 17. Appendix

### 17.1 Bundle YAML Schema

```yaml
bundles:
  <bundle_id>:                    # Required: lowercase, alphanumeric, underscores
    description: <string>         # Required: 1-200 chars
    sources: [<source_id>, ...]   # Required: list of valid source IDs
    default_count: <int>          # Optional: 1-100, default 20
```

### 17.2 Example Bundle

```yaml
bundles:
  my_ai_news:
    description: "AI and machine learning sources"
    sources:
      - googleai
      - openai
      - mitnews
      - lesswrong
    default_count: 25
```

### 17.3 Validation Rules Summary

| Field | Type | Constraints | Default |
|-------|------|-------------|---------|
| bundle_id | string | `^[a-z0-9_]+$`, max 30 chars, unique | N/A |
| description | string | 1-200 chars, non-empty | N/A |
| sources | list[string] | valid source IDs, no duplicates | [] |
| default_count | int | 1-100 | 20 |

---

**Document Status:** DRAFT
**Review Required:** YES
**Approver:** Product Owner
**Next Steps:** Implementation plan creation, technical design review
