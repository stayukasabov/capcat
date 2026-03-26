# TUI Logo — dos_rebel Font Design Spec

## Problem

`position_menu_at_bottom` was removed in v1.5.6 (inline render refactor). The ASCII
logo that it displayed is now gone from every screen.

## Goal

Restore a persistent logo at the top of every TUI screen. Logo renders once per
screen: clear → logo → blank line → questionary inline below. Standard TUI header
pattern.

## Scope

- **Files:** `capcat/core/interactive.py`, `capcat/core/source_system/bundle_ui.py`
- No new dependencies — logo string hardcoded

## Design

### Logo

Font: `dos_rebel` (pyfiglet), text: `"Capcat"`, 11 lines × 62 chars wide.
Color: `\033[38;5;202m` (orange — same as menu pointer and selected item).

Exact string (trailing spaces preserved per-line):

```
   █████████                                          █████
  ███░░░░░███                                        ░░███
 ███     ░░░   ██████   ████████   ██████   ██████   ███████
░███          ░░░░░███ ░░███░░███ ███░░███ ░░░░░███ ░░░███░
░███           ███████  ░███ ░███░███ ░░░   ███████   ░███
░░███     ███ ███░░███  ░███ ░███░███  ███ ███░░███   ░███ ███
 ░░█████████ ░░████████ ░███████ ░░██████ ░░████████  ░░█████
  ░░░░░░░░░   ░░░░░░░░  ░███░░░   ░░░░░░   ░░░░░░░░    ░░░░░
                        ░███
                        █████
                       ░░░░░
```

### `print_logo()` function

Replaces `position_menu_at_bottom`. No `menu_lines` argument. No terminal size math.

```python
def print_logo():
    print('\033[2J\033[H', end='')
    print('\033[38;5;202m' + LOGO + '\033[0m')
    print()
```

`LOGO` is a module-level constant — the exact dos_rebel string above.

### Call sites

`print_logo()` is called immediately before every `questionary.select` /
`questionary.checkbox` prompt. Fourteen call sites:

| Function | File |
|---|---|
| `start_interactive_mode` | `interactive.py` |
| `_handle_manage_sources_flow` | `interactive.py` |
| `_handle_list_sources` (loop) | `interactive.py` |
| `_handle_test_source` | `interactive.py` |
| `_handle_bundle_flow` | `interactive.py` |
| `_handle_fetch_flow` | `interactive.py` |
| `_handle_single_source_flow` | `interactive.py` |
| `_handle_single_url_flow` | `interactive.py` |
| `_prompt_for_html` | `interactive.py` |
| `_show_completion_screen` | `interactive.py` |
| `show_bundle_menu` | `bundle_ui.py` |
| `prompt_select_bundle` | `bundle_ui.py` |
| `prompt_select_sources` | `bundle_ui.py` |
| `prompt_copy_or_move` | `bundle_ui.py` |

**Intentional exclusion:** `_show_source_detail` in `interactive.py` contains a
`questionary.select` call but does NOT get `print_logo()`. This screen renders
inline immediately after a block of printed source detail fields; clearing the
screen would wipe the detail output the user just read. This exclusion is by
design, not an oversight.

### `position_menu_at_bottom` removed

The function definition is deleted from `interactive.py`. It has no remaining
callers after v1.5.6.

## Constraints

- No `pyfiglet` runtime dependency — string is hardcoded
- No `menu_lines` math — not needed with inline render
- `_show_source_detail` mini-menu: intentionally excluded — see call sites table above
- Visual-only change — no fetch, source, or bundle logic touched

## Testing

No new unit tests. Existing `tests/unit/` suite must pass unmodified.
