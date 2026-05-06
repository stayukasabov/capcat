---
layout: default
render_with_liquid: false
---

# Remove Source: Advanced Usage

## Dry Run

Preview what would be removed without making any changes:

```bash
capcat remove-source --dry-run
```

Shows which config file would be deleted and what the backup would be named.

## Batch Removal

Remove multiple sources at once from a text file (one source name per line):

```bash
# sources-to-remove.txt:
# bbcsport
# mashable

capcat remove-source --batch sources-to-remove.txt
```

## Undo

Each removal creates a timestamped backup in `.capcat/backups/`. The removal ID is printed after each removal.

```bash
# Undo the most recent removal
capcat remove-source --undo

# Undo a specific removal by ID
capcat remove-source --undo <removal-id>
```

## Backup Location

`.capcat/backups/` - managed automatically, do not edit manually.

## Usage Analytics

Before the removal confirmation, the TUI shows fetch statistics for the selected source: total articles collected, last fetch date, success rate. Use this to decide whether a source is worth keeping.

## Limitations

- Only config-driven (YAML) sources can be removed via this command
- Custom Python sources in `Config/sources/active/custom/` must be removed manually by deleting the directory
- Bundles that reference a removed source are not automatically updated
