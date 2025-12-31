# Critical Bugs Report

**Date:** 2025-12-23
**Source:** Comprehensive Functionality Testing Phase 1
**Status:** ACTIVE
**Priority:** CRITICAL

## Summary

2 critical bugs confirmed, systemic pattern identified affecting unknown number of features.

## BUG-001: list Command Non-Functional

**Severity:** CRITICAL
**Impact:** User-facing core discovery feature
**User Impact:** HIGH - Cannot discover available sources via CLI
**Documentation Impact:** HIGH - Extensively documented across multiple files

### Description

`./capcat list sources`, `./capcat list bundles`, and `./capcat list` commands print single message then exit. No source/bundle listing functionality.

### Evidence

**Code Location:** `cli.py:850-857`
```python
def list_sources_and_bundles(what: str = 'all') -> None:
    """Display available sources and bundles.

    Args:
        what: What to list - 'sources', 'bundles', or 'all'
    """
    # ... (implementation remains the same)
    print("Listing sources and bundles...")
```

**Called From:** `cli.py:884`
```python
if args.command == 'list':
    list_sources_and_bundles(args.what)
    sys.exit(0)
```

**Test Results:**
```bash
$ ./capcat list sources
Listing sources and bundles...
INFO: Using virtual environment Python

$ ./capcat list bundles
Listing sources and bundles...
INFO: Using virtual environment Python

$ ./capcat list
Listing sources and bundles...
INFO: Using virtual environment Python
```

**Expected Output (from docs/quick-start.md:142-147):**
```
TECH:
  - hn             Hacker News
  - lb             Lobsters
  - iq             InfoQ

NEWS:
  - bbc            BBC News
  - guardian       The Guardian

SCIENCE:
  - nature         Nature News
```

### Documentation References

**Affected Documentation:**
1. `docs/quick-start.md:142` - Shows expected output format
2. `docs/tutorials/01-cli-commands-exhaustive.md:170` - States "Use `./capcat list sources` to see all available source IDs"
3. `interactive-mode.md:469` - Lists CLI equivalent as `./capcat list sources`
4. `CLAUDE.md` - Quick reference includes command

**Documentation Claims:**
- Command lists sources grouped by category
- Shows source IDs and display names
- Provides bundle information
- Essential for discovering available sources

### Working Implementation Location

**File:** `core/interactive.py:287-336`
**Function:** `_handle_list_sources()`

**Implementation Status:** COMPLETE
- Fetches sources from registry ✓
- Groups by category ✓
- Formats output ✓
- Displays via questionary UI ✓

**Accessibility:** Interactive mode only
- Path: `./capcat catch` → "Manage Sources" → "List All Sources"
- NOT accessible via documented CLI command

### Root Cause

**Hypothesis:** Incomplete refactoring

**Evidence:**
1. Comment `# ... (implementation remains the same)` at line 856 indicates code removal
2. Full implementation exists in interactive.py (moved during refactor)
3. CLI stub left behind
4. Documentation never updated

**Refactoring Pattern:**
```
OLD: cli.py contains implementation
      ↓
REFACTOR: Move to core/interactive.py for questionary UI
      ↓
CURRENT: cli.py has stub, interactive.py has implementation
      ↓
FORGOT: Update CLI stub OR remove CLI command OR update docs
```

### Fix Options

#### Option A: Implement CLI Version (RECOMMENDED)

**Effort:** 2 hours
**Benefits:**
- Matches documentation
- User expectations met
- CLI completeness
- No doc updates required

**Implementation:**
```python
def list_sources_and_bundles(what: str = 'all') -> None:
    """Display available sources and bundles."""
    from cli import get_available_sources, get_available_bundles
    from core.source_system.source_registry import get_source_registry

    sources = get_available_sources()
    registry = get_source_registry()

    if what in ['sources', 'all']:
        # Group by category
        categories = {}
        for source_id, display_name in sorted(sources.items()):
            try:
                config = registry.get_source_config(source_id)
                category = config.category.upper() if config else 'OTHER'
            except:
                category = 'OTHER'

            if category not in categories:
                categories[category] = []
            categories[category].append((source_id, display_name))

        # Print formatted output
        print("\n--- Available Sources ---\n")
        for category, source_list in sorted(categories.items()):
            print(f"{category}:")
            for source_id, display_name in source_list:
                print(f"  - {source_id:15} {display_name}")
            print()

        print(f"Total: {len(sources)} sources\n")

    if what in ['bundles', 'all']:
        bundles = get_available_bundles()

        print("\n--- Available Bundles ---\n")
        for bundle_id, bundle_data in sorted(bundles.items()):
            sources_str = ", ".join(bundle_data['sources'][:3])
            if len(bundle_data['sources']) > 3:
                sources_str += f", ... ({len(bundle_data['sources'])} total)"
            desc = bundle_data.get('description', '')
            print(f"{bundle_id}: {desc}")
            print(f"  Sources: {sources_str}")
            print()
```

#### Option B: Remove CLI Command

**Effort:** 1 hour
**Benefits:**
- Honest about capabilities
- Clear separation CLI vs Interactive

**Drawbacks:**
- Extensive doc updates required
- Breaking change for users
- Reduces CLI completeness

**Implementation:**
```python
def list_sources_and_bundles(what: str = 'all') -> None:
    """Display available sources and bundles (Interactive mode only)."""
    print("\n⚠️  The 'list' command is only available in interactive mode.")
    print("    Run: ./capcat catch")
    print("    Then select: Manage Sources → List All Sources\n")
    sys.exit(1)
```

