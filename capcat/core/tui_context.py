"""TUI context flag.

Tracks whether the process is currently running inside the interactive TUI.
Used to suppress prompts (e.g. theme upgrade dialogue) that would corrupt
questionary's terminal state when called via _dispatch inside the TUI.
"""

_tui_active: bool = False


def set_tui_active(active: bool) -> None:
    """Set the TUI-active flag. Called by the TUI on entry and exit."""
    global _tui_active
    _tui_active = active


def is_tui_active() -> bool:
    """Return True if the TUI is currently running."""
    return _tui_active
