"""JSON event emission for the hidden --json CLI output mode.

Module-level state, mirroring the existing capcat.core.tui_context pattern
(set_tui_active/is_tui_active) - enabled once per command invocation rather
than threaded as a parameter through the whole fetch pipeline.
"""
from __future__ import annotations

import json as _json
from typing import Any, TextIO

_enabled = False
_stream: TextIO | None = None
_article_counts = {"fetched": 0, "errors": 0}
_html_path: str | None = None


def enable(stream: TextIO) -> None:
    """Turn on JSON event emission, writing to *stream*."""
    global _enabled, _stream
    _enabled = True
    _stream = stream


def disable() -> None:
    """Turn off JSON event emission."""
    global _enabled, _stream
    _enabled = False
    _stream = None


def is_enabled() -> bool:
    """Return whether JSON event emission is currently active."""
    return _enabled


def emit(event: str, **fields: Any) -> None:
    """Print one NDJSON line ({"event": event, **fields}) if enabled."""
    if not _enabled or _stream is None:
        return
    print(_json.dumps({"event": event, **fields}), file=_stream, flush=True)


def emit_raw(payload: dict) -> None:
    """Print *payload* as a single JSON object, no "event" wrapper.

    Used for one-shot structured output (list --json) as opposed to the
    NDJSON event stream emit() produces for fetch/bundle/single.
    """
    if not _enabled or _stream is None:
        return
    print(_json.dumps(payload), file=_stream, flush=True)


def record_article_fetched(**fields: Any) -> None:
    """Emit article_fetched and bump the running fetched counter."""
    _article_counts["fetched"] += 1
    emit("article_fetched", **fields)


def record_article_error(**fields: Any) -> None:
    """Emit article_error and bump the running error counter."""
    _article_counts["errors"] += 1
    emit("article_error", **fields)


def pop_article_counts() -> tuple[int, int]:
    """Return (fetched, errors) accumulated since the last call, then reset."""
    global _article_counts
    counts = (_article_counts["fetched"], _article_counts["errors"])
    _article_counts = {"fetched": 0, "errors": 0}
    return counts


def set_html_path(path: str | None) -> None:
    """Record the generated HTML index path/URL for the next run_complete event."""
    global _html_path
    _html_path = path


def pop_html_path() -> str | None:
    """Return the recorded HTML path, then reset it to None."""
    global _html_path
    path = _html_path
    _html_path = None
    return path
