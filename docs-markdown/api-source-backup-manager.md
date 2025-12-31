# SourceBackupManager API Documentation

## Overview

The `SourceBackupManager` provides automated backup and restore functionality for source configurations, enabling safe removal operations with undo capability.

## Module Location

```python
from core.source_system.source_backup_manager import (
    SourceBackupManager,
    BackupMetadata,
    AlwaysBackupStrategy,
    NoBackupStrategy,
    ConditionalBackupStrategy
)
```

## Classes

### BackupMetadata

Dataclass containing metadata about a backup operation.

**Attributes:**
- `backup_id: str` - Unique identifier (format: removal_YYYYMMDD_HHMMSS_microseconds)
- `timestamp: str` - ISO format timestamp of backup creation
- `sources: List[str]` - List of source IDs included in backup
- `backup_dir: Path` - Path to backup directory
- `bundle_backup: Optional[Path]` - Path to backed up bundles.yml (if exists)

**Example:**
```python
metadata = BackupMetadata(
    backup_id="removal_20250118_143027_123456",
    timestamp="2025-01-18T14:30:27.123456",
    sources=["hn", "bbc"],
    backup_dir=Path("/path/to/.capcat_backups/removal_20250118_143027_123456"),
    bundle_backup=Path("/path/to/.capcat_backups/removal_20250118_143027_123456/bundles.yml")
)
```

---

### SourceBackupManager

Main class for managing source backups.

#### Constructor

```python
def __init__(self, backup_base_dir: Optional[Path] = None)
```

**Parameters:**
- `backup_base_dir` - Base directory for backups (default: ../.capcat_backups)

**Example:**
```python
# Use default location
manager = SourceBackupManager()

# Custom location
manager = SourceBackupManager(Path("/custom/backup/path"))
```

#### Methods

##### create_backup()

Create backup of sources before removal.

```python
def create_backup(
    self,
    source_ids: List[str],
    config_paths: List[Path],
    bundles_path: Path
) -> BackupMetadata
```

**Parameters:**
- `source_ids` - List of source IDs being backed up
- `config_paths` - Paths to source config files
- `bundles_path` - Path to bundles.yml file

**Returns:**
- `BackupMetadata` with backup information

**Raises:**
- `CapcatError` - If backup creation fails

**Example:**
```python
metadata = manager.create_backup(
    source_ids=["hn", "bbc"],
    config_paths=[
        Path("sources/active/config_driven/configs/hn.yml"),
        Path("sources/active/config_driven/configs/bbc.yml")
    ],
    bundles_path=Path("sources/active/bundles.yml")
)

print(f"Backup created: {metadata.backup_id}")
# Output: Backup created: removal_20250118_143027_123456
```

##### restore_backup()

Restore sources from a backup.

```python
def restore_backup(
    self,
    backup_id: str,
    config_base_path: Path,
    bundles_path: Path
) -> List[str]
```

**Parameters:**
- `backup_id` - ID of backup to restore
- `config_base_path` - Base path for config files
- `bundles_path` - Path to bundles.yml file

**Returns:**
- List of restored source IDs

**Raises:**
- `CapcatError` - If backup not found or restore fails

**Example:**
```python
restored = manager.restore_backup(
    backup_id="removal_20250118_143027_123456",
    config_base_path=Path("sources/active/config_driven/configs"),
    bundles_path=Path("sources/active/bundles.yml")
)

print(f"Restored sources: {', '.join(restored)}")
# Output: Restored sources: hn, bbc
```

##### list_backups()

List all available backups.

```python
def list_backups(self) -> List[BackupMetadata]
```

**Returns:**
- List of BackupMetadata objects, sorted by timestamp

**Example:**
```python
backups = manager.list_backups()

for backup in backups:
    print(f"{backup.backup_id}: {len(backup.sources)} sources")
    print(f"  Created: {backup.timestamp}")
    print(f"  Sources: {', '.join(backup.sources)}")
```

##### delete_backup()

Delete a specific backup.

```python
def delete_backup(self, backup_id: str) -> None
```

**Parameters:**
- `backup_id` - ID of backup to delete

**Raises:**
- `CapcatError` - If backup not found or deletion fails

**Example:**
```python
manager.delete_backup("removal_20250118_143027_123456")
```

##### cleanup_old_backups()

Delete old backups, keeping only the most recent ones.

```python
def cleanup_old_backups(self, keep_count: int = 10) -> int
```

**Parameters:**
- `keep_count` - Number of recent backups to keep (default: 10)

**Returns:**
- Number of backups deleted

**Example:**
```python
deleted = manager.cleanup_old_backups(keep_count=5)
print(f"Deleted {deleted} old backups")
# Output: Deleted 3 old backups
```

---

### Backup Strategies

Protocol for implementing different backup strategies.

#### BackupStrategy

Base protocol.

```python
class BackupStrategy:
    def should_backup(self, source_ids: List[str]) -> bool:
        ...
```

#### AlwaysBackupStrategy

Always create backups (recommended for production).

```python
strategy = AlwaysBackupStrategy()
if strategy.should_backup(["hn", "bbc"]):
    # Create backup
    pass
```

#### NoBackupStrategy

