# core.source_system.enhanced_remove_command

**File:** `Application/core/source_system/enhanced_remove_command.py`

## Description

Enhanced remove-source command with advanced features:
- Dry-run mode
- Automatic backups
- Usage analytics
- Batch removal from file
- Undo/restore functionality

## Classes

### RemovalOptions

Options for source removal.


### EnhancedRemoveCommand

Enhanced removal command with analytics, backups, and dry-run support.
Extends base RemoveSourceCommand with advanced features.

#### Methods

##### __init__

```python
def __init__(self, base_command: RemoveSourceCommand, backup_manager: SourceBackupManager, analytics: SourceAnalytics, ui: RemovalUserInterface, logger: Optional[any] = None)
```

**Parameters:**

- `self`
- `base_command` (RemoveSourceCommand)
- `backup_manager` (SourceBackupManager)
- `analytics` (SourceAnalytics)
- `ui` (RemovalUserInterface)
- `logger` (Optional[any]) *optional*

##### execute_with_options

```python
def execute_with_options(self, options: RemovalOptions) -> None
```

Execute removal with enhanced options.

Args:
    options: RemovalOptions specifying behavior

**Parameters:**

- `self`
- `options` (RemovalOptions)

**Returns:** None

##### execute_undo

```python
def execute_undo(self, backup_id: Optional[str] = None) -> None
```

Undo a previous removal by restoring from backup.

Args:
    backup_id: Specific backup to restore (None = most recent)

**Parameters:**

- `self`
- `backup_id` (Optional[str]) *optional*

**Returns:** None

##### _execute_enhanced_removal

```python
def _execute_enhanced_removal(self, options: RemovalOptions) -> None
```

Execute standard interactive removal with enhancements.

**Parameters:**

- `self`
- `options` (RemovalOptions)

**Returns:** None

⚠️ **High complexity:** 17

##### _execute_batch_removal

```python
def _execute_batch_removal(self, options: RemovalOptions) -> None
```

Execute batch removal from file.

**Parameters:**

- `self`
- `options` (RemovalOptions)

**Returns:** None

⚠️ **High complexity:** 14

##### _create_backup

```python
def _create_backup(self, sources_info: List[SourceRemovalInfo], output_directories: Optional[List[Path]] = None) -> BackupMetadata
```

Create backup before removal.

Args:
    sources_info: List of sources being removed
    output_directories: Optional list of output directories to backup

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])
- `output_directories` (Optional[List[Path]]) *optional*

**Returns:** BackupMetadata

##### _show_analytics_summary

```python
def _show_analytics_summary(self, available_sources: List[tuple[str, str]]) -> None
```

Show analytics summary before removal.

**Parameters:**

- `self`
- `available_sources` (List[tuple[str, str]])

**Returns:** None

##### _show_selected_analytics

```python
def _show_selected_analytics(self, sources_info: List[SourceRemovalInfo]) -> None
```

Show detailed analytics for selected sources.

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** None

##### _show_dry_run_summary

```python
def _show_dry_run_summary(self, sources_info: List[SourceRemovalInfo], output_directories: Optional[List[Path]] = None) -> None
```

Show what would happen in dry-run mode.

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])
- `output_directories` (Optional[List[Path]]) *optional*

**Returns:** None

##### _select_backup_to_restore

```python
def _select_backup_to_restore(self, backups: List[BackupMetadata]) -> Optional[str]
```

Let user select which backup to restore.

**Parameters:**

- `self`
- `backups` (List[BackupMetadata])

**Returns:** Optional[str]

##### _scan_output_directories

```python
def _scan_output_directories(self, sources_info: List[SourceRemovalInfo]) -> List[Path]
```

Scan for output directories matching the sources being removed.

Searches in ../News/ for directories matching source display names or IDs.

Args:
    sources_info: List of sources being removed

Returns:
    List of Path objects for matching output directories

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** List[Path]

##### _calculate_directory_size

```python
def _calculate_directory_size(self, directories: List[Path]) -> int
```

Calculate total size of directories in bytes.

Args:
    directories: List of directory paths

Returns:
    Total size in bytes

**Parameters:**

- `self`
- `directories` (List[Path])

**Returns:** int

##### _format_size

```python
def _format_size(self, size_bytes: int) -> str
```

Format byte size as human-readable string.

Args:
    size_bytes: Size in bytes

Returns:
    Formatted string (e.g., "2.3 GB", "45.7 MB")

**Parameters:**

- `self`
- `size_bytes` (int)

**Returns:** str

##### _prompt_output_cleanup

```python
def _prompt_output_cleanup(self, directories: List[Path], total_size: int, dry_run: bool, force: bool) -> bool
```

Prompt user whether to delete output archives.

Args:
    directories: List of output directories found
    total_size: Total size in bytes
    dry_run: Whether in dry-run mode
    force: Whether to skip prompt

Returns:
    True if user wants to delete archives

**Parameters:**

- `self`
- `directories` (List[Path])
- `total_size` (int)
- `dry_run` (bool)
- `force` (bool)

**Returns:** bool

##### _backup_output_directories

```python
def _backup_output_directories(self, directories: List[Path], backup_path: Path) -> None
```

Backup output directories before deletion.

Args:
    directories: List of directories to backup
    backup_path: Path to backup directory

**Parameters:**

- `self`
- `directories` (List[Path])
- `backup_path` (Path)

**Returns:** None

##### _delete_output_directories

```python
def _delete_output_directories(self, directories: List[Path]) -> tuple[int, int]
```

Delete output directories.

Args:
    directories: List of directories to delete

Returns:
    Tuple of (number_deleted, total_size_deleted)

**Parameters:**

- `self`
- `directories` (List[Path])

**Returns:** tuple[int, int]


