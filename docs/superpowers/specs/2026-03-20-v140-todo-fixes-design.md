# Design: v1.4.0 TODO Fixes

**Date:** 2026-03-20
**Status:** Draft

## Overview

Six open TODOs from the v1.4.0 session report. Three code fixes, one verification task, and two documentation additions.

---

## TODO 1 — Fix `_write_manifest_entry_after_add` mtime heuristic

### Problem
`AddSourceCommand.execute()` currently returns `None`. `AddSourceService._write_manifest_entry_after_add()` works around this by scanning `_config_path` for the most-recently-modified file (mtime heuristic). This is fragile on slow filesystems or when multiple files share the same mtime.

### Fix
Change `AddSourceCommand.execute()` to return the `Path` of the config file it writes. `AddSourceService.add_source()` captures this return value and passes the filename directly to `_write_manifest_entry(filename)`. `AddSourceService._write_manifest_entry_after_add()` is deleted.

### Contract change

| | Before | After |
|---|---|---|
| `AddSourceCommand.execute(url: str)` | `-> None` | `-> Path` (path of written config file) |
| `AddSourceService.add_source(url: str)` | calls `_write_manifest_entry_after_add()` | captures `execute()` return value, calls `_write_manifest_entry(path.name)` |
| `AddSourceService._write_manifest_entry_after_add()` | exists | deleted |

### Tests
- Update existing tests in `tests/unit/test_add_remove_source_mirror.py` to assert `execute()` return value is used
- Add a test that `_write_manifest_entry` is called with the exact filename returned by `execute()`

---

## TODO 2 — Fix empty manifest triggering `_resync_manifest`

### Problem
`SourceConfigMirror._load_manifest()` returns `{}` for both "file absent" and "file exists but is empty or unparseable". `check_for_upgrades()` does `if not manifest: self._resync_manifest()` — the falsy check triggers re-sync for all three cases, but the spec says re-sync should only occur when the file is absent.

### Fix

**`_load_manifest()` — new return semantics:**
- Returns `None` when the manifest file does not exist on disk
- Returns `{}` (empty dict) when the file exists but is empty or contains `{}`
- Returns `{}` and logs a `WARNING` via `get_logger()` when the file exists but fails JSON parsing (parse errors are surfaced, not silently swallowed)

**`check_for_upgrades()` — updated guard:**
- `if manifest is None: self._resync_manifest(); return`
- Proceeds to Step 1 (new items), Step 2/3 (changed builtins upgrade diff) for all other values, including `{}`

> Steps 1–3 are the upgrade diff algorithm implemented in `_step1_new_items()` and `_step2_3_changed_builtins()`.

### Tests
- Test: `_load_manifest()` returns `None` when file absent
- Test: `_load_manifest()` returns `{}` when file exists and is empty
- Test: `_load_manifest()` returns `{}` and logs a warning when file is malformed JSON
- Test: `check_for_upgrades()` calls `_resync_manifest()` only when `_load_manifest()` returns `None`
- Test: `check_for_upgrades()` proceeds to Step 1 (calls `_step1_new_items`) when manifest is `{}`

---

## TODO 3 — Remove duplicate `find_project_root()` calls in `_cmd_list`

### Problem
`cli.py::_cmd_list()` contains two independent try/except blocks that each call `find_project_root()` and assign `_project_root`:
1. First block: used to construct `SourceRegistry`
2. Second block (inside the `what in ("bundles", "all")` branch): used for `get_available_bundles()`

Both blocks catch `NoProjectError` and set `_project_root = None`. The duplication is unnecessary and inconsistent.

### Fix
Hoist a single `find_project_root()` call to the top of `_cmd_list()`, before any branching on `what`. The single try/except catches `NoProjectError` and sets `_project_root = None`. The second try/except block inside the bundles branch is deleted; `_project_root` is reused directly.

### Error handling
The single hoisted block catches only `NoProjectError` (same as both existing blocks). No change to what is caught or how failures are handled — `_project_root = None` causes both registry and bundle lookups to fall back to builtins, as before.

### Tests
No new tests required — behaviour is unchanged. Existing `_cmd_list` tests still pass.

---

## TODO 4 — Verify PyPI publish of v1.4.0

### Action
Run: `pip index versions capcat`

Confirm `1.4.0` appears in the version list.

### Done criteria
- **Success:** `1.4.0` is listed in the output → mark verified, no further action
- **Failure:** `1.4.0` absent → check the GitHub Actions publish workflow run for errors and report findings to the user

---

## TODO 5 — Document `Config/sources/active/` userspace path

### Problem
`docs/reference/quick-reference.md` has no mention of `Config/sources/active/`, the first-run mirror behaviour, or `.capcat/source_hashes.json`.

### Fix
Add a **Source Management → Paths** subsection to `quick-reference.md` documenting:
- `Config/sources/active/config_driven/configs/` — per-source YAML/JSON configs
- `Config/sources/active/custom/` — custom source directories
- `Config/sources/active/bundles/bundles.yml` — bundle definitions
- `.capcat/source_hashes.json` — tracks which sources were added by you vs synced from builtins
- One-sentence explanation of first-run mirror behaviour

### Acceptance criterion
A user reading `quick-reference.md` can understand where their source configs live and that they are safe to edit.

---

## TODO 6 — Document `add-source` and `remove-source` commands

### Problem
`docs/reference/quick-reference.md` has no mention of `capcat add-source` or `capcat remove-source`. These commands were silently redirected to userspace in v1.4.0 with no user-facing documentation.

### Fix
Add a **Source Management → Commands** subsection to `quick-reference.md` with a command table:

| Command | Description |
|---------|-------------|
| `capcat add-source <url>` | Add a new RSS source (written to `Config/sources/active/config_driven/configs/`) |
| `capcat remove-source <id>` | Remove a source from `Config/sources/active/` |
| `capcat list sources` | Show all registered sources |
| `capcat list bundles` | Show all available bundles |

### Acceptance criterion
A user reading `quick-reference.md` can find and use `add-source` and `remove-source` without consulting source code.

---

## Execution Order

1. TODO 4 (verify PyPI) — no code, instant
2. TODO 3 (cli.py dedup) — trivial, isolated
3. TODO 2 (manifest None fix) — isolated to `source_config_mirror.py`
4. TODO 1 (execute() return Path) — touches `add_source_command.py` + `add_source_service.py`
5. TODO 5 (docs: paths) — `quick-reference.md` only
6. TODO 6 (docs: commands) — `quick-reference.md` only

Each code fix (TODOs 1–3) gets a fresh subagent + 2-stage review (spec compliance → code quality).
