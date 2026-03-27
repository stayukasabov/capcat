"""Regression tests for TUI post-completion screen behavior."""
import sys
import pytest
from unittest.mock import patch, MagicMock


def _run_completion(generate_html, success, user_choice="menu"):
    """Call _confirm_and_execute and capture behavior."""
    with patch("capcat.cli._dispatch"), \
         patch("capcat.core.interactive._show_completion_screen") as mock_screen, \
         patch("capcat.core.interactive._setup_logging", create=True):
        from capcat.core.interactive import _confirm_and_execute
        _confirm_and_execute("bundle", "techpro", generate_html)
    return mock_screen


def _mock_pdf_confirm():
    """Return a patch that answers 'no' to the PDF download prompt."""
    m = MagicMock()
    m.return_value.ask.return_value = False
    return patch("capcat.core.interactive.questionary.confirm", m)


def test_completion_screen_called_on_success():
    """_show_completion_screen must be called after successful dispatch."""
    with patch("capcat.cli._dispatch"), \
         patch("capcat.core.interactive._show_completion_screen") as mock_screen, \
         _mock_pdf_confirm():
        from capcat.core.interactive import _confirm_and_execute
        _confirm_and_execute("bundle", "techpro", False)
    args, kwargs = mock_screen.call_args
    assert args == (False, True)


def test_completion_screen_called_on_nonzero_exit():
    """_show_completion_screen must be called even when dispatch exits non-zero."""
    with patch("capcat.cli._dispatch", side_effect=SystemExit(1)), \
         patch("capcat.core.interactive._show_completion_screen") as mock_screen, \
         _mock_pdf_confirm():
        from capcat.core.interactive import _confirm_and_execute
        _confirm_and_execute("bundle", "techpro", False)
    args, kwargs = mock_screen.call_args
    assert args == (False, False)


def test_completion_screen_called_on_exception():
    """_show_completion_screen must be called when dispatch raises unexpectedly."""
    with patch("capcat.cli._dispatch", side_effect=RuntimeError("network down")), \
         patch("capcat.core.interactive._show_completion_screen") as mock_screen, \
         _mock_pdf_confirm():
        from capcat.core.interactive import _confirm_and_execute
        _confirm_and_execute("fetch", ["hn"], True)
    args, kwargs = mock_screen.call_args
    assert args == (True, False)


def test_completion_screen_exit_choice_calls_sys_exit():
    """Choosing 'exit' in the completion screen must call sys.exit(0)."""
    with patch("questionary.select") as mock_q, \
         patch("capcat.core.interactive._find_latest_index_html", return_value=None):
        mock_q.return_value.ask.return_value = "exit"
        from capcat.core.interactive import _show_completion_screen
        with pytest.raises(SystemExit) as exc:
            _show_completion_screen(False, True)
        assert exc.value.code == 0


def test_completion_screen_menu_choice_returns():
    """Choosing 'Back to Main Menu' must return normally (no sys.exit)."""
    with patch("questionary.select") as mock_q, \
         patch("capcat.core.interactive._find_latest_index_html", return_value=None):
        mock_q.return_value.ask.return_value = "menu"
        from capcat.core.interactive import _show_completion_screen
        _show_completion_screen(False, True)  # must not raise


def test_find_latest_index_html_returns_none_when_missing(tmp_path):
    """_find_latest_index_html returns None when no HTML files exist."""
    capcats_tmp = tmp_path / "Capcats"
    capcats_tmp.mkdir()
    with patch("capcat.core.config.get_news_dir", return_value=tmp_path), \
         patch("capcat.core.config.get_capcats_dir", return_value=capcats_tmp):
        from capcat.core.interactive import _find_latest_index_html
        assert _find_latest_index_html() is None


def test_find_latest_index_html_finds_most_recent(tmp_path):
    """_find_latest_index_html returns path to index.html in most recent News_* dir."""
    import time
    capcats_tmp = tmp_path / "Capcats"
    capcats_tmp.mkdir()
    old = tmp_path / "News_01-01-2026"
    old.mkdir()
    (old / "index.html").write_text("<html/>")
    time.sleep(0.01)
    new = tmp_path / "News_15-03-2026"
    new.mkdir()
    (new / "index.html").write_text("<html/>")

    with patch("capcat.core.config.get_news_dir", return_value=tmp_path), \
         patch("capcat.core.config.get_capcats_dir", return_value=capcats_tmp):
        from importlib import reload
        import capcat.core.interactive as m
        result = m._find_latest_index_html()

    assert result is not None
    assert "News_15-03-2026" in result


def test_find_latest_index_html_finds_single_article(tmp_path):
    """_find_latest_index_html finds article.html from a single article capture."""
    news_tmp = tmp_path / "News"
    news_tmp.mkdir()
    capcats_tmp = tmp_path / "Capcats"
    article_html = capcats_tmp / "InfoQ_24-03-2026" / "My Article" / "html" / "article.html"
    article_html.parent.mkdir(parents=True)
    article_html.write_text("<html/>")

    with patch("capcat.core.config.get_news_dir", return_value=news_tmp), \
         patch("capcat.core.config.get_capcats_dir", return_value=capcats_tmp):
        import capcat.core.interactive as m
        result = m._find_latest_index_html()

    assert result is not None
    assert "article.html" in result
    assert "InfoQ_24-03-2026" in result


def test_find_latest_index_html_prefers_newer(tmp_path):
    """_find_latest_index_html returns the most recently modified file overall."""
    import time
    news_tmp = tmp_path / "News"
    news_tmp.mkdir()
    capcats_tmp = tmp_path / "Capcats"

    # Create a batch index first
    date_dir = news_tmp / "News_01-03-2026"
    date_dir.mkdir()
    (date_dir / "index.html").write_text("<html/>")
    time.sleep(0.01)

    # Create a newer single article
    article_html = capcats_tmp / "InfoQ_24-03-2026" / "My Article" / "html" / "article.html"
    article_html.parent.mkdir(parents=True)
    article_html.write_text("<html/>")

    with patch("capcat.core.config.get_news_dir", return_value=news_tmp), \
         patch("capcat.core.config.get_capcats_dir", return_value=capcats_tmp):
        import capcat.core.interactive as m
        result = m._find_latest_index_html()

    assert result is not None
    assert "article.html" in result
