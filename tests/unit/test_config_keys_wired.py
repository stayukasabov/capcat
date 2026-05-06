"""Tests for config keys that were previously dead code.

Covers:
- remove_style_tags / remove_nav_tags
- console_level
- progress_spinner_style
- min_image_dimensions
- max_image_size_bytes
- markdown_line_breaks
"""
from unittest.mock import MagicMock, patch, call
from pathlib import Path

from capcat.core.config import FetchNewsConfig, ProcessingConfig, UIConfig, LoggingConfig


# ---------------------------------------------------------------------------
# HTML tag removal flags
# ---------------------------------------------------------------------------

def _fetch_article_content(html: str, remove_style=True, remove_nav=True):
    """Helper: run html_to_markdown with given remove_* flags active via config."""
    from capcat.core.formatter import html_to_markdown
    from capcat.core.config import ProcessingConfig, FetchNewsConfig

    cfg = FetchNewsConfig()
    cfg.processing = ProcessingConfig(
        remove_style_tags=remove_style,
        remove_nav_tags=remove_nav,
    )
    with patch("capcat.core.formatter.get_config", return_value=cfg):
        return html_to_markdown(html)


class TestRemoveTagFlags:
    def test_script_always_stripped(self):
        html = "<p>Text</p><script>alert(1)</script>"
        result = _fetch_article_content(html)
        assert "alert" not in result

    def test_remove_style_true_strips_style(self):
        html = "<p>Text</p><style>.foo{color:red}</style>"
        result = _fetch_article_content(html, remove_style=True)
        assert "color:red" not in result

    def test_remove_style_false_keeps_style_text(self):
        html = "<p>Text</p><style>.foo{color:red}</style>"
        result = _fetch_article_content(html, remove_style=False)
        assert "color" in result

    def test_remove_nav_true_strips_nav(self):
        html = "<p>Article</p><nav>Home | About</nav>"
        result = _fetch_article_content(html, remove_nav=True)
        assert "Home | About" not in result

    def test_remove_nav_false_keeps_nav(self):
        html = "<p>Article</p><nav>Home | About</nav>"
        result = _fetch_article_content(html, remove_nav=False)
        assert "Home" in result


# ---------------------------------------------------------------------------
# console_level
# ---------------------------------------------------------------------------

class TestConsoleLevelConfig:
    def test_console_level_warning_suppresses_info(self, capsys):
        from capcat.core.logging_config import setup_logging
        from capcat.core.config import LoggingConfig, FetchNewsConfig
        cfg = FetchNewsConfig()
        cfg.logging = LoggingConfig(console_level="WARNING")
        logger = setup_logging(level=cfg.logging.console_level)
        logger.info("should be suppressed")
        captured = capsys.readouterr()
        assert "should be suppressed" not in captured.out

    def test_console_level_debug_shows_debug(self, capsys):
        from capcat.core.logging_config import setup_logging
        from capcat.core.config import LoggingConfig, FetchNewsConfig
        cfg = FetchNewsConfig()
        cfg.logging = LoggingConfig(console_level="DEBUG")
        logger = setup_logging(level=cfg.logging.console_level)
        logger.debug("debug-msg")
        captured = capsys.readouterr()
        assert "debug-msg" in captured.out


# ---------------------------------------------------------------------------
# progress_spinner_style
# ---------------------------------------------------------------------------

class TestProgressSpinnerStyle:
    def test_spinner_style_passed_to_indicator(self):
        from capcat.core.progress import ProgressIndicator
        pi = ProgressIndicator("test", spinner_style="wave")
        assert pi.spinner_chars == pi.spinner_sets["wave"]

    def test_spinner_style_config_read(self):
        from capcat.core.config import UIConfig, FetchNewsConfig
        cfg = FetchNewsConfig()
        cfg.ui = UIConfig(progress_spinner_style="pulse")
        assert cfg.ui.progress_spinner_style == "pulse"


# ---------------------------------------------------------------------------
# min_image_dimensions
# ---------------------------------------------------------------------------

