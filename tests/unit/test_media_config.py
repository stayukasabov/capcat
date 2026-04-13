"""Tests for MediaConfig dataclass and 4-level media resolution chain."""
import pytest


class TestMediaConfigDefaults:
    def test_defaults(self):
        from capcat.core.config import MediaConfig
        m = MediaConfig()
        assert m.download_pdfs is False
        assert m.download_images is True
        assert m.download_videos is False
        assert m.download_audio is False
        assert m.download_documents is False

    def test_fetch_news_config_has_media(self):
        from capcat.core.config import FetchNewsConfig
        c = FetchNewsConfig()
        assert c.media is not None
        assert c.media.download_pdfs is False
        assert c.media.download_images is True


class TestMediaConfigYamlLoading:
    def test_media_section_loaded(self, tmp_path):
        settings = tmp_path / "s.yaml"
        settings.write_text(
            "media:\n"
            "  download_pdfs: true\n"
            "  download_images: false\n"
            "  download_videos: true\n"
        )
        from capcat.core.config import ConfigManager
        mgr = ConfigManager()
        mgr._load_settings_file(settings)
        assert mgr._config.media.download_pdfs is True
        assert mgr._config.media.download_images is False
        assert mgr._config.media.download_videos is True

    def test_media_section_syncs_to_processing(self, tmp_path):
        """media: keys must also update ProcessingConfig for backward compat."""
        settings = tmp_path / "s.yaml"
        settings.write_text("media:\n  download_images: false\n")
        from capcat.core.config import ConfigManager
        mgr = ConfigManager()
        mgr._load_settings_file(settings)
        assert mgr._config.processing.download_images is False

    def test_media_section_wins_over_processing_section(self, tmp_path):
        """When both media: and processing: sections are present (as in Global-settings.yaml),
        media.download_images=false must still win over processing.download_images=true."""
        settings = tmp_path / "s.yaml"
        settings.write_text(
            "media:\n"
            "  download_images: false\n"
            "processing:\n"
            "  download_images: true\n"
        )
        from capcat.core.config import ConfigManager
        mgr = ConfigManager()
        mgr._load_settings_file(settings)
        assert mgr._config.processing.download_images is False, (
            "media.download_images=false must override processing.download_images=true"
        )

    def test_unknown_media_key_does_not_raise(self, tmp_path):
        settings = tmp_path / "s.yaml"
        settings.write_text("media:\n  unknown_key: true\n")
        from capcat.core.config import ConfigManager
        mgr = ConfigManager()
        mgr._load_settings_file(settings)  # must not raise

    def test_processing_download_images_false_does_not_affect_media(self, tmp_path):
        """Old processing.download_images must NOT retroactively set media fields."""
        settings = tmp_path / "s.yaml"
        settings.write_text("processing:\n  download_images: false\n")
        from capcat.core.config import ConfigManager
        mgr = ConfigManager()
        mgr._load_settings_file(settings)
        # processing is updated
        assert mgr._config.processing.download_images is False
        # media keeps its own default (True) — only media: section controls MediaConfig
        assert mgr._config.media.download_images is True


class TestGlobalSettingsTemplate:
    def test_template_contains_media_section(self):
        from capcat.cli import GLOBAL_SETTINGS_TEMPLATE
        assert "media:" in GLOBAL_SETTINGS_TEMPLATE
        assert "download_pdfs:" in GLOBAL_SETTINGS_TEMPLATE
        assert "download_images:" in GLOBAL_SETTINGS_TEMPLATE

    def test_template_media_section_is_valid_yaml(self):
        import yaml
        from capcat.cli import GLOBAL_SETTINGS_TEMPLATE
        data = yaml.safe_load(GLOBAL_SETTINGS_TEMPLATE)
        assert "media" in data
        assert data["media"]["download_pdfs"] is False
        assert data["media"]["download_images"] is True


class TestSourceConfigMediaOverrides:
    def test_source_config_has_media_overrides_field(self):
        from capcat.core.source_system.base_source import SourceConfig
        sc = SourceConfig(name="x", display_name="X", base_url="https://x.com")
        assert hasattr(sc, "media_overrides")
        assert sc.media_overrides is None

    def test_source_config_media_overrides_set(self):
        from capcat.core.source_system.base_source import SourceConfig
        sc = SourceConfig(
            name="x", display_name="X", base_url="https://x.com",
            media_overrides={"download_pdfs": True},
        )
        assert sc.media_overrides == {"download_pdfs": True}


