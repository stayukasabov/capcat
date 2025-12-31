"""
Comprehensive test suite for remove-source command.
Tests all components in isolation and integration scenarios.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path

from core.source_system.remove_source_command import (
    RemoveSourceCommand,
    SourceRemovalInfo,
    FileSystemConfigRemover,
    RegistrySourceLister,
    RegistrySourceInfoProvider,
    BundleManagerUpdater
)
from core.source_system.removal_ui import MockRemovalUI
from core.exceptions import CapcatError


class TestRemoveSourceCommand:
    """Test the main RemoveSourceCommand class."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for RemoveSourceCommand."""
        return {
            'source_lister': Mock(),
            'source_info_provider': Mock(),
            'ui': Mock(),
            'config_remover': Mock(),
            'bundle_updater': Mock(),
            'logger': Mock()
        }

    @pytest.fixture
    def command(self, mock_dependencies):
        """Create RemoveSourceCommand with mocked dependencies."""
        return RemoveSourceCommand(**mock_dependencies)

    def test_execute_no_sources_available(self, command, mock_dependencies):
        """Test execution when no sources are available."""
        mock_dependencies['source_lister'].get_available_sources.return_value = []

        command.execute()

        mock_dependencies['ui'].show_info.assert_called_with("No sources available to remove.")
        mock_dependencies['ui'].select_sources_to_remove.assert_not_called()

    def test_execute_user_selects_no_sources(self, command, mock_dependencies):
        """Test execution when user selects no sources."""
        mock_dependencies['source_lister'].get_available_sources.return_value = [
            ('hn', 'Hacker News'),
            ('bbc', 'BBC News')
        ]
        mock_dependencies['ui'].select_sources_to_remove.return_value = []

        command.execute()

        mock_dependencies['ui'].show_info.assert_called_with("No sources selected for removal.")

    def test_execute_user_cancels_confirmation(self, command, mock_dependencies):
        """Test execution when user cancels at confirmation."""
        # Setup
        mock_dependencies['source_lister'].get_available_sources.return_value = [
            ('hn', 'Hacker News')
        ]
        mock_dependencies['ui'].select_sources_to_remove.return_value = ['hn']

        source_info = SourceRemovalInfo(
            source_id='hn',
            display_name='Hacker News',
            config_path=Path('/test/hn.yml'),
            bundles=['tech']
        )
        mock_dependencies['source_info_provider'].get_source_info.return_value = source_info
        mock_dependencies['ui'].confirm_removal.return_value = False

        # Execute
        command.execute()

        # Verify
        mock_dependencies['ui'].show_info.assert_called_with("Removal cancelled.")
        mock_dependencies['config_remover'].remove_config_file.assert_not_called()

    def test_execute_successful_removal(self, command, mock_dependencies):
        """Test successful removal of sources."""
        # Setup available sources
        mock_dependencies['source_lister'].get_available_sources.return_value = [
            ('hn', 'Hacker News'),
            ('bbc', 'BBC News')
        ]

        # User selects both sources
        mock_dependencies['ui'].select_sources_to_remove.return_value = ['hn', 'bbc']

        # Setup source info
        hn_info = SourceRemovalInfo(
            source_id='hn',
            display_name='Hacker News',
            config_path=Path('/test/hn.yml'),
            bundles=['tech', 'techpro']
        )
        bbc_info = SourceRemovalInfo(
            source_id='bbc',
            display_name='BBC News',
            config_path=Path('/test/bbc.yml'),
            bundles=['news']
        )

        mock_dependencies['source_info_provider'].get_source_info.side_effect = [hn_info, bbc_info]

        # User confirms
        mock_dependencies['ui'].confirm_removal.return_value = True

        # Setup bundle updater
        mock_dependencies['bundle_updater'].remove_source_from_all_bundles.side_effect = [
            ['tech', 'techpro'],
            ['news']
        ]

        # Execute
        command.execute()

        # Verify removal workflow
        assert mock_dependencies['config_remover'].remove_config_file.call_count == 2
        mock_dependencies['config_remover'].remove_config_file.assert_any_call(Path('/test/hn.yml'))
        mock_dependencies['config_remover'].remove_config_file.assert_any_call(Path('/test/bbc.yml'))

        # Verify bundle updates
        assert mock_dependencies['bundle_updater'].remove_source_from_all_bundles.call_count == 2

        # Verify success message
        mock_dependencies['ui'].show_success.assert_called_with("Successfully removed 2 source(s).")

    def test_execute_handles_partial_failure(self, command, mock_dependencies):
        """Test that partial failures are handled gracefully."""
        # Setup
        mock_dependencies['source_lister'].get_available_sources.return_value = [
            ('hn', 'Hacker News'),
            ('bbc', 'BBC News')
        ]
        mock_dependencies['ui'].select_sources_to_remove.return_value = ['hn', 'bbc']

        hn_info = SourceRemovalInfo(
            source_id='hn',
            display_name='Hacker News',
            config_path=Path('/test/hn.yml'),
            bundles=['tech']
        )
        bbc_info = SourceRemovalInfo(
            source_id='bbc',
            display_name='BBC News',
            config_path=Path('/test/bbc.yml'),
            bundles=['news']
        )

        mock_dependencies['source_info_provider'].get_source_info.side_effect = [hn_info, bbc_info]
        mock_dependencies['ui'].confirm_removal.return_value = True

        # First removal succeeds, second fails
        mock_dependencies['bundle_updater'].remove_source_from_all_bundles.side_effect = [
            ['tech'],
            Exception("Bundle error")
        ]

        # Execute
        command.execute()

        # Should show error but continue
        mock_dependencies['ui'].show_error.assert_called()
        # Should still show overall success for sources processed
        mock_dependencies['ui'].show_success.assert_called()