class TestMinImageDimensions:
    def test_image_below_min_pixels_rejected(self, tmp_path):
        """_download_single_image_simple must reject images below min_pixel_dimension."""
        from capcat.core.image_processor import ImageProcessor
        import struct, zlib

        # Create a valid 50×50 PNG
        def make_png(w, h):
            def chunk(name, data):
                c = zlib.crc32(name + data) & 0xffffffff
                return struct.pack(">I", len(data)) + name + data + struct.pack(">I", c)
            raw = b"\x89PNG\r\n\x1a\n"
            raw += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            row = b"\x00" + b"\xff\x00\x00" * w
            compressed = zlib.compress(row * h)
            raw += chunk(b"IDAT", compressed)
            raw += chunk(b"IEND", b"")
            return raw

        png_50 = make_png(50, 50)
        session = MagicMock()
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.headers = {"content-type": "image/png"}
        response.iter_content = MagicMock(return_value=[png_50])
        session.get.return_value = response

        processor = ImageProcessor(session)
        images_dir = str(tmp_path / "images")
        Path(images_dir).mkdir()

        result = processor._download_single_image_with_min_pixels(
            "https://example.com/img.png", images_dir, 1, min_pixel_dimension=150
        )
        assert result is None  # 50×50 < 150px - rejected

    def test_image_above_min_pixels_accepted(self, tmp_path):
        """_download_single_image_simple must keep images at or above min_pixel_dimension."""
        from capcat.core.image_processor import ImageProcessor
        import struct, zlib

        def make_png(w, h):
            def chunk(name, data):
                c = zlib.crc32(name + data) & 0xffffffff
                return struct.pack(">I", len(data)) + name + data + struct.pack(">I", c)
            raw = b"\x89PNG\r\n\x1a\n"
            raw += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            row = b"\x00" + b"\xff\x00\x00" * w
            compressed = zlib.compress(row * h)
            raw += chunk(b"IDAT", compressed)
            raw += chunk(b"IEND", b"")
            return raw

        png_200 = make_png(200, 200)
        session = MagicMock()
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.headers = {"content-type": "image/png"}
        response.iter_content = MagicMock(return_value=[png_200])
        session.get.return_value = response

        processor = ImageProcessor(session)
        images_dir = str(tmp_path / "images")
        Path(images_dir).mkdir()

        result = processor._download_single_image_with_min_pixels(
            "https://example.com/img.png", images_dir, 1, min_pixel_dimension=150
        )
        assert result is not None  # 200×200 ≥ 150px - accepted


# ---------------------------------------------------------------------------
# max_image_size_bytes
# ---------------------------------------------------------------------------

class TestMaxImageSizeBytes:
    def test_image_above_max_bytes_rejected_via_content_length(self, tmp_path):
        """Image with content-length > max_image_size_bytes must be skipped."""
        from capcat.core.image_processor import ImageProcessor

        session = MagicMock()
        head_response = MagicMock()
        head_response.headers = {"content-length": "2000000"}  # 2MB
        session.head.return_value = head_response

        processor = ImageProcessor(session)
        images_dir = str(tmp_path / "images")
        Path(images_dir).mkdir()

        result = processor._download_single_image_with_max_bytes(
            "https://example.com/big.jpg", images_dir, 1, max_bytes=1048576  # 1MB cap
        )
        assert result is None  # 2MB > 1MB - rejected
        session.get.assert_not_called()  # No download attempted

    def test_image_below_max_bytes_downloaded(self, tmp_path):
        """Image with content-length ≤ max_image_size_bytes must be downloaded."""
        from capcat.core.image_processor import ImageProcessor

        session = MagicMock()
        head_response = MagicMock()
        head_response.headers = {"content-length": "50000"}  # 50KB
        session.head.return_value = head_response

        get_response = MagicMock()
        get_response.raise_for_status = MagicMock()
        get_response.headers = {"content-type": "image/jpeg"}
        get_response.iter_content = MagicMock(return_value=[b"\xff\xd8\xff" + b"\x00" * 100])
        session.get.return_value = get_response

        processor = ImageProcessor(session)
        images_dir = str(tmp_path / "images")
        Path(images_dir).mkdir()

        result = processor._download_single_image_with_max_bytes(
            "https://example.com/img.jpg", images_dir, 1, max_bytes=1048576
        )
        assert result is not None  # 50KB < 1MB - accepted


# ---------------------------------------------------------------------------
# markdown_line_breaks
# ---------------------------------------------------------------------------

class TestMarkdownLineBreaks:
    def test_br_tag_produces_backslash_when_true(self):
        """<br> must produce a markdown hard break (\\) when markdown_line_breaks=True."""
        from capcat.core.formatter import html_to_markdown
        from capcat.core.config import ProcessingConfig, FetchNewsConfig
        cfg = FetchNewsConfig()
        cfg.processing = ProcessingConfig(markdown_line_breaks=True)
        with patch("capcat.core.formatter.get_config", return_value=cfg):
            result = html_to_markdown("<p>Line one<br>Line two</p>")
        assert "\\\n" in result or "  \n" in result

    def test_br_tag_produces_newline_only_when_false(self):
        """<br> must produce a plain newline (no \\) when markdown_line_breaks=False."""
        from capcat.core.formatter import html_to_markdown
        from capcat.core.config import ProcessingConfig, FetchNewsConfig
        cfg = FetchNewsConfig()
        cfg.processing = ProcessingConfig(markdown_line_breaks=False)
        with patch("capcat.core.formatter.get_config", return_value=cfg):
            result = html_to_markdown("<p>Line one<br>Line two</p>")
        assert "\\\n" not in result
        assert "  \n" not in result
