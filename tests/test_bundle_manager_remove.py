"""
Tests for BundleManager remove functionality.
"""

import pytest
from pathlib import Path
import yaml

from core.source_system.bundle_manager import BundleManager


class TestBundleManagerRemove:
    """Test the remove_source_from_all_bundles method."""

    def test_remove_from_single_bundle(self, tmp_path):
        """Test removing a source from a single bundle."""
        bundles_path = tmp_path / "bundles.yml"
        bundles_content = """
bundles:
  tech:
    description: Tech news
    sources:
      - hn
      - iq
      - gizmodo
  news:
    description: General news
    sources:
      - bbc
      - guardian
"""
        bundles_path.write_text(bundles_content)

        manager = BundleManager(str(bundles_path))
        updated = manager.remove_source_from_all_bundles('hn')

        assert updated == ['tech']

        # Verify the file was updated correctly
        with open(bundles_path) as f:
            data = yaml.safe_load(f)

        assert data['bundles']['tech']['sources'] == ['iq', 'gizmodo']
        assert data['bundles']['news']['sources'] == ['bbc', 'guardian']

    def test_remove_from_multiple_bundles(self, tmp_path):
        """Test removing a source that appears in multiple bundles."""
        bundles_path = tmp_path / "bundles.yml"
        bundles_content = """
bundles:
  tech:
    sources: [hn, iq]
  techpro:
    sources: [hn, lb]
  news:
    sources: [bbc]
"""
        bundles_path.write_text(bundles_content)

        manager = BundleManager(str(bundles_path))
        updated = manager.remove_source_from_all_bundles('hn')

        assert set(updated) == {'tech', 'techpro'}

        # Verify both bundles were updated
        with open(bundles_path) as f:
            data = yaml.safe_load(f)

        assert 'hn' not in data['bundles']['tech']['sources']
        assert 'hn' not in data['bundles']['techpro']['sources']
        assert data['bundles']['news']['sources'] == ['bbc']

    def test_remove_nonexistent_source(self, tmp_path):
        """Test removing a source that doesn't exist in any bundle."""
        bundles_path = tmp_path / "bundles.yml"
        bundles_content = """
bundles:
  tech:
    sources: [hn, iq]
  news:
    sources: [bbc]
"""
        bundles_path.write_text(bundles_content)

        manager = BundleManager(str(bundles_path))
        updated = manager.remove_source_from_all_bundles('nonexistent')

        assert updated == []

        # Verify nothing changed
        with open(bundles_path) as f:
            data = yaml.safe_load(f)

        assert data['bundles']['tech']['sources'] == ['hn', 'iq']
        assert data['bundles']['news']['sources'] == ['bbc']

    def test_remove_preserves_comments(self, tmp_path):
        """Test that removing sources preserves comments in YAML."""
        bundles_path = tmp_path / "bundles.yml"
        bundles_content = """# Main bundles configuration
bundles:
  # Technology sources
  tech:
    description: Tech news
    sources:
      - hn  # Hacker News
      - iq
      - gizmodo
  # News sources
  news:
    sources: [bbc]
"""
        bundles_path.write_text(bundles_content)

        manager = BundleManager(str(bundles_path))
        manager.remove_source_from_all_bundles('hn')

        # Read the file back and verify comments are preserved
        content = bundles_path.read_text()
        assert '# Main bundles configuration' in content
        assert '# Technology sources' in content
        assert '# News sources' in content

    def test_remove_last_source_from_bundle(self, tmp_path):
        """Test removing the last source from a bundle."""
        bundles_path = tmp_path / "bundles.yml"
        bundles_content = """
bundles:
  tech:
    sources: [hn]
  news:
    sources: [bbc, guardian]
"""
        bundles_path.write_text(bundles_content)

        manager = BundleManager(str(bundles_path))
        updated = manager.remove_source_from_all_bundles('hn')

        assert updated == ['tech']

        with open(bundles_path) as f:
            data = yaml.safe_load(f)

        # Bundle should still exist with empty sources list
        assert data['bundles']['tech']['sources'] == []
        assert data['bundles']['news']['sources'] == ['bbc', 'guardian']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.source_system.bundle_manager'])