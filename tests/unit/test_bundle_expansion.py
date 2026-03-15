"""Regression tests — bundle all / --all expands to source IDs, not bundle names."""
import pytest
from unittest.mock import patch

MOCK_BUNDLES = {
    "techpro": {"sources": ["hn", "lb"], "default_count": 30},
    "tech":    {"sources": ["ieee"],      "default_count": 30},
    "news":    {"sources": ["bbc"],       "default_count": 25},
    "all":     {"sources": [],            "default_count": 10},
}


def _run_bundle(args):
    """Call _cmd_bundle and capture the sources passed to process_sources."""
    captured = {}

    def fake_process(sources, **kwargs):
        captured["sources"] = sources

    with patch("capcat.core.source_system.bundle_service.get_available_bundles",
               return_value=MOCK_BUNDLES), \
         patch("capcat.commands.fetch.process_sources", side_effect=fake_process), \
         patch("capcat.cli._setup_logging"):
        from capcat.cli import _cmd_bundle
        _cmd_bundle(args)
    return captured.get("sources", [])


def test_bundle_all_name_expands_to_source_ids():
    sources = _run_bundle(["all"])
    assert "techpro" not in sources, "bundle names must not be passed as source IDs"
    assert "tech" not in sources
    assert "hn" in sources
    assert "lb" in sources
    assert "ieee" in sources
    assert "bbc" in sources


def test_bundle_all_flag_expands_to_source_ids():
    sources = _run_bundle(["--all", "ignored"])
    assert "techpro" not in sources
    assert "hn" in sources


def test_bundle_all_deduplicates():
    sources = _run_bundle(["all"])
    assert len(sources) == len(set(sources)), "duplicate source IDs in expansion"


def test_specific_bundle_passes_source_ids():
    sources = _run_bundle(["techpro"])
    assert sources == ["hn", "lb"]


def test_unknown_bundle_exits_nonzero():
    with pytest.raises(SystemExit) as exc:
        _run_bundle(["nonexistent_bundle"])
    assert exc.value.code == 1
