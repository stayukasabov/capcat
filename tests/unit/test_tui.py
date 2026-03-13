"""Test TUI entry point."""
from unittest.mock import patch


def test_tui_run_calls_interactive_menu():
    """tui.run() must call the interactive menu entry function from core."""
    # Patch at definition site, not module object
    with patch(
        "capcat.core.interactive.start_interactive_mode"
    ) as mock_menu:
        from capcat import tui
        import importlib
        importlib.reload(tui)
        tui.run()
    mock_menu.assert_called_once()
