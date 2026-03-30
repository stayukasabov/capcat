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

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Function</th>
      <th>File</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>start_interactive_mode</code></td>
      <td><code>interactive.py</code></td>
    </tr>
    <tr>
      <td><code>_handle_manage_sources_flow</code></td>
      <td><code>interactive.py</code></td>
    </tr>
    <tr>
      <td><code>_handle_list_sources</code> (loop)</td>
      <td><code>interactive.py</code></td>
    </tr>
    <tr>
      <td><code>_handle_test_source</code></td>
      <td><code>interactive.py</code></td>
    </tr>
    <tr>
      <td><code>_handle_bundle_flow</code></td>
      <td><code>interactive.py</code></td>
    </tr>
    <tr>
      <td><code>_handle_fetch_flow</code></td>
      <td><code>interactive.py</code></td>
    </tr>
    <tr>
      <td><code>_handle_single_source_flow</code></td>
      <td><code>interactive.py</code></td>
    </tr>
    <tr>
      <td><code>_handle_single_url_flow</code></td>
      <td><code>interactive.py</code></td>
    </tr>
    <tr>
      <td><code>_prompt_for_html</code></td>
      <td><code>interactive.py</code></td>
    </tr>
    <tr>
      <td><code>_show_completion_screen</code></td>
      <td><code>interactive.py</code></td>
    </tr>
    <tr>
      <td><code>show_bundle_menu</code></td>
      <td><code>bundle_ui.py</code></td>
    </tr>
    <tr>
      <td><code>prompt_select_bundle</code></td>
      <td><code>bundle_ui.py</code></td>
    </tr>
    <tr>
      <td><code>prompt_select_sources</code></td>
      <td><code>bundle_ui.py</code></td>
    </tr>
    <tr>
      <td><code>prompt_copy_or_move</code></td>
      <td><code>bundle_ui.py</code></td>
    </tr>
  </tbody>
</table>
</div>

**Intentional exclusion:** `_show_source_detail` in `interactive.py` contains a
`questionary.select` call but does NOT get `print_logo()`. This screen renders
inline immediately after a block of printed source detail fields; clearing the
screen would wipe the detail output the user just read. This exclusion is by
design, not an oversight.

### `position_menu_at_bottom` removed

The function definition (currently at lines 41–68 of `interactive.py`) is deleted
as part of this implementation. It has no remaining callers after v1.5.6.

## Constraints

- No `pyfiglet` runtime dependency — string is hardcoded
- No `menu_lines` math — not needed with inline render
- `_show_source_detail` mini-menu: intentionally excluded — see call sites table above
- Visual-only change — no fetch, source, or bundle logic touched

## Testing

No new unit tests. Existing `tests/unit/` suite must pass unmodified.
