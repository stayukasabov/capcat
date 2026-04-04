# capcat.cli

**File:** `Application/capcat/cli.py`

## Description

CLI entry point for Capcat.

Routes subcommands to legacy capcat_legacy.py / cli.py logic via delegating
stubs.  Every heavy import lives inside the function body (lazy import) so
startup stays fast and circular-import-safe.

## Constants

### GLOBAL_SETTINGS_TEMPLATE

**Value:** `'# Global Settings — Capcat\n# Edit this file to tune behavior for this vault.\n# All fields are optional. Defaults are shown in comments.\n# Restart capcat after editing.\n\n# ─── PDF Downloads ──────────────────────────────────────\npdf:\n  # Skip PDF files larger than this size in bytes.\n  # Default: 20971520 (20MB). Examples: 10485760 = 10MB, 52428800 = 50MB\n  max_pdf_size_bytes: 20971520\n\n  # Maximum number of PDFs queued per article.\n  # Default: 10\n  max_pdf_per_article: 10\n\n# ─── Network ────────────────────────────────────────────\nnetwork:\n  # TCP connection timeout in seconds. Increase for slow servers.\n  # Default: 10\n  connect_timeout: 10\n\n  # HTTP response body read timeout in seconds.\n  # Default: 30\n  read_timeout: 30\n\n  # Image and PDF download timeout in seconds.\n  # Default: 60\n  media_download_timeout: 60\n\n  # HEAD request timeout for link checking in seconds.\n  # Default: 10\n  head_request_timeout: 10\n\n  # Retry attempts on network failure.\n  # Default: 3\n  max_retries: 3\n\n  # Base delay between retries in seconds.\n  # Default: 1.0\n  retry_delay: 1.0\n\n  # Minimum seconds between requests to the same domain.\n  # Default: 1.0\n  crawl_delay: 1.0\n\n  # How long to cache robots.txt responses in minutes.\n  # Default: 15\n  robots_cache_ttl_minutes: 15\n\n  # HTTP User-Agent header sent with all requests.\n  # Default: "Capcat/2.0 (Personal news archiver)"\n  user_agent: "Capcat/2.0 (Personal news archiver)"\n\n  # HTTP connection pool size.\n  # Default: 20\n  pool_connections: 20\n\n  # Maximum concurrent connections.\n  # Default: 20\n  pool_maxsize: 20\n\n# ─── Processing ─────────────────────────────────────────\nprocessing:\n  # Default articles fetched per source per run.\n  # Per-source article_count in each source\'s config.yaml overrides this.\n  # Default: 30\n  article_count: 30\n\n  # Concurrent article fetcher workers.\n  # Default: 8\n  max_workers: 8\n\n  # HTML to Markdown conversion timeout in seconds.\n  # Default: 30\n  conversion_timeout: 30\n\n  # Maximum images downloaded per article (normal mode).\n  # Default: 20\n  max_images: 20\n\n  # Maximum images downloaded per article when --media flag is active.\n  # Default: 1000\n  max_images_media_mode: 1000\n\n  # Skip images smaller than this in pixels (width and height).\n  # Default: 150\n  min_image_dimensions: 150\n\n  # Skip images larger than this in bytes.\n  # Default: 5242880 (5MB). Example: 1048576 = 1MB\n  max_image_size_bytes: 5242880\n\n  # Maximum characters in vault filenames.\n  # Default: 100\n  max_filename_length: 100\n\n  # Download and embed images locally.\n  # Default: true\n  download_images: true\n\n  # Download video files.\n  # Default: false\n  download_videos: false\n\n  # Download audio files.\n  # Default: false\n  download_audio: false\n\n  # Download generic document files.\n  # Default: false\n  download_documents: false\n\n  # Fetch and save comments alongside articles.\n  # Default: true\n  create_comments_file: true\n\n  # Strip <script> tags from HTML before conversion.\n  # Default: true\n  remove_script_tags: true\n\n  # Strip <style> tags from HTML before conversion.\n  # Default: true\n  remove_style_tags: true\n\n  # Strip <nav> tags from HTML before conversion.\n  # Default: true\n  remove_nav_tags: true\n\n  # Preserve line breaks in markdown output.\n  # Default: true\n  markdown_line_breaks: true\n\n# ─── UI ─────────────────────────────────────────────────\nui:\n  # Spinner style for article progress.\n  # Options: dots, wave, loading, pulse, bounce, modern\n  # Default: dots\n  progress_spinner_style: dots\n\n  # Spinner style for batch operations.\n  # Options: activity, progress, pulse, wave, dots, scan\n  # Default: activity\n  batch_spinner_style: activity\n\n  # Progress bar width in characters.\n  # Default: 25\n  progress_bar_width: 25\n\n  # Show animated progress indicators.\n  # Default: true\n  show_progress_animations: true\n\n  # Use emoji in output.\n  # Default: true\n  use_emojis: true\n\n  # Use colors in terminal output.\n  # Default: true\n  use_colors: true\n\n  # Show per-article detail during fetch.\n  # Default: false\n  show_detailed_progress: false\n\n# ─── Logging ────────────────────────────────────────────\nlogging:\n  # Log level for all output. Options: DEBUG, INFO, WARNING, ERROR\n  # Default: INFO\n  default_level: INFO\n\n  # Log level for terminal output.\n  # Default: INFO\n  console_level: INFO\n\n  # Log level written to log file.\n  # Default: DEBUG\n  file_level: DEBUG\n\n  # Maximum log file size before rotation in bytes.\n  # Default: 10485760 (10MB)\n  max_log_file_size: 10485760\n\n  # Number of rotated log files to keep.\n  # Default: 5\n  log_file_backup_count: 5\n\n  # Include timestamps in log output.\n  # Default: true\n  include_timestamps: true\n\n  # Include module names in log output.\n  # Default: true\n  include_module_names: true\n\n  # Auto-create log directory if it does not exist.\n  # Default: true\n  auto_create_log_dir: true\n\n  # Colorize log output.\n  # Default: true\n  use_colors: true\n'`