class TestSourceRegistryMediaParsing:
    def _build_registry_with_yaml(self, tmp_path, yaml_content):
        from capcat.core.source_system.source_registry import SourceRegistry
        config_dir = tmp_path / "config_driven" / "configs"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "testsrc.yaml"
        config_file.write_text(yaml_content)
        registry = SourceRegistry(sources_dir=tmp_path)
        registry.discover_sources()
        return registry

    _BASE_YAML = (
        "source_id: testsrc\n"
        "name: Test\n"
        "display_name: Test Source\n"
        "base_url: https://test.com\n"
        "article_count: 10\n"
        "article_selectors:\n- a[href]\n"
        "content_selectors:\n- article\n"
    )

    def test_registry_parses_media_block(self, tmp_path):
        yaml_content = self._BASE_YAML + (
            "media:\n"
            "  download_pdfs: true\n"
            "  download_images: false\n"
        )
        registry = self._build_registry_with_yaml(tmp_path, yaml_content)
        sc = registry.get_source_config("testsrc")
        assert sc is not None
        assert sc.media_overrides == {"download_pdfs": True, "download_images": False}

    def test_registry_no_media_block_gives_none(self, tmp_path):
        registry = self._build_registry_with_yaml(tmp_path, self._BASE_YAML)
        sc = registry.get_source_config("testsrc")
        assert sc is not None
        assert sc.media_overrides is None


class TestCapcatYmlMediaParsing:
    def test_capcat_yml_media_in_source_entry(self, tmp_path):
        """media: block in capcat.yml source entry lands in source_overrides."""
        capcat_yml = tmp_path / "capcat.yml"
        capcat_yml.write_text(
            "sources:\n"
            "  - name: hn\n"
            "    article_count: 5\n"
            "    media:\n"
            "      download_pdfs: true\n"
        )
        from capcat.core.config import ConfigManager
        mgr = ConfigManager()
        mgr._load_from_file(str(capcat_yml))
        overrides = mgr._config.source_overrides.get("hn", {})
        assert overrides.get("article_count") == 5
        assert overrides.get("media") == {"download_pdfs": True}


class TestResolveMedia:
    """Unit tests for _resolve_media() 4-level resolution."""

    def _make_source_config(self, media_overrides=None):
        from capcat.core.source_system.base_source import SourceConfig
        return SourceConfig(
            name="hn", display_name="HN", base_url="https://news.ycombinator.com",
            media_overrides=media_overrides,
        )

    def _make_config(self, media_kwargs=None, source_overrides=None):
        from capcat.core.config import FetchNewsConfig
        cfg = FetchNewsConfig()
        if media_kwargs:
            for k, v in media_kwargs.items():
                setattr(cfg.media, k, v)
        if source_overrides:
            cfg.source_overrides = source_overrides
        return cfg

    def test_cli_download_files_wins(self):
        from capcat.core.unified_source_processor import _resolve_media
        sc = self._make_source_config()
        cfg = self._make_config(media_kwargs={"download_images": False})
        files, pdfs = _resolve_media(True, False, sc, cfg)
        assert files is True
        assert pdfs is False

    def test_cli_download_pdfs_wins(self):
        from capcat.core.unified_source_processor import _resolve_media
        sc = self._make_source_config()
        cfg = self._make_config(media_kwargs={"download_pdfs": False})
        files, pdfs = _resolve_media(False, True, sc, cfg)
        assert pdfs is True

    def test_global_config_fallback(self):
        from capcat.core.unified_source_processor import _resolve_media
        sc = self._make_source_config()
        cfg = self._make_config(media_kwargs={"download_pdfs": True, "download_images": False})
        files, pdfs = _resolve_media(False, False, sc, cfg)
        assert pdfs is True
        assert files is False

    def test_source_config_yaml_overrides_global(self):
        from capcat.core.unified_source_processor import _resolve_media
        sc = self._make_source_config(media_overrides={"download_pdfs": True})
        cfg = self._make_config(media_kwargs={"download_pdfs": False})
        files, pdfs = _resolve_media(False, False, sc, cfg)
        assert pdfs is True

    def test_capcat_yml_overrides_source_config_yaml(self):
        from capcat.core.unified_source_processor import _resolve_media
        sc = self._make_source_config(media_overrides={"download_pdfs": False})
        cfg = self._make_config(
            media_kwargs={"download_pdfs": False},
            source_overrides={"hn": {"media": {"download_pdfs": True}}},
        )
        files, pdfs = _resolve_media(False, False, sc, cfg)
        assert pdfs is True

    def test_images_true_sets_download_files(self):
        from capcat.core.unified_source_processor import _resolve_media
        sc = self._make_source_config()
        cfg = self._make_config(media_kwargs={"download_images": True})
        files, pdfs = _resolve_media(False, False, sc, cfg)
        assert files is True

    def test_all_false_returns_false_false(self):
        from capcat.core.unified_source_processor import _resolve_media
        sc = self._make_source_config()
        cfg = self._make_config(media_kwargs={
            "download_pdfs": False,
            "download_images": False,
            "download_videos": False,
            "download_audio": False,
            "download_documents": False,
        })
        files, pdfs = _resolve_media(False, False, sc, cfg)
        assert files is False
        assert pdfs is False
