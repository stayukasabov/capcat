"""
Tests for the AddSourceService integration layer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from core.source_system.add_source_service import AddSourceService, create_add_source_service
from core.exceptions import CapcatError


class TestAddSourceService:
    """Test the AddSourceService integration layer."""

    def test_default_initialization(self):
        """Test that service initializes with default paths."""
        with patch('core.source_system.add_source_service.Path') as mock_path:
            mock_cli_path = Mock()
            mock_cli_path.parent = Path('/app')

            with patch('cli.__file__', '/app/cli.py'):
                service = AddSourceService()

                # Verify paths are constructed correctly
                assert service._base_path == Path('/app')

    def test_custom_base_path_initialization(self):
        """Test service initialization with custom base path."""
        custom_path = Path('/custom/app')
        service = AddSourceService(custom_path)

        assert service._base_path == custom_path
        assert service._config_path == custom_path / "sources" / "active" / "config_driven" / "configs"
        assert service._bundles_path == custom_path / "sources" / "active" / "bundles.yml"

    @patch('core.source_system.add_source_service.AddSourceCommand')
    @patch('core.source_system.add_source_service.QuestionaryUserInterface')
    @patch('core.source_system.add_source_service.BundleManager')
    def test_add_source_success(self, mock_bundle_manager, mock_ui, mock_command_class):
        """Test successful source addition."""
        # Setup mocks
        mock_command = Mock()
        mock_command_class.return_value = mock_command

        service = AddSourceService(Path('/test'))

        # Execute
        service.add_source("https://test.com/rss")

        # Verify command was created and executed
        mock_command_class.assert_called_once()
        mock_command.execute.assert_called_once_with("https://test.com/rss")

    @patch('core.source_system.add_source_service.AddSourceCommand')
    def test_add_source_failure(self, mock_command_class):
        """Test source addition failure handling."""
        # Setup command to raise error
        mock_command = Mock()
        mock_command.execute.side_effect = CapcatError("Test error")
        mock_command_class.return_value = mock_command

        service = AddSourceService(Path('/test'))

        # Should propagate the error
        with pytest.raises(CapcatError, match="Test error"):
            service.add_source("https://test.com/rss")

    @patch('core.source_system.add_source_service.RssFeedIntrospectorFactory')
    @patch('core.source_system.add_source_service.QuestionaryUserInterface')
    @patch('core.source_system.add_source_service.SourceConfigGeneratorAdapter')
    @patch('core.source_system.add_source_service.BundleManager')
    @patch('core.source_system.add_source_service.SubprocessSourceTester')
    @patch('core.source_system.add_source_service.RegistryCategoryProvider')
    @patch('core.source_system.add_source_service.AddSourceCommand')
    def test_create_add_source_command_dependencies(
        self, mock_command_class, mock_category_provider, mock_source_tester,
        mock_bundle_manager, mock_config_generator, mock_ui, mock_introspector_factory
    ):
        """Test that all dependencies are properly created and injected."""
        service = AddSourceService(Path('/test'))

        # Call the private method to test dependency creation
        command = service._create_add_source_command()

        # Verify all factories and services were instantiated
        mock_introspector_factory.assert_called_once()
        mock_ui.assert_called_once()
        mock_config_generator.assert_called_once()
        mock_bundle_manager.assert_called_once()
        mock_source_tester.assert_called_once()
        mock_category_provider.assert_called_once()

        # Verify command was created with correct dependencies
        mock_command_class.assert_called_once()
        call_args = mock_command_class.call_args
        assert call_args[1]['config_path'] == Path('/test/sources/active/config_driven/configs')
        assert call_args[1]['bundles_path'] == Path('/test/sources/active/bundles.yml')

    def test_logging_integration(self):
        """Test that logging is properly integrated."""
        with patch('core.source_system.add_source_service.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            service = AddSourceService(Path('/test'))

            # Verify logger was obtained
            mock_get_logger.assert_called_with('core.source_system.add_source_service')


class TestCreateAddSourceService:
    """Test the factory function."""

    @patch('core.source_system.add_source_service.AddSourceService')
    def test_factory_function(self, mock_service_class):
        """Test that factory function creates service correctly."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        result = create_add_source_service()

        assert result == mock_service
        mock_service_class.assert_called_once_with()


class TestServiceIntegration:
    """Integration tests for the service layer."""

    @patch('subprocess.run')
    @patch('core.source_system.rss_feed_introspector.RssFeedIntrospector')
    @patch('core.source_system.source_config_generator.SourceConfigGenerator')
    @patch('core.source_system.bundle_manager.BundleManager')
    @patch('questionary.text')
    @patch('questionary.select')
    @patch('questionary.confirm')
    def test_end_to_end_integration(
        self, mock_confirm, mock_select, mock_text, mock_bundle_manager_class,
        mock_config_generator_class, mock_introspector_class, mock_subprocess
    ):
        """Test end-to-end integration with real-like components."""
        # Setup RSS introspector mock
        mock_introspector = Mock()
        mock_introspector.feed_title = "Test Feed"
        mock_introspector.base_url = "https://test.com"
        mock_introspector_class.return_value = mock_introspector

        # Setup config generator mock
        mock_config_gen = Mock()
        mock_config_gen.generate_and_save.return_value = "/test/config.yml"
        mock_config_generator_class.return_value = mock_config_gen

        # Setup bundle manager mock
        mock_bundle_mgr = Mock()
        mock_bundle_mgr.get_bundle_names.return_value = ["tech", "science"]
        mock_bundle_manager_class.return_value = mock_bundle_mgr

        # Setup questionary mocks
        mock_text.return_value.ask.return_value = "testfeed"
        mock_select.return_value.ask.side_effect = ["tech", "tech"]
        mock_confirm.return_value.ask.side_effect = [True, True]

        # Setup subprocess mock for successful test
        mock_subprocess.return_value = Mock()

        # Create service and execute
        service = AddSourceService(Path('/test'))
        service.add_source("https://test.com/rss")

        # Verify key interactions occurred
        mock_introspector_class.assert_called_once_with("https://test.com/rss")
        mock_config_gen.generate_and_save.assert_called_once()
        mock_bundle_mgr.add_source_to_bundle.assert_called_once()
        mock_subprocess.assert_called_once()

    def test_service_error_handling(self):
        """Test service-level error handling."""
        with patch('core.source_system.rss_feed_introspector.RssFeedIntrospector') as mock_introspector:
            mock_introspector.side_effect = Exception("Network error")

            service = AddSourceService(Path('/test'))

            with pytest.raises(CapcatError):
                service.add_source("https://invalid.com/rss")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.source_system.add_source_service'])