"""
Tests for ImageProcessor pixel-dimension rejection.
"""
import os
import struct
import tempfile

import pytest

from capcat.core.image_processor import ImageProcessor


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
# _read_image_dimensions — AVIF (ISO Base Media / ftyp) parsing
# BUG F1: Guardian/BBC serve AVIF files with .jpg extensions. When
# _read_image_dimensions returned None for AVIF, the pixel floor check was
# silently skipped, allowing small images through regardless of min_image_dimensions.
# ---------------------------------------------------------------------------

def _make_avif(width: int, height: int) -> bytes:
    """
    Produce a minimal AVIF-like byte stream sufficient for header detection.

    Structure:
      ftyp box  (24 bytes): size=24, 'ftyp', major='avif', minor=0, compat='mif1avif'
      ispe box  (20 bytes): size=20, 'ispe', flags=0, width, height
    """
    ftyp = (
        struct.pack(">I", 24)  # box size
        + b"ftyp"
        + b"avif"              # major brand
        + b"\x00\x00\x00\x00" # minor version
        + b"mif1"              # compatible brand 1
        + b"avif"              # compatible brand 2
    )
    ispe = (
        struct.pack(">I", 20)  # box size
        + b"ispe"
        + b"\x00\x00\x00\x00" # version + flags
        + struct.pack(">II", width, height)
    )
    return ftyp + ispe


class TestReadImageDimensionsAvif:
    """_read_image_dimensions must parse AVIF (ISO Base Media ftyp) files."""

    def _write_tmp(self, data: bytes) -> str:
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        return path

    def test_avif_normal_dimensions(self):
        path = self._write_tmp(_make_avif(1200, 800))
        try:
            result = ImageProcessor._read_image_dimensions(path)
            assert result == (1200, 800), (
                f"Expected (1200, 800), got {result}. "
                "AVIF format is not parsed — min_image_dimensions filter is silently skipped."
            )
        finally:
            os.unlink(path)

    def test_avif_small_icon_dimensions(self):
        path = self._write_tmp(_make_avif(32, 32))
        try:
            result = ImageProcessor._read_image_dimensions(path)
            assert result == (32, 32), (
                f"Expected (32, 32), got {result}."
            )
        finally:
            os.unlink(path)

    def test_avif_returns_tuple_not_none(self):
        """AVIF must not return None — that causes the pixel floor to be silently skipped."""
        path = self._write_tmp(_make_avif(640, 480))
        try:
            result = ImageProcessor._read_image_dimensions(path)
            assert result is not None, (
                "AVIF returned None — pixel dimension filter will be skipped for AVIF images."
            )
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# _MIN_PIXEL_DIMENSION threshold value
# ---------------------------------------------------------------------------

def test_min_pixel_dimension_is_64():
    assert ImageProcessor._MIN_PIXEL_DIMENSION == 64


# ---------------------------------------------------------------------------
# _is_valid_image_url — CDN proxy URL handling
# ---------------------------------------------------------------------------

class TestIsValidImageUrl:
    """_is_valid_image_url must accept CDN proxy URLs where the image extension
    is embedded inside an encoded path segment, not at the end of the path."""

    def _proc(self):
        return ImageProcessor.__new__(ImageProcessor)

    def test_plain_jpeg_url(self):
        url = "https://example.com/images/photo.jpeg"
        assert self._proc()._is_valid_image_url(url) is True

    def test_plain_png_url(self):
        assert self._proc()._is_valid_image_url("https://example.com/img.png") is True

    def test_non_image_url_rejected(self):
        assert self._proc()._is_valid_image_url("https://example.com/page.html") is False

    def test_substack_cdn_jpeg(self):
        """substackcdn.com/image/fetch/... proxy URL with .jpeg in encoded segment."""
        url = (
            "https://substackcdn.com/image/fetch/"
            "$s_!r41H!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/"
            "https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F"
            "d037a2b3-283d-4ef2-92da-b1b95e22e446_1080x683.jpeg"
        )
        assert self._proc()._is_valid_image_url(url) is True

    def test_substack_cdn_png(self):
        url = (
            "https://substackcdn.com/image/fetch/w_1456/"
            "https%3A%2F%2Fexample.s3.amazonaws.com%2Fimage.png"
        )
        assert self._proc()._is_valid_image_url(url) is True

    def test_generic_proxy_encoded_jpg(self):
        """Any CDN proxy that URL-encodes the original image URL in the path."""
        url = "https://cdn.example.com/proxy/https%3A%2F%2Forigin.com%2Fphoto.jpg"
        assert self._proc()._is_valid_image_url(url) is True

    def test_encoded_non_image_still_rejected(self):
        """Encoded URL that resolves to a non-image is still rejected."""
        url = "https://cdn.example.com/proxy/https%3A%2F%2Forigin.com%2Fpage.html"
        assert self._proc()._is_valid_image_url(url) is False

    def test_nextjs_image_proxy(self):
        """/_next/image?url=...jpg has no extension in path — must still pass."""
        url = (
            "https://www.whyisthisinteresting.com/_next/image"
            "?url=https%3A%2F%2Fimages.example.com%2Fphoto.jpg&w=1456&q=75"
        )
        assert self._proc()._is_valid_image_url(url) is True
