"""Tests for PdfConfig dataclass and from_dict() completeness."""
from capcat.core.config import (
    FetchNewsConfig,
    PdfConfig,
    _filter_fields,
)


class TestPdfConfig:
    def test_defaults(self):
        cfg = PdfConfig()
        assert cfg.max_pdf_size_bytes == 20_971_520
        assert cfg.max_pdf_per_article == 10

    def test_custom_values(self):
        cfg = PdfConfig(max_pdf_size_bytes=10_000, max_pdf_per_article=3)
        assert cfg.max_pdf_size_bytes == 10_000
        assert cfg.max_pdf_per_article == 3


class TestFetchNewsConfigPdf:
    def test_pdf_field_initialized(self):
        cfg = FetchNewsConfig()
        assert cfg.pdf is not None
        assert isinstance(cfg.pdf, PdfConfig)

    def test_pdf_defaults(self):
        cfg = FetchNewsConfig()
        assert cfg.pdf.max_pdf_size_bytes == 20_971_520

    def test_from_dict_preserves_pdf(self):
        data = {"pdf": {"max_pdf_size_bytes": 5_000_000, "max_pdf_per_article": 3}}
        cfg = FetchNewsConfig.from_dict(data)
        assert cfg.pdf.max_pdf_size_bytes == 5_000_000
        assert cfg.pdf.max_pdf_per_article == 3

    def test_from_dict_unknown_key_ignored(self):
        """_filter_fields prevents TypeError on unknown keys."""
        data = {"pdf": {"max_pdf_size_bytes": 5_000_000, "unknown_key": "ignored"}}
        cfg = FetchNewsConfig.from_dict(data)
        assert cfg.pdf.max_pdf_size_bytes == 5_000_000

    def test_from_dict_empty_pdf_uses_defaults(self):
        cfg = FetchNewsConfig.from_dict({})
        assert cfg.pdf.max_pdf_size_bytes == 20_971_520

    def test_from_dict_ui_preserved(self):
        """from_dict() must not silently drop ui section."""
        data = {"ui": {"progress_spinner_style": "wave"}}
        cfg = FetchNewsConfig.from_dict(data)
        assert cfg.ui.progress_spinner_style == "wave"


class TestFilterFields:
    def test_keeps_known_fields(self):
        result = _filter_fields(PdfConfig, {"max_pdf_size_bytes": 1, "max_pdf_per_article": 2})
        assert result == {"max_pdf_size_bytes": 1, "max_pdf_per_article": 2}

    def test_drops_unknown_fields(self):
        result = _filter_fields(PdfConfig, {"max_pdf_size_bytes": 1, "bogus": "x"})
        assert "bogus" not in result
        assert result["max_pdf_size_bytes"] == 1


import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from capcat.core.config import ConfigManager


