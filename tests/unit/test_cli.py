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


def test_single_calls_scrape_single_article() -> None:
    """'capcat single <url>' delegates to scrape_single_article."""
    with patch("capcat.commands.single.scrape_single_article") as mock_scrape:
        with patch("capcat.cli._setup_logging"):
            with patch.object(sys, "argv", ["capcat", "single", "https://example.com"]):
                from capcat.cli import main
                main()
    mock_scrape.assert_called_once()
    call_kwargs = mock_scrape.call_args[1]
    assert call_kwargs["url"] == "https://example.com"


def test_fetch_no_source_prints_usage(capsys) -> None:
    """'capcat fetch' with no source prints usage."""
    with patch.object(sys, "argv", ["capcat", "fetch"]):
        from capcat.cli import main
        main()
    out = capsys.readouterr().out
    assert "Usage" in out


def test_fetch_calls_process_sources() -> None:
    """'capcat fetch hn --count 5' delegates to process_sources."""
    with patch("capcat.commands.fetch.process_sources") as mock_proc:
        with patch("capcat.cli._setup_logging"):
            with patch.object(sys, "argv", ["capcat", "fetch", "hn", "--count", "5"]):
                from capcat.cli import main
                main()
    mock_proc.assert_called_once()
    call_kwargs = mock_proc.call_args[1]
    assert "hn" in call_kwargs["sources"]
    assert call_kwargs["args"].count == 5


def test_bundle_help_flag() -> None:
    """'capcat bundle --help' prints usage without crashing."""
    with patch.object(sys, "argv", ["capcat", "bundle", "--help"]):
        from capcat.cli import main
        main()


def test_bundle_calls_process_sources() -> None:
    """'capcat bundle tech' delegates to process_sources."""
    mock_bundles = {"tech": {"sources": ["hn", "lb"], "description": ""}}
    with patch("capcat.core.source_system.bundle_service.get_available_bundles",
               return_value=mock_bundles):
        with patch("capcat.commands.fetch.process_sources") as mock_proc:
            with patch("capcat.cli._setup_logging"):
                with patch.object(sys, "argv", ["capcat", "bundle", "tech"]):
                    from capcat.cli import main
                    main()
    mock_proc.assert_called_once()
    call_kwargs = mock_proc.call_args[1]
    assert set(call_kwargs["sources"]) == {"hn", "lb"}


def test_list_sources_prints_sources(capsys) -> None:
    """'capcat list sources' prints available sources from the registry."""
    with patch.object(sys, "argv", ["capcat", "list", "sources"]):
        from capcat.cli import main
        main()
    out = capsys.readouterr().out
    assert "Available sources" in out


def test_add_source_missing_url_exits() -> None:
    """'capcat add-source' without --url exits with code 1."""
    with patch.object(sys, "argv", ["capcat", "add-source", "--url"]):
        from capcat.cli import main
        with pytest.raises(SystemExit):
            main()


def test_add_source_calls_add_source_command(capsys) -> None:
    """'capcat add-source --url URL' calls capcat.commands.add_source.add_source."""
    with patch("capcat.commands.add_source.add_source") as mock_add:
        with patch.object(sys, "argv", ["capcat", "add-source", "--url", "https://feed.example.com"]):
            from capcat.cli import main
            main()
    mock_add.assert_called_once_with("https://feed.example.com")


def test_remove_source_calls_remove_source_command(capsys) -> None:
    """'capcat remove-source' calls capcat.commands.remove_source.remove_source."""
    with patch("capcat.commands.remove_source.remove_source") as mock_rm:
        with patch.object(sys, "argv", ["capcat", "remove-source"]):
            from capcat.cli import main
            main()
    mock_rm.assert_called_once()


def test_generate_config_calls_generate_config_command(capsys) -> None:
    """'capcat generate-config' calls capcat.commands.generate_config.generate_config."""
    with patch("capcat.commands.generate_config.generate_config") as mock_gen:
        with patch.object(sys, "argv", ["capcat", "generate-config"]):
            from capcat.cli import main
            main()
    mock_gen.assert_called_once()


def test_setup_logging_called_for_fetch() -> None:
    """_setup_logging is invoked when 'capcat fetch' runs."""
    with patch("capcat.cli._setup_logging") as mock_log:
        with patch("capcat.commands.fetch.process_sources"):
            with patch.object(sys, "argv", ["capcat", "fetch", "hn"]):
                from capcat.cli import main
                main()
    mock_log.assert_called_once()


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
