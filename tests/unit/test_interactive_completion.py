"""Tests for TUI completion screen output path display."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestFindOutputMd:
    """_find_output_md uses tui_context path first, falls back to globbing."""

    def test_uses_stored_output_dir(self, tmp_path):
        article_dir = tmp_path / "cc_30-06-2026-Test"
        article_dir.mkdir()
        md_file = article_dir / "Test.md"
        md_file.write_text("# Test")

        with patch("capcat.core.tui_context.get_last_output_dir", return_value=str(article_dir)):
            from capcat.core.interactive import _find_output_md
            result = _find_output_md()
        assert result is not None
        assert result.startswith("file://")
        assert "Test.md" in result

    def test_falls_back_to_globbing_when_no_stored_dir(self, tmp_path):
        capcats = tmp_path / "Capcats"
        article_dir = capcats / "cc_30-06-2026-Test"
        article_dir.mkdir(parents=True)
        md_file = article_dir / "Test.md"
        md_file.write_text("# Test")
        news = tmp_path / "News"
        news.mkdir()

        with patch("capcat.core.tui_context.get_last_output_dir", return_value=None), \
             patch("capcat.core.config.get_capcats_dir", return_value=capcats), \
             patch("capcat.core.config.get_news_dir", return_value=news):
            from capcat.core.interactive import _find_output_md
            result = _find_output_md()
        assert result is not None
        assert "Test.md" in result

    def test_returns_none_when_nothing_available(self, tmp_path):
        capcats = tmp_path / "Capcats"
        capcats.mkdir()
        news = tmp_path / "News"
        news.mkdir()

        with patch("capcat.core.tui_context.get_last_output_dir", return_value=None), \
             patch("capcat.core.config.get_capcats_dir", return_value=capcats), \
             patch("capcat.core.config.get_news_dir", return_value=news):
            from capcat.core.interactive import _find_output_md
            result = _find_output_md()
        assert result is None

    def test_percent_encodes_spaces_in_path(self, tmp_path):
        article_dir = tmp_path / "cc_30-06-2026-My Article"
        article_dir.mkdir()
        md_file = article_dir / "My Article.md"
        md_file.write_text("# Spaces")

        with patch("capcat.core.tui_context.get_last_output_dir", return_value=str(article_dir)):
            from capcat.core.interactive import _find_output_md
            result = _find_output_md()
        assert result is not None
        assert "%20" in result or "My%20Article" in result


class TestFindLatestArticleMd:
    """_find_latest_article_md returns the most recent .md file URI (fallback)."""

    def test_returns_none_when_no_md_files(self, tmp_path):
        capcats = tmp_path / "Capcats"
        capcats.mkdir()
        news = tmp_path / "News"
        news.mkdir()

        with patch("capcat.core.config.get_capcats_dir", return_value=capcats), \
             patch("capcat.core.config.get_news_dir", return_value=news):
            from capcat.core.interactive import _find_latest_article_md
            result = _find_latest_article_md()
        assert result is None

    def test_returns_single_article_md(self, tmp_path):
        capcats = tmp_path / "Capcats"
        article_dir = capcats / "cc_30-06-2026-Test-Article"
        article_dir.mkdir(parents=True)
        md_file = article_dir / "Test-Article.md"
        md_file.write_text("# Test")
        news = tmp_path / "News"
        news.mkdir()

        with patch("capcat.core.config.get_capcats_dir", return_value=capcats), \
             patch("capcat.core.config.get_news_dir", return_value=news):
            from capcat.core.interactive import _find_latest_article_md
            result = _find_latest_article_md()
        assert result is not None
        assert result.startswith("file://")
        assert "Test-Article.md" in result

    def test_returns_most_recent_md(self, tmp_path):
        capcats = tmp_path / "Capcats"
        old_dir = capcats / "cc_01-01-2026-Old"
        old_dir.mkdir(parents=True)
        old_md = old_dir / "Old.md"
        old_md.write_text("# Old")

        new_dir = capcats / "cc_30-06-2026-New"
        new_dir.mkdir(parents=True)
        new_md = new_dir / "New.md"
        new_md.write_text("# New")
        os.utime(old_md, (0, 0))

        news = tmp_path / "News"
        news.mkdir()

        with patch("capcat.core.config.get_capcats_dir", return_value=capcats), \
             patch("capcat.core.config.get_news_dir", return_value=news):
            from capcat.core.interactive import _find_latest_article_md
            result = _find_latest_article_md()
        assert "New.md" in result


class TestCompletionScreenShowsPath:
    """Completion screen shows markdown path when HTML is off."""

    def test_shows_md_path_via_stored_dir(self, tmp_path, capsys):
        article_dir = tmp_path / "cc_30-06-2026-Test"
        article_dir.mkdir()
        md_file = article_dir / "Test.md"
        md_file.write_text("# Test")

        with patch("capcat.core.tui_context.get_last_output_dir", return_value=str(article_dir)), \
             patch("capcat.core.interactive.print_logo"), \
             patch("capcat.core.interactive.suppress_logging"), \
             patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = "exit"
            from capcat.core.interactive import _show_completion_screen
            with pytest.raises(SystemExit):
                _show_completion_screen(generate_html=False, success=True)

        output = capsys.readouterr().out
        assert "Output:" in output
        assert "Test.md" in output

    def test_no_path_line_when_no_md_exists(self, tmp_path, capsys):
        capcats = tmp_path / "Capcats"
        capcats.mkdir()
        news = tmp_path / "News"
        news.mkdir()

        with patch("capcat.core.tui_context.get_last_output_dir", return_value=None), \
             patch("capcat.core.config.get_capcats_dir", return_value=capcats), \
             patch("capcat.core.config.get_news_dir", return_value=news), \
             patch("capcat.core.interactive.print_logo"), \
             patch("capcat.core.interactive.suppress_logging"), \
             patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = "exit"
            from capcat.core.interactive import _show_completion_screen
            with pytest.raises(SystemExit):
                _show_completion_screen(generate_html=False, success=True)

        output = capsys.readouterr().out
        assert "Output:" not in output


class TestTuiContextOutputDir:
    """tui_context stores and clears last output dir."""

    def test_set_and_get(self):
        from capcat.core.tui_context import set_last_output_dir, get_last_output_dir
        set_last_output_dir("/some/path")
        assert get_last_output_dir() == "/some/path"
        set_last_output_dir(None)

    def test_reset_clears_output_dir(self):
        from capcat.core.tui_context import set_last_output_dir, get_last_output_dir, reset_fetch_results
        set_last_output_dir("/some/path")
        reset_fetch_results()
        assert get_last_output_dir() is None
