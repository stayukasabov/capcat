# core.update_manager

**File:** `Application/core/update_manager.py`

## Description

Update Manager for Capcat.
Handles the --update flag logic for checking existing content and prompting users.

## Classes

### UpdateManager

Manages update operations for Capcat.

Handles:
- Date checking for existing content
- User prompts for missing articles/bundles
- Update logic without deleting old content

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### check_and_handle_update

```python
def check_and_handle_update(self, command_type: str, sources: List[str] = None, bundle_name: str = None, url: str = None) -> bool
```

Main update handler. Returns True if update should proceed, False if cancelled.

Args:
    command_type: 'single', 'fetch', or 'bundle'
    sources: List of source names for fetch command
    bundle_name: Bundle name for bundle command
    url: URL for single command

Returns:
    bool: True if update should proceed, False if cancelled

**Parameters:**

- `self`
- `command_type` (str)
- `sources` (List[str]) *optional*
- `bundle_name` (str) *optional*
- `url` (str) *optional*

**Returns:** bool

##### _handle_single_update

```python
def _handle_single_update(self, url: str) -> bool
```

Handle update for single article command.

**Parameters:**

- `self`
- `url` (str)

**Returns:** bool

##### _handle_fetch_update

```python
def _handle_fetch_update(self, sources: List[str]) -> bool
```

Handle update for fetch command.

**Parameters:**

- `self`
- `sources` (List[str])

**Returns:** bool

##### _handle_bundle_update

```python
def _handle_bundle_update(self, bundle_name: str) -> bool
```

Handle update for bundle command.

**Parameters:**

- `self`
- `bundle_name` (str)

**Returns:** bool

##### _prompt_update_existing_article

```python
def _prompt_update_existing_article(self, article_path: str, url: str) -> bool
```

Prompt user for updating an existing article.

**Parameters:**

- `self`
- `article_path` (str)
- `url` (str)

**Returns:** bool

##### _prompt_download_missing_article

```python
def _prompt_download_missing_article(self, url: str) -> bool
```

Prompt user to download a missing article.

**Parameters:**

- `self`
- `url` (str)

**Returns:** bool

##### _prompt_start_todays_batch

```python
def _prompt_start_todays_batch(self, command_type: str, sources_or_bundles: List[str]) -> bool
```

Prompt user to start today's batch since none exists.

**Parameters:**

- `self`
- `command_type` (str)
- `sources_or_bundles` (List[str])

**Returns:** bool

##### _prompt_mixed_source_update

```python
def _prompt_mixed_source_update(self, existing_sources: List[Tuple[str, str]], missing_sources: List[str]) -> bool
```

Prompt when some sources exist and some don't.

**Parameters:**

- `self`
- `existing_sources` (List[Tuple[str, str]])
- `missing_sources` (List[str])

**Returns:** bool

##### _prompt_update_all_existing_sources

```python
def _prompt_update_all_existing_sources(self, existing_sources: List[Tuple[str, str]]) -> bool
```

Prompt when all sources exist.

**Parameters:**

- `self`
- `existing_sources` (List[Tuple[str, str]])

**Returns:** bool

##### _prompt_download_missing_sources

```python
def _prompt_download_missing_sources(self, sources: List[str]) -> bool
```

Auto-download missing sources in update mode.

**Parameters:**

- `self`
- `sources` (List[str])

**Returns:** bool

##### _prompt_mixed_bundle_update

```python
def _prompt_mixed_bundle_update(self, bundle_name: str, existing_sources: List[Tuple[str, str]], missing_sources: List[str]) -> bool
```

Prompt when some bundle sources exist and some don't.

**Parameters:**

- `self`
- `bundle_name` (str)
- `existing_sources` (List[Tuple[str, str]])
- `missing_sources` (List[str])

**Returns:** bool

##### _prompt_update_existing_bundle

```python
def _prompt_update_existing_bundle(self, bundle_name: str, existing_sources: List[Tuple[str, str]]) -> bool
```

Prompt when entire bundle exists.

**Parameters:**

- `self`
- `bundle_name` (str)
- `existing_sources` (List[Tuple[str, str]])

**Returns:** bool

##### _prompt_download_missing_bundle

```python
def _prompt_download_missing_bundle(self, bundle_name: str, bundle_sources: List[str]) -> bool
```

Prompt when no bundle sources exist.

**Parameters:**

- `self`
- `bundle_name` (str)
- `bundle_sources` (List[str])

**Returns:** bool

##### _get_source_folder_name

```python
def _get_source_folder_name(self, source: str) -> str
```

Get the actual folder name used by the system for a source.

**Parameters:**

- `self`
- `source` (str)

**Returns:** str


## Functions

### get_update_manager

```python
def get_update_manager() -> UpdateManager
```

Get a singleton instance of UpdateManager.

**Returns:** UpdateManager

