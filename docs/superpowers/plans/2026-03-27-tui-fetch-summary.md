# TUI Fetch Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Suppress per-article WARNING logs in TUI mode and show a single "47 saved, 3 skipped (2 JS-rendered, 1 blocked)" summary line on the completion screen.

**Architecture:** Use the existing `is_tui_active()` context flag to suppress warnings at their source in `NewsSourceArticleFetcher._fetch_web_content`. Accumulate per-article outcomes via a thread-safe side-channel in `tui_context.py` (a new `record_fetch_result()` function). After dispatch completes, `_confirm_and_execute` reads the accumulated `FetchResult` and passes it to `_show_completion_screen`. No return signature changes anywhere — zero blast radius outside the four touched files.

**Tech Stack:** Python 3.11, `threading.Lock`, `dataclasses`, `collections.Counter`, `unittest.mock`

---

## File Structure

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>File</th>
      <th>Change</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>capcat/core/unified_source_processor.py</code></td>
      <td>Add <code>FetchResult</code> dataclass</td>
    </tr>
    <tr>
      <td><code>capcat/core/tui_context.py</code></td>
      <td>Add thread-safe accumulation functions</td>
    </tr>
    <tr>
      <td><code>capcat/core/article_fetcher.py</code></td>
      <td>Suppress warnings + record results in <code>NewsSourceArticleFetcher._fetch_web_content</code></td>
    </tr>
    <tr>
      <td><code>capcat/core/interactive.py</code></td>
      <td>Wire accumulation in <code>_confirm_and_execute</code>; render summary in <code>_show_completion_screen</code></td>
    </tr>
    <tr>
      <td><code>tests/unit/test_tui_completion.py</code></td>
      <td>Update 3 call-arg assertions to match new <code>fetch_result</code> param</td>
    </tr>
    <tr>
      <td><code>tests/unit/test_tui_fetch_summary.py</code></td>
      <td>New — tests for <code>FetchResult</code> and summary rendering</td>
    </tr>
  </tbody>
</table>
</div>

---

### Task 0: Create feature branch

**Files:** none

- [ ] **Step 1: Create branch**

```bash
cd ~/capcat && git checkout -b feat/tui-fetch-summary
```

Expected: `Switched to a new branch 'feat/tui-fetch-summary'`

---

### Task 1: FetchResult dataclass

**Files:**
- Modify: `capcat/core/unified_source_processor.py:1-15` (imports / top of file)

- [ ] **Step 1: Write the failing test**

In `tests/unit/test_tui_fetch_summary.py` (create new file):

```python
"""Tests for FetchResult construction and summary rendering."""
import pytest
from capcat.core.unified_source_processor import FetchResult


def test_fetch_result_saved_only():
    fr = FetchResult(saved=5, skipped=[])
    assert fr.saved == 5
    assert fr.skipped == []


def test_fetch_result_with_skipped():
    fr = FetchResult(saved=3, skipped=[("blocked", 2), ("JS-rendered", 1)])
    assert fr.saved == 3
    assert ("blocked", 2) in fr.skipped


def test_fetch_result_all_skipped():
    fr = FetchResult(saved=0, skipped=[("no content", 3)])
    assert fr.saved == 0
    assert fr.skipped[0] == ("no content", 3)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/test_tui_fetch_summary.py -v
```

Expected: `ImportError` — `FetchResult` not defined yet.

- [ ] **Step 3: Add `FetchResult` to `unified_source_processor.py`**

At the top of the file, after the existing imports, add:

```python
from dataclasses import dataclass, field


@dataclass
class FetchResult:
    saved: int
    skipped: list[tuple[str, int]] = field(default_factory=list)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/test_tui_fetch_summary.py::test_fetch_result_saved_only tests/unit/test_tui_fetch_summary.py::test_fetch_result_with_skipped tests/unit/test_tui_fetch_summary.py::test_fetch_result_all_skipped -v
```

Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
cd ~/capcat && git add capcat/core/unified_source_processor.py tests/unit/test_tui_fetch_summary.py
git commit -m "feat: add FetchResult dataclass"
```

---

### Task 2: Thread-safe accumulation in tui_context

**Files:**
- Modify: `capcat/core/tui_context.py`

The current file (20 lines) has `_tui_active: bool` and two functions. We add a thread-safe list for per-article outcomes.

- [ ] **Step 1: Write the failing tests**

Add to `tests/unit/test_tui_fetch_summary.py`:

```python
from capcat.core.tui_context import (
    reset_fetch_results,
    record_fetch_result,
    get_fetch_result,
)