Never create backups (for testing or forced removal).

```python
strategy = NoBackupStrategy()
if strategy.should_backup(["hn", "bbc"]):
    # Will never execute
    pass
```

#### ConditionalBackupStrategy

Backup only if conditions are met.

```python
strategy = ConditionalBackupStrategy(min_sources=2)
if strategy.should_backup(["hn"]):  # False (only 1 source)
    pass
if strategy.should_backup(["hn", "bbc"]):  # True (2 sources)
    pass
```

## Backup Structure

Backups are stored with the following structure:

```
.capcat_backups/
└── removal_20250118_143027_123456/
    ├── metadata.json           # Backup metadata
    ├── bundles.yml            # Backed up bundles file
    └── configs/               # Backed up config files
        ├── hn.yml
        └── bbc.yml
```

### metadata.json Format

```json
{
  "backup_id": "removal_20250118_143027_123456",
  "timestamp": "2025-01-18T14:30:27.123456",
  "sources": ["hn", "bbc"],
  "bundle_backup": "/path/to/bundles.yml"
}
```

## Usage Examples

### Complete Backup/Restore Workflow

```python
from pathlib import Path
from core.source_system.source_backup_manager import SourceBackupManager

# Initialize manager
manager = SourceBackupManager()

# Create backup before removal
metadata = manager.create_backup(
    source_ids=["hn", "bbc"],
    config_paths=[
        Path("sources/active/config_driven/configs/hn.yml"),
        Path("sources/active/config_driven/configs/bbc.yml")
    ],
    bundles_path=Path("sources/active/bundles.yml")
)

print(f"Backup created: {metadata.backup_id}")

# ... perform removal operations ...

# Restore if needed
restored_sources = manager.restore_backup(
    backup_id=metadata.backup_id,
    config_base_path=Path("sources/active/config_driven/configs"),
    bundles_path=Path("sources/active/bundles.yml")
)

print(f"Restored: {restored_sources}")
```

### Listing and Managing Backups

```python
# List all backups
backups = manager.list_backups()

print(f"Total backups: {len(backups)}")

# Show details
for backup in backups:
    age_days = (datetime.now() - datetime.fromisoformat(backup.timestamp)).days
    print(f"{backup.backup_id}: {len(backup.sources)} sources, {age_days} days old")

# Clean up old backups
deleted = manager.cleanup_old_backups(keep_count=5)
print(f"Cleaned up {deleted} old backups")
```

### Conditional Backup

```python
from core.source_system.source_backup_manager import ConditionalBackupStrategy

strategy = ConditionalBackupStrategy(min_sources=2)

sources_to_remove = ["hn", "bbc"]

if strategy.should_backup(sources_to_remove):
    metadata = manager.create_backup(
        source_ids=sources_to_remove,
        config_paths=[...],
        bundles_path=Path("...")
    )
    print(f"Backup created: {metadata.backup_id}")
else:
    print("Skipping backup (not enough sources)")
```

## Error Handling

```python
from core.exceptions import CapcatError

try:
    metadata = manager.create_backup(
        source_ids=["hn"],
        config_paths=[Path("nonexistent.yml")],
        bundles_path=Path("bundles.yml")
    )
except CapcatError as e:
    print(f"Backup failed: {e}")
    # Handle error appropriately

try:
    restored = manager.restore_backup(
        backup_id="nonexistent_backup",
        config_base_path=Path("configs"),
        bundles_path=Path("bundles.yml")
    )
except CapcatError as e:
    print(f"Restore failed: {e}")
    # Backup not found
```

## Best Practices

1. **Always Create Backups** - Use `AlwaysBackupStrategy` in production
2. **Regular Cleanup** - Run `cleanup_old_backups()` periodically
3. **Verify Before Removal** - Check backup success before deleting sources
4. **Handle Missing Files** - Backup succeeds even if config files don't exist
5. **Store Backup IDs** - Save backup_id for potential undo operations

## Thread Safety

The `SourceBackupManager` is not thread-safe. For concurrent access:
- Use file locking mechanisms
- Implement single-writer pattern
- Queue backup operations

## Performance Considerations

- Backup creation is I/O bound (file copy operations)
- Average backup time: ~10-50ms depending on file sizes
- List operations read metadata files sequentially
- Cleanup operations use bulk deletion for efficiency

## Integration with Remove Command

```python
from core.source_system.remove_source_command import RemoveSourceCommand
from core.source_system.source_backup_manager import SourceBackupManager

# Create backup manager
backup_manager = SourceBackupManager()

# Backup before removal
metadata = backup_manager.create_backup(
    source_ids=selected_sources,
    config_paths=config_paths,
    bundles_path=bundles_path
)

# Perform removal
command.execute()

# Undo if needed
if need_undo:
    backup_manager.restore_backup(
        backup_id=metadata.backup_id,
        config_base_path=config_base_path,
        bundles_path=bundles_path
    )
```

## Testing

See `tests/test_source_backup_manager.py` for comprehensive test examples.

## See Also

- [Source Analytics API](api-source-analytics.html)
- [Remove Source Command API](api-remove-source-command.html)
- [Testing Guide](TESTING-REMOVE-SOURCE.html)
