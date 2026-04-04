"""Regression tests for acceptance bug B22.

B22: _read_image_dimensions returns None for webp files, causing
     min_pixel_dimension filter to be silently skipped for all webp images.
"""
import struct
import pytest
from unittest.mock import MagicMock


def _make_vp8_webp(width: int, height: int) -> bytes:
    """Minimal VP8 (lossy) webp header with given dimensions."""
    data = bytearray(30)
    data[0:4] = b"RIFF"
    struct.pack_into("<I", data, 4, 22)
    data[8:12] = b"WEBP"
    data[12:16] = b"VP8 "
    struct.pack_into("<I", data, 16, 10)
    data[20:23] = b"\x00\x00\x00"   # frame tag
    data[23:26] = b"\x9d\x01\x2a"   # VP8 start code
    struct.pack_into("<H", data, 26, width)
    struct.pack_into("<H", data, 28, height)
    return bytes(data)


def _make_vp8l_webp(width: int, height: int) -> bytes:
    """Minimal VP8L (lossless) webp header with given dimensions."""
    data = bytearray(25)
    data[0:4] = b"RIFF"
    struct.pack_into("<I", data, 4, 17)
    data[8:12] = b"WEBP"
    data[12:16] = b"VP8L"
    struct.pack_into("<I", data, 16, 5)
    data[20] = 0x2F  # VP8L signature
    bits = (width - 1) | ((height - 1) << 14)
    struct.pack_into("<I", data, 21, bits)
    return bytes(data)


def _make_vp8x_webp(width: int, height: int) -> bytes:
    """Minimal VP8X (extended) webp header with given dimensions."""
    data = bytearray(30)
    data[0:4] = b"RIFF"
    struct.pack_into("<I", data, 4, 22)
    data[8:12] = b"WEBP"
    data[12:16] = b"VP8X"
    struct.pack_into("<I", data, 16, 10)
    data[20:24] = b"\x00\x00\x00\x00"  # flags
    data[24:27] = struct.pack("<I", width - 1)[:3]
    data[27:30] = struct.pack("<I", height - 1)[:3]
    return bytes(data)


class TestReadImageDimensionsWebp:
    """_read_image_dimensions must return correct (w, h) for all webp variants."""

    def _dims(self, tmp_path, data, name="img.webp"):
        from capcat.core.image_processor import ImageProcessor
        p = tmp_path / name
        p.write_bytes(data)
        return ImageProcessor._read_image_dimensions(str(p))

    def test_vp8_lossy_returns_dimensions(self, tmp_path):
        assert self._dims(tmp_path, _make_vp8_webp(1536, 864)) == (1536, 864)

    def test_vp8l_lossless_returns_dimensions(self, tmp_path):
        assert self._dims(tmp_path, _make_vp8l_webp(800, 600)) == (800, 600)

    def test_vp8x_extended_returns_dimensions(self, tmp_path):
        assert self._dims(tmp_path, _make_vp8x_webp(1920, 1080)) == (1920, 1080)

    def test_vp8_returns_none_for_truncated_header(self, tmp_path):
        from capcat.core.image_processor import ImageProcessor
        p = tmp_path / "trunc.webp"
        p.write_bytes(_make_vp8_webp(100, 100)[:20])  # truncated before dims
        assert ImageProcessor._read_image_dimensions(str(p)) is None


class TestMinPixelDimensionWebp:
    """min_pixel_dimension filter must reject webp images below threshold."""

    def _make_processor(self, session):
        from capcat.core.image_processor import get_image_processor
        return get_image_processor(session)

    def test_webp_below_threshold_is_rejected(self, tmp_path):
        """VP8 webp at 1536x864 rejected by min_pixel_dimension=5000."""
        session = MagicMock()
        session.head.return_value.headers = {}
        response = MagicMock()
        response.headers = {"content-type": "image/webp"}
        response.iter_content.return_value = [_make_vp8_webp(1536, 864)]
        session.get.return_value = response

        processor = self._make_processor(session)
        result = processor._download_single_image_filtered(
            "http://example.com/img.webp",
            str(tmp_path),
            1,
            min_pixel_dimension=5000,
        )
        assert result is None
        assert not any(tmp_path.iterdir())

    def test_webp_above_threshold_is_kept(self, tmp_path):
        """VP8 webp at 6000x6000 kept by min_pixel_dimension=5000."""
        session = MagicMock()
        session.head.return_value.headers = {}
        response = MagicMock()
        response.headers = {"content-type": "image/webp"}
        response.iter_content.return_value = [_make_vp8_webp(6000, 6000)]
        session.get.return_value = response

        processor = self._make_processor(session)
        result = processor._download_single_image_filtered(
            "http://example.com/img.webp",
            str(tmp_path),
            1,
            min_pixel_dimension=5000,
        )
        assert result is not None
