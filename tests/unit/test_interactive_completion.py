"""Tests for TUI completion screen output path display."""

import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestFindLatestArticleMd:
    """_find_latest_article_md returns the most recent .md file URI."""

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
        # Ensure different mtime
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

    def test_shows_md_path_when_html_off(self, tmp_path, capsys):
        capcats = tmp_path / "Capcats"
        article_dir = capcats / "cc_30-06-2026-Test"
        article_dir.mkdir(parents=True)
        md_file = article_dir / "Test.md"
        md_file.write_text("# Test")
        news = tmp_path / "News"
        news.mkdir()

        with patch("capcat.core.config.get_capcats_dir", return_value=capcats), \
             patch("capcat.core.config.get_news_dir", return_value=news), \
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

        with patch("capcat.core.config.get_capcats_dir", return_value=capcats), \
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
