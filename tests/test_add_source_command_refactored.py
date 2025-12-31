"""
Comprehensive test suite for the refactored add-source command.
Tests all components in isolation and integration scenarios.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from typing import List, Optional

from core.source_system.add_source_command import (
    AddSourceCommand,
    SourceMetadata,
    RssFeedIntrospectorFactory,
    SourceConfigGeneratorAdapter,
    SubprocessSourceTester,
    RegistryCategoryProvider
)
from core.source_system.questionary_ui import QuestionaryUserInterface, MockUserInterface
from core.exceptions import ValidationError, CapcatError


class TestSourceMetadata:
    """Test the SourceMetadata value object."""

    def test_valid_metadata(self):
        """Test that valid metadata validates successfully."""
        metadata = SourceMetadata(
            source_id="testabc123",
            display_name="Test Source",
            base_url="https://test.com",
            rss_url="https://test.com/rss",
            category="tech"
        )
        # Should not raise
        metadata.validate()

    def test_invalid_source_id_non_alphanumeric(self):
        """Test that non-alphanumeric source ID raises ValidationError."""
        metadata = SourceMetadata(
            source_id="test-source",  # Contains hyphen
            display_name="Test Source",
            base_url="https://test.com",
            rss_url="https://test.com/rss",
            category="tech"
        )
        with pytest.raises(ValidationError, match="Must be alphanumeric"):
            metadata.validate()

    def test_invalid_empty_display_name(self):
        """Test that empty display name raises ValidationError."""
        metadata = SourceMetadata(
            source_id="testsource",
            display_name="   ",  # Only whitespace
            base_url="https://test.com",
            rss_url="https://test.com/rss",
            category="tech"
        )
        with pytest.raises(ValidationError, match="Cannot be empty"):
            metadata.validate()

    def test_invalid_empty_category(self):
        """Test that empty category raises ValidationError."""
        metadata = SourceMetadata(
            source_id="testsource",
            display_name="Test Source",
            base_url="https://test.com",
            rss_url="https://test.com/rss",
            category=""  # Empty
        )
        with pytest.raises(ValidationError, match="Cannot be empty"):
            metadata.validate()


class TestMockUserInterface:
    """Test the MockUserInterface for testing purposes."""

    def test_mock_responses(self):
        """Test that MockUserInterface returns configured responses."""
        responses = {
            'source_id': 'customid',
            'category': 'science',
            'confirm_bundle': True,
            'bundle': 'techbundle',
            'confirm_test': True
        }
        ui = MockUserInterface(responses)

        assert ui.get_source_id('defaultid') == 'customid'
        assert ui.select_category(['tech', 'science']) == 'science'
        assert ui.confirm_bundle_addition() is True
        assert ui.select_bundle(['techbundle', 'newsbundle']) == 'techbundle'
        assert ui.confirm_test_fetch() is True

    def test_mock_calls_tracking(self):
        """Test that MockUserInterface tracks all method calls."""
        ui = MockUserInterface({})

        ui.get_source_id('test')
        ui.select_category(['tech'])
        ui.show_success('Success!')

        expected_calls = [
            ('get_source_id', 'test'),
            ('select_category', ['tech']),
            ('show_success', 'Success!')
        ]
        assert ui.calls == expected_calls


class TestQuestionaryUserInterface:
    """Test the QuestionaryUserInterface."""

    @pytest.fixture
    def mock_questionary(self):
        """Create a mock questionary module."""
        mock = Mock()
        return mock

    def test_get_source_id_success(self, mock_questionary):
        """Test successful source ID input."""
        mock_questionary.text.return_value.ask.return_value = "testsource"

        ui = QuestionaryUserInterface(mock_questionary)
        result = ui.get_source_id("suggested")

        assert result == "testsource"
        mock_questionary.text.assert_called_once_with(
            "Enter a unique source ID (alphanumeric):",
            default="suggested"
        )

    def test_get_source_id_empty_exits(self, mock_questionary):
        """Test that empty source ID causes system exit."""
        mock_questionary.text.return_value.ask.return_value = ""

        ui = QuestionaryUserInterface(mock_questionary)

        with pytest.raises(SystemExit) as exc_info:
            ui.get_source_id("suggested")

        assert exc_info.value.code == 1

    def test_select_category_success(self, mock_questionary):
        """Test successful category selection."""
        mock_questionary.select.return_value.ask.return_value = "tech"

        ui = QuestionaryUserInterface(mock_questionary)
        result = ui.select_category(["tech", "science"])

        assert result == "tech"
        mock_questionary.select.assert_called_once_with(
            "Assign a category:",
            choices=["tech", "science"],
            use_indicator=True
        )

    def test_select_category_no_categories_exits(self, mock_questionary):
        """Test that empty categories list causes system exit."""
        ui = QuestionaryUserInterface(mock_questionary)

        with pytest.raises(SystemExit) as exc_info:
            ui.select_category([])

        assert exc_info.value.code == 1

    def test_confirm_bundle_addition(self, mock_questionary):
        """Test bundle addition confirmation."""
        mock_questionary.confirm.return_value.ask.return_value = True

        ui = QuestionaryUserInterface(mock_questionary)
        result = ui.confirm_bundle_addition()

        assert result is True
        mock_questionary.confirm.assert_called_once_with("Add this source to a bundle?")

    def test_confirm_bundle_addition_none_returns_false(self, mock_questionary):
        """Test that None response returns False."""
        mock_questionary.confirm.return_value.ask.return_value = None

        ui = QuestionaryUserInterface(mock_questionary)
        result = ui.confirm_bundle_addition()

        assert result is False


class TestAddSourceCommand:
    """Test the main AddSourceCommand class."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for AddSourceCommand."""
        return {
            'introspector_factory': Mock(),
            'ui': Mock(),
            'config_generator': Mock(),
            'bundle_manager': Mock(),
            'source_tester': Mock(),
            'category_provider': Mock(),
            'config_path': Path('/test/config'),
            'bundles_path': Path('/test/bundles.yml'),
            'logger': Mock()
        }

    @pytest.fixture
    def command(self, mock_dependencies):
        """Create AddSourceCommand with mocked dependencies."""
        return AddSourceCommand(**mock_dependencies)

    def test_execute_happy_path(self, command, mock_dependencies):
        """Test successful execution of add-source command."""
        # Setup mocks
        mock_introspector = Mock()
        mock_introspector.feed_title = "Test Feed"
        mock_introspector.base_url = "https://test.com"

        mock_dependencies['introspector_factory'].create.return_value = mock_introspector
        mock_dependencies['ui'].get_source_id.return_value = "testfeed"
        mock_dependencies['ui'].select_category.return_value = "tech"
        mock_dependencies['ui'].confirm_bundle_addition.return_value = True
        mock_dependencies['ui'].select_bundle.return_value = "techbundle"
        mock_dependencies['ui'].confirm_test_fetch.return_value = True

        mock_dependencies['category_provider'].get_available_categories.return_value = ["tech", "science"]
        mock_dependencies['config_generator'].generate_and_save.return_value = Path("/test/config.yml")
        mock_dependencies['bundle_manager'].get_bundle_names.return_value = ["techbundle"]
        mock_dependencies['source_tester'].test_source.return_value = True

        # Execute
        command.execute("https://test.com/rss")

        # Verify workflow
        mock_dependencies['introspector_factory'].create.assert_called_once_with("https://test.com/rss")
        mock_dependencies['ui'].get_source_id.assert_called_once()
        mock_dependencies['ui'].select_category.assert_called_once_with(["tech", "science"])

        # Verify metadata passed to config generator
        config_call_args = mock_dependencies['config_generator'].generate_and_save.call_args[0]
        metadata = config_call_args[0]
        assert metadata.source_id == "testfeed"
        assert metadata.display_name == "Test Feed"
        assert metadata.base_url == "https://test.com"
        assert metadata.rss_url == "https://test.com/rss"
        assert metadata.category == "tech"

        mock_dependencies['bundle_manager'].add_source_to_bundle.assert_called_once_with("testfeed", "techbundle")
        mock_dependencies['source_tester'].test_source.assert_called_once_with("testfeed")
        mock_dependencies['ui'].show_success.assert_called()

    def test_execute_no_bundle_integration(self, command, mock_dependencies):
        """Test execution when user declines bundle integration."""
        # Setup mocks
        mock_introspector = Mock()
        mock_introspector.feed_title = "Test Feed"
        mock_introspector.base_url = "https://test.com"

        mock_dependencies['introspector_factory'].create.return_value = mock_introspector
        mock_dependencies['ui'].get_source_id.return_value = "testfeed"
        mock_dependencies['ui'].select_category.return_value = "tech"
        mock_dependencies['ui'].confirm_bundle_addition.return_value = False  # User declines
        mock_dependencies['ui'].confirm_test_fetch.return_value = False

        mock_dependencies['category_provider'].get_available_categories.return_value = ["tech"]
        mock_dependencies['config_generator'].generate_and_save.return_value = Path("/test/config.yml")

        # Execute
        command.execute("https://test.com/rss")

        # Verify bundle methods not called
        mock_dependencies['bundle_manager'].get_bundle_names.assert_not_called()
        mock_dependencies['bundle_manager'].add_source_to_bundle.assert_not_called()

    def test_execute_introspection_failure(self, command, mock_dependencies):
        """Test handling of introspection failure."""
        mock_dependencies['introspector_factory'].create.side_effect = CapcatError("Feed error")

        with pytest.raises(CapcatError, match="Feed error"):
            command.execute("https://invalid.com/rss")

        mock_dependencies['ui'].show_error.assert_called_with("Failed to introspect feed: Feed error")

    def test_execute_config_generation_failure(self, command, mock_dependencies):
        """Test handling of config generation failure."""
        # Setup successful introspection
        mock_introspector = Mock()
        mock_introspector.feed_title = "Test Feed"
        mock_introspector.base_url = "https://test.com"

        mock_dependencies['introspector_factory'].create.return_value = mock_introspector
        mock_dependencies['ui'].get_source_id.return_value = "testfeed"
        mock_dependencies['ui'].select_category.return_value = "tech"
        mock_dependencies['category_provider'].get_available_categories.return_value = ["tech"]

        # Simulate config generation failure
        mock_dependencies['config_generator'].generate_and_save.side_effect = Exception("Config error")

        with pytest.raises(CapcatError):
            command.execute("https://test.com/rss")

        mock_dependencies['ui'].show_error.assert_called_with("Failed to generate configuration: Config error")

    def test_execute_bundle_integration_failure_continues(self, command, mock_dependencies):
        """Test that bundle integration failure doesn't stop the workflow."""
        # Setup successful introspection
        mock_introspector = Mock()
        mock_introspector.feed_title = "Test Feed"
        mock_introspector.base_url = "https://test.com"

        mock_dependencies['introspector_factory'].create.return_value = mock_introspector
        mock_dependencies['ui'].get_source_id.return_value = "testfeed"
        mock_dependencies['ui'].select_category.return_value = "tech"
        mock_dependencies['ui'].confirm_bundle_addition.return_value = True
        mock_dependencies['ui'].confirm_test_fetch.return_value = False

        mock_dependencies['category_provider'].get_available_categories.return_value = ["tech"]
        mock_dependencies['config_generator'].generate_and_save.return_value = Path("/test/config.yml")

        # Simulate bundle failure
        mock_dependencies['bundle_manager'].get_bundle_names.side_effect = Exception("Bundle error")

        # Should not raise, should continue to completion
        command.execute("https://test.com/rss")

        mock_dependencies['ui'].show_error.assert_called_with("Failed to add to bundle: Bundle error")
        mock_dependencies['ui'].show_success.assert_called()

    def test_generate_source_id_suggestion(self, command):
        """Test source ID suggestion generation."""
        result = command._generate_source_id_suggestion("The Verge - Latest Tech News!")
        assert result == "thevergelatesttechnews"

    def test_generate_source_id_suggestion_length_limit(self, command):
        """Test that source ID suggestion is limited to 20 characters."""
        long_title = "This is a very long feed title that should be truncated"
        result = command._generate_source_id_suggestion(long_title)
        assert len(result) <= 20
        assert result == "thisisaverylongfeedti"