class TestFileSystemConfigRemover:
    """Test the FileSystemConfigRemover."""

    def test_remove_existing_file(self, tmp_path):
        """Test removing an existing config file."""
        # Create a test file
        test_file = tmp_path / "test.yml"
        test_file.write_text("test content")

        remover = FileSystemConfigRemover()
        remover.remove_config_file(test_file)

        assert not test_file.exists()

    def test_remove_nonexistent_file(self, tmp_path):
        """Test removing a file that doesn't exist."""
        test_file = tmp_path / "nonexistent.yml"

        remover = FileSystemConfigRemover()
        # Should not raise an error
        remover.remove_config_file(test_file)


class TestRegistrySourceLister:
    """Test the RegistrySourceLister."""

    @patch('core.source_system.source_registry.get_source_registry')
    def test_successful_listing(self, mock_get_registry):
        """Test successful source listing from registry."""
        mock_registry = Mock()
        mock_registry.get_available_sources.return_value = ['hn', 'bbc']

        mock_config_hn = Mock()
        mock_config_hn.display_name = 'Hacker News'
        mock_config_bbc = Mock()
        mock_config_bbc.display_name = 'BBC News'

        # Configs returned in alphabetical order: bbc, hn
        mock_registry.get_source_config.side_effect = [mock_config_bbc, mock_config_hn]
        mock_get_registry.return_value = mock_registry

        lister = RegistrySourceLister()
        sources = lister.get_available_sources()

        assert sources == [('bbc', 'BBC News'), ('hn', 'Hacker News')]  # Sorted

    @patch('core.source_system.source_registry.get_source_registry')
    def test_listing_failure(self, mock_get_registry):
        """Test handling of registry failure."""
        mock_get_registry.side_effect = Exception("Registry error")

        lister = RegistrySourceLister()

        with pytest.raises(CapcatError, match="Failed to load sources from registry"):
            lister.get_available_sources()


class TestRegistrySourceInfoProvider:
    """Test the RegistrySourceInfoProvider."""

    @patch('core.source_system.source_registry.get_source_registry')
    def test_get_source_info_success(self, mock_get_registry, tmp_path):
        """Test successful source info retrieval."""
        # Setup registry
        mock_registry = Mock()
        mock_config = Mock()
        mock_config.display_name = 'Hacker News'
        mock_registry.get_source_config.return_value = mock_config
        mock_get_registry.return_value = mock_registry

        # Setup bundles file
        bundles_path = tmp_path / "bundles.yml"
        bundles_content = """
bundles:
  tech:
    sources: [hn, iq]
  techpro:
    sources: [hn, lb]
"""
        bundles_path.write_text(bundles_content)

        # Test
        provider = RegistrySourceInfoProvider(tmp_path, bundles_path)
        info = provider.get_source_info('hn')

        assert info is not None
        assert info.source_id == 'hn'
        assert info.display_name == 'Hacker News'
        assert info.config_path == tmp_path / "hn.yml"
        assert set(info.bundles) == {'tech', 'techpro'}

    @patch('core.source_system.source_registry.get_source_registry')
    def test_get_source_info_not_found(self, mock_get_registry, tmp_path):
        """Test when source is not found."""
        mock_registry = Mock()
        mock_registry.get_source_config.return_value = None
        mock_get_registry.return_value = mock_registry

        bundles_path = tmp_path / "bundles.yml"
        bundles_path.write_text("bundles: {}")

        provider = RegistrySourceInfoProvider(tmp_path, bundles_path)
        info = provider.get_source_info('nonexistent')

        assert info is None


