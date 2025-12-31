
import pytest
from ruamel.yaml import YAML
from pathlib import Path

from core.source_system.bundle_manager import BundleManager

# --- Test Fixtures ---

@pytest.fixture
def sample_bundles_content():
    """Provides a sample bundles.yml content with comments."""
    return """# Pre-defined source bundles for easy fetching.

bundles:
  # Technology News
  tech:
    - gizmodo
    - futurism
    - ieee

  # General News
  news:
    - bbc
    - guardian
"""

@pytest.fixture
def bundle_file(tmp_path, sample_bundles_content):
    """Creates a temporary bundles.yml file."""
    p = tmp_path / "bundles.yml"
    p.write_text(sample_bundles_content, encoding="utf-8")
    return str(p)

# --- Test Cases ---

def test_get_bundle_names(bundle_file):
    """Tests that the manager can correctly list bundle names."""
    manager = BundleManager(bundle_file)
    names = manager.get_bundle_names()
    assert sorted(names) == sorted(["tech", "news"])

def test_add_source_to_bundle(bundle_file):
    """
    Test 3.1 (Add to Bundle): Asserts that a new source ID is correctly added
    to a specified bundle while preserving comments and structure.
    """
    manager = BundleManager(bundle_file)
    manager.add_source_to_bundle("newsource", "tech")

    yaml = YAML()
    with open(bundle_file, 'r') as f:
        data = yaml.load(f)

    assert "newsource" in data["bundles"]["tech"]
    assert len(data["bundles"]["tech"]) == 4

    # Check that comments are preserved (this is tricky to assert directly,
    # but we can check the raw text)
    raw_content = Path(bundle_file).read_text()
    assert "# Technology News" in raw_content

def test_add_source_to_nonexistent_bundle(bundle_file):
    """Tests that adding a source to a non-existent bundle raises an error."""
    manager = BundleManager(bundle_file)
    with pytest.raises(ValueError, match="Bundle 'nonexistent' not found."):
        manager.add_source_to_bundle("newsource", "nonexistent")
