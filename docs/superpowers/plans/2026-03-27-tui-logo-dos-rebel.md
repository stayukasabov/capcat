# TUI Logo dos_rebel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the removed `position_menu_at_bottom` logo with a new `print_logo()` function using the dos_rebel font, called at all 14 questionary screens.

**Architecture:** Add a `LOGO` module-level constant and `print_logo()` to `interactive.py`. Delete `position_menu_at_bottom`. Call `print_logo()` before every questionary prompt in both `interactive.py` and `bundle_ui.py`.

**Tech Stack:** Python 3, questionary, ANSI escape codes. No new dependencies.

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
      <td>Modify</td>
      <td><code>capcat/core/source_system/bundle_ui.py</code></td>
    </tr>
    <tr>
      <td>Test (must pass)</td>
      <td><code>tests/unit/</code> (full suite)</td>
    </tr>
  </tbody>
</table>
</div>

---

### Task 1: Branch

- [ ] **Step 1: Create branch**

```bash
cd ~/capcat && git checkout main && git checkout -b feat/tui-logo-dos-rebel
```

---

### Task 2: Add LOGO constant and print_logo(), delete position_menu_at_bottom

**Files:**
- Modify: `capcat/core/interactive.py` — lines 27–68

- [ ] **Step 1: Replace the blank line + position_menu_at_bottom block with LOGO constant and print_logo()**

In `capcat/core/interactive.py`, replace this block (lines 28–68):

```python


@contextlib.contextmanager
```

...through the end of `position_menu_at_bottom` (line 68), replacing with:

```python

LOGO = (
    "   █████████                                          █████   \n"
    "  ███░░░░░███                                        ░░███    \n"
    " ███     ░░░   ██████   ████████   ██████   ██████   ███████  \n"
    "░███          ░░░░░███ ░░███░░███ ███░░███ ░░░░░███ ░░░███░   \n"
    "░███           ███████  ░███ ░███░███ ░░░   ███████   ░███    \n"
    "░░███     ███ ███░░███  ░███ ░███░███  ███ ███░░███   ░███ ███\n"
    " ░░█████████ ░░████████ ░███████ ░░██████ ░░████████  ░░█████ \n"
    "  ░░░░░░░░░   ░░░░░░░░  ░███░░░   ░░░░░░   ░░░░░░░░    ░░░░░  \n"
    "                        ░███                                  \n"
    "                        █████                                 \n"
    "                       ░░░░░                                  "
)


def print_logo():
    print('\033[2J\033[H', end='')
    print('\033[38;5;202m' + LOGO + '\033[0m')
    print()


@contextlib.contextmanager
```

Also remove the `import shutil` line (line 9) since it was only used by `position_menu_at_bottom`.

