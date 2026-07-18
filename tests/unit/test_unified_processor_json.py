"""Tests for json_events wiring in _process_articles_with_new_system."""
import io
import json
from unittest.mock import MagicMock

from capcat.core import json_events
from capcat.core.unified_source_processor import UnifiedSourceProcessor


class _FakeArticle:
    def __init__(self, title, url):
        self.title = title
        self.url = url


def _make_processor():
    processor = UnifiedSourceProcessor.__new__(UnifiedSourceProcessor)
    processor.logger = MagicMock()
    processor.config = MagicMock()
    processor.config.processing.max_workers = 1
    return processor


def test_article_fetched_event_emitted_on_success(tmp_path, monkeypatch):
    article_path = tmp_path / "01_Title"
    article_path.mkdir()

    processor = _make_processor()
    monkeypatch.setattr(
        processor, "_process_single_article_new_system",
        lambda *a, **kw: (True, str(article_path)),
    )
    source = MagicMock()
    source.config.display_name = "Hacker News"
    source.config.name = "hn"
    article = _FakeArticle("Some Title", "https://example.com/a")

    stream = io.StringIO()
    json_events.enable(stream)
    processor._process_articles_with_new_system(
        source, [article], str(tmp_path), download_files=False,
        quiet=True, verbose=False,
    )
    json_events.disable()

    lines = [json.loads(line) for line in stream.getvalue().strip().splitlines() if line]
    fetched_events = [line for line in lines if line["event"] == "article_fetched"]
    assert len(fetched_events) == 1
    assert fetched_events[0]["source"] == "hn"
    assert fetched_events[0]["index"] == 1
    assert fetched_events[0]["title"] == "Some Title"
    assert fetched_events[0]["url"] == "https://example.com/a"


def test_article_error_event_emitted_on_failure(monkeypatch, tmp_path):
    processor = _make_processor()
    monkeypatch.setattr(
        processor, "_process_single_article_new_system",
        lambda *a, **kw: (False, None),
    )
    source = MagicMock()
    source.config.display_name = "Hacker News"
    source.config.name = "hn"
    article = _FakeArticle("Bad Title", "https://example.com/b")

    stream = io.StringIO()
    json_events.enable(stream)
    processor._process_articles_with_new_system(
        source, [article], str(tmp_path), download_files=False,
        quiet=True, verbose=False,
    )
    json_events.disable()

    lines = [json.loads(line) for line in stream.getvalue().strip().splitlines() if line]
    error_events = [line for line in lines if line["event"] == "article_error"]
    assert len(error_events) == 1
    assert error_events[0]["source"] == "hn"
    assert error_events[0]["url"] == "https://example.com/b"


def test_media_downloaded_emitted_when_images_present(monkeypatch, tmp_path):
    article_dir = tmp_path / "article_output"
    article_dir.mkdir()
    (article_dir / "images").mkdir()
    (article_dir / "images" / "photo1.jpg").write_bytes(b"x")
    (article_dir / "images" / "photo2.png").write_bytes(b"x")

    processor = _make_processor()
    monkeypatch.setattr(
        processor, "_process_single_article_new_system",
        lambda *a, **kw: (True, str(article_dir)),
    )
    source = MagicMock()
    source.config.display_name = "Hacker News"
    source.config.name = "hn"
    article = _FakeArticle("Title", "https://example.com/c")

    stream = io.StringIO()
    json_events.enable(stream)
    processor._process_articles_with_new_system(
        source, [article], str(tmp_path), download_files=True,
        quiet=True, verbose=False,
    )
    json_events.disable()

    lines = [json.loads(line) for line in stream.getvalue().strip().splitlines() if line]
    media_events = [line for line in lines if line["event"] == "media_downloaded"]
    assert len(media_events) == 1
    assert media_events[0]["type"] == "image"
    assert media_events[0]["count"] == 2
    assert media_events[0]["article_index"] == 1


def test_no_media_downloaded_event_when_no_media_present(tmp_path, monkeypatch):
    article_dir = tmp_path / "article_output_plain"
    article_dir.mkdir()

    processor = _make_processor()
    monkeypatch.setattr(
        processor, "_process_single_article_new_system",
        lambda *a, **kw: (True, str(article_dir)),
    )
    source = MagicMock()
    source.config.display_name = "Hacker News"
    source.config.name = "hn"
    article = _FakeArticle("Title", "https://example.com/d")

    stream = io.StringIO()
    json_events.enable(stream)
    processor._process_articles_with_new_system(
        source, [article], str(tmp_path), download_files=False,
        quiet=True, verbose=False,
    )
    json_events.disable()

    lines = [json.loads(line) for line in stream.getvalue().strip().splitlines() if line]
    media_events = [line for line in lines if line["event"] == "media_downloaded"]
    assert media_events == []
