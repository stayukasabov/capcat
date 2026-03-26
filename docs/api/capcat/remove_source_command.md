# capcat.core.source_system.remove_source_command

**File:** `Application/capcat/core/source_system/remove_source_command.py`

## Description

Base classes and implementations for the remove-source command.

Provides the command pattern foundation used by EnhancedRemoveCommand
and RemoveSourceService:
  - SourceRemovalInfo: value object describing a source to be removed
  - RemovalUserInterface: ABC for UI interactions (enables testability)
  - RemoveSourceCommand: orchestrates selection → confirmation → removal
  - RegistrySourceLister: queries SourceRegistry for available sources
  - RegistrySourceInfoProvider: builds SourceRemovalInfo from config files
  - FileSystemConfigRemover: deletes YAML config files from disk
  - BundleManagerUpdater: removes the source from bundles.yml

## Classes

### SourceRemovalInfo

Describes a source that is about to be removed.

Attributes:
    source_id: Machine-readable source identifier (e.g. ``"hn"``).
    display_name: Human-readable name shown in the UI.
    config_path: Filesystem path to the source YAML config file.
    bundles: List of bundle names that include this source.


### RemovalUserInterface

**Inherits from:** abc.ABC

Abstract interface for all UI interactions during source removal.

Concrete implementations live in removal_ui.py (questionary-based)
and tests/fixtures (mock-based).

#### Methods

##### select_sources_to_remove

```python
def select_sources_to_remove(self, sources: List[tuple]) -> List[str]
```

Prompt the user to select one or more sources.

Args:
    sources: List of ``(source_id, display_name)`` tuples.

Returns:
    List of selected source IDs.

**Parameters:**

- `self`
- `sources` (List[tuple])

**Returns:** List[str]

##### show_removal_summary

```python
def show_removal_summary(self, sources_info: List[SourceRemovalInfo]) -> None
```

Show a summary of what will be removed before confirming.

Args:
    sources_info: Sources scheduled for removal.

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** None

##### confirm_removal

```python
def confirm_removal(self, sources_info: List[SourceRemovalInfo]) -> bool
```

Ask the user to confirm the removal.

Args:
    sources_info: Sources scheduled for removal.

Returns:
    ``True`` if the user confirmed, ``False`` to abort.

**Parameters:**

- `self`
- `sources_info` (List[SourceRemovalInfo])

**Returns:** bool

##### show_success

```python
def show_success(self, message: str) -> None
```

Display a success notification.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_error

```python
def show_error(self, message: str) -> None
```

Display an error notification.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_info

```python
def show_info(self, message: str) -> None
```

Display an informational message.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None


### SourceLister

**Inherits from:** abc.ABC

Returns the list of removable sources as (source_id, display_name) pairs.

#### Methods

##### list_sources

```python
def list_sources(self) -> List[tuple]
```

Return ``[(source_id, display_name), ...]`` for every available source.

**Parameters:**

- `self`

**Returns:** List[tuple]


### SourceInfoProvider

**Inherits from:** abc.ABC

Builds SourceRemovalInfo objects for a list of source IDs.

#### Methods

##### get_sources_info

```python
def get_sources_info(self, source_ids: List[str]) -> List[SourceRemovalInfo]
```

Return removal metadata for each requested source_id.

Args:
    source_ids: IDs returned by the UI selection step.

Returns:
    One SourceRemovalInfo per valid source ID.

**Parameters:**

- `self`
- `source_ids` (List[str])

**Returns:** List[SourceRemovalInfo]


### ConfigRemover

**Inherits from:** abc.ABC

Deletes a source's config file from disk.

#### Methods

##### remove_config

```python
def remove_config(self, source_info: SourceRemovalInfo) -> None
```

Remove the config file described by *source_info*.

Args:
    source_info: Removal metadata including the config path.

**Parameters:**

- `self`
- `source_info` (SourceRemovalInfo)

**Returns:** None


### BundleUpdater

**Inherits from:** abc.ABC

Removes a source ID from all bundles in bundles.yml.

#### Methods

##### remove_from_bundles

```python
def remove_from_bundles(self, source_id: str) -> None
```

Strip *source_id* from every bundle that contains it.

Args:
    source_id: The source to remove from bundles.

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** None


### RemoveSourceCommand

Orchestrates the interactive remove-source workflow.

