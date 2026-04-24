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

    def test_processing_download_images_false_not_overwritten_by_media_true(self, tmp_path):
        """When both sections present, processing.download_images=false must survive.

        Regression for B2: media: second-pass sync overwrote processing.download_images=False
        with True when media.download_images was True (the default).
        """
        settings = tmp_path / "s.yaml"
        settings.write_text(
            "media:\n  download_images: true\n"
            "processing:\n  download_images: false\n"
        )
        from capcat.core.config import ConfigManager
        mgr = ConfigManager()
        mgr._load_settings_file(settings)
        assert mgr._config.processing.download_images is False, (
            "processing.download_images=false must survive when media.download_images=true"
        )


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

    def test_processing_download_images_false_gates_media_true(self):
        """_resolve_media must return files=False when processing.download_images=False,
        even when media.download_images=True.

        Regression for B2: media.download_images=True made _resolve_media return
        files=True regardless of processing.download_images, causing images to
        download even when the user set processing.download_images=false.
        """
        from capcat.core.unified_source_processor import _resolve_media
        sc = self._make_source_config()
        cfg = self._make_config(media_kwargs={"download_images": True})
        cfg.processing.download_images = False  # user explicitly disabled
        files, _ = _resolve_media(False, False, sc, cfg)
        assert files is False, (
            "files must be False when processing.download_images=False, "
            f"even though media.download_images=True. Got files={files}"
        )

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


class TestResolveMediaForceNoPdfs:
    """BUG: TUI 'No PDFs' answer is ignored when config has download_pdfs=True.

    _resolve_media(False, False, ...) falls through to config.media.download_pdfs.
    If the user's Global-settings.yaml has download_pdfs=True (e.g. left over from
    acceptance testing), PDFs download even after the user chose 'No' in the TUI.

    Fix: force_no_pdfs=True parameter overrides config, ensuring TUI 'No' wins.
    """

    def _make_source_config(self):
        from capcat.core.source_system.base_source import SourceConfig
        return SourceConfig(
            name="hn", display_name="HN", base_url="https://news.ycombinator.com",
            category="tech",
        )

    def _make_config_with_pdfs_true(self):
        from capcat.core.config import FetchNewsConfig, MediaConfig
        cfg = FetchNewsConfig()
        cfg.media = MediaConfig(download_pdfs=True)
        return cfg

    def test_force_no_pdfs_overrides_config_true(self):
        """force_no_pdfs=True must return pdfs=False even when config has download_pdfs=True."""
        from capcat.core.unified_source_processor import _resolve_media
        sc = self._make_source_config()
        cfg = self._make_config_with_pdfs_true()

        _, pdfs = _resolve_media(False, False, sc, cfg, force_no_pdfs=True)

        assert pdfs is False, (
            f"Expected pdfs=False with force_no_pdfs=True, got {pdfs}. "
            "TUI 'No PDFs' answer is being ignored — config.media.download_pdfs=True wins."
        )

    def test_force_no_pdfs_overrides_source_config_yaml(self):
        """force_no_pdfs=True must win even when source config.yaml overrides download_pdfs=True."""
        from capcat.core.unified_source_processor import _resolve_media
        from capcat.core.source_system.base_source import SourceConfig
        sc = SourceConfig(
            name="hn", display_name="HN", base_url="https://news.ycombinator.com",
            category="tech",
            media_overrides={"download_pdfs": True},
        )
        from capcat.core.config import FetchNewsConfig, MediaConfig
        cfg = FetchNewsConfig()
        cfg.media = MediaConfig(download_pdfs=False)

        _, pdfs = _resolve_media(False, False, sc, cfg, force_no_pdfs=True)

        assert pdfs is False

    def test_force_no_pdfs_false_still_uses_config(self):
        """force_no_pdfs=False (default) must not change existing config-driven behaviour."""
        from capcat.core.unified_source_processor import _resolve_media
        sc = self._make_source_config()
        cfg = self._make_config_with_pdfs_true()

        _, pdfs = _resolve_media(False, False, sc, cfg, force_no_pdfs=False)

        assert pdfs is True, "Default behaviour (force_no_pdfs=False) must not suppress config pdfs=True"


