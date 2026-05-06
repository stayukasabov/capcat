"""
Regression tests for B1: article_count in capcat.yml sources list is silently
ignored.

Current broken behaviour: ConfigManager._merge_config_data drops the 'sources'
key with a warning. _resolve_count has no vault-level tier. Setting
article_count: 5 for hn in capcat.yml has no effect - the builtin source
config.yaml value (30) is always used.

Fixed behaviour: capcat.yml sources list is parsed into
FetchNewsConfig.source_overrides = {"hn": {"article_count": 5}}.
_resolve_count checks this dict as a new tier between the CLI flag and the
source's own config.yaml value.

Resolution chain after fix:
  CLI --count > capcat.yml sources list > source config.yaml > Global-settings.yaml default
"""

import os
import pytest
from capcat.core.config import FetchNewsConfig, ConfigManager


class TestFetchNewsConfigSourceOverrides:
    """FetchNewsConfig must have a source_overrides dict field."""

    def test_source_overrides_field_exists(self):
        """FetchNewsConfig must have a source_overrides dict field."""
        config = FetchNewsConfig()
        assert hasattr(config, "source_overrides"), (
            "FetchNewsConfig must have a source_overrides attribute"
        )
        assert isinstance(config.source_overrides, dict), (
            "source_overrides must be a dict"
        )

    def test_source_overrides_empty_by_default(self):
        """source_overrides must be an empty dict on fresh FetchNewsConfig."""
        config = FetchNewsConfig()
        assert config.source_overrides == {}, (
            "source_overrides must be empty dict by default"
        )


class TestConfigManagerParsesSourcesList:
    """ConfigManager must parse capcat.yml sources list into source_overrides."""

    def test_sources_list_article_count_stored_in_overrides(self, tmp_path):
        """
        When capcat.yml contains:
          sources:
            - name: hn
              article_count: 5
        ConfigManager must store {"hn": {"article_count": 5}} in source_overrides.
        """
        capcat_yml = tmp_path / "capcat.yml"
        capcat_yml.write_text(
            "sources:\n  - name: hn\n    article_count: 5\nbundles: {}\n"
        )

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            manager = ConfigManager()
            config = manager.load_config()
        finally:
            os.chdir(old_cwd)

        assert "hn" in config.source_overrides, (
            "source_overrides must contain 'hn' key after loading capcat.yml"
        )
        assert config.source_overrides["hn"].get("article_count") == 5, (
            f"Expected article_count=5 for hn, got: {config.source_overrides.get('hn')}"
        )

    def test_multiple_sources_all_stored(self, tmp_path):
        """All sources with overrides in capcat.yml must appear in source_overrides."""
        capcat_yml = tmp_path / "capcat.yml"
        capcat_yml.write_text(
            "sources:\n"
            "  - name: hn\n    article_count: 3\n"
            "  - name: lb\n    article_count: 7\n"
            "bundles: {}\n"
        )

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            manager = ConfigManager()
            config = manager.load_config()
        finally:
            os.chdir(old_cwd)

        assert config.source_overrides.get("hn", {}).get("article_count") == 3
        assert config.source_overrides.get("lb", {}).get("article_count") == 7

    def test_source_without_article_count_not_in_overrides(self, tmp_path):
        """A source entry with no article_count must not create a spurious entry."""
        capcat_yml = tmp_path / "capcat.yml"
        capcat_yml.write_text(
            "sources:\n  - name: hn\nbundles: {}\n"
        )

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            manager = ConfigManager()
            config = manager.load_config()
        finally:
            os.chdir(old_cwd)

        override = config.source_overrides.get("hn", {})
        assert "article_count" not in override, (
            "article_count must not appear in overrides when not set in capcat.yml"
        )


class TestResolvCountVaultTier:
    """_resolve_count must use vault capcat.yml article_count as new tier."""

    def test_vault_count_overrides_source_config(self):
        """
        When vault source_overrides has article_count for a source,
        _resolve_count must return it instead of the source config.yaml value.
        """
        from capcat.core.unified_source_processor import _resolve_count
        from capcat.core.source_system.base_source import SourceConfig
        from capcat.core.config import FetchNewsConfig

        source_config = SourceConfig(
            name="hn",
            display_name="Hacker News",
            base_url="https://news.ycombinator.com",
            article_count=30,
        )
        config = FetchNewsConfig()
        config.source_overrides = {"hn": {"article_count": 5}}

        result = _resolve_count(
            cli_count=None,
            source_config=source_config,
            config=config,
        )

        assert result == 5, (
            f"Expected vault override of 5, got {result}. "
            "capcat.yml source article_count must override source config.yaml value."
        )

    def test_cli_count_overrides_vault_count(self):
        """CLI --count must still win over vault capcat.yml override."""
        from capcat.core.unified_source_processor import _resolve_count
        from capcat.core.source_system.base_source import SourceConfig
        from capcat.core.config import FetchNewsConfig

        source_config = SourceConfig(
            name="hn",
            display_name="Hacker News",
            base_url="https://news.ycombinator.com",
            article_count=30,
        )
        config = FetchNewsConfig()
        config.source_overrides = {"hn": {"article_count": 5}}

        result = _resolve_count(cli_count=2, source_config=source_config, config=config)

        assert result == 2, (
            f"CLI --count=2 must override vault override of 5, got {result}"
        )

    def test_source_config_used_when_no_vault_override(self):
        """When no vault override exists, source config.yaml value is used."""
        from capcat.core.unified_source_processor import _resolve_count
        from capcat.core.source_system.base_source import SourceConfig
        from capcat.core.config import FetchNewsConfig

        source_config = SourceConfig(
            name="hn",
            display_name="Hacker News",
            base_url="https://news.ycombinator.com",
            article_count=30,
        )
        config = FetchNewsConfig()
        config.source_overrides = {}

        result = _resolve_count(cli_count=None, source_config=source_config, config=config)

        assert result == 30, (
            f"Source config.yaml value (30) must be used when no vault override, got {result}"
        )

    def test_global_default_used_when_source_count_is_none(self):
        """Global config fallback must be used when source config has no article_count."""
        from capcat.core.unified_source_processor import _resolve_count
        from capcat.core.source_system.base_source import SourceConfig
        from capcat.core.config import FetchNewsConfig, ProcessingConfig

        source_config = SourceConfig(
            name="hn",
            display_name="Hacker News",
            base_url="https://news.ycombinator.com",
            article_count=None,
        )
        config = FetchNewsConfig()
        config.source_overrides = {}
        config.processing = ProcessingConfig(article_count=15)

        result = _resolve_count(cli_count=None, source_config=source_config, config=config)

        assert result == 15, (
            f"Global processing.article_count=15 must be used as final fallback, got {result}"
        )
