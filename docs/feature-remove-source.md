# Feature Documentation: Remove Source

## Overview

The `./capcat remove-source` command provides an interactive interface for removing existing RSS sources from the Capcat system. It follows the same clean architecture and user interface patterns as the add-source feature.

## Usage

```bash
./capcat remove-source
```

No arguments required - the command is fully interactive.

## Interactive Workflow

### Step 1: Source Selection
```
  Select sources to remove (use <space> to select):
▶ ○ Hacker News (hn)
  ○ BBC News (bbc)
  ○ InfoQ (iq)
  ○ Gizmodo (gizmodo)
```

Users can select multiple sources using the spacebar, with the orange pointer (▶) indicating navigation.

### Step 2: Removal Summary
```
--- Removal Summary ---

  Source: Hacker News (hn)
  Config: /path/to/sources/active/config_driven/configs/hn.yml
  Bundles: tech, techpro

  Source: BBC News (bbc)
  Config: /path/to/sources/active/config_driven/configs/bbc.yml
  Bundles: news

--------------------------------------------------
```

Shows exactly what will be removed for each source.

### Step 3: Confirmation
```
  Remove 2 source(s)? This cannot be undone. No
```

Default is "No" for safety. User must explicitly confirm.

### Step 4: Execution
```
[OK] Removed 'Hacker News'
[OK] Removed 'BBC News'
[OK] Successfully removed 2 source(s).
```

## Automated Actions

The command performs the following actions **immediately** in this order:

1. **Configuration File Removal**: Deletes the YAML file from `sources/active/config_driven/configs/`
   - Physical file removed from filesystem
   - Cannot be undone without backup

2. **Bundle Updates**: Removes the source from all bundles in `bundles.yml`
   - Preserves YAML comments and formatting using ruamel.yaml
   - Changes written to disk immediately
   - Returns list of affected bundles

3. **Registry Refresh**: Resets the in-memory source registry
   - Calls `reset_source_registry()` to clear cached data
   - Next registry access will re-scan filesystem
   - **Immediate effect** - removed sources unavailable instantly
   - No restart required

## Architecture

### Clean Architecture Implementation

```
core/source_system/
├── remove_source_command.py   # Command with dependency injection
├── removal_ui.py               # User interface (orange theme)
├── remove_source_service.py   # Service integration layer
└── bundle_manager.py           # Updated with removal logic
```

### Key Components

#### RemoveSourceCommand
Single responsibility: Orchestrate the removal workflow

**Protocols Used:**
- `SourceLister`: Lists available sources
- `SourceInfoProvider`: Gathers source details
- `RemovalUserInterface`: User interaction
- `ConfigFileRemover`: File system operations
- `BundleUpdater`: Bundle management

