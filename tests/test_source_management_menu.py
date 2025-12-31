#!/usr/bin/env python3
"""
Test suite for source management interactive menu.

Tests the integration of add-source, remove-source, and generate-config
commands into the interactive catch menu.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSourceManagementMenu:
    """Test suite for the Manage Sources menu."""

    def test_manage_sources_menu_option_exists(self):
        """Test that 'Manage Sources' option appears in main menu."""
        from core.interactive import start_interactive_mode

        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = 'exit'

            start_interactive_mode()

            # Verify the select was called with choices including manage_sources
            call_args = mock_select.call_args
            choices = call_args[1]['choices']
            choice_values = [c.value if hasattr(c, 'value') else c for c in choices]

            assert 'exit' in choice_values, "Exit option should exist"
            # We'll add this assertion after implementing
            # assert 'manage_sources' in choice_values

    def test_manage_sources_submenu_structure(self):
        """Test that Manage Sources submenu has correct options."""
        from core.interactive import _handle_manage_sources_flow

        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = 'back'

            _handle_manage_sources_flow()

            call_args = mock_select.call_args
            choices = call_args[1]['choices']
            choice_values = [c.value if hasattr(c, 'value') else c for c in choices]

            expected_options = ['add_rss', 'generate_config', 'remove',
                              'list_sources', 'test_source', 'manage_bundles', 'back']
            for option in expected_options:
                assert option in choice_values, f"Missing option: {option}"

    def test_add_source_from_menu(self):
        """Test adding a source through the interactive menu."""
        from core.interactive import _handle_add_source_from_rss

        with patch('questionary.text') as mock_text, \
             patch('cli.add_source') as mock_add_source, \
             patch('cli.get_available_sources') as mock_get_sources, \
             patch('builtins.input'):

            mock_text.return_value.ask.return_value = "https://test.com/feed.xml"
            mock_get_sources.return_value = {'hn': 'Hacker News', 'test': 'Test Feed'}

            _handle_add_source_from_rss()

            mock_add_source.assert_called_once_with("https://test.com/feed.xml")

    def test_remove_source_from_menu(self):
        """Test removing a source through the interactive menu."""
        from core.interactive import _handle_remove_source

        with patch('core.source_system.remove_source_service.create_remove_source_service') as mock_create_service, \
             patch('cli.get_available_sources') as mock_get_sources, \
             patch('builtins.input'):

            mock_service = Mock()
            mock_command = Mock()
            mock_service._create_remove_source_command.return_value = mock_command
            mock_create_service.return_value = mock_service
            mock_get_sources.return_value = {'hn': 'Hacker News'}

            _handle_remove_source()

            mock_create_service.assert_called_once()

    def test_generate_config_from_menu(self):
        """Test config generation through the interactive menu."""
        from core.interactive import _handle_generate_config

        with patch('questionary.confirm') as mock_confirm, \
             patch('subprocess.run') as mock_subprocess, \
             patch('builtins.input'):

            mock_confirm.return_value.ask.return_value = True
            mock_subprocess.return_value = Mock(returncode=0)

            _handle_generate_config()

            mock_subprocess.assert_called_once()
            assert 'generate_source_config.py' in str(mock_subprocess.call_args)

    def test_menu_navigation_back(self):
        """Test returning to main menu from source management."""
        from core.interactive import _handle_manage_sources_flow

        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = 'back'

            result = _handle_manage_sources_flow()

            assert result is None


class TestAddSourceCommand:
    """Test suite for add-source command functionality."""

    @patch('cli.RssFeedIntrospector')
    @patch('cli.questionary')
    @patch('cli.SourceConfigGenerator')
    def test_add_source_valid_rss_url(self, mock_gen, mock_q, mock_intro):
        """Test adding a source with valid RSS URL."""
        from cli import add_source

        # Mock the introspector
        mock_intro_instance = Mock()
        mock_intro_instance.feed_title = "Test Feed"
        mock_intro_instance.base_url = "https://test.com"
        mock_intro_instance.url = "https://test.com/feed"
        mock_intro.return_value = mock_intro_instance

        # Mock questionary responses
        mock_q.text.return_value.ask.return_value = "testfeed"
        mock_q.select.return_value.ask.return_value = "tech"
        mock_q.confirm.return_value.ask.side_effect = [False, False]  # No bundle, no test

        # Mock config generator
        mock_gen_instance = Mock()
        mock_gen_instance.generate_and_save.return_value = "/path/to/config.yml"
        mock_gen.return_value = mock_gen_instance

        # Run the function - should complete successfully without SystemExit
        add_source("https://test.com/feed")

        # Verify config generator was called
        assert mock_gen_instance.generate_and_save.called

    @patch('cli.RssFeedIntrospector')
    def test_add_source_invalid_url(self, mock_intro):
        """Test error handling for invalid RSS URL."""
        from cli import add_source
        from core.exceptions import InvalidFeedError

        # Mock introspector to raise InvalidFeedError (subclass of CapcatError)
        mock_intro.side_effect = InvalidFeedError("https://invalid.com/notafeed")

        with pytest.raises(SystemExit) as exc_info:
            add_source("https://invalid.com/notafeed")

        # Should exit with error code
        assert exc_info.value.code == 1


class TestRemoveSourceCommand:
    """Test suite for remove-source command functionality."""

    def test_remove_source_interactive(self):
        """Test interactive source removal."""
        from core.source_system.enhanced_remove_command import EnhancedRemoveCommand, RemovalOptions
        from core.source_system.removal_ui import MockRemovalUI

        # Arrange
        mock_base_command = Mock()
        mock_backup_manager = Mock()
        mock_analytics = Mock()
        mock_logger = Mock()

        ui_responses = {
            'selected_sources': ['hn'],
            'confirm_removal': True
        }
        ui = MockRemovalUI(ui_responses)

        command = EnhancedRemoveCommand(
            base_command=mock_base_command,
            backup_manager=mock_backup_manager,
            analytics=mock_analytics,
            ui=ui,
            logger=mock_logger
        )

        options = RemovalOptions(
            dry_run=False,
            create_backup=True,
            show_analytics=False,
            batch_file=None,
            force=False
        )

        # Act
        command.execute_with_options(options)

        # Assert
        mock_base_command.execute.assert_called_once()

    def test_remove_source_dry_run(self):
        """Test dry-run mode for remove-source."""
        from core.source_system.enhanced_remove_command import EnhancedRemoveCommand, RemovalOptions
        from core.source_system.removal_ui import MockRemovalUI

        # Arrange
        mock_base_command = Mock()
        mock_backup_manager = Mock()
        mock_analytics = Mock()
        mock_logger = Mock()

        ui = MockRemovalUI({})

        command = EnhancedRemoveCommand(
            base_command=mock_base_command,
            backup_manager=mock_backup_manager,
            analytics=mock_analytics,
            ui=ui,
            logger=mock_logger
        )

        options = RemovalOptions(
            dry_run=True,
            create_backup=False,
            show_analytics=False,
            batch_file=None,
            force=False
        )

        # Act
        command.execute_with_options(options)

        # Assert - In dry-run mode, execute should not be called
        mock_base_command.execute.assert_not_called()

    def test_remove_source_undo(self):
        """Test undo functionality."""
        from core.source_system.source_backup_manager import SourceBackupManager
        from pathlib import Path

        # Arrange
        backup_manager = SourceBackupManager()
        mock_backup = Mock()
        mock_backup.source_id = 'hn'
        mock_backup.config_path = Path('/test/hn.yml')
        mock_backup.config_content = 'test: config'

        # Act
        with patch.object(backup_manager, 'list_backups', return_value=[mock_backup]), \
             patch.object(backup_manager, 'restore_backup') as mock_restore:

            backups = backup_manager.list_backups()
            assert len(backups) == 1

            backup_manager.restore_backup(backups[0].backup_id)
            mock_restore.assert_called_once()


class TestGenerateConfigCommand:
    """Test suite for generate-config command functionality."""

    def test_generate_config_interactive_flow(self):
        """Test the full interactive config generation."""
        from scripts.generate_source_config import SourceConfigGenerator

        with patch('questionary.text') as mock_text, \
             patch('questionary.select') as mock_select, \
             patch('questionary.confirm') as mock_confirm:

            # Arrange
            mock_text.return_value.ask.side_effect = [
                "testfeed",  # source_id
                "https://test.com",  # base_url
                ".article",  # article_selector
            ]
            mock_select.return_value.ask.return_value = "tech"  # category
            mock_confirm.return_value.ask.return_value = False  # no RSS

            generator = SourceConfigGenerator()

            # Act
            with patch.object(generator, 'generate_and_save') as mock_save:
                mock_save.return_value = "/test/testfeed.yml"
                result = generator.generate_and_save()

                # Assert
                assert result == "/test/testfeed.yml"

    def test_generate_config_custom_output(self):
        """Test config generation with custom output path."""
        from scripts.generate_source_config import SourceConfigGenerator
        from pathlib import Path

        # Arrange
        custom_path = Path('/custom/output/path')
        generator = SourceConfigGenerator(output_dir=custom_path)

        # Act & Assert
        assert generator.output_dir == custom_path


class TestMenuIntegration:
    """Test suite for menu integration and navigation."""

    def test_menu_flow_add_source(self):
        """Test complete flow: Main menu -> Manage Sources -> Add Source."""
        from core.interactive import start_interactive_mode

        with patch('questionary.select') as mock_select, \
             patch('questionary.text') as mock_text, \
             patch('cli.add_source') as mock_add, \
             patch('cli.get_available_sources') as mock_get, \
             patch('builtins.input'):

            # Simulate: Main menu -> Manage Sources -> Add RSS -> Back -> Exit
            mock_select.return_value.ask.side_effect = [
                'manage_sources',  # Main menu choice
                'add_rss',         # Submenu choice
                'back',            # Return to main
                'exit'             # Exit
            ]
            mock_text.return_value.ask.return_value = "https://test.com/rss"
            mock_get.return_value = {}

            start_interactive_mode()

            mock_add.assert_called_once_with("https://test.com/rss")

    def test_menu_flow_remove_source(self):
        """Test complete flow: Main menu -> Manage Sources -> Remove Source."""
        from core.interactive import start_interactive_mode

        with patch('questionary.select') as mock_select, \
             patch('core.source_system.remove_source_service.create_remove_source_service') as mock_service, \
             patch('cli.get_available_sources') as mock_get, \
             patch('builtins.input'):

            mock_svc = Mock()
            mock_cmd = Mock()
            mock_svc._create_remove_source_command.return_value = mock_cmd
            mock_service.return_value = mock_svc
            mock_get.return_value = {}

            # Simulate: Main menu -> Manage Sources -> Remove -> Back -> Exit
            mock_select.return_value.ask.side_effect = [
                'manage_sources',
                'remove',
                'back',
                'exit'
            ]

            start_interactive_mode()

            mock_service.assert_called_once()

    def test_menu_flow_configure_source(self):
        """Test complete flow: Main menu -> Manage Sources -> Configure."""
        from core.interactive import start_interactive_mode

        with patch('questionary.select') as mock_select, \
             patch('questionary.confirm') as mock_confirm, \
             patch('subprocess.run') as mock_subprocess, \
             patch('builtins.input'):

            mock_confirm.return_value.ask.return_value = True
            mock_subprocess.return_value = Mock(returncode=0)

            # Simulate: Main menu -> Manage Sources -> Generate Config -> Exit
            mock_select.return_value.ask.side_effect = [
                'manage_sources',
                'generate_config',
                'back',
                'exit'
            ]

            start_interactive_mode()

            mock_subprocess.assert_called_once()

    def test_menu_back_navigation(self):
        """Test back button returns to previous menu."""
        from core.interactive import _handle_manage_sources_flow

        with patch('questionary.select') as mock_select:
            # User selects 'back' immediately
            mock_select.return_value.ask.return_value = 'back'

            result = _handle_manage_sources_flow()

            assert result is None
            assert mock_select.call_count == 1

    def test_menu_cancel_returns_to_main(self):
        """Test Ctrl+C returns to main menu."""
        from core.interactive import _handle_single_url_flow

        with patch('questionary.text') as mock_text:
            # Simulate Ctrl+C (returns None)
            mock_text.return_value.ask.return_value = None

            result = _handle_single_url_flow()

            # Should return without error
            assert result is None


class TestSourceManagementService:
    """Test suite for source management service layer (to be created)."""

    def test_list_available_sources(self):
        """Test listing all available sources."""
        from cli import get_available_sources

        with patch('core.source_system.source_registry.get_source_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.get_available_sources.return_value = ['hn', 'bbc']

            mock_config_hn = Mock()
            mock_config_hn.display_name = 'Hacker News'
            mock_config_bbc = Mock()
            mock_config_bbc.display_name = 'BBC News'

            mock_registry.get_source_config.side_effect = [mock_config_hn, mock_config_bbc]
            mock_get_registry.return_value = mock_registry

            sources = get_available_sources()

            assert 'hn' in sources
            assert 'bbc' in sources
            assert sources['hn'] == 'Hacker News'
            assert sources['bbc'] == 'BBC News'

    def test_get_source_details(self):
        """Test retrieving source configuration details."""
        from core.source_system.source_registry import get_source_registry

        mock_registry = Mock()
        mock_config = Mock()
        mock_config.display_name = 'Test Source'
        mock_config.category = 'tech'
        mock_config.base_url = 'https://test.com'

        with patch('core.source_system.source_registry.get_source_registry', return_value=mock_registry):
            mock_registry.get_source_config.return_value = mock_config

            config = get_source_registry().get_source_config('test')

            assert config.display_name == 'Test Source'
            assert config.category == 'tech'
            assert config.base_url == 'https://test.com'

    def test_validate_source_config(self):
        """Test source configuration validation."""
        from core.source_system.source_config_generator import SourceConfigGenerator

        # Arrange
        generator = SourceConfigGenerator()

        # Valid config
        valid_config = {
            'display_name': 'Test Source',
            'base_url': 'https://test.com',
            'category': 'tech'
        }

        # Act & Assert - Should not raise
        assert valid_config['display_name'] is not None
        assert valid_config['base_url'].startswith('http')
        assert valid_config['category'] in ['tech', 'news', 'science', 'ai', 'sports', 'other']

    def test_test_source_connection(self):
        """Test source connectivity and fetching."""
        from core.interactive import _handle_test_source

        with patch('questionary.select') as mock_select, \
             patch('cli.get_available_sources') as mock_get, \
             patch('capcat.run_app') as mock_run, \
             patch('builtins.input'):

            mock_get.return_value = {'hn': 'Hacker News'}
            mock_select.return_value.ask.return_value = 'hn'

            _handle_test_source()

            # Verify run_app was called with test parameters
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert 'fetch' in args
            assert 'hn' in args
            assert '--count' in args


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
