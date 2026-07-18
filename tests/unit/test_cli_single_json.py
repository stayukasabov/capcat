"""Tests for hidden --json event emission around capcat single."""
import io
import json

from capcat import cli
from capcat.core import json_events


def test_single_success_emits_full_event_sequence(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "capcat.commands.single.scrape_single_article",
        lambda **kwargs: (True, str(tmp_path / "18-07-2026-some-article")),
    )
    monkeypatch.setattr(cli, "_setup_logging", lambda **kwargs: None)

    stream = io.StringIO()
    json_events.enable(stream)
    cli._cmd_single(["https://example.com/a"], json_output=True)
    json_events.disable()

    lines = [json.loads(line) for line in stream.getvalue().strip().splitlines() if line]
    events = [line["event"] for line in lines]
    assert events == ["run_start", "source_start", "article_fetched", "source_complete", "run_complete"]
    assert lines[0]["command"] == "single"
    fetched = next(line for line in lines if line["event"] == "article_fetched")
    assert fetched["url"] == "https://example.com/a"
    run_complete = next(line for line in lines if line["event"] == "run_complete")
    assert run_complete["total_fetched"] == 1
    assert run_complete["total_errors"] == 0


def test_single_failure_emits_article_error(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "capcat.commands.single.scrape_single_article",
        lambda **kwargs: (False, str(tmp_path)),
    )
    monkeypatch.setattr(cli, "_setup_logging", lambda **kwargs: None)

    stream = io.StringIO()
    json_events.enable(stream)
    cli._cmd_single(["https://example.com/b"], json_output=True)
    json_events.disable()

    lines = [json.loads(line) for line in stream.getvalue().strip().splitlines() if line]
    events = [line["event"] for line in lines]
    assert "article_error" in events
    run_complete = next(line for line in lines if line["event"] == "run_complete")
    assert run_complete["total_errors"] == 1


def test_single_without_json_flag_emits_nothing(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "capcat.commands.single.scrape_single_article",
        lambda **kwargs: (True, str(tmp_path)),
    )
    monkeypatch.setattr(cli, "_setup_logging", lambda **kwargs: None)
    json_events.disable()
    cli._cmd_single(["https://example.com/c"], json_output=False)
    assert json_events.is_enabled() is False
