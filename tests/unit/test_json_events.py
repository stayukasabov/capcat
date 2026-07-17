"""Tests for capcat.core.json_events - the --json NDJSON emitter."""
import io
import json

from capcat.core import json_events


def test_emit_does_nothing_when_disabled():
    json_events.disable()
    result = json_events.emit("run_start", command="fetch")
    assert result is None


def test_emit_writes_ndjson_line_when_enabled():
    stream = io.StringIO()
    json_events.enable(stream)
    json_events.emit("run_start", command="fetch", sources=["hn"], count=10)
    json_events.disable()
    decoded = json.loads(stream.getvalue().strip())
    assert decoded == {
        "event": "run_start", "command": "fetch", "sources": ["hn"], "count": 10,
    }


def test_disable_stops_emission():
    stream = io.StringIO()
    json_events.enable(stream)
    json_events.disable()
    json_events.emit("run_complete", total_fetched=1)
    assert stream.getvalue() == ""


def test_is_enabled_reflects_state():
    json_events.disable()
    assert json_events.is_enabled() is False
    stream = io.StringIO()
    json_events.enable(stream)
    assert json_events.is_enabled() is True
    json_events.disable()


def test_emit_raw_writes_bare_object_no_event_key():
    stream = io.StringIO()
    json_events.enable(stream)
    json_events.emit_raw({"sources": [{"id": "hn", "name": "Hacker News"}]})
    json_events.disable()
    decoded = json.loads(stream.getvalue().strip())
    assert decoded == {"sources": [{"id": "hn", "name": "Hacker News"}]}
    assert "event" not in decoded


def test_record_article_fetched_emits_and_counts():
    stream = io.StringIO()
    json_events.enable(stream)
    json_events.record_article_fetched(source="hn", index=1, title="T", url="u", output_path="p")
    json_events.disable()
    decoded = json.loads(stream.getvalue().strip())
    assert decoded == {
        "event": "article_fetched", "source": "hn", "index": 1,
        "title": "T", "url": "u", "output_path": "p",
    }
    assert json_events.pop_article_counts() == (1, 0)


def test_record_article_error_emits_and_counts():
    stream = io.StringIO()
    json_events.enable(stream)
    json_events.record_article_error(source="hn", url="u", error="timeout")
    json_events.disable()
    decoded = json.loads(stream.getvalue().strip())
    assert decoded == {"event": "article_error", "source": "hn", "url": "u", "error": "timeout"}
    assert json_events.pop_article_counts() == (0, 1)


def test_pop_article_counts_resets_to_zero():
    stream = io.StringIO()
    json_events.enable(stream)
    json_events.record_article_fetched(source="hn", index=1, title="T", url="u", output_path="p")
    json_events.pop_article_counts()
    assert json_events.pop_article_counts() == (0, 0)
    json_events.disable()


def test_html_path_defaults_to_none():
    assert json_events.pop_html_path() is None


def test_set_and_pop_html_path_resets_to_none():
    json_events.set_html_path("file:///tmp/index.html")
    assert json_events.pop_html_path() == "file:///tmp/index.html"
    assert json_events.pop_html_path() is None
