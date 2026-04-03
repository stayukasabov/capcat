"""Regression test — themes update prompt must not block non-interactive runs."""
from unittest.mock import patch


def _run_check(tmp_path):
    """Call check_theme_upgrade with a project_root that has a Config/themes/ dir."""
    from capcat.core.config import check_theme_upgrade
    themes_dir = tmp_path / "Config" / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    check_theme_upgrade(project_root=tmp_path)


class TestThemesPromptNonInteractive:
    def test_no_prompt_when_stdin_not_tty(self, tmp_path):
        """check_theme_upgrade must not call input() when stdin is not a tty."""
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input") as mock_input,
            patch("capcat.core.tui_context.is_tui_active", return_value=False),
        ):
            mock_stdin.isatty.return_value = False
            _run_check(tmp_path)

        mock_input.assert_not_called()

    def test_no_block_when_stdin_not_tty(self, tmp_path):
        """check_theme_upgrade must return immediately when stdin is non-interactive."""
        import threading
        result = []

        def run():
            with (
                patch("sys.stdin") as mock_stdin,
                patch("capcat.core.tui_context.is_tui_active", return_value=False),
            ):
                mock_stdin.isatty.return_value = False
                _run_check(tmp_path)
                result.append("done")

        t = threading.Thread(target=run)
        t.start()
        t.join(timeout=2)
        assert "done" in result, "check_theme_upgrade blocked for >2s in non-interactive mode"

    def test_prompt_fires_when_stdin_is_tty(self, tmp_path):
        """check_theme_upgrade must still prompt when stdin is a real tty."""
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input", return_value="n") as mock_input,
            patch("capcat.core.tui_context.is_tui_active", return_value=False),
        ):
            mock_stdin.isatty.return_value = True
            _run_check(tmp_path)

        mock_input.assert_called_once()