## Functions

### _print_help

```python
def _print_help() -> None
```

Print the top-level usage text to stdout and return.

**Returns:** None

### run_app

```python
def run_app(args: list) -> None
```

Programmatic entry point — run capcat with a pre-built argument list.

**Parameters:**

- `args` (list)

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

Route a raw argument list to the appropriate command handler.

Handles global flags (-L, --version, --help) before delegating to
per-command functions. Exits with code 1 on unknown commands.

Args:
    args: sys.argv[1:] with the program name already removed.

**Parameters:**

- `args` (list[str])

**Returns:** None

⚠️ **High complexity:** 15

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

Handle the ``capcat init`` command.

Creates ``.capcat/`` state directory and ``Config/`` scaffold in cwd.
Exits with code 1 if the project is already initialized (unless
``--reinit`` is passed).

Args:
    args: Remaining arguments after ``init`` (e.g. ``["--reinit"]``).

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

⚠️ **High complexity:** 14

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

### _cmd_settings

```python
def _cmd_settings(args: list[str]) -> None
```

Write the Global-settings.yaml template to `Config/` in the current vault.

The file controls vault-wide defaults: network timeouts, image limits, PDF rules,
logging, and UI preferences. Per-source article counts are not set here — edit the
source's own `Config/sources/active/<source>/config.yaml` instead.

**Options:**

- `--force` — Overwrite an existing `Global-settings.yaml` with the latest template.
  All local edits will be lost. Back up the file first if you want to preserve custom
  values. Use after a capcat upgrade to pick up newly added settings.

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

### _auto_init

```python
def _auto_init(command: str) -> None
```

Initialize a capcat project in cwd if not already initialized.

Runs silently before any command except init/help/version.

**Parameters:**

- `command` (str)

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

### _expand_bundles

```python
def _expand_bundles(bundle_names)
```

**Parameters:**

- `bundle_names`

