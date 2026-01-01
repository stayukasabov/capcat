# core.source_system.bundle_manager

**File:** `Application/core/source_system/bundle_manager.py`

## Classes

### BundleManager

Manages the addition of sources to bundles in the bundles.yml file,
preserving comments and structure.

#### Methods

##### __init__

```python
def __init__(self, bundle_file_path: str)
```

Args:
    bundle_file_path: The absolute path to the bundles.yml file.

**Parameters:**

- `self`
- `bundle_file_path` (str)

##### _load_data

```python
def _load_data(self)
```

Loads the YAML data from the file.

**Parameters:**

- `self`

##### _save_data

```python
def _save_data(self)
```

Saves the modified YAML data back to the file.

**Parameters:**

- `self`

##### get_bundle_names

```python
def get_bundle_names(self) -> list[str]
```

Returns a list of all available bundle names.

**Parameters:**

- `self`

**Returns:** list[str]

##### add_source_to_bundle

```python
def add_source_to_bundle(self, source_id: str, bundle_name: str)
```

Adds a source ID to a specified bundle and saves the file.

Args:
    source_id: The ID of the source to add.
    bundle_name: The name of the bundle to add the source to.

Raises:
    ValueError: If the bundle_name does not exist.

**Parameters:**

- `self`
- `source_id` (str)
- `bundle_name` (str)

##### remove_source_from_all_bundles

```python
def remove_source_from_all_bundles(self, source_id: str) -> list[str]
```

Removes a source ID from all bundles and saves the file.

Args:
    source_id: The ID of the source to remove.

Returns:
    List of bundle names that were updated.

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** list[str]

##### create_bundle

```python
def create_bundle(self, bundle_id: str, description: str, default_count: int = 20, sources: list = None) -> None
```

Create new bundle in bundles.yml.

Args:
    bundle_id: Unique bundle identifier (lowercase_with_underscores)
    description: Bundle description (1-200 chars)
    default_count: Default article count (1-100, default 20)
    sources: Initial source list (optional, default [])

Raises:
    ValueError: If bundle_id exists or invalid

**Parameters:**

- `self`
- `bundle_id` (str)
- `description` (str)
- `default_count` (int) *optional*
- `sources` (list) *optional*

**Returns:** None

##### delete_bundle

```python
def delete_bundle(self, bundle_id: str) -> None
```

Delete bundle from bundles.yml.

Args:
    bundle_id: Bundle to delete

Raises:
    ValueError: If bundle not found or protected

**Parameters:**

- `self`
- `bundle_id` (str)

**Returns:** None

##### update_bundle_metadata

```python
def update_bundle_metadata(self, bundle_id: str, description: str = None, default_count: int = None) -> None
```

Update bundle metadata (description and/or default_count).

Args:
    bundle_id: Bundle to update
    description: New description (optional)
    default_count: New default count (optional)

Raises:
    ValueError: If bundle not found or no changes provided

**Parameters:**

- `self`
- `bundle_id` (str)
- `description` (str) *optional*
- `default_count` (int) *optional*

**Returns:** None

##### get_bundle_details

```python
def get_bundle_details(self, bundle_id: str) -> dict
```

Get detailed information about a bundle.

Args:
    bundle_id: Bundle to query

Returns:
    Dictionary with bundle metadata and statistics

Raises:
    ValueError: If bundle not found

**Parameters:**

- `self`
- `bundle_id` (str)

**Returns:** dict

##### list_bundles

```python
def list_bundles(self) -> list
```

Get list of all bundles with basic info.

Returns:
    List of bundle dictionaries with id, description, source_count

**Parameters:**

- `self`

**Returns:** list

##### add_sources_to_bundle

```python
def add_sources_to_bundle(self, bundle_id: str, source_ids: list) -> int
```

Add multiple sources to bundle.

Args:
    bundle_id: Target bundle
    source_ids: List of source IDs to add

Returns:
    Number of sources added (excludes duplicates)

Raises:
    ValueError: If bundle not found

**Parameters:**

- `self`
- `bundle_id` (str)
- `source_ids` (list)

**Returns:** int

##### remove_sources_from_bundle

```python
def remove_sources_from_bundle(self, bundle_id: str, source_ids: list) -> int
```

Remove multiple sources from bundle.

Args:
    bundle_id: Target bundle
    source_ids: List of source IDs to remove

Returns:
    Number of sources removed

Raises:
    ValueError: If bundle not found

**Parameters:**

- `self`
- `bundle_id` (str)
- `source_ids` (list)

**Returns:** int

##### move_source_between_bundles

```python
def move_source_between_bundles(self, source_id: str, from_bundle_id: str, to_bundle_id: str, copy_mode: bool = False) -> dict
```

Move or copy source from one bundle to another.

Args:
    source_id: Source to move/copy
    from_bundle_id: Source bundle
    to_bundle_id: Target bundle
    copy_mode: If True, copy (keep in source). If False, move (remove from source)

Returns:
    Dictionary with 'added' and 'removed' status

Raises:
    ValueError: If bundles not found or source not in from_bundle

**Parameters:**

- `self`
- `source_id` (str)
- `from_bundle_id` (str)
- `to_bundle_id` (str)
- `copy_mode` (bool) *optional*

**Returns:** dict

##### get_source_bundle_memberships

```python
def get_source_bundle_memberships(self, source_id: str) -> list
```

Get list of bundles containing a source.

Args:
    source_id: Source to query

Returns:
    List of bundle IDs containing the source

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** list

##### bulk_add_by_category

```python
def bulk_add_by_category(self, bundle_id: str, category: str) -> int
```

Add all sources from a category to bundle.

Args:
    bundle_id: Target bundle
    category: Source category (tech, news, etc.)

Returns:
    Number of sources added

Raises:
    ValueError: If bundle not found

**Parameters:**

- `self`
- `bundle_id` (str)
- `category` (str)

**Returns:** int

##### bulk_remove_by_category

```python
def bulk_remove_by_category(self, bundle_id: str, category: str) -> int
```

Remove all sources from a category from bundle.

Args:
    bundle_id: Target bundle
    category: Source category (tech, news, etc.)

Returns:
    Number of sources removed

Raises:
    ValueError: If bundle not found

**Parameters:**

- `self`
- `bundle_id` (str)
- `category` (str)

**Returns:** int