def test_record_and_get_empty():
    reset_fetch_results()
    fr = get_fetch_result()
    assert fr.saved == 0
    assert fr.skipped == []


def test_record_successes():
    reset_fetch_results()
    record_fetch_result(True, None)
    record_fetch_result(True, None)
    fr = get_fetch_result()
    assert fr.saved == 2
    assert fr.skipped == []


def test_record_mixed():
    reset_fetch_results()
    record_fetch_result(True, None)
    record_fetch_result(False, "blocked")
    record_fetch_result(False, "JS-rendered")
    record_fetch_result(False, "blocked")
    fr = get_fetch_result()
    assert fr.saved == 1
    skipped_dict = dict(fr.skipped)
    assert skipped_dict["blocked"] == 2
    assert skipped_dict["JS-rendered"] == 1


def test_reset_clears_previous():
    reset_fetch_results()
    record_fetch_result(True, None)
    record_fetch_result(True, None)
    reset_fetch_results()
    fr = get_fetch_result()
    assert fr.saved == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/test_tui_fetch_summary.py -k "record_and_get or record_successes or record_mixed or reset_clears" -v
```

Expected: `ImportError` — functions not defined yet.

- [ ] **Step 3: Add accumulation to `tui_context.py`**

Replace the entire content of `capcat/core/tui_context.py` with:

```python
"""TUI context flag and per-fetch result accumulation.

Tracks whether the process is currently running inside the interactive TUI.
Used to suppress prompts and per-article warnings that would corrupt
questionary's terminal state when called via _dispatch inside the TUI.
"""
import threading
from collections import Counter

_tui_active: bool = False
_tui_results_lock = threading.Lock()
_tui_results: list[tuple[bool, "str | None"]] = []


def set_tui_active(active: bool) -> None:
    """Set the TUI-active flag. Called by the TUI on entry and exit."""
    global _tui_active
    _tui_active = active


def is_tui_active() -> bool:
    """Return True if the TUI is currently running."""
    return _tui_active


def reset_fetch_results() -> None:
    """Clear accumulated fetch results. Call before each fetch dispatch."""
    with _tui_results_lock:
        _tui_results.clear()


def record_fetch_result(success: bool, reason: "str | None") -> None:
    """Record one article outcome. Thread-safe. No-op outside TUI."""
    with _tui_results_lock:
        _tui_results.append((success, reason))


def get_fetch_result() -> "FetchResult":
    """Build and return a FetchResult from accumulated outcomes."""
    from capcat.core.unified_source_processor import FetchResult
    with _tui_results_lock:
        saved = sum(1 for ok, r in _tui_results if r is None and ok)
        counts = Counter(r for ok, r in _tui_results if r is not None)
    return FetchResult(saved=saved, skipped=list(counts.items()))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/test_tui_fetch_summary.py -v
```

Expected: all tests that exist so far PASS.

- [ ] **Step 5: Run full unit suite**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/ -q
```

Expected: all PASS (no regressions).

- [ ] **Step 6: Commit**

```bash
cd ~/capcat && git add capcat/core/tui_context.py tests/unit/test_tui_fetch_summary.py
git commit -m "feat: add thread-safe fetch result accumulation to tui_context"
```

---

### Task 3: Warning suppression + result recording in `NewsSourceArticleFetcher._fetch_web_content`

**Files:**
- Modify: `capcat/core/article_fetcher.py:2802-3182`

The method currently has these failure paths. For each one: (a) demote `self.logger.warning` to `self.logger.debug` when `is_tui_active()`, and (b) call `record_fetch_result(False, reason)` before returning.

