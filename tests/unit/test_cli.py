"""Test CLI routing and command dispatch."""
from __future__ import annotations
import sys
from unittest.mock import patch, MagicMock
import pytest


def test_catch_routes_to_tui():
    """'capcat catch' must invoke tui.run()."""
    with patch("capcat.tui.run") as mock_run:
        with patch.object(sys, "argv", ["capcat", "catch"]):
            from capcat import cli
            import importlib
            importlib.reload(cli)
            cli.main()
    mock_run.assert_called_once()


def test_init_routes_to_init_command(tmp_path):
    """'capcat init' must invoke init_project on cwd."""
    with patch("capcat.commands.init.init_project") as mock_init:
        with patch.object(sys, "argv", ["capcat", "init"]):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                from capcat.cli import main
                main()
    mock_init.assert_called_once()


def test_unknown_command_exits_nonzero():
    """Unknown command must exit with non-zero code."""
    with patch.object(sys, "argv", ["capcat", "unknowncmd123"]):
        from capcat.cli import main
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1


def test_help_flag_exits_cleanly():
    """'capcat --help' must print help and exit cleanly."""
    with patch.object(sys, "argv", ["capcat", "--help"]):
        from capcat.cli import main
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 0 or exc.code is None


def test_no_args_prints_help(capsys) -> None:
    """'capcat' with no args prints help without crashing."""
    with patch.object(sys, "argv", ["capcat"]):
        from capcat.cli import main
        main()
    out = capsys.readouterr().out
    assert "capcat" in out.lower()


def test_L_flag_missing_filename_exits() -> None:
    """-L without filename exits with code 1."""
    with patch.object(sys, "argv", ["capcat", "-L"]):
        from capcat.cli import main
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1


def test_single_no_url_prints_usage(capsys) -> None:
    """'capcat single' with no URL prints usage."""
    with patch.object(sys, "argv", ["capcat", "single"]):
        from capcat.cli import main
        main()
    out = capsys.readouterr().out
    assert "Usage" in out


def test_single_help_flag(capsys) -> None:
    """'capcat single --help' prints usage without crashing."""
    with patch.object(sys, "argv", ["capcat", "single", "--help"]):
        from capcat.cli import main
        main()
    out = capsys.readouterr().out
    assert "Usage" in out


def test_single_calls_run_legacy() -> None:
    """'capcat single <url>' delegates to _run_legacy."""
    with patch("capcat.cli._run_legacy") as mock_legacy:
        with patch.object(sys, "argv", ["capcat", "single", "https://example.com"]):
            from capcat.cli import main
            main()
    mock_legacy.assert_called_once()
    call_args = mock_legacy.call_args[0][0]
    assert call_args["action"] == "single"
    assert call_args["url"] == "https://example.com"


def test_fetch_no_source_prints_usage(capsys) -> None:
    """'capcat fetch' with no source prints usage."""
    with patch.object(sys, "argv", ["capcat", "fetch"]):
        from capcat.cli import main
        main()
    out = capsys.readouterr().out
    assert "Usage" in out


def test_fetch_calls_run_legacy() -> None:
    """'capcat fetch hn --count 5' delegates to _run_legacy."""
    with patch("capcat.cli._run_legacy") as mock_legacy:
        with patch.object(sys, "argv", ["capcat", "fetch", "hn", "--count", "5"]):
            from capcat.cli import main
            main()
    mock_legacy.assert_called_once()
    call_args = mock_legacy.call_args[0][0]
    assert call_args["action"] == "fetch"
    assert call_args["count"] == 5


def test_bundle_help_flag() -> None:
    """'capcat bundle --help' prints usage without crashing."""
    with patch.object(sys, "argv", ["capcat", "bundle", "--help"]):
        from capcat.cli import main
        main()


def test_bundle_calls_run_legacy() -> None:
    """'capcat bundle tech' delegates to _run_legacy."""
    mock_cli = MagicMock()
    mock_cli.get_available_bundles.return_value = {"tech": {"sources": ["hn", "lb"]}}
    with patch("capcat.cli._run_legacy") as mock_legacy:
        with patch.dict(sys.modules, {"cli": mock_cli}):
            with patch.object(sys, "argv", ["capcat", "bundle", "tech"]):
                from capcat.cli import main
                main()
    mock_legacy.assert_called_once()
    call_args = mock_legacy.call_args[0][0]
    assert call_args["action"] == "bundle"


def test_list_calls_legacy_list(capsys) -> None:
    """'capcat list sources' calls legacy list_sources_and_bundles."""
    with patch("capcat.cli._run_legacy") as _:
        # list command uses a BRIDGE import, mock the bridge module
        mock_cli = MagicMock()
        with patch.dict(sys.modules, {"cli": mock_cli}):
            with patch.object(sys, "argv", ["capcat", "list", "sources"]):
                from capcat.cli import main
                main()
    mock_cli.list_sources_and_bundles.assert_called_once_with("sources")


def test_add_source_missing_url_exits() -> None:
    """'capcat add-source' without --url exits with code 1."""
    with patch.object(sys, "argv", ["capcat", "add-source", "--url"]):
        from capcat.cli import main
        with pytest.raises(SystemExit):
            main()


def test_add_source_calls_legacy(capsys) -> None:
    """'capcat add-source --url URL' calls legacy add_source."""
    mock_cli = MagicMock()
    with patch.dict(sys.modules, {"cli": mock_cli}):
        with patch.object(sys, "argv", ["capcat", "add-source", "--url", "https://feed.example.com"]):
            from capcat.cli import main
            main()
    mock_cli.add_source.assert_called_once_with("https://feed.example.com")


def test_remove_source_calls_legacy(capsys) -> None:
    """'capcat remove-source' calls legacy remove_source."""
    mock_cli = MagicMock()
    with patch.dict(sys.modules, {"cli": mock_cli}):
        with patch.object(sys, "argv", ["capcat", "remove-source"]):
            from capcat.cli import main
            main()
    mock_cli.remove_source.assert_called_once()


def test_generate_config_calls_legacy(capsys) -> None:
    """'capcat generate-config' calls legacy generate_config_command."""
    mock_cli = MagicMock()
    with patch.dict(sys.modules, {"cli": mock_cli}):
        with patch.object(sys, "argv", ["capcat", "generate-config"]):
            from capcat.cli import main
            main()
    mock_cli.generate_config_command.assert_called_once()


def test_run_legacy_import_error_exits() -> None:
    """_run_legacy exits with code 1 when capcat_legacy is not importable."""
    with patch.dict(sys.modules, {"capcat_legacy": None}):
        from capcat.cli import _run_legacy
        with pytest.raises(SystemExit) as exc_info:
            _run_legacy({"action": "test"})
    assert exc_info.value.code == 1


def test_init_reinit_flag(tmp_path) -> None:
    """'capcat init --reinit' passes reinit=True to init_project."""
    with patch("capcat.commands.init.init_project") as mock_init:
        with patch.object(sys, "argv", ["capcat", "init", "--reinit"]):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                from capcat.cli import main
                main()
    mock_init.assert_called_once_with(tmp_path, reinit=True)


def test_init_already_initialized_exits(tmp_path) -> None:
    """'capcat init' exits with code 1 when AlreadyInitializedError raised."""
    from capcat.commands.init import AlreadyInitializedError
    with patch("capcat.commands.init.init_project", side_effect=AlreadyInitializedError("already")):
        with patch.object(sys, "argv", ["capcat", "init"]):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                from capcat.cli import main
                with pytest.raises(SystemExit) as exc_info:
                    main()
    assert exc_info.value.code == 1
