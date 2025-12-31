# core.interactive

**File:** `Application/core/interactive.py`

## Description

Interactive mode for Capcat.

## Functions

### suppress_logging

```python
def suppress_logging()
```

A context manager to temporarily suppress logging.

### position_menu_at_bottom

```python
def position_menu_at_bottom(menu_lines = 10)
```

Position cursor for bottom-aligned menu display.

Args:
    menu_lines: Number of lines the menu will occupy (default: 10)

**Parameters:**

- `menu_lines` *optional*

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

Handle listing all available sources.

### _show_source_details

```python
def _show_source_details(source_id, registry)
```

Display detailed information about a source.

**Parameters:**

- `source_id`
- `registry`

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

### _handle_manage_bundles

```python
def _handle_manage_bundles()
```

Handle bundle management submenu.

⚠️ **High complexity:** 11