class TestSubprocessSourceTester:
    """Test the SubprocessSourceTester."""

    @patch('subprocess.run')
    def test_successful_test(self, mock_run):
        """Test successful source testing."""
        mock_run.return_value = Mock()

        tester = SubprocessSourceTester()
        result = tester.test_source("testsource")

        assert result is True
        mock_run.assert_called_once_with(
            ["./capcat", "fetch", "testsource", "--count", "1"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

    @patch('subprocess.run')
    def test_failed_test_called_process_error(self, mock_run):
        """Test failed source testing due to subprocess error."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')

        tester = SubprocessSourceTester()
        result = tester.test_source("testsource")

        assert result is False

    @patch('subprocess.run')
    def test_failed_test_timeout(self, mock_run):
        """Test failed source testing due to timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 30)

        tester = SubprocessSourceTester()
        result = tester.test_source("testsource")

        assert result is False

    @patch('subprocess.run')
    def test_failed_test_file_not_found(self, mock_run):
        """Test failed source testing due to missing capcat command."""
        mock_run.side_effect = FileNotFoundError()

        tester = SubprocessSourceTester()
        result = tester.test_source("testsource")

        assert result is False


class TestRegistryCategoryProvider:
    """Test the RegistryCategoryProvider."""

    @patch('core.source_system.add_source_command.get_source_registry')
    def test_successful_category_extraction(self, mock_get_registry):
        """Test successful category extraction from registry."""
        # Setup mock registry
        mock_registry = Mock()
        mock_registry.get_available_sources.return_value = ['source1', 'source2']

        mock_config1 = Mock()
        mock_config1.category = 'tech'
        mock_config2 = Mock()
        mock_config2.category = 'science'

        mock_registry.get_source_config.side_effect = [mock_config1, mock_config2]
        mock_get_registry.return_value = mock_registry

        provider = RegistryCategoryProvider()
        categories = provider.get_available_categories()

        assert set(categories) == {'science', 'tech'}  # Sorted order

    @patch('core.source_system.add_source_command.get_source_registry')
    def test_fallback_categories_on_error(self, mock_get_registry):
        """Test fallback categories when registry fails."""
        mock_get_registry.side_effect = Exception("Registry error")

        provider = RegistryCategoryProvider()
        categories = provider.get_available_categories()

        expected_fallback = ['tech', 'news', 'science', 'ai', 'sports', 'general']
        assert categories == expected_fallback

    @patch('core.source_system.add_source_command.get_source_registry')
    def test_fallback_categories_when_empty(self, mock_get_registry):
        """Test fallback categories when registry returns empty list."""
        mock_registry = Mock()
        mock_registry.get_available_sources.return_value = []
        mock_get_registry.return_value = mock_registry

        provider = RegistryCategoryProvider()
        categories = provider.get_available_categories()

        expected_fallback = ['tech', 'news', 'science', 'ai', 'sports', 'general']
        assert categories == expected_fallback


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_workflow_integration(self):
        """Test complete add-source workflow with real-like dependencies."""
        # Create mock dependencies that interact realistically
        mock_introspector = Mock()
        mock_introspector.feed_title = "Ars Technica"
        mock_introspector.base_url = "https://arstechnica.com"

        introspector_factory = Mock()
        introspector_factory.create.return_value = mock_introspector

        ui_responses = {
            'source_id': 'arstechnica',
            'category': 'tech',
            'confirm_bundle': True,
            'bundle': 'techbundle',
            'confirm_test': True
        }
        ui = MockUserInterface(ui_responses)

        config_generator = Mock()
        config_generator.generate_and_save.return_value = Path('/test/arstechnica.yml')

        bundle_manager = Mock()
        bundle_manager.get_bundle_names.return_value = ['techbundle', 'newsbundle']

        source_tester = Mock()
        source_tester.test_source.return_value = True

        category_provider = Mock()
        category_provider.get_available_categories.return_value = ['tech', 'science']

        # Create command
        command = AddSourceCommand(
            introspector_factory=introspector_factory,
            ui=ui,
            config_generator=config_generator,
            bundle_manager=bundle_manager,
            source_tester=source_tester,
            category_provider=category_provider,
            config_path=Path('/test/config'),
            bundles_path=Path('/test/bundles.yml'),
            logger=Mock()
        )

        # Execute
        command.execute("https://arstechnica.com/rss")

        # Verify complete workflow
        assert len(ui.calls) == 6  # All UI interactions occurred
        config_generator.generate_and_save.assert_called_once()
        bundle_manager.add_source_to_bundle.assert_called_once_with('arstechnica', 'techbundle')
        source_tester.test_source.assert_called_once_with('arstechnica')

    def test_workflow_with_user_cancellation(self):
        """Test workflow when user cancels at various points."""
        # Test cancellation during source ID input
        ui_responses = {
            'source_id': '',  # Empty source ID should cause exit
        }
        ui = MockUserInterface(ui_responses)

        # Override the get_source_id to simulate SystemExit
        def mock_get_source_id(suggested):
            ui.calls.append(('get_source_id', suggested))
            import sys
            sys.exit(1)

        ui.get_source_id = mock_get_source_id

        mock_introspector = Mock()
        mock_introspector.feed_title = "Test Feed"
        mock_introspector.base_url = "https://test.com"

        introspector_factory = Mock()
        introspector_factory.create.return_value = mock_introspector

        command = AddSourceCommand(
            introspector_factory=introspector_factory,
            ui=ui,
            config_generator=Mock(),
            bundle_manager=Mock(),
            source_tester=Mock(),
            category_provider=Mock(),
            config_path=Path('/test'),
            bundles_path=Path('/test'),
            logger=Mock()
        )

        # Should raise SystemExit
        with pytest.raises(SystemExit):
            command.execute("https://test.com/rss")


if __name__ == '__main__':
    # Run tests with coverage
    pytest.main([
        __file__,
        '-v',
        '--cov=core.source_system.add_source_command',
        '--cov=core.source_system.questionary_ui',
        '--cov-report=term-missing'
    ])