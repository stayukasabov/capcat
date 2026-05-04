---
layout: default
render_with_liquid: false
---

# capcat.commands.remove_source

**File:** `Application/capcat/commands/remove_source.py`

## Description

Remove-source command — interactive source removal with backup/undo support.

## Functions

### remove_source

```python
def remove_source(args: argparse.Namespace) -> None
```

Enhanced command to remove existing sources.

Args:
    args: Namespace with dry_run, no_backup, no_analytics, force, batch, undo.

**Parameters:**

- `args` (argparse.Namespace)

**Returns:** None

