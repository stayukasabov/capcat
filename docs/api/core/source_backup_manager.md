# core.source_system.source_backup_manager

**File:** `Application/core/source_system/source_backup_manager.py`

## Description

Backup and restore functionality for source configurations.
Enables undo capability and safe removal operations.

## Classes

### BackupMetadata

Metadata about a backup operation.


### SourceBackupManager

Manages backup and restore of source configurations.
Supports undo functionality and safe deletions.

#### Methods

##### __init__

```python
def __init__(self, backup_base_dir: Optional[Path] = None)
```

Initialize backup manager.

Args:
    backup_base_dir: Base directory for backups (default: .capcat_backups)

**Parameters:**

- `self`
- `backup_base_dir` (Optional[Path]) *optional*

##### create_backup

```python
def create_backup(self, source_ids: List[str], config_paths: List[Path], bundles_path: Path) -> BackupMetadata
```

Create backup of sources before removal.

Args:
    source_ids: List of source IDs being backed up
    config_paths: Paths to source config files
    bundles_path: Path to bundles.yml file

Returns:
    BackupMetadata with backup information

**Parameters:**

- `self`
- `source_ids` (List[str])
- `config_paths` (List[Path])
- `bundles_path` (Path)

**Returns:** BackupMetadata

##### restore_backup

```python
def restore_backup(self, backup_id: str, config_base_path: Path, bundles_path: Path) -> List[str]
```

Restore sources from a backup.

Args:
    backup_id: ID of backup to restore
    config_base_path: Base path for config files
    bundles_path: Path to bundles.yml file

Returns:
    List of restored source IDs

**Parameters:**

- `self`
- `backup_id` (str)
- `config_base_path` (Path)
- `bundles_path` (Path)

**Returns:** List[str]

##### list_backups

```python
def list_backups(self) -> List[BackupMetadata]
```

List all available backups.

Returns:
    List of BackupMetadata objects

**Parameters:**

- `self`

**Returns:** List[BackupMetadata]

##### delete_backup

```python
def delete_backup(self, backup_id: str) -> None
```

Delete a backup.

Args:
    backup_id: ID of backup to delete

**Parameters:**

- `self`
- `backup_id` (str)

**Returns:** None

##### cleanup_old_backups

```python
def cleanup_old_backups(self, keep_count: int = 10) -> int
```

Delete old backups, keeping only the most recent ones.

Args:
    keep_count: Number of recent backups to keep

Returns:
    Number of backups deleted

**Parameters:**

- `self`
- `keep_count` (int) *optional*

**Returns:** int

##### _save_metadata

```python
def _save_metadata(self, metadata: BackupMetadata) -> None
```

Save backup metadata to JSON file.

**Parameters:**

- `self`
- `metadata` (BackupMetadata)

**Returns:** None

##### _load_metadata

```python
def _load_metadata(self, backup_dir: Path) -> BackupMetadata
```

Load backup metadata from JSON file.

**Parameters:**

- `self`
- `backup_dir` (Path)

**Returns:** BackupMetadata


### BackupStrategy

Protocol for different backup strategies.

#### Methods

##### should_backup

```python
def should_backup(self, source_ids: List[str]) -> bool
```

Determine if backup should be created.

**Parameters:**

- `self`
- `source_ids` (List[str])

**Returns:** bool


### AlwaysBackupStrategy

**Inherits from:** BackupStrategy

Always create backups.

#### Methods

##### should_backup

```python
def should_backup(self, source_ids: List[str]) -> bool
```

**Parameters:**

- `self`
- `source_ids` (List[str])

**Returns:** bool


### ConditionalBackupStrategy

**Inherits from:** BackupStrategy

Backup only if conditions are met.

#### Methods

##### __init__

```python
def __init__(self, min_sources: int = 1)
```

**Parameters:**

- `self`
- `min_sources` (int) *optional*

##### should_backup

```python
def should_backup(self, source_ids: List[str]) -> bool
```

**Parameters:**

- `self`
- `source_ids` (List[str])

**Returns:** bool


### NoBackupStrategy

**Inherits from:** BackupStrategy

Never create backups (for testing or forced removal).

#### Methods

##### should_backup

```python
def should_backup(self, source_ids: List[str]) -> bool
```

**Parameters:**

- `self`
- `source_ids` (List[str])

**Returns:** bool


