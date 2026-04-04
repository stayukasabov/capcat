"""Regression tests for acceptance bugs B15-B21.

B15: min_image_dimensions and max_image_size_bytes applied as pipeline
B16: max_filename_length applies to md filenames, not just folders
B17: user_agent config respected when non-default
B18: max_retries config respected
B19: use_colors: false suppresses ANSI in progress output
B20: get_progress_indicator no longer references removed show_progress_animations
B21: get_batch_progress passes progress_spinner_style to BatchProgress
"""
import os
import tempfile
from unittest.mock import MagicMock, patch, call

import pytest


# ---------------------------------------------------------------------------
# B15 — image filter pipeline
# ---------------------------------------------------------------------------

class TestImageFilterPipeline:
    """_download_single_image_filtered applies max_bytes AND min_pixel filters."""

    def _make_processor(self, session):
        from capcat.core.image_processor import get_image_processor
        return get_image_processor(session)

    def test_max_bytes_rejects_large_image(self, tmp_path):
        """Image whose content-length exceeds max_image_bytes is skipped."""
        session = MagicMock()
        session.head.return_value.headers = {"content-length": "5000"}
        processor = self._make_processor(session)
        result = processor._download_single_image_filtered(
            "http://example.com/img.jpg",
            str(tmp_path),
            1,
            max_image_bytes=1024,
        )
        assert result is None
        session.get.assert_not_called()

    def test_max_bytes_allows_small_image(self, tmp_path):
        """Image within byte ceiling is downloaded."""
        img_data = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # small fake JPEG
        session = MagicMock()
        session.head.return_value.headers = {"content-length": str(len(img_data))}
        response = MagicMock()
        response.headers = {"content-type": "image/jpeg"}
        response.iter_content.return_value = [img_data]
        session.get.return_value = response
        processor = self._make_processor(session)
        result = processor._download_single_image_filtered(
            "http://example.com/img.jpg",
            str(tmp_path),
            1,
            max_image_bytes=10_000,
        )
        assert result is not None

    def test_min_pixel_rejects_small_image(self, tmp_path):
        """Image whose dimensions are below min_pixel_dimension is deleted after download."""
        # Minimal 1x1 PNG
        png_1x1 = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01"  # width=1
            b"\x00\x00\x00\x01"  # height=1
            b"\x08\x02\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        session = MagicMock()
        session.head.return_value.headers = {}
        response = MagicMock()
        response.headers = {"content-type": "image/png"}
        response.iter_content.return_value = [png_1x1]
        session.get.return_value = response
        processor = self._make_processor(session)
        result = processor._download_single_image_filtered(
            "http://example.com/img.png",
            str(tmp_path),
            1,
            min_pixel_dimension=100,
        )
        assert result is None
        # File must be cleaned up
        assert not any(tmp_path.iterdir())

    def test_both_filters_applied_max_bytes_blocks_first(self, tmp_path):
        """max_image_bytes check runs before download; min_pixel never reached."""
        session = MagicMock()
        session.head.return_value.headers = {"content-length": "99999"}
        processor = self._make_processor(session)
        result = processor._download_single_image_filtered(
            "http://example.com/img.jpg",
            str(tmp_path),
            1,
            max_image_bytes=1024,
            min_pixel_dimension=5000,
        )
        assert result is None
        session.get.assert_not_called()

    def test_both_filters_max_bytes_passes_then_pixels_filter(self, tmp_path):
        """Image passes byte ceiling but is rejected by pixel floor."""
        png_1x1 = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01"  # width=1
            b"\x00\x00\x00\x01"  # height=1
            b"\x08\x02\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        session = MagicMock()
        session.head.return_value.headers = {"content-length": str(len(png_1x1))}
        response = MagicMock()
        response.headers = {"content-type": "image/png"}
        response.iter_content.return_value = [png_1x1]
        session.get.return_value = response
        processor = self._make_processor(session)
        result = processor._download_single_image_filtered(
            "http://example.com/img.png",
            str(tmp_path),
            1,
            max_image_bytes=10_000,
            min_pixel_dimension=5000,
        )
        assert result is None
        assert not any(tmp_path.iterdir())


# ---------------------------------------------------------------------------
# B16 — max_filename_length applies to md filenames
# ---------------------------------------------------------------------------

class TestMaxFilenameLengthMd:
    def test_article_md_filename_respects_config(self):
        from capcat.core.storage_manager import article_md_filename
        from capcat.core.config import FetchNewsConfig, ProcessingConfig

        cfg = FetchNewsConfig()
        cfg.processing = ProcessingConfig(max_filename_length=15)
        with patch("capcat.core.storage_manager.get_config", return_value=cfg):
            name = article_md_filename("This Is A Very Long Title Indeed For Testing")
        stem = name.replace(".md", "")
        assert len(stem) <= 15, f"Stem too long: {stem!r}"

    def test_comments_md_filename_respects_config(self):
        from capcat.core.storage_manager import comments_md_filename
        from capcat.core.config import FetchNewsConfig, ProcessingConfig

        cfg = FetchNewsConfig()
        cfg.processing = ProcessingConfig(max_filename_length=15)
        with patch("capcat.core.storage_manager.get_config", return_value=cfg):
            name = comments_md_filename("This Is A Very Long Title Indeed For Testing")
        stem = name.replace("-Comments.md", "")
        assert len(stem) <= 15, f"Stem too long: {stem!r}"

    def test_article_md_filename_default_length(self):
        from capcat.core.storage_manager import article_md_filename
        from capcat.core.config import FetchNewsConfig, ProcessingConfig

        cfg = FetchNewsConfig()
        cfg.processing = ProcessingConfig(max_filename_length=100)
        with patch("capcat.core.storage_manager.get_config", return_value=cfg):
            name = article_md_filename("Short Title")
        assert name == "Short-Title.md"


