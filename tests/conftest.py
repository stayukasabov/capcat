"""Shared fixtures for all tests."""
from __future__ import annotations
import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """A temporary directory to use as a capcat project root."""
    return tmp_path


@pytest.fixture(autouse=True)
def mock_pynput(monkeypatch):
    """Mock pynput on headless environments to prevent CI failures."""
    mock = MagicMock()
    monkeypatch.setitem(sys.modules, "pynput", mock)
    monkeypatch.setitem(sys.modules, "pynput.keyboard", mock)
    monkeypatch.setitem(sys.modules, "pynput.mouse", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_yt_dlp(monkeypatch):
    """Mock yt_dlp in unit tests to avoid requiring the package at test time."""
    mock = MagicMock()
    monkeypatch.setitem(sys.modules, "yt_dlp", mock)
    return mock
