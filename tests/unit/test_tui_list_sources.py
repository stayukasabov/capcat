"""Tests for List All Sources TUI - detail view and article_count edit."""
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
    """_edit_source_count must write the new count to the source YAML file."""
    from unittest.mock import patch

    # Set up a userspace YAML with article_count: 30
    config_dir = tmp_path / "Config" / "sources" / "active" / "config_driven" / "configs"
    config_dir.mkdir(parents=True)
    yaml_file = config_dir / "bbc.yaml"
    yaml_file.write_text(
        "display_name: BBC News\n"
        "base_url: https://www.bbc.com/news\n"
        "article_count: 30  # Change the article count if needed\n"
    )

    mock_config = _make_mock_config(article_count=30)

    with patch("capcat.core.config.find_project_root", return_value=tmp_path):
        with patch("capcat.core.interactive.questionary") as mock_q:
            mock_q.text.return_value.ask.return_value = "15"
            with patch("capcat.core.interactive.input", return_value=""):
                from capcat.core.interactive import _edit_source_count
                _edit_source_count("bbc", mock_config)

    content = yaml_file.read_text()
    assert "article_count: 15" in content
