"""Tests for per-source article_count field and count resolution."""
from capcat.core.source_system.base_source import SourceConfig


def _config(**kwargs) -> SourceConfig:
    defaults = dict(
        name="test", display_name="Test", base_url="https://test.com",
    )
    defaults.update(kwargs)
    return SourceConfig(**defaults)


class TestSourceConfigArticleCount:
    def test_default_is_30(self):
        assert _config().article_count == 30

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

    def test_registry_defaults_to_30_when_field_absent(self, tmp_path):
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
        assert cfg.article_count == 30
