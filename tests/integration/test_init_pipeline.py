"""Integration: capcat init then list sources."""
import os
import subprocess
import sys
from pathlib import Path

# Ensure subprocess calls can find the capcat package
_PROJECT_ROOT = str(Path(__file__).parent.parent.parent)
_SUBPROCESS_ENV = {**os.environ, "PYTHONPATH": _PROJECT_ROOT}


def test_init_creates_project_structure(tmp_path):
    """capcat init must create .capcat/ and Config/ structure."""
    result = subprocess.run(
        [sys.executable, "-m", "capcat", "init"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=_SUBPROCESS_ENV,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".capcat").is_dir()
    assert (tmp_path / "Config" / "capcat.yml").is_file()


def test_list_sources_after_init(tmp_path):
    """capcat list sources must run without error after init."""
    subprocess.run(
        [sys.executable, "-m", "capcat", "init"],
        cwd=tmp_path,
        check=True,
        env=_SUBPROCESS_ENV,
    )
    result = subprocess.run(
        [sys.executable, "-m", "capcat", "list", "sources"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=_SUBPROCESS_ENV,
    )
    assert result.returncode == 0, result.stderr