- [ ] **Step 2: Run tests**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/ -q
```

Expected: all pass.

- [ ] **Step 3: Commit**

```bash
cd ~/capcat && git add capcat/core/interactive.py
git commit -m "feat: add LOGO constant and print_logo(), remove position_menu_at_bottom"
```

---

### Task 3: Add print_logo() calls — interactive.py (10 sites)

**Files:**
- Modify: `capcat/core/interactive.py`

Add `print_logo()` immediately before each questionary prompt call. One edit per function.

- [ ] **Step 1: start_interactive_mode**

```python
# before
        with suppress_logging():
            prompt_text = "  What would you like me to do?" if first_run else "  Select an option:"
            action = questionary.select(

# after
        print_logo()
        with suppress_logging():
            prompt_text = "  What would you like me to do?" if first_run else "  Select an option:"
            action = questionary.select(
```

- [ ] **Step 2: _handle_manage_sources_flow**

```python
# before
    while True:
        with suppress_logging():
            action = questionary.select(
                "  Source Management - Select an option:",

# after
    while True:
        print_logo()
        with suppress_logging():
            action = questionary.select(
                "  Source Management - Select an option:",
```

- [ ] **Step 3: _handle_list_sources**

```python
# before
    while True:
        with suppress_logging():
            selected = questionary.select(
                "  Browse sources (select to view details):",

# after
    while True:
        print_logo()
        with suppress_logging():
            selected = questionary.select(
                "  Browse sources (select to view details):",
```

- [ ] **Step 4: _handle_test_source**

```python
# before
    with suppress_logging():
        source_id = questionary.select(
            "  Select source to test:",

# after
    print_logo()
    with suppress_logging():
        source_id = questionary.select(
            "  Select source to test:",
```

- [ ] **Step 5: _handle_bundle_flow**

```python
# before
    with suppress_logging():
        bundle = questionary.select(
            "  Select a news bundle and hit Enter for activation.",

# after
    print_logo()
    with suppress_logging():
        bundle = questionary.select(
            "  Select a news bundle and hit Enter for activation.",
```

- [ ] **Step 6: _handle_fetch_flow**

```python
# before
    with suppress_logging():
        selected_sources = questionary.checkbox(
            "  Select sources (Space to select, Enter to confirm):",

# after
    print_logo()
    with suppress_logging():
        selected_sources = questionary.checkbox(
            "  Select sources (Space to select, Enter to confirm):",
```

- [ ] **Step 7: _handle_single_source_flow**

```python
# before
    with suppress_logging():
        source = questionary.select(
            "  Select a source and hit Enter for activation.",

# after
    print_logo()
    with suppress_logging():
        source = questionary.select(
            "  Select a source and hit Enter for activation.",
```

- [ ] **Step 8: _handle_single_url_flow**

```python
# before
    print("  (Use Ctrl+C to go to the Main Menu)")

# after
    print_logo()
    print("  (Use Ctrl+C to go to the Main Menu)")
```

- [ ] **Step 9: _prompt_for_html**

```python
# before
    with suppress_logging():
        response = questionary.select(
            "  Generate HTML for web browsing?",

# after
    print_logo()
    with suppress_logging():
        response = questionary.select(
            "  Generate HTML for web browsing?",
```

- [ ] **Step 10: _show_completion_screen**

```python
# before
    status_label = "Done" if success else "Completed with errors"

# after
    print_logo()
    status_label = "Done" if success else "Completed with errors"
```

- [ ] **Step 11: Run tests**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/ -q
```

Expected: all pass.

- [ ] **Step 12: Commit**

```bash
cd ~/capcat && git add capcat/core/interactive.py
git commit -m "feat: add print_logo() to all interactive.py questionary screens"
```

---

### Task 4: Add print_logo() calls — bundle_ui.py (4 sites)

**Files:**
- Modify: `capcat/core/source_system/bundle_ui.py`

Use a lazy import to avoid circular imports. Add once at the top of each method.

- [ ] **Step 1: show_bundle_menu**

```python
# before
        return questionary.select(
            "  Bundle Management - Select an option:",

# after
        from capcat.core.interactive import print_logo
        print_logo()
        return questionary.select(
            "  Bundle Management - Select an option:",
```

- [ ] **Step 2: prompt_select_bundle**

```python
# before
        selected = questionary.select(
            message,
            choices=choices,
            style=self.style,
            qmark="",
            pointer="▶",
        ).ask()

# after
        from capcat.core.interactive import print_logo
        print_logo()
        selected = questionary.select(
            message,
            choices=choices,
            style=self.style,
            qmark="",
            pointer="▶",
        ).ask()
```

- [ ] **Step 3: prompt_select_sources**

```python
# before
        selected = questionary.checkbox(
            message,
            choices=choices,
            style=self.style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use Space to select, Enter to confirm)",
        ).ask()

# after
        from capcat.core.interactive import print_logo
        print_logo()
        selected = questionary.checkbox(
            message,
            choices=choices,
            style=self.style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use Space to select, Enter to confirm)",
        ).ask()
```

- [ ] **Step 4: prompt_copy_or_move**

```python
# before
        return questionary.select(
            "  Copy or Move?",

# after
        from capcat.core.interactive import print_logo
        print_logo()
        return questionary.select(
            "  Copy or Move?",
```

- [ ] **Step 5: Run tests**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/ -q
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
cd ~/capcat && git add capcat/core/source_system/bundle_ui.py
git commit -m "feat: add print_logo() to all bundle_ui.py questionary screens"
```

---

### Task 5: Merge to main and release

- [ ] **Step 1: Merge**

```bash
cd ~/capcat && git checkout main && git merge feat/tui-logo-dos-rebel
```

- [ ] **Step 2: Run full suite**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/ -q
```

Expected: all pass.

- [ ] **Step 3: Bump version, tag, push**

```bash
# Edit capcat/__init__.py: bump __version__ from "1.5.6" to "1.5.7"
git add capcat/__init__.py
git commit -m "bump: version to 1.5.7"
git tag v1.5.7
git push origin main && git push origin v1.5.7
```

- [ ] **Step 4: Regenerate docs**

```bash
cd ~/capcat && source venv/bin/activate && python3 scripts/run_docs.py
git add docs/ && git commit -m "docs: regenerate API docs for v1.5.7"
git push origin main
```
