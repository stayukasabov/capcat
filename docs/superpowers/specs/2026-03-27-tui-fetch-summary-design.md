# TUI Fetch Summary Design Spec

## Problem

Capcat emits a WARNING log per failed article during fetch (JS-rendered pages, 403s, timeouts, empty markdown). In TUI mode this populates the screen with noise the user cannot act on. In CLI mode the per-article detail is useful for scripting and debugging.

## Goal

- TUI mode: clean screen during fetch, single summary line on the completion screen
- CLI mode: unchanged — per-article warnings still appear

## Scope

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
      <td><code>capcat/core/article_fetcher.py</code></td>
    </tr>
    <tr>
      <td>Modify</td>
      <td><code>capcat/core/unified_source_processor.py</code></td>
    </tr>
    <tr>
      <td>Modify</td>
      <td><code>capcat/core/interactive.py</code></td>
    </tr>
    <tr>
      <td>Test (must pass)</td>
      <td><code>tests/unit/</code></td>
    </tr>
  </tbody>
</table>
</div>

## Design

### FetchResult dataclass

A lightweight result object returned by the processor after a fetch run.

```python
@dataclass
class FetchResult:
    saved: int
    skipped: list[tuple[str, int]]  # [("JS-rendered", 2), ("blocked", 1)]
```

Defined in `unified_source_processor.py`. The `skipped` list entries use short human-readable reason strings that map from the failure categories already present in the fetcher.

Reason strings:
- `"JS-rendered"` — SPA with no extractable content
- `"blocked"` — 403 / anti-bot protection
- `"not found"` — 404
- `"timeout"` — request timed out
- `"no content"` — empty markdown after extraction
- `"error"` — all other failures

### tui_mode flag

`tui_mode: bool = False` is added to:

1. `NewsSourceArticleFetcher._fetch_web_content` — when `True`, per-article warnings are emitted at DEBUG instead of WARNING. The failure reason string is returned as part of the `(success, title, folder)` tuple or via a side-channel so the processor can accumulate it.

2. `unified_source_processor` public entry points — accepts `tui_mode`, passes it to the fetcher, accumulates per-article outcomes into a `FetchResult`.

3. `_confirm_and_execute` in `interactive.py` — passes `tui_mode=True` when calling dispatch, receives the `FetchResult`.

### Completion screen

`_show_completion_screen` gains a `fetch_result: FetchResult | None = None` parameter.

Rendering logic:

```
# nothing skipped
47 saved

# some skipped
47 saved, 3 skipped (2 JS-rendered, 1 blocked)

# all skipped
0 saved, 5 skipped (3 JS-rendered, 2 blocked)
```

The summary line appears below the "Done" / "Completed with errors" status label, before the navigation choices.

### CLI mode

No change. `tui_mode` defaults to `False`. All per-article warnings continue to appear at WARNING level.

## Failure reason propagation

`_fetch_web_content` currently returns `(bool, title, folder_path)`. The reason for failure needs to reach the processor. Two options:

- Extend the return tuple to `(bool, title, folder_path, reason)` — simple, explicit
- Use a side-channel list passed by reference — avoids changing call signatures across the codebase

**Decision: thread-safe side-channel via `tui_context.py`.** The spec originally proposed extending the return tuple to 4 elements, but tracing the actual call chain revealed the reason would need to propagate through `base_source.py` (abstract interface) and all 7+ concrete source implementations (hn, lb, youtube, medium, vimeo, substack, twitter, config_driven_source). That is 15+ files for a change that could break the source interface.

Instead: `NewsSourceArticleFetcher._fetch_web_content` calls `record_fetch_result(success, reason)` from `tui_context` at every terminal return point (no-op outside TUI). `tui_context.py` gains three functions: `reset_fetch_results()`, `record_fetch_result(success, reason)`, and `get_fetch_result() -> FetchResult`. No return signatures change anywhere. The `(bool, title, folder_path)` 3-tuple return stays unchanged — `tests/test_pdf_skip_prompt.py:271` does not need updating.

## Constraints

- No new dependencies
- CLI behavior unchanged
- `tests/unit/` must pass. No existing test modifies `_fetch_web_content`'s return signature (the 3-tuple return is unchanged). New unit tests for `FetchResult` construction, `tui_context` accumulation, and summary rendering are expected.
- Summary line only appears in TUI mode
- If `saved == 0` and `skipped == 0` (e.g. source returned no articles), no summary line is shown
