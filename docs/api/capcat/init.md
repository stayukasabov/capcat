---
layout: default
render_with_liquid: false
---

# capcat.commands.init

**File:** `Application/capcat/commands/init.py`

## Description

Implementation of capcat init command.

## Constants

### GITIGNORE_BLOCK

**Value:** `'\n# capcat - managed entries\n.capcat/\nNews/\nCapcats/\n'`

## Classes

### AlreadyInitializedError

**Inherits from:** Exception

Raised when init is called on an existing project without --reinit.


## Functions

### _copy_themes_to

```python
def _copy_themes_to(dest: Path) -> None
```

Copy base.css and design-system.css from package themes to dest.

**Parameters:**

- `dest` (Path)

**Returns:** None

### init_project

```python
def init_project(root: Path, reinit: bool = False) -> None
```

Initialize a capcat project in the given directory.

Args:
    root: Directory to initialize as a capcat project.
    reinit: If True, reset .capcat/ internal state only.

Raises:
    AlreadyInitializedError: If project exists and reinit is False.

**Parameters:**

- `root` (Path)
- `reinit` (bool) *optional*

**Returns:** None

