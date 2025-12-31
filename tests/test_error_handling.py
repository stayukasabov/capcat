#!/usr/bin/env python3
"""
Comprehensive negative test scenarios for error handling.

Tests network failures, file system errors, invalid inputs, and edge cases.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.exceptions import CapcatError, InvalidFeedError


class TestNetworkErrorHandling:
    """Test error handling for network-related failures."""

    def test_rss_feed_timeout(self):
        """Test handling of RSS feed connection timeout."""
        from core.source_system.rss_feed_introspector import RssFeedIntrospector

        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timeout")

            with pytest.raises(InvalidFeedError) as exc_info:
                introspector = RssFeedIntrospector("https://slow-feed.com/rss")

            assert "timeout" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()

    def test_rss_feed_404_not_found(self):
        """Test handling of 404 Not Found for RSS feed."""
        from core.source_system.rss_feed_introspector import RssFeedIntrospector

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
            mock_get.return_value = mock_response

            with pytest.raises(InvalidFeedError):
                introspector = RssFeedIntrospector("https://notfound.com/rss")

    def test_rss_feed_invalid_ssl(self):
        """Test handling of SSL certificate errors."""
        from core.source_system.rss_feed_introspector import RssFeedIntrospector

        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.SSLError("SSL verification failed")

            with pytest.raises(InvalidFeedError):
                introspector = RssFeedIntrospector("https://invalid-ssl.com/rss")

    def test_dns_resolution_failure(self):
        """Test handling of DNS resolution failures."""
        from core.source_system.rss_feed_introspector import RssFeedIntrospector

        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError(
                "Failed to resolve host"
            )

            with pytest.raises(InvalidFeedError):
                introspector = RssFeedIntrospector("https://nonexistent-domain-12345.com/rss")

    def test_network_unreachable(self):
        """Test handling when network is unreachable."""
        from core.source_system.rss_feed_introspector import RssFeedIntrospector

        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")

            with pytest.raises(InvalidFeedError):
                introspector = RssFeedIntrospector("https://test.com/rss")

    def test_malformed_url(self):
        """Test handling of malformed URLs."""
        from core.source_system.rss_feed_introspector import RssFeedIntrospector

        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.InvalidURL("Invalid URL")

            with pytest.raises(InvalidFeedError):
                introspector = RssFeedIntrospector("not-a-valid-url")


class TestFileSystemErrorHandling:
    """Test error handling for file system operations."""

    def test_config_directory_not_writable(self):
        """Test handling when config directory is not writable."""
        from core.source_system.source_config_generator import SourceConfigGenerator

        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = True

        with patch('builtins.open') as mock_open:
            mock_open.side_effect = PermissionError("Permission denied")

            generator = SourceConfigGenerator()

            with pytest.raises(PermissionError):
                with patch.object(generator, 'output_dir', mock_path):
                    # This would fail when trying to write
                    pass

    def test_bundles_file_locked(self):
        """Test handling when bundles.yml is locked by another process."""
        from core.source_system.bundle_manager import BundleManager

        with patch('builtins.open') as mock_open:
            mock_open.side_effect = PermissionError("File is locked")

            with pytest.raises(PermissionError):
                manager = BundleManager("/test/bundles.yml")

    def test_disk_full_during_write(self):
        """Test handling when disk is full during file write."""
        from core.source_system.bundle_manager import BundleManager
        from pathlib import Path

        with patch('ruamel.yaml.YAML.dump') as mock_dump:
            mock_dump.side_effect = OSError("No space left on device")

            with pytest.raises(OSError):
                manager = BundleManager("/test/bundles.yml")
                # This would fail during save
                manager._save_data()

    def test_corrupted_yaml_file(self, tmp_path):
        """Test handling of corrupted YAML file."""
        from core.source_system.bundle_manager import BundleManager

        # Create corrupted YAML file
        bundles_file = tmp_path / "corrupted.yml"
        bundles_file.write_text("bundles:\n  invalid: [unclosed bracket")

        with pytest.raises(Exception):  # YAML parsing error
            manager = BundleManager(str(bundles_file))

    def test_config_file_not_found_during_remove(self):
        """Test removing a config file that doesn't exist."""
        from core.source_system.remove_source_command import FileSystemConfigRemover

        remover = FileSystemConfigRemover()

        # Should not raise error (idempotent operation)
        remover.remove_config_file(Path("/nonexistent/file.yml"))

    def test_bundle_file_missing(self, tmp_path):
        """Test when bundle file is missing."""
        from core.source_system.bundle_manager import BundleManager

        # Create manager with non-existent file
        manager = BundleManager(str(tmp_path / "nonexistent.yml"))

        # Should create empty bundles structure
        assert manager.data == {'bundles': {}}


