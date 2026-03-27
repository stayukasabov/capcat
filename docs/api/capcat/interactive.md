# capcat.core.interactive

**File:** `Application/capcat/core/interactive.py`

## Description

Interactive mode for Capcat.

## Constants

### LOGO

**Value:** `'\n\n       ____\n     / ____|                     _\n    | |     __ _ _ __   ___ __ _| |_\n    | |    / _  |  _ \\ / __/ _  | __|\n    | |___| (_| | |_) | (_| (_| | |_\n     \\_____\\__,_|  __/ \\___\\__,_\\__|\n                | |\n                |_|'`

### _LOGO_ROWS

**Value:** `10`

## Functions

### print_logo

```python
def print_logo(menu_lines = 0)
```

**Parameters:**

- `menu_lines` *optional*

### suppress_logging

```python
def suppress_logging()
```

A context manager to temporarily suppress logging.

### start_interactive_mode

```python
def start_interactive_mode()
```

Starts the interactive user interface.

### _handle_manage_sources_flow

```python
def _handle_manage_sources_flow()
```

Handles the logic for source management submenu.

### _handle_add_source_from_rss

```python
def _handle_add_source_from_rss()
```

Handle adding a new source from RSS feed.

### _handle_generate_config

```python
def _handle_generate_config()
```

Handle generating a custom source config.

### _handle_remove_source

```python
def _handle_remove_source()
```

Handle removing existing sources.

### _handle_list_sources

```python
def _handle_list_sources()
```

Handle listing all available sources with interactive detail view.

### _show_source_detail

```python
def _show_source_detail(source_id, config)
```

Display detailed information about a source and offer to edit article_count.

**Parameters:**

- `source_id`
- `config`

### _edit_source_count

```python
def _edit_source_count(source_id, config)
```

Prompt for a new article_count and write it to the userspace YAML.

**Parameters:**

- `source_id`
- `config`

⚠️ **High complexity:** 14

### _handle_test_source

```python
def _handle_test_source()
```

Handle testing a source.

### _handle_bundle_flow

```python
def _handle_bundle_flow()
```

Handles the logic for the bundle selection flow.

### _handle_fetch_flow

```python
def _handle_fetch_flow()
```

Handles the logic for the fetch (multi-source) flow.

### _handle_single_source_flow

```python
def _handle_single_source_flow()
```

Handles the logic for the single source selection flow.

### _handle_single_url_flow

```python
def _handle_single_url_flow()
```

Handles the logic for the single URL flow.

### _prompt_for_html

```python
def _prompt_for_html(action, selection)
```

Prompts for HTML generation.

**Parameters:**

- `action`
- `selection`

### _confirm_and_execute

```python
def _confirm_and_execute(action, selection, generate_html)
```

Prints a summary and executes the command by calling run_app directly.

**Parameters:**

- `action`
- `selection`
- `generate_html`

⚠️ **High complexity:** 12

### _show_completion_screen

```python
def _show_completion_screen(generate_html: bool, success: bool) -> None
```

Show post-execution screen with status, HTML link, and navigation choices.

Args:
    generate_html: Whether HTML generation was requested.
    success: Whether the command completed without errors.

**Parameters:**

- `generate_html` (bool)
- `success` (bool)

**Returns:** None

### _find_latest_index_html

```python
def _find_latest_index_html() -> 'str | None'
```

Find the most recently modified HTML output file.

Checks both batch fetch index pages (News_*/index.html) and single
article pages (Capcats/*/*/html/article.html), returning whichever
was modified most recently.

Returns:
    Absolute path string to the HTML file, or None if not found.

**Returns:** 'str | None'

### _handle_manage_bundles

```python
def _handle_manage_bundles()
```

Handle bundle management submenu.

⚠️ **High complexity:** 12

