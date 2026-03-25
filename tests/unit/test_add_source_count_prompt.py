"""Tests for article_count prompt in the add-source flow."""
from unittest.mock import MagicMock, patch
from capcat.core.source_system.add_source_command import SourceMetadata, UserInterface


def test_source_metadata_has_article_count():
    """SourceMetadata must carry article_count."""
    m = SourceMetadata(
        source_id="test",
        display_name="Test",
        base_url="https://test.com",
        rss_url="https://test.com/feed",
        category="tech",
        article_count=15,
    )
    assert m.article_count == 15


def test_source_metadata_article_count_defaults_30():
    m = SourceMetadata(
        source_id="test",
        display_name="Test",
        base_url="https://test.com",
        rss_url="https://test.com/feed",
        category="tech",
    )
    assert m.article_count == 30


def test_user_interface_protocol_has_get_article_count():
    """UserInterface Protocol must declare get_article_count."""
    import inspect
    members = {name for name, _ in inspect.getmembers(UserInterface)}
    assert "get_article_count" in members, (
        "UserInterface Protocol is missing get_article_count()"
    )


def test_mock_user_interface_returns_30_by_default():
    from capcat.core.source_system.questionary_ui import MockUserInterface
    ui = MockUserInterface()
    assert ui.get_article_count() == 30


def test_count_written_to_yaml(tmp_path):
    """add-source must write article_count to the generated YAML."""
    import yaml
    from capcat.core.source_system.add_source_command import (
        AddSourceCommand, SourceMetadata
    )
    metadata = SourceMetadata(
        source_id="mytest",
        display_name="My Test",
        base_url="https://mytest.com",
        rss_url="https://mytest.com/feed",
        category="tech",
        article_count=12,
    )
    config_dir = tmp_path / "config_driven" / "configs"
    config_dir.mkdir(parents=True)

    from capcat.core.source_system.add_source_command import SourceConfigGeneratorAdapter
    from capcat.core.source_system.source_config_generator import SourceConfigGenerator
    adapter = SourceConfigGeneratorAdapter(SourceConfigGenerator)
    written = adapter.generate_and_save(metadata, config_dir)

    data = yaml.safe_load(written.read_text())
    assert data.get("article_count") == 12, (
        f"article_count not written to YAML. Got: {data}"
    )
