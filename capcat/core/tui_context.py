"""TUI context flag and per-fetch result accumulation.

Tracks whether the process is currently running inside the interactive TUI.
Used to suppress prompts and per-article warnings that would corrupt
questionary's terminal state when called via _dispatch inside the TUI.
"""
import threading
from collections import Counter

_tui_active: bool = False
_tui_results_lock = threading.Lock()
_tui_results: list[tuple[bool, str | None]] = []


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


def record_fetch_result(success: bool, reason: str | None) -> None:
    """Record one article outcome. Thread-safe."""
    with _tui_results_lock:
        _tui_results.append((success, reason))


def get_fetch_result() -> "FetchResult":
    """Build and return a FetchResult from accumulated outcomes."""
    from capcat.core.unified_source_processor import FetchResult
    with _tui_results_lock:
        saved = sum(1 for ok, r in _tui_results if r is None and ok)
        counts = Counter(r for ok, r in _tui_results if r is not None)
    return FetchResult(saved=saved, skipped=list(counts.items()))