Failure → reason string mappings:
- Timeout (line 2830) → `"timeout"`
- HTTP 403 (line 2833-2836) → `"blocked"`
- HTTP 404 (line 2837-2840) → `"not found"`
- HTTP 429, 5xx, other (lines 2841-2852) → `"error"`
- `ConnectionError` (line 2854-2857) → `"error"`
- `RequestException` (line 2859-2861) → `"error"`
- `Exception` (line 2862-2864) → `"error"`
- HTML parse failure (line 2873-2874) → `"error"`
- SPA detection (line 2890-2894) → `"JS-rendered"`
- HTML conversion failure (line 2962-2966) → `"error"`
- Empty markdown (line 2968-2970) → `"no content"`
- Directory creation errors (lines 2983-2997) → `"error"`
- File write errors (lines 2066-3083) → `"error"`
- Success (line 3182) → `record_fetch_result(True, None)`

- [ ] **Step 1: Write the failing tests**

Add to `tests/unit/test_tui_fetch_summary.py`:

```python
import requests
from unittest.mock import patch, MagicMock
from capcat.core.tui_context import reset_fetch_results, get_fetch_result, set_tui_active


def _make_fetcher():
    """Create a minimal NewsSourceArticleFetcher for testing."""
    from capcat.core.article_fetcher import NewsSourceArticleFetcher
    session = MagicMock(spec=requests.Session)
    config = {
        "name": "test",
        "source_id": "test",
        "content_selectors": ["body"],
        "skip_patterns": [],
    }
    return NewsSourceArticleFetcher(config, session)


def test_tui_suppresses_timeout_warning():
    """In TUI mode, timeout does not emit WARNING and records reason."""
    fetcher = _make_fetcher()
    set_tui_active(True)
    reset_fetch_results()
    try:
        with patch.object(fetcher, "_fetch_url_with_retry",
                          side_effect=requests.exceptions.Timeout()):
            with patch.object(fetcher, "_check_pdf_size_and_prompt", return_value=False):
                fetcher.session.get = MagicMock(side_effect=requests.exceptions.Timeout())
                result = fetcher._fetch_web_content("T", "http://x.com/a", 0, "/tmp")
        fr = get_fetch_result()
        assert fr.skipped == [("timeout", 1)]
        assert result == (False, None, None)
    finally:
        set_tui_active(False)


def test_tui_suppresses_403_warning():
    """In TUI mode, HTTP 403 does not emit WARNING and records 'blocked'."""
    fetcher = _make_fetcher()
    set_tui_active(True)
    reset_fetch_results()
    try:
        http_err = requests.exceptions.HTTPError(response=MagicMock(status_code=403))
        fetcher.session.get = MagicMock(side_effect=http_err)
        with patch.object(fetcher, "_fetch_url_with_retry", side_effect=http_err):
            result = fetcher._fetch_web_content("T", "http://x.com/a", 0, "/tmp")
        fr = get_fetch_result()
        assert dict(fr.skipped)["blocked"] == 1
        assert result == (False, None, None)
    finally:
        set_tui_active(False)


def test_tui_records_spa_as_js_rendered():
    """SPA detection records 'JS-rendered' reason in TUI mode."""
    fetcher = _make_fetcher()
    set_tui_active(True)
    reset_fetch_results()
    try:
        spa_html = '<html><body><div id="root"></div></body></html>'
        mock_resp = MagicMock()
        mock_resp.text = spa_html
        mock_resp.headers = {"Content-Type": "text/html"}
        with patch.object(fetcher, "_fetch_url_with_retry", return_value=mock_resp):
            result = fetcher._fetch_web_content("T", "http://spa.com/a", 0, "/tmp")
        fr = get_fetch_result()
        assert dict(fr.skipped).get("JS-rendered", 0) == 1
    finally:
        set_tui_active(False)


def test_cli_mode_does_not_record():
    """Outside TUI mode, a failed fetch does NOT record anything."""
    # Ensure TUI is inactive (default)
    reset_fetch_results()
    fetcher = _make_fetcher()
    # Trigger a timeout failure without TUI active
    with patch.object(fetcher, "_fetch_url_with_retry",
                      side_effect=requests.exceptions.Timeout()):
        fetcher._fetch_web_content("T", "http://x.com/a", 0, "/tmp")
    fr = get_fetch_result()
    # Nothing should be recorded — guard is conditional on is_tui_active()
    assert fr.saved == 0
    assert fr.skipped == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/test_tui_fetch_summary.py -k "suppresses or records or cli_mode" -v
```

