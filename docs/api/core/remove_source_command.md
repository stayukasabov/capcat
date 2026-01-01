# core.source_system.remove_source_command

**File:** `Application/core/source_system/remove_source_command.py`

## Description

Professional implementation of the remove-source command using clean architecture.
Follows the same patterns as add-source for consistency.

## Classes

### SourceRemovalInfo

Information about a source to be removed.


### SourceLister

**Inherits from:** Protocol

Protocol for listing available sources.

#### Methods

##### get_available_sources

```python
def get_available_sources(self) -> List[tuple[str, str]]
```

Get list of available sources.

Returns:
    List of tuples (source_id, display_name)

**Parameters:**

- `self`

**Returns:** List[tuple[str, str]]


### SourceInfoProvider

**Inherits from:** Protocol

Protocol for getting source information.

#### Methods

##### get_source_info

```python
def get_source_info(self, source_id: str) -> Optional[SourceRemovalInfo]
```

Get detailed information about a source.

Args:
    source_id: Source identifier

Returns:
    SourceRemovalInfo or None if not found

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** Optional[SourceRemovalInfo]


### RemovalUserInterface

**Inherits from:** Protocol

Protocol for user interaction during removal.

#### Methods

##### select_sources_to_remove

```python
def select_sources_to_remove(self, sources: List[tuple[str, str]]) -> List[str]
```

Let user select sources to remove.

Args:
    sources: List of (source_id, display_name) tuples

Returns:
    List of selected source IDs

**Parameters:**

- `self`
- `sources` (List[tuple[str, str]])

**Returns:** List[str]

##### confirm_removal

```python
def confirm_removal(self, sources_info: List[SourceRemovalInfo]) -> bool
```

Confirm removal with user.

Args:
    sources_info: Information about sources to be removed

Returns:
    True if user confirms, False otherwise

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** bool

##### show_removal_summary

```python
def show_removal_summary(self, sources_info: List[SourceRemovalInfo]) -> None
```

Show summary of what will be removed.

Args:
    sources_info: Information about sources to be removed

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** None

##### show_success

```python
def show_success(self, message: str) -> None
```

Display success message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_error

```python
def show_error(self, message: str) -> None
```

Display error message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_info

```python
def show_info(self, message: str) -> None
```

Display informational message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None


### ConfigFileRemover

**Inherits from:** Protocol

Protocol for removing configuration files.

#### Methods

##### remove_config_file

```python
def remove_config_file(self, config_path: Path) -> None
```

Remove a configuration file.

Args:
    config_path: Path to config file to remove

**Parameters:**

- `self`
- `config_path` (Path)

**Returns:** None


### BundleUpdater

**Inherits from:** Protocol

Protocol for updating bundles.

#### Methods

##### remove_source_from_all_bundles

```python
def remove_source_from_all_bundles(self, source_id: str) -> List[str]
```

Remove source from all bundles.

Args:
    source_id: Source identifier

Returns:
    List of bundle names that were updated

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** List[str]


### RemoveSourceCommand

Command to remove existing sources.

Follows clean architecture principles with dependency injection
and single responsibility per component.

#### Methods

##### __init__

```python
def __init__(self, source_lister: SourceLister, source_info_provider: SourceInfoProvider, ui: RemovalUserInterface, config_remover: ConfigFileRemover, bundle_updater: BundleUpdater, logger: Optional[any] = None)
```

**Parameters:**

- `self`
- `source_lister` (SourceLister)
- `source_info_provider` (SourceInfoProvider)
- `ui` (RemovalUserInterface)
- `config_remover` (ConfigFileRemover)
- `bundle_updater` (BundleUpdater)
- `logger` (Optional[any]) *optional*

##### execute

```python
def execute(self) -> None
```

Execute the remove-source command.

Raises:
    CapcatError: If removal fails

**Parameters:**

- `self`

**Returns:** None

##### _get_available_sources

```python
def _get_available_sources(self) -> List[tuple[str, str]]
```

Step 1: Get list of available sources.

**Parameters:**

- `self`

**Returns:** List[tuple[str, str]]

##### _gather_sources_info

```python
def _gather_sources_info(self, source_ids: List[str]) -> List[SourceRemovalInfo]
```

Step 3: Gather detailed information about sources to remove.

**Parameters:**

- `self`
- `source_ids` (List[str])

**Returns:** List[SourceRemovalInfo]

##### _remove_sources

```python
def _remove_sources(self, sources_info: List[SourceRemovalInfo]) -> None
```

Step 5: Remove sources and update system.

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** None

##### _refresh_registry

```python
def _refresh_registry(self) -> None
```

Refresh the source registry to reflect filesystem changes.

**Parameters:**

- `self`

**Returns:** None


### FileSystemConfigRemover

Concrete implementation for removing config files and directories.

#### Methods

##### remove_config_file

```python
def remove_config_file(self, config_path: Path) -> None
```

Remove configuration file or directory from filesystem.

**Parameters:**

- `self`
- `config_path` (Path)

**Returns:** None


### RegistrySourceLister

Source lister using the source registry.

#### Methods

##### get_available_sources

```python
def get_available_sources(self) -> List[tuple[str, str]]
```

Get sources from registry.

**Parameters:**

- `self`

**Returns:** List[tuple[str, str]]


### RegistrySourceInfoProvider

Source info provider using registry and filesystem.

#### Methods

##### __init__

```python
def __init__(self, config_base_path: Path, bundles_path: Path)
```

**Parameters:**

- `self`
- `config_base_path` (Path)
- `bundles_path` (Path)

##### get_source_info

```python
def get_source_info(self, source_id: str) -> Optional[SourceRemovalInfo]
```

Get source information from registry and bundles.

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** Optional[SourceRemovalInfo]

##### _find_bundles_with_source

```python
def _find_bundles_with_source(self, source_id: str) -> List[str]
```

Find all bundles containing the source.

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** List[str]


### BundleManagerUpdater

Bundle updater using BundleManager.

#### Methods

##### __init__

```python
def __init__(self, bundles_path: Path)
```

**Parameters:**

- `self`
- `bundles_path` (Path)

##### remove_source_from_all_bundles

```python
def remove_source_from_all_bundles(self, source_id: str) -> List[str]
```

Remove source from all bundles it appears in.

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** List[str]