class TestLoadSettingsFile:
    def _make_yaml(self, content: str, tmp_path: Path) -> Path:
        f = tmp_path / "Global-settings.yaml"
        f.write_text(content)
        return f

    def test_missing_file_is_silently_ignored(self, tmp_path):
        mgr = ConfigManager()
        mgr._config = __import__('capcat.core.config', fromlist=['FetchNewsConfig']).FetchNewsConfig()
        mgr._load_settings_file(tmp_path / "nonexistent.yaml")  # must not raise

    def test_vault_overrides_default(self, tmp_path):
        mgr = ConfigManager()
        path = self._make_yaml("pdf:\n  max_pdf_size_bytes: 1000000\n", tmp_path)
        mgr._config = __import__('capcat.core.config', fromlist=['FetchNewsConfig']).FetchNewsConfig()
        mgr._load_settings_file(path)
        assert mgr._config.pdf.max_pdf_size_bytes == 1_000_000

    def test_sources_and_bundles_silenced(self, tmp_path):
        mgr = ConfigManager()
        path = self._make_yaml(
            "sources:\n  - foo\nbundles:\n  - bar\npdf:\n  max_pdf_per_article: 3\n",
            tmp_path
        )
        mgr._config = __import__('capcat.core.config', fromlist=['FetchNewsConfig']).FetchNewsConfig()
        mgr._load_settings_file(path)
        # sources/bundles silently dropped; pdf applied
        assert mgr._config.pdf.max_pdf_per_article == 3

    def test_unknown_section_logged_not_raised(self, tmp_path):
        mgr = ConfigManager()
        path = self._make_yaml("unknown_section:\n  foo: bar\n", tmp_path)
        mgr._config = __import__('capcat.core.config', fromlist=['FetchNewsConfig']).FetchNewsConfig()
        mgr._load_settings_file(path)  # must not raise

    def test_unknown_key_in_known_section_ignored(self, tmp_path):
        mgr = ConfigManager()
        path = self._make_yaml(
            "pdf:\n  max_pdf_size_bytes: 999\n  bogus_key: ignored\n", tmp_path
        )
        mgr._config = __import__('capcat.core.config', fromlist=['FetchNewsConfig']).FetchNewsConfig()
        mgr._load_settings_file(path)
        assert mgr._config.pdf.max_pdf_size_bytes == 999

    def test_user_then_vault_merge_order(self, tmp_path):
        """Vault-level setting overrides user-level; unset keys keep user value."""
        user_dir = tmp_path / "user"
        vault_dir = tmp_path / "vault"
        user_dir.mkdir()
        vault_dir.mkdir()
        (user_dir / "Global-settings.yaml").write_text(
            "pdf:\n  max_pdf_size_bytes: 5000000\n  max_pdf_per_article: 7\n"
        )
        (vault_dir / "Global-settings.yaml").write_text(
            "pdf:\n  max_pdf_size_bytes: 1000000\n"
        )
        mgr = ConfigManager()
        from capcat.core.config import FetchNewsConfig
        mgr._config = FetchNewsConfig()
        mgr._load_settings_file(user_dir / "Global-settings.yaml")
        mgr._load_settings_file(vault_dir / "Global-settings.yaml")
        # vault wins on max_pdf_size_bytes
        assert mgr._config.pdf.max_pdf_size_bytes == 1_000_000
        # user value for max_pdf_per_article preserved (vault didn't set it)
        assert mgr._config.pdf.max_pdf_per_article == 7

    def test_load_config_fires_settings_files_unconditionally(self, tmp_path, monkeypatch):
        """load_config() must load user-level and vault-level settings without --config flag."""
        # Arrange: user-level and vault-level files with different pdf values
        user_dir = tmp_path / "home" / ".config" / "capcat"
        vault_dir = tmp_path / "vault" / "Config"
        user_dir.mkdir(parents=True)
        vault_dir.mkdir(parents=True)
        (user_dir / "Global-settings.yaml").write_text(
            "pdf:\n  max_pdf_size_bytes: 3000000\n  max_pdf_per_article: 5\n"
        )
        (vault_dir / "Global-settings.yaml").write_text(
            "pdf:\n  max_pdf_size_bytes: 1000000\n"
        )

        # Patch Path.home() to return our fake home, and cwd to return fake vault
        monkeypatch.chdir(tmp_path / "vault")
        with patch("capcat.core.config.Path.home", return_value=tmp_path / "home"):
            mgr = ConfigManager()
            # Suppress env var loading and legacy capcat.yml search
            cfg = mgr.load_config(load_env=False)

        # vault overrides user on max_pdf_size_bytes
        assert cfg.pdf.max_pdf_size_bytes == 1_000_000
        # user value preserved for max_pdf_per_article
        assert cfg.pdf.max_pdf_per_article == 5


class TestNewConfigFields:
    def test_processing_new_fields_defaults(self):
        from capcat.core.config import ProcessingConfig
        cfg = ProcessingConfig()
        assert cfg.article_count == 30
        assert cfg.max_images == 20
        assert cfg.max_images_media_mode == 1000
        assert cfg.min_image_dimensions == 150
        assert cfg.max_image_size_bytes == 5_242_880
        assert cfg.conversion_timeout == 30

    def test_network_new_fields_defaults(self):
        from capcat.core.config import NetworkConfig
        cfg = NetworkConfig()
        assert cfg.crawl_delay == 1.0
        assert cfg.robots_cache_ttl_minutes == 15

    def test_processing_fields_loadable_from_yaml(self, tmp_path):
        from capcat.core.config import ConfigManager, FetchNewsConfig
        yaml_content = (
            "processing:\n"
            "  article_count: 50\n"
            "  max_images: 10\n"
            "  conversion_timeout: 60\n"
        )
        path = tmp_path / "Global-settings.yaml"
        path.write_text(yaml_content)
        mgr = ConfigManager()
        mgr._config = FetchNewsConfig()
        mgr._load_settings_file(path)
        assert mgr._config.processing.article_count == 50
        assert mgr._config.processing.max_images == 10
        assert mgr._config.processing.conversion_timeout == 60

    def test_network_fields_loadable_from_yaml(self, tmp_path):
        from capcat.core.config import ConfigManager, FetchNewsConfig
        yaml_content = "network:\n  crawl_delay: 2.5\n  robots_cache_ttl_minutes: 30\n"
        path = tmp_path / "Global-settings.yaml"
        path.write_text(yaml_content)
        mgr = ConfigManager()
        mgr._config = FetchNewsConfig()
        mgr._load_settings_file(path)
        assert mgr._config.network.crawl_delay == 2.5
        assert mgr._config.network.robots_cache_ttl_minutes == 30