class TestArticleFetcherImageGate:
    """download_files=True must enable images even when processing.download_images=False.

    When _resolve_media returns download_files=True (because a source-level or CLI
    override enables images), ArticleFetcher must respect that and not skip images
    based solely on processing.download_images.
    """

    IMAGE_URL = "https://example.com/photo.jpg"

    def _run_filter(self, download_files: bool, download_images_cfg: bool) -> list:
        """Run _process_embedded_media_efficiently and return attempted download URLs."""
        import requests
        from unittest.mock import MagicMock, patch
        from bs4 import BeautifulSoup
        from capcat.core.article_fetcher import NewsSourceArticleFetcher
        from capcat.core.config import FetchNewsConfig

        cfg = FetchNewsConfig()
        cfg.processing.download_images = download_images_cfg

        session = MagicMock(spec=requests.Session)
        source_config = {
            "name": "test", "base_url": "https://example.com",
            "content_selectors": ["article"], "article_selectors": ["a"],
        }
        fetcher = NewsSourceArticleFetcher(source_config, session, download_files=download_files)

        html = f'<img src="{self.IMAGE_URL}"/>'
        soup = BeautifulSoup(html, "html.parser")

        attempted = []

        def fake_download(url, *args, **kwargs):
            attempted.append(url)
            return None  # don't actually write anything

        with (
            patch("capcat.core.article_fetcher.get_config", return_value=cfg),
            patch("capcat.core.article_fetcher.download_file", side_effect=fake_download),
        ):
            fetcher._process_embedded_media_efficiently(soup, "", "/tmp", self.IMAGE_URL)

        return attempted

    def test_download_files_true_enables_images_when_config_false(self):
        """download_files=True must attempt image download even when processing.download_images=False."""
        attempted = self._run_filter(download_files=True, download_images_cfg=False)
        assert self.IMAGE_URL in attempted, (
            "Image URL must reach download_file() when download_files=True, "
            "regardless of processing.download_images"
        )

    def test_both_false_skips_images(self):
        """download_files=False and processing.download_images=False must skip images."""
        attempted = self._run_filter(download_files=False, download_images_cfg=False)
        assert self.IMAGE_URL not in attempted, (
            "Image URL must NOT reach download_file() when both flags are False"
        )

    def test_config_true_enables_images_normally(self):
        """processing.download_images=True must attempt image download (existing behaviour)."""
        attempted = self._run_filter(download_files=False, download_images_cfg=True)
        assert self.IMAGE_URL in attempted, (
            "Image URL must reach download_file() when processing.download_images=True"
        )


class TestUnifiedMediaProcessorGate:
    """media_enabled=True must bypass processing.download_images=False gate.

    BUG E1: UnifiedMediaProcessor.process_article_media() has a `media_enabled`
    parameter but line 50 only checks `get_config().processing.download_images`.
    When a source-level override sets download_files=True on the fetcher,
    process_article_media is called without media_enabled=True, so the gate
    always blocks images when global download_images=False.
    """

    def _call_processor(self, media_enabled: bool, download_images_cfg: bool) -> bool:
        """Call process_article_media and return whether image_processor was invoked."""
        from unittest.mock import MagicMock, patch
        from capcat.core.unified_media_processor import UnifiedMediaProcessor
        from capcat.core.config import FetchNewsConfig

        cfg = FetchNewsConfig()
        cfg.processing.download_images = download_images_cfg

        called = []

        mock_image_processor = MagicMock()
        mock_image_processor.process_article_images.side_effect = (
            lambda *a, **kw: called.append(True) or {}
        )

        with (
            patch("capcat.core.unified_media_processor.get_config", return_value=cfg),
            patch(
                "capcat.core.unified_media_processor.get_image_processor",
                return_value=mock_image_processor,
            ),
            patch.object(
                UnifiedMediaProcessor, "_load_source_config", return_value={}
            ),
        ):
            UnifiedMediaProcessor.process_article_media(
                content="text",
                html_content="<html></html>",
                url="https://example.com/article",
                article_folder="/tmp",
                source_name="test",
                session=MagicMock(),
                media_enabled=media_enabled,
            )

        return bool(called)

    def test_media_enabled_true_bypasses_download_images_false(self):
        """media_enabled=True must invoke image processor even when download_images=False."""
        invoked = self._call_processor(media_enabled=True, download_images_cfg=False)
        assert invoked, (
            "image_processor must be called when media_enabled=True, "
            "regardless of processing.download_images"
        )

    def test_media_enabled_false_download_images_false_skips(self):
        """media_enabled=False + download_images=False must skip image processing."""
        invoked = self._call_processor(media_enabled=False, download_images_cfg=False)
        assert not invoked, (
            "image_processor must NOT be called when both media_enabled=False "
            "and processing.download_images=False"
        )

    def test_media_enabled_false_download_images_true_proceeds(self):
        """media_enabled=False + download_images=True must still process images."""
        invoked = self._call_processor(media_enabled=False, download_images_cfg=True)
        assert invoked, (
            "image_processor must be called when processing.download_images=True"
        )