Expected: FAIL — warning suppression and recording not yet implemented.

- [ ] **Step 3: Add imports at top of `article_fetcher.py`**

Find the existing import block near the top of `capcat/core/article_fetcher.py`. Add after the existing imports:

```python
from capcat.core.tui_context import is_tui_active, record_fetch_result
```

- [ ] **Step 4: Update all failure paths in `NewsSourceArticleFetcher._fetch_web_content`**

In `capcat/core/article_fetcher.py`, locate `NewsSourceArticleFetcher._fetch_web_content` (at line ~2802). Apply the following changes to each failure path:

**Timeout (around line 2829-2831):**
```python
        except requests.exceptions.Timeout:
            if is_tui_active():
                self.logger.debug(f"Timeout fetching article content from {url}")
                record_fetch_result(False, "timeout")
            else:
                self.logger.warning(f"Timeout fetching article content from {url}")
            return False, None, None
```

**HTTP errors (around lines 2832-2853):**
```python
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                reason = "blocked"
                msg = f"Access forbidden for article {url} - anti-bot protection detected"
            elif e.response.status_code == 404:
                reason = "not found"
                msg = f"Article not found at {url} - may have been deleted"
            elif e.response.status_code == 429:
                reason = "error"
                msg = f"Rate limited accessing {url} - try reducing request frequency"
            elif e.response.status_code >= 500:
                reason = "error"
                msg = f"Server error ({e.response.status_code}) fetching {url} - temporary issue"
            else:
                reason = "error"
                msg = f"HTTP error {e.response.status_code} fetching {url}"
            if is_tui_active():
                self.logger.debug(msg)
                record_fetch_result(False, reason)
            else:
                self.logger.warning(msg)
            return False, None, None
```

**ConnectionError (around line 2854-2858):**
```python
        except requests.exceptions.ConnectionError:
            if is_tui_active():
                self.logger.debug(f"Connection error fetching {url} - network may be unavailable")
                record_fetch_result(False, "error")
            else:
                self.logger.warning(f"Connection error fetching {url} - network may be unavailable")
            return False, None, None
```

**RequestException (around lines 2859-2861):**
```python
        except requests.exceptions.RequestException as e:
            if is_tui_active():
                self.logger.debug(f"Request error fetching {url}: {e}")
                record_fetch_result(False, "error")
            else:
                self.logger.warning(f"Request error fetching {url}: {e}")
            return False, None, None
```

**Unexpected Exception (around lines 2862-2864):**
```python
        except Exception as e:
            if is_tui_active():
                self.logger.debug(f"Unexpected error fetching {url}: {e}")
                record_fetch_result(False, "error")
            else:
                self.logger.error(f"Unexpected error fetching {url}: {e}")
            return False, None, None
```

**SPA detection (around lines 2888-2894):**
```python
            if spa_root and len(body_text) < 100:
                if is_tui_active():
                    self.logger.debug(
                        f"JavaScript-rendered page at {url} - cannot extract without browser"
                    )
                    record_fetch_result(False, "JS-rendered")
                else:
                    self.logger.warning(
                        f"JavaScript-rendered page at {url} - content requires "
                        f"browser execution and cannot be extracted"
                    )
                return False, None, None
```

**Empty markdown (around lines 2968-2970):**
```python
        if not markdown_content:
            if is_tui_active():
                self.logger.debug(f"Empty markdown for {url}")
                record_fetch_result(False, "no content")
            else:
                self.logger.warning(f"Empty markdown for {url}")
            return False, None, None
```

