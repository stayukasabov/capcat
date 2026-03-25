"""Audit tests for Remove Existing Sources TUI flow."""
from unittest.mock import MagicMock, patch


def test_remove_source_handler_does_not_crash():
    """_handle_remove_source must not raise on invocation with mocked services."""
    mock_service = MagicMock()
    mock_service._create_remove_source_command.return_value = MagicMock()
    mock_enhanced = MagicMock()

    with patch(
        "capcat.core.source_system.remove_source_service.create_remove_source_service",
        return_value=mock_service,
    ):
        with patch(
            "capcat.core.source_system.enhanced_remove_command.EnhancedRemoveCommand",
            return_value=mock_enhanced,
        ):
            with patch(
                "capcat.core.source_system.removal_ui.QuestionaryRemovalUI",
                return_value=MagicMock(),
            ):
                with patch(
                    "capcat.core.source_system.source_backup_manager.SourceBackupManager",
                    return_value=MagicMock(),
                ):
                    with patch(
                        "capcat.core.source_system.source_analytics.SourceAnalytics",
                        return_value=MagicMock(),
                    ):
                        with patch(
                            "capcat.core.source_system.bundle_service.get_available_sources",
                            return_value={},
                        ):
                            with patch("builtins.input", return_value=""):
                                from capcat.core.interactive import _handle_remove_source
                                _handle_remove_source()  # must not raise


def test_remove_source_calls_execute_with_options():
    """_handle_remove_source must call execute_with_options on the EnhancedRemoveCommand."""
    mock_enhanced = MagicMock()
    mock_service = MagicMock()
    mock_service._create_remove_source_command.return_value = MagicMock()

    with patch(
        "capcat.core.source_system.remove_source_service.create_remove_source_service",
        return_value=mock_service,
    ):
        with patch(
            "capcat.core.source_system.enhanced_remove_command.EnhancedRemoveCommand",
            return_value=mock_enhanced,
        ):
            with patch(
                "capcat.core.source_system.removal_ui.QuestionaryRemovalUI",
                return_value=MagicMock(),
            ):
                with patch(
                    "capcat.core.source_system.source_backup_manager.SourceBackupManager",
                    return_value=MagicMock(),
                ):
                    with patch(
                        "capcat.core.source_system.source_analytics.SourceAnalytics",
                        return_value=MagicMock(),
                    ):
                        with patch(
                            "capcat.core.source_system.bundle_service.get_available_sources",
                            return_value={},
                        ):
                            with patch("builtins.input", return_value=""):
                                from capcat.core.interactive import _handle_remove_source
                                _handle_remove_source()

    mock_enhanced.execute_with_options.assert_called_once()