# ---------------------------------------------------------------------------
# B17 — user_agent config respected
# ---------------------------------------------------------------------------

class TestUserAgentConfig:
    def _create_session_with_ua(self, user_agent):
        from capcat.core.config import FetchNewsConfig, NetworkConfig
        from capcat.core.session_pool import SessionPool
        cfg = FetchNewsConfig()
        cfg.network = NetworkConfig(user_agent=user_agent)
        with patch("capcat.core.session_pool.get_config", return_value=cfg):
            pool = SessionPool()
            pool.config = cfg  # inject config directly on singleton
            return pool._create_session("test_source")

    def test_custom_user_agent_used(self):
        session = self._create_session_with_ua("TestBot/1.0")
        assert session.headers["User-Agent"] == "TestBot/1.0"

    def test_default_user_agent_rotates(self):
        from capcat.core.session_pool import USER_AGENTS
        session = self._create_session_with_ua("Capcat/2.0 (Personal news archiver)")
        assert session.headers["User-Agent"] in USER_AGENTS


# ---------------------------------------------------------------------------
# B18 — max_retries config respected
# ---------------------------------------------------------------------------

class TestMaxRetriesConfig:
    def _pool_with_retries(self, max_retries):
        from capcat.core.config import FetchNewsConfig, NetworkConfig
        from capcat.core.session_pool import SessionPool
        cfg = FetchNewsConfig()
        cfg.network = NetworkConfig(max_retries=max_retries)
        with patch("capcat.core.session_pool.get_config", return_value=cfg):
            pool = SessionPool()
            pool.config = cfg
            return pool

    def test_max_retries_zero_passed_to_adapter(self):
        pool = self._pool_with_retries(0)
        with patch("capcat.core.session_pool.requests.adapters.HTTPAdapter") as mock_adapter:
            mock_adapter.return_value = MagicMock()
            pool._create_session("test_source")
            kwargs = mock_adapter.call_args.kwargs
            assert kwargs["max_retries"] == 0

    def test_max_retries_custom_value(self):
        pool = self._pool_with_retries(5)
        with patch("capcat.core.session_pool.requests.adapters.HTTPAdapter") as mock_adapter:
            mock_adapter.return_value = MagicMock()
            pool._create_session("test_source")
            kwargs = mock_adapter.call_args.kwargs
            assert kwargs["max_retries"] == 5


# ---------------------------------------------------------------------------
# B19 — use_colors: false suppresses ANSI in BatchProgress
# ---------------------------------------------------------------------------

class TestUseColorsConfig:
    def test_use_colors_false_no_ansi_in_start_banner(self, capsys):
        from capcat.core.progress import BatchProgress
        from capcat.core.config import FetchNewsConfig, UIConfig

        cfg = FetchNewsConfig()
        cfg.ui = UIConfig(use_colors=False)
        with patch("capcat.core.progress.get_config", return_value=cfg):
            bp = BatchProgress("Test Op", 3)
            with patch.object(bp, "_hide_cursor"), \
                 patch("capcat.core.logging_config.set_progress_active"):
                bp.start()

        captured = capsys.readouterr().out
        assert "\033[" not in captured, f"ANSI codes found: {captured!r}"

    def test_use_colors_true_has_ansi_in_start_banner(self, capsys):
        from capcat.core.progress import BatchProgress
        from capcat.core.config import FetchNewsConfig, UIConfig

        cfg = FetchNewsConfig()
        cfg.ui = UIConfig(use_colors=True)
        with patch("capcat.core.progress.get_config", return_value=cfg):
            bp = BatchProgress("Test Op", 3)
            with patch.object(bp, "_hide_cursor"), \
                 patch("capcat.core.logging_config.set_progress_active"):
                bp.start()

        captured = capsys.readouterr().out
        assert "\033[" in captured


# ---------------------------------------------------------------------------
# B20 — get_progress_indicator no longer crashes on missing attribute
# ---------------------------------------------------------------------------

class TestGetProgressIndicator:
    def test_get_progress_indicator_does_not_raise(self):
        from capcat.core.progress import get_progress_indicator
        from capcat.core.config import FetchNewsConfig, UIConfig

        cfg = FetchNewsConfig()
        cfg.ui = UIConfig(progress_spinner_style="dots")
        with patch("capcat.core.progress.get_config", return_value=cfg):
            indicator = get_progress_indicator("test", 5)
        assert indicator is not None


# ---------------------------------------------------------------------------
# B21 — get_batch_progress passes spinner_style to BatchProgress
# ---------------------------------------------------------------------------

class TestBatchProgressSpinnerStyle:
    def test_spinner_style_from_config_passed_to_batch_progress(self):
        from capcat.core.progress import get_batch_progress
        from capcat.core.config import FetchNewsConfig, UIConfig

        cfg = FetchNewsConfig()
        cfg.ui = UIConfig(progress_spinner_style="wave")
        with patch("capcat.core.progress.get_config", return_value=cfg):
            bp = get_batch_progress("Test", 3, quiet=False)
        assert bp.spinner_chars == bp.spinner_sets["wave"]

    def test_spinner_style_dots_is_default(self):
        from capcat.core.progress import get_batch_progress
        from capcat.core.config import FetchNewsConfig, UIConfig

        cfg = FetchNewsConfig()
        cfg.ui = UIConfig(progress_spinner_style="dots")
        with patch("capcat.core.progress.get_config", return_value=cfg):
            bp = get_batch_progress("Test", 3, quiet=False)
        assert bp.spinner_chars == bp.spinner_sets["dots"]
