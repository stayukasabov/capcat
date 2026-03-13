"""TUI entry point — delegates to core interactive module."""
from __future__ import annotations


def run() -> None:
    """Launch the Capcat interactive TUI."""
    from capcat.core.interactive import start_interactive_mode
    start_interactive_mode()
