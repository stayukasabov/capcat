"""Tests for capcat settings command and init template write."""
from pathlib import Path
from unittest.mock import patch
import pytest


class TestCmdSettings:
    def test_writes_global_settings_yaml(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "Config").mkdir()

        from capcat.cli import _cmd_settings
        _cmd_settings([])

        out = tmp_path / "Config" / "Global-settings.yaml"
        assert out.exists()
        content = out.read_text()
        assert "max_pdf_size_bytes" in content
        assert "article_count" in content
        assert "crawl_delay" in content

    def test_does_not_overwrite_existing_without_force(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "Config").mkdir()
        existing = tmp_path / "Config" / "Global-settings.yaml"
        existing.write_text("original content")

        from capcat.cli import _cmd_settings
        _cmd_settings([])

        assert existing.read_text() == "original content"

    def test_overwrites_with_force(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "Config").mkdir()
        existing = tmp_path / "Config" / "Global-settings.yaml"
        existing.write_text("original content")

        from capcat.cli import _cmd_settings
        _cmd_settings(["--force"])

        assert existing.read_text() != "original content"
        assert "max_pdf_size_bytes" in existing.read_text()

    def test_settings_dispatched_from_cli(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "Config").mkdir()

        with patch("capcat.cli._auto_init"), patch("capcat.cli._cmd_settings") as mock_cmd:
            from capcat.cli import _dispatch
            _dispatch(["settings"])
            mock_cmd.assert_called_once_with([])


class TestInitUserTemplate:
    def test_init_writes_user_level_template_on_first_init(self, tmp_path, monkeypatch):
        user_cfg = tmp_path / ".config" / "capcat"
        monkeypatch.setenv("HOME", str(tmp_path))

        with patch("capcat.commands.init.init_project"), \
             patch("capcat.cli._auto_init"):
            from capcat.cli import _cmd_init
            _cmd_init([])

        out = user_cfg / "Global-settings.yaml"
        assert out.exists()
        assert "max_pdf_size_bytes" in out.read_text()

    def test_init_does_not_overwrite_existing_user_template(self, tmp_path, monkeypatch):
        user_cfg = tmp_path / ".config" / "capcat"
        user_cfg.mkdir(parents=True)
        (user_cfg / "Global-settings.yaml").write_text("custom content")
        monkeypatch.setenv("HOME", str(tmp_path))

        with patch("capcat.commands.init.init_project"), \
             patch("capcat.cli._auto_init"):
            from capcat.cli import _cmd_init
            _cmd_init([])

        assert (user_cfg / "Global-settings.yaml").read_text() == "custom content"

    def test_reinit_skips_user_template(self, tmp_path, monkeypatch):
        user_cfg = tmp_path / ".config" / "capcat"
        monkeypatch.setenv("HOME", str(tmp_path))

        with patch("capcat.commands.init.init_project"), \
             patch("capcat.cli._auto_init"):
            from capcat.cli import _cmd_init
            _cmd_init(["--reinit"])

        assert not (user_cfg / "Global-settings.yaml").exists()
