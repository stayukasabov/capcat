# capcat.cli

**File:** `Application/capcat/cli.py`

## Description

CLI entry point for Capcat.

Routes subcommands to legacy capcat_legacy.py / cli.py logic via delegating
stubs.  Every heavy import lives inside the function body (lazy import) so
startup stays fast and circular-import-safe.

## Functions

### _print_help

```python
def _print_help() -> None
```

**Returns:** None

### main

```python
def main() -> None
```

Main entry point.  Routes to TUI or CLI dispatch.

**Returns:** None

### _dispatch

```python
def _dispatch(args: list[str]) -> None
```

**Parameters:**

- `args` (list[str])

**Returns:** None

⚠️ **High complexity:** 13

### _pop_flag

```python
def _pop_flag(args: list[str]) -> tuple[bool, list[str]]
```

Remove boolean flags from *args*, return (found, remaining).

**Parameters:**

- `args` (list[str])

**Returns:** tuple[bool, list[str]]

### _pop_value

```python
def _pop_value(args: list[str]) -> tuple[str | None, list[str]]
```

Remove a flag that takes one value, return (value, remaining).

**Parameters:**

- `args` (list[str])

**Returns:** tuple[str | None, list[str]]

### _cmd_init

```python
def _cmd_init(args: list[str]) -> None
```

**Parameters:**

- `args` (list[str])

**Returns:** None

### _cmd_single

```python
def _cmd_single(args: list[str], log_file: str | None = None) -> None
```

capcat single <url> [--output DIR] [--media] [--html] [--update]
[--verbose] [--quiet] [--log-file FILE]

**Parameters:**

- `args` (list[str])
- `log_file` (str | None) *optional*

**Returns:** None

### _cmd_fetch

```python
def _cmd_fetch(args: list[str], log_file: str | None = None) -> None
```

capcat fetch <sources> [--count N] [--output DIR] [--media] [--html]
[--update] [--verbose] [--quiet] [--log-file FILE]

**Parameters:**

- `args` (list[str])
- `log_file` (str | None) *optional*

**Returns:** None

### _cmd_bundle

```python
def _cmd_bundle(args: list[str], log_file: str | None = None) -> None
```

capcat bundle <name> [--count N] [--output DIR] [--media] [--html]
[--all] [--update] [--verbose] [--quiet] [--log-file FILE]

**Parameters:**

- `args` (list[str])
- `log_file` (str | None) *optional*

**Returns:** None

### _cmd_list

```python
def _cmd_list(args: list[str]) -> None
```

capcat list [sources|bundles|all]

**Parameters:**

- `args` (list[str])

**Returns:** None

### _cmd_add_source

```python
def _cmd_add_source(args: list[str]) -> None
```

capcat add-source --url <feed-url>

**Parameters:**

- `args` (list[str])

**Returns:** None

### _cmd_remove_source

```python
def _cmd_remove_source(args: list[str]) -> None
```

capcat remove-source [--dry-run] [--batch FILE] [--undo [ID]]
[--no-backup] [--no-analytics] [--force]

**Parameters:**

- `args` (list[str])

**Returns:** None

### _cmd_generate_config

```python
def _cmd_generate_config(args: list[str]) -> None
```

capcat generate-config [--output FILE]

**Parameters:**

- `args` (list[str])

**Returns:** None

### _setup_logging

```python
def _setup_logging(verbose: bool = False, quiet: bool = False, log_file: str | None = None) -> None
```

Configure logging for the current command.

**Parameters:**

- `verbose` (bool) *optional*
- `quiet` (bool) *optional*
- `log_file` (str | None) *optional*

**Returns:** None

