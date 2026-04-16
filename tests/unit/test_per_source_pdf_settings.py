"""
Regression tests for per-source PDF settings.

Spec: docs/superpowers/specs/2026-04-16-per-source-pdf-settings-design.md
"""
from unittest.mock import MagicMock, patch


def _make_fetcher(source_config):
    with (
        patch("capcat.core.article_fetcher.get_config"),
        patch("capcat.core.article_fetcher.initialize_pdf_manager"),
        patch("capcat.core.ethical_scraping.get_ethical_manager"),
    ):
        from capcat.core.article_fetcher import NewsSourceArticleFetcher
        return NewsSourceArticleFetcher(source_config, MagicMock())


class TestSourceMaxPdfBytes:
    """_source_max_pdf_bytes returns per-source override or global fallback."""

    def test_returns_per_source_bytes_when_yaml_has_max_pdf_size_mb(self):
        fetcher = _make_fetcher({"name": "test", "media": {"max_pdf_size_mb": 5}})
        assert fetcher._source_max_pdf_bytes() == 5 * 1024 * 1024

    def test_returns_global_bytes_when_no_yaml_entry(self):
        mock_config = MagicMock()
        mock_config.pdf.max_pdf_size_bytes = 12345678
        with patch("capcat.core.article_fetcher.get_config", return_value=mock_config):
            fetcher = _make_fetcher({"name": "test"})
            assert fetcher._source_max_pdf_bytes() == 12345678


class TestResolveMediaPerSourcePdf:
    """_resolve_media honours source YAML download_pdfs and force_no_pdfs."""

    def _make_source_config(self, download_pdfs_override=None):
        sc = MagicMock()
        sc.media_overrides = (
            {"download_pdfs": download_pdfs_override}
            if download_pdfs_override is not None
            else {}
        )
        return sc

    def _make_config(self, download_pdfs=False):
        mock_config = MagicMock()
        mock_config.media.download_pdfs = download_pdfs
        mock_config.media.download_images = False
        mock_config.media.download_videos = False
        mock_config.media.download_audio = False
        mock_config.media.download_documents = False
        mock_config.source_overrides = {}
        return mock_config

    def test_source_yaml_true_overrides_global_false(self):
        """Source YAML download_pdfs: true wins over global download_pdfs: False."""
        from capcat.core.unified_source_processor import _resolve_media
        source_config = self._make_source_config(download_pdfs_override=True)
        _files, pdfs = _resolve_media(
            download_files=False,
            download_pdfs=False,
            source_config=source_config,
            config=self._make_config(download_pdfs=False),
            force_no_pdfs=False,
        )
        assert pdfs is True

    def test_force_no_pdfs_overrides_source_yaml_true(self):
        """TUI 'No' (force_no_pdfs=True) beats source YAML download_pdfs: true."""
        from capcat.core.unified_source_processor import _resolve_media
        source_config = self._make_source_config(download_pdfs_override=True)
        _files, pdfs = _resolve_media(
            download_files=False,
            download_pdfs=False,
            source_config=source_config,
            config=self._make_config(download_pdfs=False),
            force_no_pdfs=True,
        )
        assert pdfs is False


class TestTuiFlagEmission:
    """TUI PDF menu emits correct flags for each choice."""

    def _run_confirm_and_execute(self, pdf_choice, action="bundle", selection="all"):
        """Invoke _confirm_and_execute with a mocked PDF questionary answer."""
        import capcat.core.interactive as interactive_mod

        captured_args = []

        def fake_dispatch(args):
            captured_args.extend(args)

        with (
            patch.object(interactive_mod.questionary, "select") as mock_select,
            patch("capcat.cli._dispatch", side_effect=fake_dispatch),
            patch("capcat.core.interactive._show_completion_screen"),
            patch("capcat.core.tui_context.is_tui_active", return_value=False),
        ):
            mock_select.return_value.ask.return_value = pdf_choice
            interactive_mod._confirm_and_execute(action, selection, generate_html=False)

        return captured_args

    def test_source_defaults_emits_no_pdf_flag(self):
        """'Source defaults' must not append --pdfs or --no-pdfs."""
        args = self._run_confirm_and_execute("source_defaults")
        assert "--pdfs" not in args
        assert "--no-pdfs" not in args

    def test_yes_emits_pdfs_flag(self):
        args = self._run_confirm_and_execute("yes")
        assert "--pdfs" in args
        assert "--no-pdfs" not in args

    def test_no_emits_no_pdfs_flag(self):
        args = self._run_confirm_and_execute("no")
        assert "--no-pdfs" in args
        assert "--pdfs" not in args
