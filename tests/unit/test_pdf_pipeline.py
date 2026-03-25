"""
Tests for PDF pipeline: html generator pdf_link inclusion and TUI --media flag.
"""
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_article(tmp_path, content="# Title\n\nBody text."):
    md = tmp_path / "article.md"
    md.write_text(content, encoding="utf-8")
    return str(md)


def _gen():
    from capcat.htmlgen.generator import ArticleHTMLGenerator
    return ArticleHTMLGenerator()


def _render(tmp_path, html_subfolder=True):
    """Render an article and return the HTML string."""
    md_path = _make_article(tmp_path)
    html = _gen().generate_article_html_from_template(
        markdown_path=md_path,
        article_title="Test Article",
        breadcrumb_path=["Test"],
        source_config={},
        html_subfolder=html_subfolder,
    )
    return html


# ---------------------------------------------------------------------------
# pdf_link bar presence
# ---------------------------------------------------------------------------

class TestPdfLinkBar:
    def test_bar_present_when_pdf_exists(self, tmp_path):
        files_dir = tmp_path / "files"
        files_dir.mkdir()
        (files_dir / "paper.pdf").touch()
        html = _render(tmp_path)
        assert '<div class="pdf-download-bar">' in html

    def test_bar_absent_when_no_files_dir(self, tmp_path):
        html = _render(tmp_path)
        assert '<div class="pdf-download-bar">' not in html

    def test_bar_absent_when_files_dir_empty(self, tmp_path):
        (tmp_path / "files").mkdir()
        html = _render(tmp_path)
        assert '<div class="pdf-download-bar">' not in html

    def test_bar_absent_when_files_dir_has_no_pdfs(self, tmp_path):
        files_dir = tmp_path / "files"
        files_dir.mkdir()
        (files_dir / "image.png").touch()
        html = _render(tmp_path)
        assert '<div class="pdf-download-bar">' not in html

    def test_pdf_filename_appears_in_bar(self, tmp_path):
        files_dir = tmp_path / "files"
        files_dir.mkdir()
        (files_dir / "2603.22745.pdf").touch()
        html = _render(tmp_path)
        assert "2603.22745" in html

    def test_multiple_pdfs_all_appear(self, tmp_path):
        files_dir = tmp_path / "files"
        files_dir.mkdir()
        (files_dir / "paper-a.pdf").touch()
        (files_dir / "paper-b.pdf").touch()
        html = _render(tmp_path)
        assert "paper-a" in html
        assert "paper-b" in html


# ---------------------------------------------------------------------------
# pdf_link href prefix depends on html_subfolder
# ---------------------------------------------------------------------------

class TestPdfLinkPath:
    def test_subfolder_true_uses_dotdot_prefix(self, tmp_path):
        files_dir = tmp_path / "files"
        files_dir.mkdir()
        (files_dir / "paper.pdf").touch()
        html = _render(tmp_path, html_subfolder=True)
        assert 'href="../files/paper.pdf"' in html

    def test_subfolder_false_uses_relative_prefix(self, tmp_path):
        files_dir = tmp_path / "files"
        files_dir.mkdir()
        (files_dir / "paper.pdf").touch()
        html = _render(tmp_path, html_subfolder=False)
        assert 'href="files/paper.pdf"' in html


# ---------------------------------------------------------------------------
# TUI: --media flag appended when user answers yes to PDF prompt
# ---------------------------------------------------------------------------

class TestTuiMediaFlag:
    def test_media_flag_appended_when_yes(self):
        dispatched = []

        confirm_mock = MagicMock()
        confirm_mock.return_value.ask.return_value = True

        with patch("capcat.core.interactive.questionary.confirm", confirm_mock), \
             patch("capcat.cli._dispatch", side_effect=lambda a: dispatched.extend(a)), \
             patch("capcat.core.interactive._show_completion_screen"):
            from capcat.core.interactive import _confirm_and_execute
            _confirm_and_execute("fetch", ["hn"], False)

        assert "--media" in dispatched

    def test_media_flag_not_appended_when_no(self):
        dispatched = []

        confirm_mock = MagicMock()
        confirm_mock.return_value.ask.return_value = False

        with patch("capcat.core.interactive.questionary.confirm", confirm_mock), \
             patch("capcat.cli._dispatch", side_effect=lambda a: dispatched.extend(a)), \
             patch("capcat.core.interactive._show_completion_screen"):
            from capcat.core.interactive import _confirm_and_execute
            _confirm_and_execute("fetch", ["hn"], False)

        assert "--media" not in dispatched