**All `return False, None, None` paths after the file-write block (directory/file errors) — these are already at `error` level, not WARNING. Add recording only:**
```python
# Before each remaining `return False, None, None` that follows an
# self.logger.error(...) call in the directory/file write sections:
if is_tui_active():
    record_fetch_result(False, "error")
return False, None, None
```

**Success path (line ~3182):**
```python
        self.logger.info(f"Saved article: {page_title}")
        if is_tui_active():
            record_fetch_result(True, None)
        return True, filename, article_folder_path
```

- [ ] **Step 5: Run the new tests**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/test_tui_fetch_summary.py -v
```

Expected: all PASS.

- [ ] **Step 6: Run full unit suite**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/ -q
```

Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
cd ~/capcat && git add capcat/core/article_fetcher.py tests/unit/test_tui_fetch_summary.py
git commit -m "feat: suppress per-article warnings in TUI mode and record fetch outcomes"
```

---

### Task 4: Summary rendering in `_show_completion_screen` + wiring in `_confirm_and_execute`

**Files:**
- Modify: `capcat/core/interactive.py`
- Modify: `tests/unit/test_tui_completion.py`

- [ ] **Step 1: Write failing tests for summary rendering**

Add to `tests/unit/test_tui_fetch_summary.py`:

```python
from unittest.mock import patch
from capcat.core.unified_source_processor import FetchResult


def _run_show_completion(generate_html, success, fetch_result=None):
    """Run _show_completion_screen with menu choice patched to 'menu'."""
    with patch("questionary.select") as mock_q, \
         patch("capcat.core.interactive._find_latest_index_html", return_value=None), \
         patch("builtins.print") as mock_print:
        mock_q.return_value.ask.return_value = "menu"
        from capcat.core.interactive import _show_completion_screen
        _show_completion_screen(generate_html, success, fetch_result=fetch_result)
    return [str(c) for c in mock_print.call_args_list]


def test_completion_no_summary_when_no_fetch_result():
    """No summary line when fetch_result is None."""
    lines = _run_show_completion(False, True, fetch_result=None)
    assert not any("saved" in l for l in lines)


def test_completion_summary_saved_only():
    """'47 saved' shown when nothing skipped."""
    fr = FetchResult(saved=47, skipped=[])
    lines = _run_show_completion(False, True, fetch_result=fr)
    assert any("47 saved" in l for l in lines)
    assert not any("skipped" in l for l in lines)


def test_completion_summary_with_skipped():
    """'47 saved, 3 skipped (2 blocked, 1 JS-rendered)' shown when skipped > 0."""
    fr = FetchResult(saved=47, skipped=[("blocked", 2), ("JS-rendered", 1)])
    lines = _run_show_completion(False, True, fetch_result=fr)
    combined = " ".join(lines)
    assert "47 saved" in combined
    assert "3 skipped" in combined
    assert "blocked" in combined


def test_completion_no_summary_when_zero_zero():
    """No summary when saved=0 and skipped=0 (source returned no articles)."""
    fr = FetchResult(saved=0, skipped=[])
    lines = _run_show_completion(False, True, fetch_result=fr)
    assert not any("saved" in l for l in lines)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/test_tui_fetch_summary.py -k "completion" -v