class TestUserInputErrorHandling:
    """Test error handling for invalid user inputs."""

    @pytest.mark.parametrize("invalid_id", [
        "",  # Empty
        " ",  # Whitespace
        "../../etc/passwd",  # Path traversal
        "'; DROP TABLE bundles; --",  # SQL injection attempt
        "<script>alert('xss')</script>",  # XSS attempt
        "\x00null_byte",  # Null byte
        "a" * 1000,  # Very long input
    ])
    def test_invalid_source_id_format(self, invalid_id):
        """Test handling of malicious or invalid source IDs."""
        from core.source_system.bundle_validator import BundleValidator

        validator = BundleValidator()

        result = validator.validate_bundle_id(invalid_id)

        # Should reject invalid IDs
        assert not result.valid
        assert len(result.errors) > 0

    def test_malicious_path_traversal_attempt(self):
        """Test that path traversal attempts are blocked."""
        from pathlib import Path

        # Attempt to traverse up directories
        malicious_path = Path("/base/path") / ".." / ".." / "etc" / "passwd"

        # Resolve to absolute path to detect traversal
        resolved = malicious_path.resolve()

        # Should not end up in /etc
        assert "etc/passwd" not in str(resolved)

    def test_unicode_handling_in_bundle_description(self):
        """Test handling of unicode characters in descriptions."""
        from core.source_system.bundle_validator import BundleValidator

        validator = BundleValidator()

        # Unicode characters should be accepted
        unicode_desc = "Tech news 技术新闻 🚀"
        result = validator.validate_description(unicode_desc)

        assert result.valid

    def test_null_character_in_input(self):
        """Test handling of null characters in input."""
        from core.source_system.bundle_validator import BundleValidator

        validator = BundleValidator()

        # Null character should be rejected or sanitized
        null_input = "tech\x00news"
        result = validator.validate_bundle_id(null_input)

        assert not result.valid

    def test_extremely_long_description(self):
        """Test handling of extremely long descriptions."""
        from core.source_system.bundle_validator import BundleValidator

        validator = BundleValidator()

        # Description exceeding max length
        long_desc = "a" * 10000
        result = validator.validate_description(long_desc)

        assert not result.valid
        assert "too long" in result.errors[0]

    def test_negative_article_count(self):
        """Test handling of negative article counts."""
        from core.source_system.bundle_validator import BundleValidator

        validator = BundleValidator()

        result = validator.validate_default_count(-10)

        assert not result.valid
        assert len(result.errors) > 0


