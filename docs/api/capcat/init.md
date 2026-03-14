# capcat.commands.init

**File:** `Application/capcat/commands/init.py`

## Description

Implementation of capcat init command.

## Constants

### GITIGNORE_BLOCK

**Value:** `'\n# capcat — managed entries\n.capcat/\nNews/\nCapcats/\n'`

### DEFAULT_CONFIG

**Value:** `'# Capcat configuration\n# See: https://github.com/<owner>/capcat/docs/quick-start.md\n\nsources: []\nbundles: {}\n'`

## Classes

### AlreadyInitializedError

**Inherits from:** Exception

Raised when init is called on an existing project without --reinit.


## Functions

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

