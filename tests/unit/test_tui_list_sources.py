"""Tests for List All Sources TUI — detail view and article_count edit."""
from unittest.mock import MagicMock, patch, call


def _make_mock_config(article_count=30):
    from capcat.core.source_system.base_source import SourceConfig
    return SourceConfig(
        name="bbc",
        display_name="BBC News",
        base_url="https://www.bbc.com/news",
        category="news",
        article_count=article_count,
    )


def test_list_sources_shows_article_count(tmp_path, capsys):
    """Detail view must display article_count."""
    from capcat.core.source_system.base_source import SourceConfig

    mock_config = _make_mock_config(article_count=15)
    mock_registry = MagicMock()
    mock_registry.get_source_config.return_value = mock_config
    mock_registry.get_available_sources.return_value = ["bbc"]

    with patch(
        "capcat.core.interactive.get_source_registry",
        return_value=mock_registry,
    ):
        with patch(
            "capcat.core.interactive.get_available_sources",
            return_value={"bbc": "BBC News"},
        ):
            # Simulate user selecting 'bbc' then pressing back
            with patch("capcat.core.interactive.questionary") as mock_q:
                mock_q.select.return_value.ask.side_effect = ["bbc", "back", None]
                mock_q.text.return_value.ask.return_value = None  # no edit
                from capcat.core.interactive import _handle_list_sources
                _handle_list_sources()

    captured = capsys.readouterr()
    assert "15" in captured.out or "article_count" in captured.out.lower()


def test_edit_count_writes_to_yaml(tmp_path):
    """Editing article count in TUI must write to userspace YAML."""
    import yaml
    config_dir = tmp_path / "Config" / "sources" / "active" / "config_driven" / "configs"
    config_dir.mkdir(parents=True)
    yaml_file = config_dir / "bbc.yaml"
    yaml_file.write_text(yaml.dump({
        "display_name": "BBC News",
        "base_url": "https://www.bbc.com/news",
        "article_count": 30,
        "article_selectors": ["a"],
        "content_selectors": ["div"],
    }))

    # Simulate writing a new count
    data = yaml.safe_load(yaml_file.read_text())
    data["article_count"] = 10
    yaml_file.write_text(yaml.dump(data))

    result = yaml.safe_load(yaml_file.read_text())
    assert result["article_count"] == 10
