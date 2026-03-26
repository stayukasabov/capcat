# TUI Menu Bottom Blank Row — Design Spec

## Problem

Every TUI menu screen should show one persistent empty row at the bottom of the
terminal below the entire menu block, matching the visual behaviour of the startup
(main menu) screen. Several screens are missing this row.

## Root Cause

The blank row on the startup screen exists because `menu_lines=10` is 1 greater
than questionary's actual rendered height for that screen (9 lines). The spare row
sits empty below the questionary block.

Other screens lose this row because:
- Screens with `print()` calls between `position_menu_at_bottom` and
  `questionary.select` consume the spare row.
- The source detail mini-menu (line 348) has no `position_menu_at_bottom` call and
  no `instruction=` argument at all.
- Some screens have `menu_lines` exactly equal to actual rendered height.

## Goal

Every `questionary.select` call renders one blank row below its instruction text,
visible while the menu is active.

## Scope

- **File:** `capcat/core/interactive.py`
- **No other files changed**

## Design

### Change 1 — Append trailing `\n` to all existing `instruction=` strings

The instruction is the last line questionary renders. Since all menus use
`position_menu_at_bottom`, the instruction IS the terminal bottom of the menu block.
A trailing `\n` adds one blank row below it, independent of `menu_lines` math and
any `print()` calls above questionary.

```python
# before
instruction="\n   (Use arrow keys to navigate)"
# after
instruction="\n   (Use arrow keys to navigate)\n"
```

Affected call sites (all in `interactive.py`):

| Approx. line | Function |
|---|---|
| 92 | `start_interactive_mode` |
| 143 | `_handle_manage_sources_flow` |
| 305 | `_handle_list_sources` |
| 470 | `_handle_test_source` |
| 541 | `_handle_manage_bundles` (bundle select) |
| 569 | `_handle_manage_bundles` (source assign) |
| 597 | `_handle_single_source_flow` |
| 653 | `_prompt_for_html` |
| 750 | `_show_completion_screen` |

### Change 2 — Add `instruction=` to source detail mini-menu

Line 348 (`_show_source_detail`) has a 2-choice select with no `instruction=`.
Add:

```python
instruction="\n",
```

No nav hint is needed on a 2-choice screen; the `\n` alone provides the blank row
and aligns the visual style with all other menus.

### Change 3 — `menu_lines` adjustments

Two screens are currently tight and need `+1` to prevent questionary from
overflowing into the new blank row:

| Function | Current | New |
|---|---|---|
| `_prompt_for_html` | `menu_lines=8` | `menu_lines=9` |
| `_show_completion_screen` | `menu_lines=10` | `menu_lines=11` |

Screens with `menu_lines=15` have enough headroom and require no change.

## Constraints

- Visual-only change — no logic affected
- No new functions or helpers introduced
- The `position_menu_at_bottom` function itself is not modified

## Testing

No unit test needed. The change is purely cosmetic. Existing `test_tui_completion.py`
tests must continue to pass unmodified.
