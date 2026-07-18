"""Tests for json_events wiring in capcat.commands.fetch.process_sources."""
import argparse
import io
import json
import logging

from capcat.commands.fetch import process_sources
from capcat.core import json_events


def _fake_args(**overrides):
    defaults = dict(count=None, quiet=True, verbose=False, media=False, pdfs=False, no_pdfs=False)
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_process_sources_emits_run_start_and_run_complete(monkeypatch):
    monkeypatch.setattr(
        "capcat.commands.fetch.process_source_articles", lambda **kwargs: None
    )
    stream = io.StringIO()
    json_events.enable(stream)
    process_sources(
        sources=["hn"], args=_fake_args(), config=None,
        logger=logging.getLogger("test"), command="fetch",
    )
    json_events.disable()

    lines = [json.loads(line) for line in stream.getvalue().strip().splitlines()]
    events = [line["event"] for line in lines]
    assert events == ["run_start", "source_start", "source_complete", "run_complete"]
    assert lines[0]["command"] == "fetch"
    assert lines[0]["sources"] == ["hn"]
    assert lines[-1]["total_fetched"] == 0
    assert lines[-1]["total_errors"] == 0
    assert lines[-1]["html_path"] is None


def test_process_sources_source_complete_reflects_article_counts(monkeypatch):
    def fake_process(**kwargs):
        json_events.record_article_fetched(
            source="hn", index=1, title="T1", url="u1", output_path="p1"
        )
        json_events.record_article_error(source="hn", url="u2", error="timeout")

    monkeypatch.setattr("capcat.commands.fetch.process_source_articles", fake_process)
    stream = io.StringIO()
    json_events.enable(stream)
    process_sources(
        sources=["hn"], args=_fake_args(), config=None,
        logger=logging.getLogger("test"), command="fetch",
    )
    json_events.disable()

    lines = [json.loads(line) for line in stream.getvalue().strip().splitlines()]
    source_complete = next(line for line in lines if line["event"] == "source_complete")
    assert source_complete["fetched"] == 1
    assert source_complete["errors"] == 1
    run_complete = next(line for line in lines if line["event"] == "run_complete")
    assert run_complete["total_fetched"] == 1
    assert run_complete["total_errors"] == 1


def test_process_sources_html_path_flows_to_run_complete(monkeypatch):
    def fake_process(**kwargs):
        json_events.set_html_path("file:///tmp/News/index.html")

    monkeypatch.setattr("capcat.commands.fetch.process_source_articles", fake_process)
    stream = io.StringIO()
    json_events.enable(stream)
    process_sources(
        sources=["hn"], args=_fake_args(), config=None,
        logger=logging.getLogger("test"), command="fetch", generate_html=True,
    )
    json_events.disable()

    lines = [json.loads(line) for line in stream.getvalue().strip().splitlines()]
    run_complete = next(line for line in lines if line["event"] == "run_complete")
    assert run_complete["html_path"] == "file:///tmp/News/index.html"


def test_process_sources_emits_nothing_when_json_disabled(monkeypatch):
    monkeypatch.setattr(
        "capcat.commands.fetch.process_source_articles", lambda **kwargs: None
    )
    json_events.disable()
    result = process_sources(
        sources=["hn"], args=_fake_args(), config=None,
        logger=logging.getLogger("test"), command="fetch",
    )
    assert result == {"successful": ["hn"], "failed": [], "total": 1}
