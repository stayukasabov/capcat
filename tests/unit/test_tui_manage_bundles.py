"""Audit tests for Manage Bundles TUI flow."""
from unittest.mock import MagicMock, patch

from capcat.core.config import NoProjectError


def _make_mock_service(side_effect=None, return_value=None):
    mock_service = MagicMock()
    if side_effect is not None:
        mock_service.ui.show_bundle_menu.side_effect = side_effect
    else:
        mock_service.ui.show_bundle_menu.return_value = return_value
    return mock_service


def test_handle_manage_bundles_does_not_crash():
    """_handle_manage_bundles must not raise when user selects back immediately.

    BundleService is a local import inside _handle_manage_bundles; patch at the
    source module path. find_project_root raises NoProjectError so the fallback
    builtin bundles.yml path is used — BundleService is still patched, so no
    filesystem access occurs.
    """
    mock_service = _make_mock_service(return_value=None)

    with patch(
        "capcat.core.source_system.bundle_service.BundleService",
        return_value=mock_service,
    ):
        with patch(
            "capcat.core.config.find_project_root",
            side_effect=NoProjectError("no project"),
        ):
            from capcat.core.interactive import _handle_manage_bundles
            _handle_manage_bundles()  # must not raise


def test_handle_manage_bundles_back_action_exits_loop():
    """show_bundle_menu returning 'back' must exit the while loop cleanly."""
    mock_service = _make_mock_service(return_value="back")

    with patch(
        "capcat.core.source_system.bundle_service.BundleService",
        return_value=mock_service,
    ):
        with patch(
            "capcat.core.config.find_project_root",
            side_effect=NoProjectError("no project"),
        ):
            from capcat.core.interactive import _handle_manage_bundles
            _handle_manage_bundles()

    mock_service.ui.show_bundle_menu.assert_called_once()


def test_handle_manage_bundles_list_action_calls_service():
    """'list' action must delegate to service.execute_list_bundles()."""
    mock_service = _make_mock_service(side_effect=["list", None])

    with patch(
        "capcat.core.source_system.bundle_service.BundleService",
        return_value=mock_service,
    ):
        with patch(
            "capcat.core.config.find_project_root",
            side_effect=NoProjectError("no project"),
        ):
            from capcat.core.interactive import _handle_manage_bundles
            _handle_manage_bundles()

    mock_service.execute_list_bundles.assert_called_once()
