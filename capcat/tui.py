"""TUI entry point — delegates to core interactive module."""
from __future__ import annotations


def run() -> None:
    """Launch the Capcat interactive TUI."""
    from capcat.core.tui_context import set_tui_active
    from capcat.core.interactive import start_interactive_mode
    set_tui_active(True)
    try:
        start_interactive_mode()
    finally:
        set_tui_active(False)
