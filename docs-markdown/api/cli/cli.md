# cli

**File:** `Application/cli.py`

## Description

Professional CLI interface for Capcat using subcommand architecture.
Follows industry standards like git, docker, and kubernetes.

## Constants

### AVAILABLE_SOURCES

**Value:** `get_available_sources()`

### BUNDLES

**Value:** `get_available_bundles()`

## Functions

### get_available_sources

```python
def get_available_sources() -> Dict[str, str]
```

Get available sources from the source registry.

Falls back to hardcoded sources if registry fails to load.

Returns:
    Dictionary mapping source IDs to display names

Raises:
    Exception: Caught and logged, triggers fallback sources

**Returns:** Dict[str, str]

### get_available_bundles

```python
def get_available_bundles() -> Dict[str, Dict[str, Any]]
```

Get available bundles from bundles.yml file.

Auto-populates 'all' bundle with all available sources from registry.
Falls back to hardcoded bundles if file loading fails.

Returns:
    Dictionary mapping bundle IDs to bundle data (sources, description)

Raises:
    Exception: Caught and logged, triggers fallback bundles

**Returns:** Dict[str, Dict[str, Any]]

### _get_fallback_sources

```python
def _get_fallback_sources() -> Dict[str, str]
```

Fallback source definitions if registry fails.

Provides minimal set of core sources for basic functionality.

Returns:
    Dictionary of hardcoded source IDs to display names

**Returns:** Dict[str, str]

### _get_fallback_bundles

```python
def _get_fallback_bundles() -> Dict[str, Dict[str, Any]]
```

Fallback bundle definitions if registry fails.

Provides minimal set of core bundles for basic functionality.

Returns:
    Dictionary of hardcoded bundle IDs to bundle data

**Returns:** Dict[str, Dict[str, Any]]

### run_capcat_fetch

```python
def run_capcat_fetch(source_id: str, count: int) -> bool
```

Run the './capcat fetch' command as a subprocess for testing new source.

Designed to be easily mockable in tests.

Args:
    source_id: Source identifier to test
    count: Number of articles to fetch

Returns:
    True if fetch successful, False otherwise

Raises:
    subprocess.CalledProcessError: If fetch command fails

**Parameters:**

- `source_id` (str)
- `count` (int)

**Returns:** bool

### add_source

```python
def add_source(url: str) -> None
```

Interactive command to add a new RSS-based source.

Guides user through: RSS inspection, configuration, bundle assignment,
and test fetch. Creates YAML config in sources/active/config_driven/configs/.

Args:
    url: RSS feed URL to add as new source

Raises:
    SystemExit: If user cancels or configuration fails

**Parameters:**

- `url` (str)

**Returns:** None

⚠️ **High complexity:** 12

### remove_source

```python
def remove_source(args: argparse.Namespace) -> None
```

Enhanced command to remove existing sources with advanced options.

Supports dry-run, backup, analytics, batch removal, and undo operations.

Args:
    args: Parsed command-line arguments with removal options

Raises:
    CapcatError: If source removal fails
    SystemExit: If user cancels operation

**Parameters:**

- `args` (argparse.Namespace)

**Returns:** None

### _handle_undo

```python
def _handle_undo(backup_id: str) -> None
```

Handle undo/restore operation.

Restores sources from backup using specified backup ID.

Args:
    backup_id: Backup identifier to restore from

Raises:
    CapcatError: If restore operation fails

**Parameters:**

- `backup_id` (str)

**Returns:** None

### generate_config_command

```python
def generate_config_command(args: argparse.Namespace) -> None
```

Launch the interactive config generator script.

Executes scripts/generate_source_config.py as subprocess.

Args:
    args: Parsed command-line arguments with optional output path

Raises:
    SystemExit: If script not found or execution fails

**Parameters:**

- `args` (argparse.Namespace)

**Returns:** None

### create_parser

```python
def create_parser() -> argparse.ArgumentParser
```

Create the main argument parser with subcommands.

Defines global options and all subcommands (single, fetch, bundle, catch,
add-source, remove-source, generate-config, list).

Returns:
    Configured ArgumentParser instance

**Returns:** argparse.ArgumentParser

### parse_sources

```python
def parse_sources(sources_str: str) -> List[str]
```

Parse comma-separated sources string and validate.

Args:
    sources_str: Comma-separated source identifiers

Returns:
    List of validated source IDs

Raises:
    ValidationError: If any source ID is unknown

**Parameters:**

- `sources_str` (str)

**Returns:** List[str]

### validate_arguments

```python
def validate_arguments(args: argparse.Namespace) -> Dict[str, Any]
```

Validate and process parsed arguments.

Converts argparse Namespace to configuration dictionary for capcat.py.
Handles all subcommands and validates required arguments.

Args:
    args: Parsed command-line arguments

Returns:
    Configuration dictionary with action, sources, options

Raises:
    ValidationError: If required arguments missing or invalid

**Parameters:**

- `args` (argparse.Namespace)

**Returns:** Dict[str, Any]

⚠️ **High complexity:** 14

### list_sources_and_bundles

```python
def list_sources_and_bundles(what: str = 'all') -> None
```

Display available sources and bundles.

Args:
    what: What to list - 'sources', 'bundles', or 'all'

**Parameters:**

- `what` (str) *optional*

**Returns:** None

⚠️ **High complexity:** 11

### parse_arguments

```python
def parse_arguments(argv: Optional[List[str]] = None) -> Dict[str, Any]
```

Parse command line arguments and return validated configuration.

Handles immediate-exit commands (list, add-source, remove-source,
generate-config, catch) and validates remaining commands.

Args:
    argv: Command line arguments (uses sys.argv if None)

Returns:
    Validated configuration dictionary

Raises:
    ValidationError: If arguments invalid
    SystemExit: For immediate-exit commands

**Parameters:**

- `argv` (Optional[List[str]]) *optional*

**Returns:** Dict[str, Any]

### main

```python
def main() -> None
```

Main entry point for direct CLI script execution.

Parses arguments and executes commands. Used when cli.py run directly.
Normal usage goes through capcat.py which imports functions from here.

**Returns:** None

