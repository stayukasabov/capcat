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
- Screens with `print()` calls between `position_menu_at_bottom` and the
  questionary prompt consume the spare row.
- The source detail mini-menu (line ~348) has no `position_menu_at_bottom` call
  and no `instruction=` argument at all.
- Some screens have `menu_lines` exactly equal to actual rendered height.

## Goal

Every questionary prompt renders one blank row below its instruction text,
visible while the menu is active, independent of `menu_lines` accuracy.

## Scope

- **File:** `capcat/core/interactive.py` only
- **Applies to:** all questionary prompts that have an `instruction=` argument
  (`questionary.select` and `questionary.checkbox`)
- No other files changed

## Design

### Change 1 — Append trailing `\n` to all existing `instruction=` strings

The instruction is the last line questionary renders. Since all menus use
`position_menu_at_bottom`, the instruction IS the terminal bottom of the menu block.
A trailing `\n` adds one blank row below it, within questionary's own rendering
and independent of `menu_lines` math or extra `print()` calls above the prompt.

```python
# before
instruction="\n   (Use arrow keys to navigate)"
# after
instruction="\n   (Use arrow keys to navigate)\n"
```

Affected call sites (all in `interactive.py`):

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Approx. line</th>
      <th>Prompt type</th>
      <th>Function</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>92</td>
      <td>select</td>
      <td><code>start_interactive_mode</code></td>
    </tr>
    <tr>
      <td>143</td>
      <td>select</td>
      <td><code>_handle_manage_sources_flow</code></td>
    </tr>
    <tr>
      <td>305</td>
      <td>select</td>
      <td><code>_handle_list_sources</code></td>
    </tr>
    <tr>
      <td>470</td>
      <td>select</td>
      <td><code>_handle_test_source</code></td>
    </tr>
    <tr>
      <td>541</td>
      <td>select</td>
      <td><code>_handle_manage_bundles</code> (bundle select)</td>
    </tr>
    <tr>
      <td>569</td>
      <td>**checkbox**</td>
      <td><code>_handle_fetch_flow</code> (source assign)</td>
    </tr>
    <tr>
      <td>597</td>
      <td>select</td>
      <td><code>_handle_single_source_flow</code></td>
    </tr>
    <tr>
      <td>653</td>
      <td>select</td>
      <td><code>_prompt_for_html</code></td>
    </tr>
    <tr>
      <td>750</td>
      <td>select</td>
      <td><code>_show_completion_screen</code></td>
    </tr>
  </tbody>
</table>
</div>

Note: line 569 is a `questionary.checkbox` call. It is included because the same
`instruction=` mechanism applies to checkbox prompts and the same blank-row rule
should hold for all interactive menu-style screens.

### Change 2 — Add `instruction=` to source detail mini-menu (~line 348)

`_show_source_detail` has a 2-choice `questionary.select` with no `instruction=`.
Add:

```python
instruction="\n",
```

**Positioning note:** `position_menu_at_bottom` is intentionally NOT added to this
screen. The detail block above the mini-menu contains a variable number of printed
lines (source config fields vary by source type), making accurate bottom-alignment
impractical. The mini-menu renders wherever the cursor lands after the detail output.
The trailing `\n` in the instruction still provides the blank row below the choices,
consistent with the visual rule, even without bottom-positioning.

### Change 3 — `menu_lines` adjustments

Adding a trailing `\n` increases questionary's rendered height by 1 line. Most
screens have sufficient headroom. The two tight screens that need adjustment:

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Function</th>
      <th>Current</th>
      <th>New</th>
      <th>Reason</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>_prompt_for_html</code></td>
      <td><code>menu_lines=8</code></td>
      <td><code>menu_lines=9</code></td>
      <td>Currently 1 spare row; +1 rendering consumes it</td>
    </tr>
    <tr>
      <td><code>_show_completion_screen</code></td>
      <td><code>menu_lines=10</code></td>
      <td><code>menu_lines=11</code></td>
      <td>Extra <code>print()</code> calls already consume most headroom</td>
    </tr>
  </tbody>
</table>
</div>

`_handle_manage_sources_flow` (`menu_lines=12`) currently has 2 spare rows with its
7-item menu (rendered height ~10). After adding the trailing `\n` it has 1 spare row.
No adjustment needed.

Screens with `menu_lines=15` have ample headroom and require no change.

## Constraints

- Visual-only change — no logic affected
- No new functions or helpers introduced
- `position_menu_at_bottom` itself is not modified

## Testing

No unit test needed. The change is purely cosmetic. Existing `test_tui_completion.py`
tests must continue to pass unmodified.
