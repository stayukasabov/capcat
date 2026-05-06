---
layout: default
render_with_liquid: false
---

# Remove Source

`capcat remove-source` interactively removes RSS sources with safety features.

## Usage

```bash
capcat remove-source
```

No arguments required - fully interactive.

## Interactive Flow

1. Shows all active config-driven sources as a selectable list
2. Confirm removal
3. Source config file is deleted; source disappears from `capcat list sources`

## Options

```bash
# Preview without making changes
capcat remove-source --dry-run

# Remove multiple sources from a file (one source name per line)
capcat remove-source --batch sources-to-remove.txt

# Undo a previous removal
capcat remove-source --undo
capcat remove-source --undo <removal-id>
```

## Automatic Backups

Before removing, Capcat backs up the source config to `.capcat/backups/`. The backup ID is shown after removal and is used with `--undo`.

## Usage Analytics

The removal UI shows fetch statistics for each source (article count, last fetched) to help decide whether to keep or remove.

## Also Available in TUI

From `capcat catch` → "Manage sources" → "Remove source".

## Note

Only config-driven sources (YAML files) can be removed via this command. Custom Python sources in `Config/sources/active/custom/` must be removed manually.
