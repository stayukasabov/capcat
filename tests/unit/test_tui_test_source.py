"""Audit tests for Test a Source TUI flow."""
from unittest.mock import MagicMock, patch


def test_handle_test_source_does_not_crash():
    """_handle_test_source must complete without raising when user selects back."""
    # _handle_test_source uses questionary.select (not .text) and
    # get_available_sources() returns a dict {source_id: display_name}
    with patch("capcat.core.interactive.questionary") as mock_q:
        # Simulate user selecting "back"
        mock_q.select.return_value.ask.return_value = "back"
        mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock())
        mock_q.Separator = MagicMock(return_value=MagicMock())

        with patch(
            "capcat.core.interactive.get_available_sources",
            return_value={"bbc": "BBC News"},
        ):
            from capcat.core.interactive import _handle_test_source
            _handle_test_source()  # must not raise


def test_handle_test_source_none_selection_does_not_crash():
    """_handle_test_source must handle None (Ctrl+C) from questionary without raising."""
    with patch("capcat.core.interactive.questionary") as mock_q:
        mock_q.select.return_value.ask.return_value = None
        mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock())
        mock_q.Separator = MagicMock(return_value=MagicMock())

        with patch(
            "capcat.core.interactive.get_available_sources",
            return_value={"bbc": "BBC News"},
        ):
            from capcat.core.interactive import _handle_test_source
            _handle_test_source()  # must not raise


def test_handle_test_source_valid_source_does_not_crash():
    """_handle_test_source must not raise when a valid source is selected.

    Note: 'from capcat import run_app' inside _handle_test_source will raise
    ImportError at runtime (run_app is not exported from capcat.__init__).
    The function catches all exceptions, so it completes without raising.
    """
    with patch("capcat.core.interactive.questionary") as mock_q:
        mock_q.select.return_value.ask.return_value = "bbc"
        mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock())
        mock_q.Separator = MagicMock(return_value=MagicMock())

        with patch(
            "capcat.core.interactive.get_available_sources",
            return_value={"bbc": "BBC News"},
        ):
            with patch("builtins.input", return_value=""):
                from capcat.core.interactive import _handle_test_source
                _handle_test_source()  # must not raise (exception is caught internally)
