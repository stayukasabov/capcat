"""Tests for userspace bundle routing in get_available_bundles."""
from __future__ import annotations

from pathlib import Path
import pytest

from capcat.core.source_system.bundle_service import get_available_bundles


def test_get_available_bundles_reads_userspace_when_file_exists(tmp_path):
    bundles_dir = tmp_path / "Config" / "sources" / "active" / "bundles"
    bundles_dir.mkdir(parents=True)
    (bundles_dir / "bundles.yml").write_text(
        "bundles:\n  custom_bundle:\n    sources: [hn]\n    description: test\n"
    )
    result = get_available_bundles(project_root=tmp_path)
    assert "custom_bundle" in result


def test_get_available_bundles_falls_back_to_builtin_when_user_file_absent(tmp_path):
    # No Config/sources/active/bundles/ in tmp_path
    result = get_available_bundles(project_root=tmp_path)
    assert isinstance(result, dict)
    assert len(result) > 0


def test_get_available_bundles_no_project_root_uses_builtin():
    result = get_available_bundles()
    assert isinstance(result, dict)
    assert len(result) > 0