**Required Doc Updates:**
- docs/quick-start.md
- docs/tutorials/01-cli-commands-exhaustive.md
- docs/interactive-mode.md
- CLAUDE.md

#### Option C: Redirect CLI to Interactive

**Effort:** 30 minutes
**Benefits:**
- Provides functionality
- No doc updates

**Drawbacks:**
- Unexpected UX (launches UI for CLI command)
- Not truly CLI accessible

### Recommendation

**Implement Option A**

**Rationale:**
- Documentation extensively describes CLI usage
- Users expect CLI command based on help text
- Maintains feature parity between CLI and Interactive
- Aligns with documented behavior
- Low implementation effort

### Testing Requirements

**Unit Tests:**
```python
def test_list_sources_cli():
    """Verify list sources produces categorized output."""
    result = subprocess.run(['./capcat', 'list', 'sources'], capture_output=True, text=True)
    assert 'TECH:' in result.stdout
    assert 'NEWS:' in result.stdout
    assert '- hn' in result.stdout
    assert 'Total:' in result.stdout

def test_list_bundles_cli():
    """Verify list bundles produces bundle information."""
    result = subprocess.run(['./capcat', 'list', 'bundles'], capture_output=True, text=True)
    assert 'tech:' in result.stdout.lower()
    assert 'news:' in result.stdout.lower()
    assert 'Sources:' in result.stdout
```

**Integration Tests:**
- Verify source count matches registry
- Verify categories match source configs
- Verify bundle sources match bundles.yml

**Regression Prevention:**
- Add to CI/CD pipeline
- Require passing before merge
- Document testing requirements

---

## BUG-002: config Command Not Implemented

**Severity:** MEDIUM
**Impact:** User-facing feature
**User Impact:** MEDIUM - Feature advertised but unavailable
**Documentation Impact:** LOW - Minimal documentation

### Description

`./capcat config` command prints "not yet implemented" message.

### Evidence

**Code Location:** `cli.py:895-898`
```python
elif args.command == 'config':
    # ... (config logic)
    print("Config command not yet implemented.")
    sys.exit(0)
```

**Test Result:**
```bash
$ ./capcat config
Config command not yet implemented.
INFO: Using virtual environment Python
```

**Visibility:** Command appears in `./capcat --help` as available

### Fix Options

#### Option A: Implement Config Management

**Features:**
- View current config
- Set config values
- Validate config
- Show config file location

**Effort:** 4-6 hours

#### Option B: Remove Command

**Effort:** 15 minutes
**Change:** Remove from argparse, update help

### Recommendation

**Option B: Remove Command**

**Rationale:**
- Minimal documentation
- Config managed via capcat.yml file
- Not critical feature
- Low user impact
- Reduces maintenance burden

---

## Systemic Issue: Incomplete Refactoring Pattern

**Severity:** CRITICAL
**Impact:** Unknown number of features
**Pattern Recognition:** HIGH confidence

### Pattern Identified

**Indicators:**
1. Stub functions with comment `# ... (implementation remains the same)`
2. Working implementation exists elsewhere (interactive.py)
3. Documentation describes full functionality
4. No connection between stub and implementation

### Potential Affected Features

**Requires Phase 2 Testing:**
- All CLI commands (single, fetch, bundle, add-source, remove-source, generate-config)
- Interactive mode workflows
- HTML generation
- Template system
- Source management features
- Validation engine
- Performance monitoring

### Audit Strategy

**Phase 2 Requirements:**
1. Test EVERY documented CLI command functionally
2. Verify interactive mode features work
3. Cross-reference all documentation claims
4. Create feature availability matrix

### Prevention

**Process Requirements:**
1. No code merges without functional tests
2. Documentation updates required with code changes
3. CLI-Interactive feature parity documented
4. Automated testing for all user-facing features

---

## Impact Assessment

### User Impact

**Immediate:**
- Cannot discover sources via CLI
- Must use interactive mode or read documentation
- Breaking documented workflows
- Trust erosion

**Long-term:**
- Documentation credibility damaged
- Hesitation to use documented features
- Support burden (bug reports)

### Developer Impact

**Immediate:**
- Unknown scope of affected features
- Extensive testing required
- Documentation audit required

**Long-term:**
- Technical debt accumulation
- Maintenance burden
- Code quality concerns

### Documentation Impact

**Files Affected:**
- docs/quick-start.md
- docs/tutorials/01-cli-commands-exhaustive.md
- docs/interactive-mode.md
- docs/architecture.md
- CLAUDE.md
- README.md (if exists)

**Update Effort:** 2-3 hours minimum

---

## Action Items

### Immediate (Today)

1. ✅ Document critical bugs (this file)
2. 🔄 Implement `list_sources_and_bundles()` CLI version
3. ⏸️ Remove or document `config` command
4. ⏸️ Update CLAUDE.md with accurate commands

### Short-term (This Week)

1. ⏸️ Complete Phase 2 functional testing
2. ⏸️ Create BUGS-MINOR.md for non-critical issues
3. ⏸️ Update all affected documentation
4. ⏸️ Create feature availability matrix

### Medium-term (This Month)

1. ⏸️ Implement automated test suite
2. ⏸️ Add CI/CD testing requirements
3. ⏸️ Code audit for similar patterns
4. ⏸️ Establish code review checklist

---

**Status:** Phase 1 Complete, Fixes Pending
**Next Review:** After BUG-001 fix implementation
**Owner:** TBD
