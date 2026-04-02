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
        data = {"ui": {"use_emojis": False}}
        cfg = FetchNewsConfig.from_dict(data)
        assert cfg.ui.use_emojis is False


class TestFilterFields:
    def test_keeps_known_fields(self):
        result = _filter_fields(PdfConfig, {"max_pdf_size_bytes": 1, "max_pdf_per_article": 2})
        assert result == {"max_pdf_size_bytes": 1, "max_pdf_per_article": 2}

    def test_drops_unknown_fields(self):
        result = _filter_fields(PdfConfig, {"max_pdf_size_bytes": 1, "bogus": "x"})
        assert "bogus" not in result
        assert result["max_pdf_size_bytes"] == 1
