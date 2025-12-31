# Advanced Features: Enhanced Remove-Source

## Overview

The remove-source command now includes six powerful enhancements for safer, smarter source management:

1. **Dry-Run Mode** - Preview changes before executing
2. **Automatic Backups** - Safe removal with undo capability
3. **Usage Analytics** - Data-driven removal decisions
4. **Batch Removal** - Remove multiple sources from file
5. **Undo/Restore** - Restore previously removed sources
6. **Integration** - Analytics integrated into workflow

## Feature Details

### 1. Dry-Run Mode

Preview exactly what will be removed without making any changes.

**Usage:**
```bash
./capcat remove-source --dry-run
```

**Output:**
```
--- Source Usage Analytics ---
Most Active Sources:
  Hacker News: 45 fetches, daily
  BBC News: 12 fetches, weekly

--- Removal Summary ---
  Source: InfoQ (iq)
  Config: .../configs/iq.yml
  Bundles: tech

[DRY RUN] No changes made.

Actions that would be performed:
  InfoQ (iq):
    - Delete: .../configs/iq.yml
    - Remove from bundles: tech

To execute, run without --dry-run flag.
```

**Benefits:**
- Verify correct sources selected
- See bundle impact before removal
- No risk of accidental deletion
- Perfect for learning the tool

### 2. Automatic Backups

Every removal creates a timestamped backup for safety.

**Default Behavior:**
```bash
./capcat remove-source
# Automatic backup created
```

**Skip Backup** (not recommended):
```bash
./capcat remove-source --no-backup
```

**Backup Structure:**
```
.capcat_backups/
└── removal_20250118_143022/
    ├── metadata.json
    ├── configs/
    │   ├── hn.yml
    │   └── bbc.yml
    └── bundles.yml
```

**Metadata Example:**
```json
{
  "backup_id": "removal_20250118_143022",
  "timestamp": "2025-01-18T14:30:22.123456",
  "sources": ["hn", "bbc"],
  "bundle_backup": "/path/to/bundles.yml"
}
```

**Automatic Cleanup:**
- Keeps 10 most recent backups by default
- Older backups automatically pruned
- Manual cleanup available

### 3. Usage Analytics

Make informed decisions based on actual usage patterns.

**Tracked Metrics:**
- Total fetches
- Success/failure rates
- Last used date
- Fetch frequency (daily/weekly/monthly/rarely/never)
- Articles fetched count
- Average articles per fetch

**Analytics Display:**
```
--- Source Usage Analytics ---

Most Active Sources:
  Hacker News: 45 fetches, daily
  BBC News: 12 fetches, weekly
  InfoQ: 3 fetches, monthly

Unused sources (2): old_source1, old_source2

--- Selected Sources Analytics ---

InfoQ (iq)
  Fetches: 3, Frequency: monthly
  [CONSIDER] Rarely used

BBC News (bbc)
  Fetches: 12, Frequency: weekly
  [ACTIVE] Regular use
```

**Recommendation Categories:**
- `[RECOMMENDED]` - Never used or 90+ days inactive
- `[WARNING]` - Low success rate (<30%)
- `[CONSIDER]` - Rarely used
- `[ACTIVE]` - Regular use

**Skip Analytics:**
```bash
./capcat remove-source --no-analytics
```

**Analytics File Location:**
```
.capcat_analytics/usage.json
```

### 4. Batch Removal

Remove multiple sources from a file list.

**Create Batch File:**
```bash
cat > sources_to_remove.txt <<EOF
# Sources to remove
hn
bbc
old_source1
old_source2
# Lines starting with # are ignored
EOF
```

**Execute Batch Removal:**
```bash
./capcat remove-source --batch sources_to_remove.txt
```

**Output:**
```
Batch removal: 4 sources from sources_to_remove.txt

--- Removal Summary ---
  Source: Hacker News (hn)
  Config: .../hn.yml
  Bundles: tech, techpro

  Source: BBC News (bbc)
  Config: .../bbc.yml
  Bundles: news

  Remove 4 source(s)? This cannot be undone. Yes

Batch removal complete: 4 sources removed.
Backup: removal_20250118_143500
```

**Batch + Dry-Run:**
```bash
./capcat remove-source --batch sources.txt --dry-run
```

**Force Mode** (skip confirmations):
```bash
./capcat remove-source --batch sources.txt --force
```

### 5. Undo/Restore Functionality

Restore previously removed sources from backups.

**Undo Last Removal:**
```bash
./capcat remove-source --undo
```

**Undo Specific Backup:**
```bash
./capcat remove-source --undo removal_20250118_143022
```

**Interactive Selection:**
```
--- Restore Sources from Backup ---

  Select backup to restore:
> removal_20250118_143022 - 2 sources - 2025-01-18 14:30:22
  removal_20250118_100500 - 1 sources - 2025-01-18 10:05:00

Restoring backup: removal_20250118_143022
Timestamp: 2025-01-18T14:30:22.123456
Sources: hn, bbc

  Proceed with restore? No

Restore cancelled.
```