class TestBundleManagerUpdater:
    """Test the BundleManagerUpdater."""

    def test_remove_source_from_bundles(self, tmp_path):
        """Test removing source from bundles."""
        bundles_path = tmp_path / "bundles.yml"
        bundles_content = """
bundles:
  tech:
    sources: [hn, iq, gizmodo]
  news:
    sources: [bbc, guardian]
  techpro:
    sources: [hn, lb]
"""
        bundles_path.write_text(bundles_content)

        updater = BundleManagerUpdater(bundles_path)
        updated = updater.remove_source_from_all_bundles('hn')

        assert set(updated) == {'tech', 'techpro'}

        # Verify file was updated
        import yaml
        with open(bundles_path) as f:
            data = yaml.safe_load(f)

        assert 'hn' not in data['bundles']['tech']['sources']
        assert 'hn' not in data['bundles']['techpro']['sources']
        assert 'bbc' in data['bundles']['news']['sources']  # Unchanged


class TestMockRemovalUI:
    """Test the MockRemovalUI for testing purposes."""

    def test_mock_responses(self):
        """Test that MockRemovalUI returns configured responses."""
        responses = {
            'selected_sources': ['hn', 'bbc'],
            'confirm_removal': True
        }
        ui = MockRemovalUI(responses)

        sources = [('hn', 'Hacker News'), ('bbc', 'BBC News')]
        assert ui.select_sources_to_remove(sources) == ['hn', 'bbc']
        assert ui.confirm_removal([]) is True

    def test_mock_calls_tracking(self):
        """Test that MockRemovalUI tracks all calls."""
        ui = MockRemovalUI({})

        ui.select_sources_to_remove([('hn', 'HN')])
        ui.show_info("Test")
        ui.show_success("Done")

        assert len(ui.calls) == 3
        assert ui.calls[0][0] == 'select_sources_to_remove'
        assert ui.calls[1] == ('show_info', 'Test')
        assert ui.calls[2] == ('show_success', 'Done')


class TestIntegration:
    """Integration tests for remove-source."""

    def test_full_removal_workflow(self, tmp_path):
        """Test complete removal workflow with real-like components."""
        # Setup test files
        config_path = tmp_path / "configs"
        config_path.mkdir()

        hn_config = config_path / "hn.yml"
        hn_config.write_text("display_name: Hacker News\n")

        bundles_path = tmp_path / "bundles.yml"
        bundles_path.write_text("""
bundles:
  tech:
    sources: [hn, iq]
""")

        # Create mocks
        mock_lister = Mock()
        mock_lister.get_available_sources.return_value = [('hn', 'Hacker News')]

        mock_info_provider = Mock()
        source_info = SourceRemovalInfo(
            source_id='hn',
            display_name='Hacker News',
            config_path=hn_config,
            bundles=['tech']
        )
        mock_info_provider.get_source_info.return_value = source_info

        ui_responses = {
            'selected_sources': ['hn'],
            'confirm_removal': True
        }
        ui = MockRemovalUI(ui_responses)

        # Create command
        command = RemoveSourceCommand(
            source_lister=mock_lister,
            source_info_provider=mock_info_provider,
            ui=ui,
            config_remover=FileSystemConfigRemover(),
            bundle_updater=BundleManagerUpdater(bundles_path),
            logger=Mock()
        )

        # Execute
        command.execute()

        # Verify file was deleted
        assert not hn_config.exists()

        # Verify bundle was updated
        import yaml
        with open(bundles_path) as f:
            data = yaml.safe_load(f)
        assert 'hn' not in data['bundles']['tech']['sources']

        # Verify UI interactions
        assert ('show_success', 'Successfully removed 1 source(s).') in ui.calls


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.source_system.remove_source_command'])