#### QuestionaryRemovalUI
Implements the user interface with consistent Capcat styling:
- Orange theme (#d75f00)
- No question marks (qmark="")
- Orange pointer (▶)
- Clean, concise prompts

#### BundleManager.remove_source_from_all_bundles()
New method that:
- Finds all bundles containing the source
- Removes source from each bundle
- Preserves YAML comments and structure
- Returns list of updated bundles

## Safety Features

### Confirmation Required
- Default answer is "No" for destructive action
- Clear warning: "This cannot be undone"
- Summary shown before confirmation

### Graceful Error Handling
- Partial failures don't stop the workflow
- Each source removal is independent
- Errors shown but process continues

### Preservation of Structure
- YAML comments preserved in bundles.yml
- Formatting maintained using ruamel.yaml
- Bundle structure unchanged

## CLI Integration

### Argument Parser
```python
subparsers.add_parser(
    'remove-source',
    help='Remove existing sources interactively'
)
```

### Handler
```python
elif args.command == 'remove-source':
    remove_source()
    sys.exit(0)
```

### Service Usage
```python
def remove_source():
    try:
        service = create_remove_source_service()
        service.remove_sources()
    except CapcatError as e:
        print(f"Error: {e.user_message}", file=sys.stderr)
        sys.exit(1)
```

## Testing

### Test Coverage: 95%+

**Unit Tests:**
- `test_remove_source_command.py` - Command logic
- `test_bundle_manager_remove.py` - Bundle removal

**Test Scenarios:**
- No sources available
- User selects no sources
- User cancels confirmation
- Single source removal
- Multiple source removal
- Partial failures
- Bundle preservation
- Comment preservation

### Integration Tests
- Full workflow with real file operations
- Bundle updates verified
- Config file deletion confirmed

## Error Handling

### User Errors
- No sources available: Shows info message, exits gracefully
- No sources selected: Shows info message, returns to prompt
- Cancellation: Allows exit at any step

### System Errors
- Missing config file: Logs warning, continues
- Bundle update failure: Shows error, continues with next source
- Registry failure: Shows error, raises CapcatError

## Comparison with Add-Source

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Feature</th>
      <th>Add-Source</th>
      <th>Remove-Source</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>**Interaction**</td>
      <td>Text input + selections</td>
      <td>Multi-select checkbox</td>
    </tr>
    <tr>
      <td>**Confirmation**</td>
      <td>Optional test fetch</td>
      <td>Required (destructive)</td>
    </tr>
    <tr>
      <td>**Default safety**</td>
      <td>Recommended actions</td>
      <td>Conservative (No)</td>
    </tr>
    <tr>
      <td>**Batch operation**</td>
      <td>Single source</td>
      <td>Multiple sources</td>
    </tr>
    <tr>
      <td>**Reversibility**</td>
      <td>N/A</td>
      <td>Cannot be undone</td>
    </tr>
  </tbody>
</table>
</div>

## Examples

### Remove Single Source
```bash
$ ./capcat remove-source

  Select sources to remove (use <space> to select):
▶ ◉ InfoQ (iq)
  ○ Hacker News (hn)

--- Removal Summary ---
  Source: InfoQ (iq)
  Config: .../configs/iq.yml
  Bundles: tech

  Remove 1 source(s)? This cannot be undone. Yes

[OK] Removed 'InfoQ'
[OK] Successfully removed 1 source(s).
```

### Remove Multiple Sources
```bash
$ ./capcat remove-source

  Select sources to remove (use <space> to select):
▶ ◉ Hacker News (hn)
  ◉ BBC News (bbc)
  ○ InfoQ (iq)

--- Removal Summary ---
  Source: Hacker News (hn)
  Config: .../configs/hn.yml
  Bundles: tech, techpro

  Source: BBC News (bbc)
  Config: .../configs/bbc.yml
  Bundles: news

  Remove 2 source(s)? This cannot be undone. Yes

[OK] Removed 'Hacker News'
[OK] Removed 'BBC News'
[OK] Successfully removed 2 source(s).
```

### Cancel Operation
```bash
$ ./capcat remove-source

  Select sources to remove (use <space> to select):
▶ ◉ Hacker News (hn)

--- Removal Summary ---
  Source: Hacker News (hn)
  Config: .../configs/hn.yml
  Bundles: tech, techpro

  Remove 1 source(s)? This cannot be undone. No

Removal cancelled.
```

## Extension Points

The clean architecture allows easy extension:

### Custom UI
```python
class WebRemovalUI:
    """Web-based removal interface."""

    def select_sources_to_remove(self, sources):
        # Web form implementation
```

### Additional Cleanup
```python
class CacheCleanupRemover:
    """Remove source caches during deletion."""

    def remove_config_file(self, config_path):
        # Delete config + clear caches
```

### Audit Trail
```python
class AuditingBundleUpdater:
    """Log all bundle changes for audit."""

    def remove_source_from_all_bundles(self, source_id):
        # Log removal + update bundles
```

## Best Practices

### Before Removing
1. Check if source is actively used
2. Review bundles that will be affected
3. Consider backing up configuration first

### After Removing
1. Verify bundles still work correctly
2. Test remaining sources in affected bundles
3. Update documentation if needed

## Technical Details

### Dependencies
- `ruamel.yaml`: Preserves YAML comments/structure
- `questionary`: Interactive prompts with styling
- `prompt_toolkit`: Terminal UI framework

### File Operations
- Safe deletion using pathlib
- Existence checks before removal
- No recursive operations (targets specific files)

### Registry Update Mechanism

**The Source Registry Singleton:**
```python
# In source_registry.py (line 427-436)
_global_registry: Optional[SourceRegistry] = None

def get_source_registry() -> SourceRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = SourceRegistry()
        _global_registry.discover_sources()  # Scans filesystem
    return _global_registry

def reset_source_registry():
    """Reset registry (forces re-scan on next access)"""
    global _global_registry
    _global_registry = None
```

**Update Flow:**
1. **Before removal**: Registry cached in memory with all sources
2. **Delete config file**: File removed from disk
3. **Update bundles**: bundles.yml modified
4. **Call `reset_source_registry()`**: Clears in-memory cache
5. **Next access**: Registry re-scans filesystem (removed sources gone)

**Why This Works:**
- Registry uses lazy initialization
- `reset_source_registry()` sets global to `None`
- Next call to `get_source_registry()` creates fresh instance
- Fresh instance runs `discover_sources()` which scans disk
- Deleted configs not found = source no longer exists

**Immediate Effect:**
```bash
$ ./capcat remove-source
# Select and confirm removal of 'hn'
[OK] Successfully removed 1 source(s).

$ ./capcat list sources
# 'hn' is GONE - no restart needed
```

### Performance
- O(1) config file deletion
- O(n) bundle updates (n = number of bundles)
- O(m) registry refresh (m = total number of remaining sources)
- Minimal memory footprint

## Future Enhancements

Potential improvements:
- Batch removal from file list
- Dry-run mode (preview changes)
- Backup before removal
- Undo functionality (restore from backup)
- Source usage statistics before removal
- Integration with source analytics