**After Restore:**
- Config files restored to original location
- Bundles.yml restored
- Registry automatically refreshed
- Sources immediately available

### 6. Integration with Analytics

Analytics are seamlessly integrated into the workflow.

**Before Selection:**
Shows most active sources and unused sources to help decision-making.

**After Selection:**
Shows detailed stats for each selected source with recommendations.

**Continuous Tracking:**
Analytics persist across sessions for historical insights.

## Command Reference

### Basic Commands
```bash
# Interactive removal
./capcat remove-source

# Preview changes
./capcat remove-source --dry-run

# Remove without backup
./capcat remove-source --no-backup

# Remove without analytics
./capcat remove-source --no-analytics

# Force (skip confirmations)
./capcat remove-source --force
```

### Batch Operations
```bash
# Batch removal
./capcat remove-source --batch sources.txt

# Batch with dry-run
./capcat remove-source --batch sources.txt --dry-run

# Batch with force
./capcat remove-source --batch sources.txt --force
```

### Undo Operations
```bash
# Undo last removal
./capcat remove-source --undo

# Undo specific backup
./capcat remove-source --undo removal_20250118_143022
```

### Combined Flags
```bash
# Dry-run without analytics
./capcat remove-source --dry-run --no-analytics

# Batch removal without backup (not recommended)
./capcat remove-source --batch sources.txt --no-backup

# Force batch removal
./capcat remove-source --batch sources.txt --force
```

## Use Cases

### Scenario 1: Clean Up Unused Sources

```bash
# Check what's unused (dry-run)
./capcat remove-source --dry-run

# Analytics will show:
# - Unused sources (never used or 30+ days)
# - Low performers (poor success rates)

# Selectively remove based on data
./capcat remove-source
```

### Scenario 2: Bulk Cleanup

```bash
# Create list of sources to remove
echo "old_source1
old_source2
old_source3" > cleanup.txt

# Preview the cleanup
./capcat remove-source --batch cleanup.txt --dry-run

# Execute cleanup
./capcat remove-source --batch cleanup.txt
```

### Scenario 3: Safe Experimentation

```bash
# Remove a source (backup created automatically)
./capcat remove-source

# Try the system without it

# Changed your mind? Undo it!
./capcat remove-source --undo
```

### Scenario 4: Production Migration

```bash
# List sources to migrate off old server
cat > migrate.txt <<EOF
legacy_source1
legacy_source2
legacy_source3
EOF

# Preview impact
./capcat remove-source --batch migrate.txt --dry-run

# Check analytics for usage patterns
# Shows which sources are still active

# Execute with force for automation
./capcat remove-source --batch migrate.txt --force
```

## File Locations

### Backups
```
.capcat_backups/
└── removal_YYYYMMDD_HHMMSS/
    ├── metadata.json
    ├── configs/
    └── bundles.yml
```

### Analytics
```
.capcat_analytics/
└── usage.json
```

### Batch Files
```
Any text file, one source ID per line
# Comments allowed
```

## Best Practices

### Always Use Dry-Run First
```bash
./capcat remove-source --dry-run
```
Verify selections before executing.

### Review Analytics
Pay attention to recommendation tags:
- `[RECOMMENDED]` - Safe to remove
- `[WARNING]` - Investigate first
- `[ACTIVE]` - Keep unless necessary

### Keep Backups Enabled
Only use `--no-backup` when absolutely certain.

### Use Batch Files for Documentation
Batch files serve as documentation of why sources were removed:
```bash
cat > deprecated_sources.txt <<EOF
# Deprecated sources - replaced 2025-01-18
# Reason: Moving to new API-based sources
old_api_source1
old_api_source2
EOF
```

### Test Restore Procedure
Periodically verify undo functionality works:
```bash
# Remove a test source
./capcat remove-source  # Remove test_source

# Verify it's gone
./capcat list sources

# Restore it
./capcat remove-source --undo

# Verify it's back
./capcat list sources
```

## Troubleshooting

### Backup Not Created
**Problem:** No backup message shown
**Solution:** Check `.capcat_backups/` directory exists and is writable

### Analytics Not Showing
**Problem:** No usage statistics displayed
**Solution:** Analytics require usage history. New installations won't have data yet.

### Undo Fails
**Problem:** Cannot restore backup
**Solution:** Verify backup exists in `.capcat_backups/` directory

### Batch File Errors
**Problem:** Sources not found in batch file
**Solution:** Verify source IDs are correct with `./capcat list sources`

## Performance Considerations

### Analytics Overhead
- Minimal: JSON file I/O only
- No impact on fetch operations
- File size: ~1KB per source

### Backup Space
- Each backup: ~few KB per source
- Auto-cleanup keeps 10 most recent
- Manual cleanup available

### Restore Speed
- Instant for small configs
- Scales linearly with file count

## Security Notes

### Backup Files
- Contain sensitive source configurations
- Stored in `.capcat_backups/` (git-ignored)
- No credentials stored (only configs)

### Analytics Data
- Usage metrics only
- No article content
- No personal information

### File Permissions
- Backups inherit source directory permissions
- Analytics file created with user permissions