"""
Tests for ImageProcessor URL path filtering and pixel-dimension rejection.
"""
import os
import struct
import tempfile

import pytest

from capcat.core.image_processor import ImageProcessor


# ---------------------------------------------------------------------------
# _UI_PATH_PATTERNS — URL path filtering
# ---------------------------------------------------------------------------

class TestUIPathPatterns:
    """_extract_image_urls skips images whose URL path matches _UI_PATH_PATTERNS."""

    def _processor(self):
        return ImageProcessor.__new__(ImageProcessor)

    def _path_is_blocked(self, url_path: str) -> bool:
        """Return True if the path would be filtered by _UI_PATH_PATTERNS."""
        proc = self._processor()
        from urllib.parse import urlparse
        path = urlparse(f"https://example.com{url_path}").path.lower()
        return any(p in path for p in ImageProcessor._UI_PATH_PATTERNS)

    # Paths that SHOULD be filtered
    def test_icon_in_path(self):
        assert self._path_is_blocked("/assets/icon-32.png")

    def test_logo_in_path(self):
        assert self._path_is_blocked("/static/images/logo.svg")

    def test_social_in_path(self):
        assert self._path_is_blocked("/img/social-share.png")

    def test_pixel_tracker(self):
        assert self._path_is_blocked("/track/pixel.gif")

    def test_1x1_tracker(self):
        assert self._path_is_blocked("/beacon/1x1.gif")

    def test_nav_image(self):
        assert self._path_is_blocked("/ui/nav-arrow.png")

    def test_spinner(self):
        assert self._path_is_blocked("/loading/spinner.gif")

    # Real-world cases from arXiv (the original motivation for this feature)
    def test_arxiv_abspage_logo(self):
        assert self._path_is_blocked("/static/base/images/arxiv-logo.png")

    def test_arxiv_social_icon(self):
        assert self._path_is_blocked("/static/browse/0.3.4/images/icons/social/twitter.png")

    # Paths that should NOT be filtered
    def test_article_figure_passes(self):
        assert not self._path_is_blocked("/figures/fig1.png")

    def test_bbc_content_image_passes(self):
        assert not self._path_is_blocked("/news/special/2024/newsspec_46817/hi/image.png")

    def test_guardian_content_image_passes(self):
        assert not self._path_is_blocked(
            "/img/media/2024/photo-article-main.jpg"
        )

    def test_arxiv_content_image_passes(self):
        assert not self._path_is_blocked("/html/2403.12345/assets/x1.png")

    def test_deep_path_no_keyword_passes(self):
        assert not self._path_is_blocked("/content/uploads/2024/03/photo.jpg")


# ---------------------------------------------------------------------------
# _read_image_dimensions — PNG and JPEG header parsing
# ---------------------------------------------------------------------------

def _make_png(width: int, height: int) -> bytes:
    """Produce a minimal but valid PNG header (signature + IHDR chunk)."""
    sig = b"\x89PNG\r\n\x1a\n"
    # IHDR: length(4) + "IHDR"(4) + w(4) + h(4) + bit_depth(1) + color_type(1)
    #       + compression(1) + filter(1) + interlace(1) = 13 bytes data
    ihdr_data = struct.pack(">II", width, height) + b"\x08\x02\x00\x00\x00"
    ihdr_len = struct.pack(">I", len(ihdr_data))
    # CRC is not checked in our parser, so use zeros
    ihdr_crc = b"\x00\x00\x00\x00"
    return sig + ihdr_len + b"IHDR" + ihdr_data + ihdr_crc


def _make_jpeg(width: int, height: int) -> bytes:
    """Produce a minimal JPEG byte stream with a SOF0 marker."""
    soi = b"\xff\xd8"
    # SOF0 marker: FF C0 + length(2) + precision(1) + height(2) + width(2) + components(1)
    sof_data = b"\x08" + struct.pack(">HH", height, width) + b"\x03"
    sof_len = struct.pack(">H", 2 + len(sof_data))
    sof0 = b"\xff\xc0" + sof_len + sof_data
    eoi = b"\xff\xd9"
    return soi + sof0 + eoi


class TestReadImageDimensions:
    def _write_tmp(self, data: bytes) -> str:
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        return path

    def test_png_normal_dimensions(self):
        path = self._write_tmp(_make_png(800, 600))
        try:
            assert ImageProcessor._read_image_dimensions(path) == (800, 600)
        finally:
            os.unlink(path)

    def test_png_small_icon(self):
        path = self._write_tmp(_make_png(32, 32))
        try:
            assert ImageProcessor._read_image_dimensions(path) == (32, 32)
        finally:
            os.unlink(path)

    def test_jpeg_normal_dimensions(self):
        path = self._write_tmp(_make_jpeg(1200, 800))
        try:
            assert ImageProcessor._read_image_dimensions(path) == (1200, 800)
        finally:
            os.unlink(path)

    def test_jpeg_small_icon(self):
        path = self._write_tmp(_make_jpeg(16, 16))
        try:
            assert ImageProcessor._read_image_dimensions(path) == (16, 16)
        finally:
            os.unlink(path)

    def test_unknown_format_returns_none(self):
        path = self._write_tmp(b"RIFF\x00\x00\x00\x00WEBP")
        try:
            assert ImageProcessor._read_image_dimensions(path) is None
        finally:
            os.unlink(path)

    def test_empty_file_returns_none(self):
        path = self._write_tmp(b"")
        try:
            assert ImageProcessor._read_image_dimensions(path) is None
        finally:
            os.unlink(path)

    def test_nonexistent_file_returns_none(self):
        assert ImageProcessor._read_image_dimensions("/tmp/does_not_exist_capcat.png") is None


# ---------------------------------------------------------------------------
# _MIN_PIXEL_DIMENSION threshold value
# ---------------------------------------------------------------------------

def test_min_pixel_dimension_is_64():
    assert ImageProcessor._MIN_PIXEL_DIMENSION == 64
