
import pytest
import yaml
from pathlib import Path

from core.source_system.source_config_generator import SourceConfigGenerator

# --- Test Fixtures ---

@pytest.fixture
def source_metadata():
    """Provides mock data for generating a source configuration."""
    return {
        "source_id": "testsource",
        "display_name": "Test Source",
        "base_url": "https://www.test.com/",
        "rss_url": "https://www.test.com/feed.rss",
        "category": "tech"
    }

# --- Test Cases ---

def test_generate_yaml_content(source_metadata):
    """
    Test 2.1 (Content Generation): Asserts that SourceConfigGenerator produces
    a string with the correct YAML format and content.
    """
    generator = SourceConfigGenerator(source_metadata)
    yaml_content_str = generator.generate_yaml_content()

    # PyYAML's safe_load is fine for verification
    data = yaml.safe_load(yaml_content_str)

    assert data["display_name"] == "Test Source"
    assert data["base_url"] == "https://www.test.com/"
    assert data["category"] == "tech"
    assert data["rss_url"] == "https://www.test.com/feed.rss"
    assert data["article_selectors"] == ["summary"] # Default
    assert data["content_selectors"] == ["summary"] # Default

def test_generate_and_save(source_metadata, tmp_path):
    """
    Test 2.2 (File Creation): Asserts the generate_and_save method writes the
    file to the correct path.
    """
    # The PRD specifies a fixed path, but for testing, we use a temporary directory.
    # The real implementation will construct the final path.
    config_dir = tmp_path / "configs"
    config_dir.mkdir()

    generator = SourceConfigGenerator(source_metadata)
    saved_path = generator.generate_and_save(str(config_dir))

    expected_file = config_dir / "testsource.yml"

    assert saved_path == str(expected_file)
    assert expected_file.exists()

    with open(expected_file, 'r') as f:
        content = f.read()
        assert "display_name: Test Source" in content
        assert "rss_url: https://www.test.com/feed.rss" in content
