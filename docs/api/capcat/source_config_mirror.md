# capcat.core.source_config_mirror

**File:** `Application/capcat/core/source_config_mirror.py`

## Description

Mirror builtin source configs to userspace Config/sources/active/.

## Constants

### _CONFIG_DRIVEN_EXTS

**Value:** `{'.yaml', '.yml', '.json'}`

### _SKIP_DIRS

**Value:** `{'__pycache__'}`

## Classes

### SourceConfigMirror

Copy and track builtin source configs in userspace.

#### Methods

##### __init__

```python
def __init__(self, project_root: Path, tui_mode: bool) -> None
```

**Parameters:**

- `self`
- `project_root` (Path)
- `tui_mode` (bool)

**Returns:** None

##### is_mirrored

```python
def is_mirrored(self) -> bool
```

True if any domain dir exists under Config/sources/active/.

**Parameters:**

- `self`

**Returns:** bool

##### run_first_mirror

```python
def run_first_mirror(self) -> None
```

Copy all three domains, write manifest, print message.

**Parameters:**

- `self`

**Returns:** None

##### check_for_upgrades

```python
def check_for_upgrades(self) -> None
```

Diff all domains vs manifest. Prompt for new items and changed builtins.

**Parameters:**

- `self`

**Returns:** None

##### _compute_hash

```python
def _compute_hash(self, path: Path) -> str
```

**Parameters:**

- `self`
- `path` (Path)

**Returns:** str

##### _load_manifest

```python
def _load_manifest(self) -> Optional[dict]
```

**Parameters:**

- `self`

**Returns:** Optional[dict]

##### _save_manifest

```python
def _save_manifest(self, manifest: dict) -> None
```

**Parameters:**

- `self`
- `manifest` (dict)

**Returns:** None

##### _prompt

```python
def _prompt(self, message: str) -> str
```

Display prompt; use questionary in TUI mode, print+input in CLI mode.

Returns 'n' silently when stdin is not a tty (non-interactive/background run).

**Parameters:**

- `self`
- `message` (str)

**Returns:** str

##### _builtin_config_driven_dir

```python
def _builtin_config_driven_dir(self) -> Path
```

**Parameters:**

- `self`

**Returns:** Path

##### _user_config_driven_dir

```python
def _user_config_driven_dir(self) -> Path
```

**Parameters:**

- `self`

**Returns:** Path

##### _builtin_custom_dir

```python
def _builtin_custom_dir(self) -> Path
```

**Parameters:**

- `self`

**Returns:** Path

##### _user_custom_dir

```python
def _user_custom_dir(self) -> Path
```

**Parameters:**

- `self`

**Returns:** Path

##### _builtin_bundles_dir

```python
def _builtin_bundles_dir(self) -> Path
```

**Parameters:**

- `self`

**Returns:** Path

##### _user_bundles_dir

```python
def _user_bundles_dir(self) -> Path
```

**Parameters:**

- `self`

**Returns:** Path

##### _mirror_config_driven

```python
def _mirror_config_driven(self, manifest: dict) -> None
```

**Parameters:**

- `self`
- `manifest` (dict)

**Returns:** None

##### _mirror_custom

```python
def _mirror_custom(self, manifest: dict) -> None
```

**Parameters:**

- `self`
- `manifest` (dict)

**Returns:** None

##### _mirror_bundles

```python
def _mirror_bundles(self, manifest: dict) -> None
```

**Parameters:**

- `self`
- `manifest` (dict)

**Returns:** None

##### _step1_new_items

```python
def _step1_new_items(self, manifest: dict) -> dict
```

Detect and silently copy items present in builtins but absent from user mirror.

**Parameters:**

- `self`
- `manifest` (dict)

**Returns:** dict

⚠️ **High complexity:** 27

##### _step2_3_changed_builtins

```python
def _step2_3_changed_builtins(self, manifest: dict) -> dict
```

Detects builtin files whose hash has changed since the last mirror and applies the appropriate update strategy:

- **app-owned** (`.py` files): always overwritten automatically; backup created if the user had local edits.
- **config-owned, unmodified**: silently overwritten.
- **config-owned, user-modified**: interactive prompt (skipped silently in non-interactive / `-q` mode).

**Backward compatibility:** manifest entries that lack an `ownership` field are treated as app-owned when the key ends in `.py`, regardless of the stored value. This covers vaults created before the `ownership` field was introduced and prevents stale source files from persisting after a capcat upgrade.

**Parameters:**

- `self`
- `manifest` (dict)

**Returns:** dict

⚠️ **High complexity:** 15

##### _prompt_config_updates

```python
def _prompt_config_updates(self, manifest: dict, candidates: list) -> dict
```

Interactive prompt for config-owned files that the user has modified.

**Parameters:**

- `self`
- `manifest` (dict)
- `candidates` (list)

**Returns:** dict

⚠️ **High complexity:** 12

##### _backup

```python
def _backup(self, resolved_user_files: list) -> Path
```

Copy user files to timestamped backup dir. Raises OSError on failure.

**Parameters:**

- `self`
- `resolved_user_files` (list)

**Returns:** Path

##### _diff_files

```python
def _diff_files(self, user_file: Path, builtin_file: Path) -> str
```

Return a unified diff of user_file vs builtin_file.

fromfile='your version', tofile='new default'.
Returns empty string if files are identical.

**Parameters:**

- `self`
- `user_file` (Path)
- `builtin_file` (Path)

**Returns:** str

##### _resolve_user_file

```python
def _resolve_user_file(self, key: str) -> Optional[Path]
```

Locate the actual user file for a manifest key. Returns None if absent.

**Parameters:**

- `self`
- `key` (str)

**Returns:** Optional[Path]

##### _builtin_file_for_key

```python
def _builtin_file_for_key(self, key: str) -> Optional[Path]
```

Return the builtin file Path for a manifest key, or None if not present.

**Parameters:**

- `self`
- `key` (str)

**Returns:** Optional[Path]

##### _resync_manifest

```python
def _resync_manifest(self) -> None
```

Rebuild manifest from current user files when source_hashes.json is missing.

Uses the actual installed builtin hash as the baseline so future
check_for_upgrades() diffs are accurate.

**Parameters:**

- `self`

**Returns:** None

⚠️ **High complexity:** 17


## Functions

### _key_display_name

```python
def _key_display_name(key: str) -> str
```

Convert a manifest key to a short human-readable name.

**Parameters:**

- `key` (str)

**Returns:** str