Steps:
  1. List available sources via *source_lister*.
  2. Let the user select via *ui*.
  3. Gather removal info via *source_info_provider*.
  4. Show summary and ask for confirmation via *ui*.
  5. Delete config via *config_remover*.
  6. Update bundles via *bundle_updater*.

Args:
    source_lister: Provides ``[(source_id, display_name)]``.
    source_info_provider: Builds SourceRemovalInfo objects.
    ui: User-facing interaction layer.
    config_remover: Removes YAML config files.
    bundle_updater: Keeps bundles.yml consistent.
    logger: Optional logger; defaults to module logger.

#### Methods

##### __init__

```python
def __init__(self, source_lister: SourceLister, source_info_provider: SourceInfoProvider, ui: RemovalUserInterface, config_remover: ConfigRemover, bundle_updater: BundleUpdater, logger: Optional[Any] = None) -> None
```

**Parameters:**

- `self`
- `source_lister` (SourceLister)
- `source_info_provider` (SourceInfoProvider)
- `ui` (RemovalUserInterface)
- `config_remover` (ConfigRemover)
- `bundle_updater` (BundleUpdater)
- `logger` (Optional[Any]) *optional*

**Returns:** None

##### execute

```python
def execute(self) -> None
```

Run the full interactive removal workflow.

**Parameters:**

- `self`

**Returns:** None

##### _remove_sources

```python
def _remove_sources(self, sources_info: List['SourceRemovalInfo']) -> None
```

Remove a list of sources (config + bundles) without UI interaction.

Used by EnhancedRemoveCommand after confirmation has been handled.

Args:
    sources_info: Sources to remove.

**Parameters:**

- `self`
- `sources_info` (List['SourceRemovalInfo'])

**Returns:** None

##### _refresh_registry

```python
def _refresh_registry(self) -> None
```

Reset the global source registry so it reflects removed sources.

**Parameters:**

- `self`

**Returns:** None


### RegistrySourceLister

**Inherits from:** SourceLister

Lists sources via SourceRegistry — reads the live registry at call time.

#### Methods

##### list_sources

```python
def list_sources(self) -> List[tuple]
```

Return ``[(source_id, display_name)]`` for every user-removable source.

Builtin sources (shipped with the application) are excluded — they
cannot be removed and would silently no-op if the removal were attempted.

**Parameters:**

- `self`

**Returns:** List[tuple]


### RegistrySourceInfoProvider

**Inherits from:** SourceInfoProvider

Builds SourceRemovalInfo by inspecting config files and bundles.yml.

Args:
    config_path: Directory containing per-source YAML config files.
    bundles_path: Path to bundles.yml.

#### Methods

##### __init__

```python
def __init__(self, config_path: Path, bundles_path: Path) -> None
```

**Parameters:**

- `self`
- `config_path` (Path)
- `bundles_path` (Path)

**Returns:** None

##### get_sources_info

```python
def get_sources_info(self, source_ids: List[str]) -> List[SourceRemovalInfo]
```

Build SourceRemovalInfo for each source_id.

Args:
    source_ids: IDs selected for removal.

Returns:
    List of SourceRemovalInfo, one per valid ID.

**Parameters:**

- `self`
- `source_ids` (List[str])

**Returns:** List[SourceRemovalInfo]

##### _load_bundles_map

```python
def _load_bundles_map(self) -> dict
```

Return ``{source_id: [bundle_name, ...]}`` from bundles.yml.

**Parameters:**

- `self`

**Returns:** dict


### FileSystemConfigRemover

**Inherits from:** ConfigRemover

Deletes the YAML config file for a source from disk.

#### Methods

##### remove_config

```python
def remove_config(self, source_info: SourceRemovalInfo) -> None
```

Delete the config file if it exists.

Args:
    source_info: Contains the config_path to delete.

**Parameters:**

- `self`
- `source_info` (SourceRemovalInfo)

**Returns:** None


### BundleManagerUpdater

**Inherits from:** BundleUpdater

Removes a source from all entries in bundles.yml.

Args:
    bundles_path: Path to bundles.yml.

#### Methods

##### __init__

```python
def __init__(self, bundles_path: Path) -> None
```

**Parameters:**

- `self`
- `bundles_path` (Path)

**Returns:** None

##### remove_from_bundles

```python
def remove_from_bundles(self, source_id: str) -> None
```

Strip *source_id* from every bundle in bundles.yml.

Args:
    source_id: Source to remove from all bundles.

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** None


