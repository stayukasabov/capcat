---
layout: default
render_with_liquid: false
---

# Source Management

All source management operations are available both in the TUI and via CLI.

## TUI Access

```bash
capcat catch
```

Select "Manage sources" from the main menu.

## CLI Commands

```bash
capcat list sources              # list all active sources
capcat add-source --url <url>    # add from RSS/Atom feed
capcat remove-source             # interactive removal
capcat remove-source --dry-run   # preview without changes
capcat remove-source --undo      # undo last removal
```

## Adding a Source

**Via CLI:**
```bash
capcat add-source --url https://example.com/feed.xml
```

**Manually** - drop a YAML file in `Config/sources/active/config_driven/configs/`. See [Source Development](/docs/source-development.html).

**Custom Python source** - implement `BaseSource` in `Config/sources/active/custom/<name>/source.py`.

## Removing a Source

`capcat remove-source` shows an interactive list of all config-driven sources. Select one, confirm, and it's removed. Backup is created automatically for undo.

Only config-driven (YAML) sources can be removed this way. Custom Python sources require manual deletion.

## Listing Sources

```bash
capcat list sources    # active sources
capcat list bundles    # defined bundles
capcat list all        # both
```