```

Expected: FAIL — `_show_completion_screen` does not accept `fetch_result` yet.

- [ ] **Step 3: Update `_show_completion_screen` in `capcat/core/interactive.py`**

Locate `_show_completion_screen` (currently at line ~708). Change its signature and add summary rendering:

```python
def _show_completion_screen(
    generate_html: bool,
    success: bool,
    fetch_result=None,
) -> None:
    """Show post-execution screen with status, HTML link, and navigation choices.

    Args:
        generate_html: Whether HTML generation was requested.
        success: Whether the command completed without errors.
        fetch_result: Optional FetchResult with saved/skipped counts (TUI only).
    """
    print_logo()
    status_label = "Done" if success else "Completed with errors"
    print(f"\n  {status_label}")

    if fetch_result is not None:
        saved = fetch_result.saved
        total_skipped = sum(n for _, n in fetch_result.skipped)
        if saved > 0 or total_skipped > 0:
            if total_skipped == 0:
                print(f"\n  {saved} saved")
            else:
                parts = ", ".join(
                    f"{n} {r}" for r, n in fetch_result.skipped
                )
                print(f"\n  {saved} saved, {total_skipped} skipped ({parts})")

    if generate_html:
        html_path = _find_latest_index_html()
        if html_path:
            print(f"\n  HTML index: file://{html_path}")
        else:
            print("\n  HTML index: not found")

    print()

    with suppress_logging():
        choice = questionary.select(
            "  What would you like to do next?",
            choices=[
                questionary.Choice("Back to Main Menu", "menu"),
                questionary.Choice("Exit", "exit"),
            ],
            style=custom_style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use arrow keys to navigate)",
        ).ask()

    if not choice or choice == "exit":
        print("Exiting interactive mode.")
        sys.exit(0)
    # choice == "menu": return, call stack unwinds to start_interactive_mode() while loop
```

- [ ] **Step 4: Update `_confirm_and_execute` in `capcat/core/interactive.py`**

Locate `_confirm_and_execute` (currently at line ~651). Add import and wiring:

At the top of the function body (after the `summary` lines), add the import guard:

```python
def _confirm_and_execute(action, selection, generate_html):
    """Prints a summary and executes the command by calling run_app directly."""
    from capcat.core.tui_context import is_tui_active, reset_fetch_results, get_fetch_result

    summary = f"Action: {action}\n"
    # ... (existing summary lines unchanged) ...

    # (existing args construction unchanged)

    # Reset accumulator before fetch (TUI only)
    if is_tui_active():
        reset_fetch_results()

    success = True
    try:
        print("Executing command...")
        from capcat.cli import _dispatch
        _dispatch(args)
    except SystemExit as e:
        if e.code != 0:
            print(f"\nCommand finished with error code: {e.code}")
            success = False
    except Exception as e:
        print(f"\nError: {e}")
        success = False

    fetch_result = get_fetch_result() if is_tui_active() else None
    _show_completion_screen(generate_html, success, fetch_result=fetch_result)
```

- [ ] **Step 5: Update `tests/unit/test_tui_completion.py` call-arg assertions**

Three `assert_called_once_with` checks currently verify `_show_completion_screen` is called with `(bool, bool)`. After our change, `_confirm_and_execute` always passes `fetch_result=` as a keyword. Update lines 31, 41, 51:

**Line 31** — change:
```python
mock_screen.assert_called_once_with(False, True)
```
to:
```python
args, kwargs = mock_screen.call_args
assert args == (False, True)
```

**Line 41** — change:
```python
mock_screen.assert_called_once_with(False, False)
```
to:
```python
args, kwargs = mock_screen.call_args
assert args == (False, False)
```

**Line 51** — change:
```python
mock_screen.assert_called_once_with(True, False)
```
to:
```python
args, kwargs = mock_screen.call_args
assert args == (True, False)
```

- [ ] **Step 6: Run new summary tests**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/test_tui_fetch_summary.py -v
```

Expected: all PASS.

- [ ] **Step 7: Run full unit suite**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/ -q
```

Expected: all PASS — including updated `test_tui_completion.py`.

- [ ] **Step 8: Commit**

```bash
cd ~/capcat && git add capcat/core/interactive.py tests/unit/test_tui_completion.py tests/unit/test_tui_fetch_summary.py
git commit -m "feat: show fetch summary on TUI completion screen"
```

---

### Task 5: Branch, git branch setup, and merge

- [ ] **Step 1: Verify all unit tests pass**

```bash
cd ~/capcat && source venv/bin/activate && pytest tests/unit/ -v
```

Expected: all PASS.

- [ ] **Step 2: Use finishing-a-development-branch skill**

Invoke `superpowers:finishing-a-development-branch` to present merge options.
