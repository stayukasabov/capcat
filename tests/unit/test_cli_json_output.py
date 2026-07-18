"""Tests for the --json flag wiring in capcat.cli._dispatch."""
import io
import sys

import pytest

from capcat import cli


def test_json_flag_is_stripped_before_command_routing(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    captured_args = {}

    def fake_cmd_list(args, json_output=False):
        captured_args["args"] = args
        captured_args["json_output"] = json_output

    monkeypatch.setattr(cli, "_cmd_list", fake_cmd_list)
    monkeypatch.setattr(cli, "_auto_init", lambda command: None)
    cli._dispatch(["list", "sources", "--json"])
    assert captured_args["args"] == ["sources"]
    assert captured_args["json_output"] is True


def test_json_mode_redirects_human_print_to_stderr(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "_auto_init", lambda command: None)

    def fake_cmd_list(args, json_output=False):
        print("human readable line")

    monkeypatch.setattr(cli, "_cmd_list", fake_cmd_list)
    cli._dispatch(["list", "sources", "--json"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "human readable line" in captured.err


def test_without_json_flag_print_still_goes_to_stdout(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "_auto_init", lambda command: None)

    def fake_cmd_list(args, json_output=False):
        print("human readable line")
        assert json_output is False

    monkeypatch.setattr(cli, "_cmd_list", fake_cmd_list)
    cli._dispatch(["list", "sources"])
    captured = capsys.readouterr()
    assert "human readable line" in captured.out
    assert captured.err == ""


def test_stdout_is_restored_after_json_command_even_on_exception(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "_auto_init", lambda command: None)
    real_stdout = sys.stdout

    def fake_cmd_list(args, json_output=False):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "_cmd_list", fake_cmd_list)
    with pytest.raises(RuntimeError):
        cli._dispatch(["list", "sources", "--json"])
    assert sys.stdout is real_stdout


def test_unexpected_exception_emits_fatal_error_event(monkeypatch, tmp_path):
    import io
    import json as _json
    from capcat.core import json_events

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "_auto_init", lambda command: None)

    def fake_cmd_list(args, json_output=False):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "_cmd_list", fake_cmd_list)
    stream = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stream)

    with pytest.raises(RuntimeError):
        cli._dispatch(["list", "sources", "--json"])

    lines = [_json.loads(line) for line in stream.getvalue().strip().splitlines() if line]
    assert lines == [{"event": "error", "message": "boom"}]
    json_events.disable()


def test_list_sources_json_shape(monkeypatch, tmp_path):
    from capcat.core import json_events

    class FakeConfig:
        def __init__(self, display_name, category, hidden):
            self.display_name = display_name
            self.category = category
            self.hidden = hidden

    class FakeRegistry:
        def __init__(self, project_root=None):
            pass

        def discover_sources(self):
            pass

        def get_available_sources(self):
            return ["hn", "twitter"]

        def get_source_config(self, sid):
            if sid == "hn":
                return FakeConfig("Hacker News", "tech", False)
            return FakeConfig("Twitter", "social", True)

    monkeypatch.setattr(
        "capcat.core.source_system.source_registry.SourceRegistry", FakeRegistry
    )
    monkeypatch.setattr(
        "capcat.core.config.find_project_root", lambda: tmp_path
    )

    stream = io.StringIO()
    json_events.enable(stream)
    cli._cmd_list(["sources"], json_output=True)
    json_events.disable()

    import json
    decoded = json.loads(stream.getvalue().strip())
    assert decoded == {
        "sources": [
            {"id": "hn", "name": "Hacker News", "category": "tech", "hidden": False},
            {"id": "twitter", "name": "Twitter", "category": "social", "hidden": True},
        ]
    }