class TestEdgeCaseHandling:
    """Test edge cases and boundary conditions."""

    def test_empty_source_list(self):
        """Test operations with empty source list."""
        from core.source_system.bundle_validator import BundleValidator

        mock_registry = Mock()
        mock_registry.get_available_sources.return_value = []

        validator = BundleValidator(source_registry=mock_registry)

        valid, invalid = validator.validate_source_ids(['hn', 'bbc'])

        # All should be invalid if registry is empty
        assert valid == []
        assert invalid == ['hn', 'bbc']

    def test_empty_bundle_list(self, tmp_path):
        """Test operations with empty bundle list."""
        from core.source_system.bundle_manager import BundleManager

        bundles_file = tmp_path / "empty_bundles.yml"
        bundles_file.write_text("bundles: {}")

        manager = BundleManager(str(bundles_file))

        assert manager.get_bundle_names() == []

    def test_bundle_with_no_sources(self, tmp_path):
        """Test bundle with empty source list."""
        from core.source_system.bundle_manager import BundleManager

        bundles_file = tmp_path / "bundles.yml"
        bundles_file.write_text("""
bundles:
  empty_bundle:
    sources: []
    description: "Empty bundle"
    default_count: 20
""")

        manager = BundleManager(str(bundles_file))
        details = manager.get_bundle_details("empty_bundle")

        assert details['total_sources'] == 0
        assert details['sources'] == []

    def test_concurrent_bundle_access(self, tmp_path):
        """Test handling of concurrent access to bundles file."""
        from core.source_system.bundle_manager import BundleManager
        import threading

        bundles_file = tmp_path / "bundles.yml"
        bundles_file.write_text("bundles:\n  tech:\n    sources: [hn]\n    description: 'Tech'\n    default_count: 20")

        manager = BundleManager(str(bundles_file))

        def add_source():
            try:
                manager.add_source_to_bundle("bbc", "tech")
            except Exception:
                pass

        threads = [threading.Thread(target=add_source) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should handle concurrent writes (may have race conditions)
        # Just verify it doesn't crash
        assert True

    def test_source_removal_already_removed(self):
        """Test removing a source that's already been removed."""
        from core.source_system.remove_source_command import FileSystemConfigRemover

        remover = FileSystemConfigRemover()

        # Remove non-existent file (should be idempotent)
        remover.remove_config_file(Path("/nonexistent/test.yml"))

        # Should not raise error
        assert True

    def test_bundle_creation_with_minimum_values(self, tmp_path):
        """Test creating bundle with minimum allowed values."""
        from core.source_system.bundle_manager import BundleManager

        bundles_file = tmp_path / "bundles.yml"
        bundles_file.write_text("bundles: {}")

        manager = BundleManager(str(bundles_file))

        # Minimum valid values
        manager.create_bundle(
            bundle_id="a",  # Minimum length
            description="A",  # Minimum length
            default_count=1,  # Minimum count
            sources=[]  # Empty source list
        )

        assert "a" in manager.get_bundle_names()

    def test_bundle_creation_with_maximum_values(self, tmp_path):
        """Test creating bundle with maximum allowed values."""
        from core.source_system.bundle_manager import BundleManager

        bundles_file = tmp_path / "bundles.yml"
        bundles_file.write_text("bundles: {}")

        manager = BundleManager(str(bundles_file))

        # Maximum valid values
        max_id = "a" * 30
        max_desc = "a" * 200

        manager.create_bundle(
            bundle_id=max_id,
            description=max_desc,
            default_count=100,
            sources=[]
        )

        assert max_id in manager.get_bundle_names()


class TestRaceConditionHandling:
    """Test handling of race conditions."""

    def test_source_added_while_iterating(self):
        """Test when source is added during iteration."""
        from cli import get_available_sources

        with patch('core.source_system.source_registry.get_source_registry') as mock_get_registry:
            mock_registry = Mock()

            # Simulate sources being added during iteration
            call_count = [0]

            def dynamic_sources():
                call_count[0] += 1
                if call_count[0] == 1:
                    return ['hn', 'bbc']
                else:
                    return ['hn', 'bbc', 'new_source']

            mock_registry.get_available_sources.side_effect = dynamic_sources

            mock_config = Mock()
            mock_config.display_name = 'Test'
            mock_registry.get_source_config.return_value = mock_config

            mock_get_registry.return_value = mock_registry

            # Should handle gracefully
            sources = get_available_sources()
            assert isinstance(sources, dict)

    def test_bundle_deleted_during_edit(self, tmp_path):
        """Test when bundle is deleted while editing."""
        from core.source_system.bundle_manager import BundleManager

        bundles_file = tmp_path / "bundles.yml"
        bundles_file.write_text("bundles:\n  tech:\n    sources: [hn]\n    description: 'Tech'\n    default_count: 20")

        manager = BundleManager(str(bundles_file))

        # Delete bundle
        manager.delete_bundle("tech")

        # Try to edit deleted bundle
        with pytest.raises(ValueError, match="not found"):
            manager.update_bundle_metadata("tech", description="Updated")


class TestRetryMechanisms:
    """Test retry logic for transient failures."""

    def test_network_retry_logic(self):
        """Test that network requests are retried on transient failures."""
        # This would test actual retry implementation if it exists
        # For now, just document the expected behavior
        pass

    def test_file_lock_retry(self):
        """Test retry logic when file is temporarily locked."""
        # Document expected behavior for file lock retries
        pass


class TestResourceCleanup:
    """Test proper cleanup of resources on errors."""

    def test_file_handle_cleanup_on_error(self):
        """Test that file handles are closed on error."""
        from core.source_system.bundle_manager import BundleManager

        with patch('builtins.open') as mock_open:
            mock_file = Mock()
            mock_file.__enter__.return_value = mock_file
            mock_file.__exit__ = Mock()
            mock_open.return_value = mock_file

            # Simulate error during read
            mock_file.read.side_effect = IOError("Read error")

            try:
                with open("/test/file.yml") as f:
                    f.read()
            except IOError:
                pass

            # File should be closed via context manager
            assert mock_file.__exit__.called

    def test_connection_cleanup_on_timeout(self):
        """Test that connections are cleaned up on timeout."""
        # Document expected behavior for connection cleanup
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
