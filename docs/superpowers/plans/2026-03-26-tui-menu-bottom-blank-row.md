# TUI Menu Bottom Blank Row Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one persistent blank row below every TUI menu screen by appending a trailing `\n` to all `instruction=` strings in `interactive.py`.

**Architecture:** Pure cosmetic change in a single file. The `instruction=` argument is the last line questionary renders; a trailing `\n` makes the blank row part of questionary's own output, independent of terminal-size math. Two `menu_lines` values are bumped by 1 to absorb the extra rendered line.

**Tech Stack:** Python 3, questionary, existing `position_menu_at_bottom` layout system.

---

## File Map

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Action</th>
      <th>File</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Modify</td>
      <td><code>capcat/core/interactive.py</code></td>
    </tr>
    <tr>
      <td>Test (existing, must pass)</td>
      <td><code>tests/unit/test_tui_completion.py</code></td>
    </tr>
    <tr>
      <td>Test (existing, must pass)</td>
      <td><code>tests/unit/test_tui_*.py</code></td>
    </tr>
  </tbody>
</table>
</div>

No new files created.

---

### Task 1: Branch

- [ ] **Step 1: Create branch**

```bash
cd ~/capcat && git checkout main && git checkout -b fix/tui-menu-bottom-blank-row
```

---

### Task 2: Append trailing `\n` to all nine `instruction=` strings

**Files:**
- Modify: `capcat/core/interactive.py` — lines 92, 143, 305, 470, 541, 569, 597, 653, 750

Each of these lines currently ends with `"`. Change the closing `"` so the string ends with `\n"`.

- [ ] **Step 1: Apply the seven identical `instruction=` changes in one pass**

Seven of the nine strings are identical. Use `replace_all=true` (or equivalent) so all seven are changed in a single edit operation:

```
old: instruction="\n   (Use arrow keys to navigate)",
new: instruction="\n   (Use arrow keys to navigate)\n",
```

This replaces all seven occurrences at once (lines 92, 143, 470, 541, 597, 653, 750).

- [ ] **Step 2: Apply the two unique `instruction=` changes individually**

These two strings are unique — edit each one separately:

```
# line 305 — unique string
old: instruction="\n   (Use arrow keys, Enter to view details)",
new: instruction="\n   (Use arrow keys, Enter to view details)\n",

# line 569 — unique string
old: instruction="\n   (Use Space to select multiple sources, Enter to confirm)",
new: instruction="\n   (Use Space to select multiple sources, Enter to confirm)\n",
```

- [ ] **Step 3: Verify all nine were changed**

```bash
cd ~/capcat && grep -n 'instruction=' capcat/core/interactive.py
```

Expected: all 9 occurrences end with `\n",`. Confirm count is exactly 9.

- [ ] **Step 4: Run tests**

```bash
cd ~/capcat && python3 -m pytest tests/unit/ -q
```

Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add capcat/core/interactive.py
git commit -m "fix: append trailing newline to all instruction strings for bottom blank row"
```

---

### Task 3: Add `instruction="\n"` to source detail mini-menu

**Files:**
- Modify: `capcat/core/interactive.py` — `_show_source_detail` function, the 2-choice `questionary.select` call (~line 348)

This select currently has no `instruction=` argument.

- [ ] **Step 1: Locate the call**

Read lines 345–360 of `capcat/core/interactive.py`. Confirm the `questionary.select` block at ~line 348 has no `instruction=`.

- [ ] **Step 2: Add instruction argument**

Insert `instruction="\n",` after the `pointer="▶",` line in that block:

```python
action = questionary.select(
    "  Options:",
    choices=[
        questionary.Choice("Edit article count", "edit"),
        questionary.Choice("Back", "back"),
    ],
    style=custom_style,
    qmark="",
    pointer="▶",
    instruction="\n",       # ← add this line
).ask()
```

- [ ] **Step 3: Run tests**

```bash
cd ~/capcat && python3 -m pytest tests/unit/ -q
```

Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add capcat/core/interactive.py
git commit -m "fix: add instruction newline to source detail mini-menu for blank row"
```

---

### Task 4: Adjust `menu_lines` on two tight screens

**Files:**
- Modify: `capcat/core/interactive.py` — `_prompt_for_html` (line 639, `menu_lines=8`) and `_show_completion_screen` (line 726, `menu_lines=10`)

- [ ] **Step 1: Locate both calls**

```bash
grep -n 'menu_lines=' capcat/core/interactive.py
```

Confirm:
- `_prompt_for_html` uses `menu_lines=8`
- `_show_completion_screen` uses `menu_lines=10`

- [ ] **Step 2: Bump both values**

**Edit 1** — `_prompt_for_html` (unique, safe to match by value alone):
```
old: position_menu_at_bottom(menu_lines=8)
new: position_menu_at_bottom(menu_lines=9)
```

**Edit 2** — `_show_completion_screen` only. There are two `menu_lines=10` calls in the file (lines 75 and 726). Use the surrounding context unique to line 726 as the `old_string` anchor:
```
old:
    """
    position_menu_at_bottom(menu_lines=10)

    status_label = "Done" if success else "Completed with errors"

new:
    """
    position_menu_at_bottom(menu_lines=11)

    status_label = "Done" if success else "Completed with errors"
```

The `start_interactive_mode` call at line 75 stays at `menu_lines=10` — do not change it.

- [ ] **Step 3: Verify grep shows correct values**

```bash
grep -n 'menu_lines=' capcat/core/interactive.py
```

Expected:
- line 75: `menu_lines=10` (unchanged — startup screen)
- line 127: `menu_lines=12` (unchanged)
- `_prompt_for_html` call: `menu_lines=9` (was 8)
- line 726: `menu_lines=11` (was 10)
- all `menu_lines=15` calls: unchanged

- [ ] **Step 4: Run full test suite**

```bash
cd ~/capcat && python3 -m pytest tests/unit/ -q
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add capcat/core/interactive.py
git commit -m "fix: bump menu_lines on prompt_for_html and completion screen to absorb extra instruction line"
```

---

### Task 5: Merge to main

- [ ] **Step 1: Merge**

```bash
cd ~/capcat && git checkout main && git merge fix/tui-menu-bottom-blank-row
```

- [ ] **Step 2: Run full suite one final time**

```bash
python3 -m pytest tests/unit/ -q
```

Expected: all pass.
