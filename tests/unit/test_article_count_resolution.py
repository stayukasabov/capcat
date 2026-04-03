"""Tests for per-source article_count field and count resolution."""
from unittest.mock import MagicMock
from capcat.core.source_system.base_source import SourceConfig


def _config(**kwargs) -> SourceConfig:
    defaults = dict(
        name="test", display_name="Test", base_url="https://test.com",
    )
    defaults.update(kwargs)
    return SourceConfig(**defaults)


class TestSourceConfigArticleCount:
    def test_default_is_none(self):
        assert _config().article_count is None

    def test_explicit_value_stored(self):
        assert _config(article_count=15).article_count == 15

    def test_zero_not_accepted(self):
        """article_count must be positive — 0 should raise ValueError."""
        import pytest
        with pytest.raises(ValueError):
            _config(article_count=0)

    def test_negative_not_accepted(self):
        import pytest
        with pytest.raises(ValueError):
            _config(article_count=-5)


class TestRegistryLoadsArticleCount:
    def test_registry_reads_article_count_from_yaml(self, tmp_path):
        """Registry must promote article_count from YAML into SourceConfig."""
        import yaml
        cfg_dir = tmp_path / "config_driven" / "configs"
        cfg_dir.mkdir(parents=True)
        (cfg_dir / "mysource.yaml").write_text(yaml.dump({
            "display_name": "My Source",
            "base_url": "https://mysource.com",
            "article_count": 15,
            "article_selectors": ["a.article"],
            "content_selectors": ["div.content"],
        }))
        from capcat.core.source_system.source_registry import SourceRegistry
        reg = SourceRegistry(sources_dir=str(tmp_path))
        reg.discover_sources()
        cfg = reg.get_source_config("mysource")
        assert cfg is not None
        assert cfg.article_count == 15

    def test_registry_defaults_to_none_when_field_absent(self, tmp_path):
        """When article_count is absent from YAML, SourceConfig.article_count is None."""
        import yaml
        cfg_dir = tmp_path / "config_driven" / "configs"
        cfg_dir.mkdir(parents=True)
        (cfg_dir / "nosource.yaml").write_text(yaml.dump({
            "display_name": "No Count",
            "base_url": "https://nosource.com",
            "article_selectors": ["a"],
            "content_selectors": ["div"],
        }))
        from capcat.core.source_system.source_registry import SourceRegistry
        reg = SourceRegistry(sources_dir=str(tmp_path))
        reg.discover_sources()
        cfg = reg.get_source_config("nosource")
        assert cfg.article_count is None


class TestCountResolution:
    def test_explicit_cli_count_overrides_source(self):
        """When CLI count is provided, it wins over source article_count."""
        from capcat.core.unified_source_processor import _resolve_count
        from capcat.core.config import FetchNewsConfig, ProcessingConfig
        source_config = _config(article_count=10)
        cfg = FetchNewsConfig()
        cfg.processing = ProcessingConfig(article_count=30)
        assert _resolve_count(cli_count=20, source_config=source_config, config=cfg) == 20

    def test_none_cli_uses_source_count(self):
        """When CLI count is None and no vault override, source article_count is used."""
        from capcat.core.unified_source_processor import _resolve_count
        from capcat.core.config import FetchNewsConfig, ProcessingConfig
        source_config = _config(article_count=15)
        cfg = FetchNewsConfig()
        cfg.processing = ProcessingConfig(article_count=30)
        assert _resolve_count(cli_count=None, source_config=source_config, config=cfg) == 15

    def test_none_cli_none_source_falls_back_to_global(self):
        """When both CLI and source count are absent, global config default applies."""
        from capcat.core.unified_source_processor import _resolve_count
        from capcat.core.config import FetchNewsConfig, ProcessingConfig
        source_config = _config()  # article_count defaults to None
        cfg = FetchNewsConfig()
        cfg.processing = ProcessingConfig(article_count=42)
        assert _resolve_count(cli_count=None, source_config=source_config, config=cfg) == 42
