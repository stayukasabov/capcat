# TUI Fetch Summary Design Spec

## Problem

Capcat emits a WARNING log per failed article during fetch (JS-rendered pages, 403s, timeouts, empty markdown). In TUI mode this populates the screen with noise the user cannot act on. In CLI mode the per-article detail is useful for scripting and debugging.

## Goal

- TUI mode: clean screen during fetch, single summary line on the completion screen
- CLI mode: unchanged — per-article warnings still appear

## Scope

| Action | File |
|---|---|
| Modify | `capcat/core/article_fetcher.py` |
| Modify | `capcat/core/unified_source_processor.py` |
| Modify | `capcat/core/interactive.py` |
| Test (must pass) | `tests/unit/` |

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

**Decision: extend the return tuple to 4 elements.** The new signature is `(bool, title, folder_path, reason)` where `reason: str | None` — `None` on success, one of the reason strings above on failure.

There is exactly one external call site: `config_driven_source.py:144` in `ConfigDrivenSource` (the method that fetches a single article). Both `_fetch_web_content` and this call site need updating. The internal recursive calls within `article_fetcher.py` (lines 470, 476) are forwarding calls within the same class and also need the 4-element unpack updated.

## Constraints

- No new dependencies
- CLI behavior unchanged
- `tests/unit/` must pass. `tests/test_pdf_skip_prompt.py:271` unpacks `_fetch_web_content` as a 3-element tuple and must be updated to a 4-element unpack (add `_reason` to the unpack). No other existing tests touch `_fetch_web_content` directly. New unit tests for `FetchResult` construction and summary rendering are expected.
- Summary line only appears in TUI mode
- If `saved == 0` and `skipped == 0` (e.g. source returned no articles), no summary line is shown
