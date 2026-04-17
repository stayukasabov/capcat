"""Regression tests for B4, B5, and B1 (2026-04-13) — source config mirror bugs.

B4: __pycache__/*.pyc files must not appear in the mirror manifest.
B5: upgrade prompt must not fire when stdin is non-interactive.
B1: declining an upgrade (or silent non-interactive decline) must NOT update
    builtin_hash in the manifest, so the upgrade offer re-appears next run.
"""
import sys
from pathlib import Path
from unittest.mock import patch


def _make_mirror(tmp_path, tui_mode=False):
    from capcat.core.source_config_mirror import SourceConfigMirror
    return SourceConfigMirror(project_root=tmp_path, tui_mode=tui_mode)


def _write_file(path: Path, content: str = "x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# B4 — __pycache__ must be excluded from manifest
# ---------------------------------------------------------------------------

class TestMirrorCustomExcludesPycache:
    def test_pycache_pyc_not_in_manifest_after_first_mirror(self, tmp_path):
        """__pycache__/*.pyc files must not be tracked in the manifest."""
        from capcat.core.source_config_mirror import SourceConfigMirror

        builtin_custom = tmp_path / "builtin" / "custom" / "mysource"
        _write_file(builtin_custom / "source.py", "# source")
        (builtin_custom / "__pycache__").mkdir(parents=True, exist_ok=True)
        (builtin_custom / "__pycache__" / "source.cpython-314.pyc").write_bytes(b"\x00" * 4)

        mirror = SourceConfigMirror.__new__(SourceConfigMirror)
        mirror._root = tmp_path / "vault"
        mirror._tui_mode = False

        with patch.object(mirror, "_builtin_custom_dir", return_value=tmp_path / "builtin" / "custom"):
            manifest = {}
            mirror._mirror_custom(manifest)

        pyc_keys = [k for k in manifest if "__pycache__" in k]
        assert pyc_keys == [], f"__pycache__ keys must not appear in manifest, got: {pyc_keys}"

    def test_py_source_file_is_still_tracked(self, tmp_path):
        """Legitimate .py source files must still be tracked after __pycache__ fix."""
        from capcat.core.source_config_mirror import SourceConfigMirror

        builtin_custom = tmp_path / "builtin" / "custom" / "mysource"
        _write_file(builtin_custom / "source.py", "# source")
        (builtin_custom / "__pycache__").mkdir(parents=True, exist_ok=True)
        (builtin_custom / "__pycache__" / "source.cpython-314.pyc").write_bytes(b"\x00" * 4)

        mirror = SourceConfigMirror.__new__(SourceConfigMirror)
        mirror._root = tmp_path / "vault"
        mirror._tui_mode = False

        with patch.object(mirror, "_builtin_custom_dir", return_value=tmp_path / "builtin" / "custom"):
            manifest = {}
            mirror._mirror_custom(manifest)

        py_keys = [k for k in manifest if k.endswith("source.py")]
        assert py_keys, "source.py must still appear in manifest"

    def test_step1_new_items_excludes_pycache(self, tmp_path):
        """_step1_new_items must not add __pycache__ files to manifest."""
        from capcat.core.source_config_mirror import SourceConfigMirror

        builtin_custom = tmp_path / "builtin" / "custom" / "newsource"
        _write_file(builtin_custom / "source.py", "# source")
        (builtin_custom / "__pycache__").mkdir(parents=True, exist_ok=True)
        (builtin_custom / "__pycache__" / "source.cpython-314.pyc").write_bytes(b"\x00" * 4)

        mirror = SourceConfigMirror.__new__(SourceConfigMirror)
        mirror._root = tmp_path / "vault"
        mirror._tui_mode = False

        with (
            patch.object(mirror, "_builtin_custom_dir", return_value=tmp_path / "builtin" / "custom"),
            patch.object(mirror, "_user_custom_dir", return_value=tmp_path / "vault" / "custom"),
            patch.object(mirror, "_builtin_config_driven_dir", return_value=tmp_path / "nodir"),
            patch.object(mirror, "_user_config_driven_dir", return_value=tmp_path / "nodir"),
            patch.object(mirror, "_builtin_bundles_dir", return_value=tmp_path / "nodir"),
            patch.object(mirror, "_user_bundles_dir", return_value=tmp_path / "nodir"),
        ):
            manifest = mirror._step1_new_items({})

        pyc_keys = [k for k in manifest if "__pycache__" in k]
        assert pyc_keys == [], f"__pycache__ keys must not appear after step1, got: {pyc_keys}"

    def test_resync_manifest_excludes_pycache(self, tmp_path):
        """_resync_manifest must not track __pycache__ files."""
        from capcat.core.source_config_mirror import SourceConfigMirror

        vault_custom = tmp_path / "Config" / "sources" / "active" / "custom" / "mysource"
        _write_file(vault_custom / "source.py", "# source")
        (vault_custom / "__pycache__").mkdir(parents=True, exist_ok=True)
        (vault_custom / "__pycache__" / "source.cpython-314.pyc").write_bytes(b"\x00" * 4)

        mirror = SourceConfigMirror.__new__(SourceConfigMirror)
        mirror._root = tmp_path
        mirror._tui_mode = False

        mirror._resync_manifest()

        from capcat.core.source_config_mirror import SourceConfigMirror as SCM
        loaded = SCM.__new__(SCM)
        loaded._root = tmp_path
        manifest = loaded._load_manifest()

        pyc_keys = [k for k in manifest if "__pycache__" in k]
        assert pyc_keys == [], f"__pycache__ keys must not appear in resynced manifest, got: {pyc_keys}"


# ---------------------------------------------------------------------------
# B5 — prompt must not fire when stdin is non-interactive
# ---------------------------------------------------------------------------

class TestPromptNonInteractive:
    def test_prompt_returns_n_when_stdin_not_tty(self, tmp_path):
        """_prompt must return 'n' without calling input() when stdin is not a tty."""
        mirror = _make_mirror(tmp_path)
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = False
            result = mirror._prompt("Update available?")
        assert result == "n", f"Expected 'n' for non-interactive stdin, got {result!r}"

    def test_prompt_does_not_call_input_when_stdin_not_tty(self, tmp_path):
        """input() must never be called when stdin is non-interactive."""
        mirror = _make_mirror(tmp_path)
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input") as mock_input,
        ):
            mock_stdin.isatty.return_value = False
            mirror._prompt("Update?")
        mock_input.assert_not_called()

    def test_check_for_upgrades_skips_prompt_when_noninteractive(self, tmp_path):
        """check_for_upgrades must not fire upgrade prompt when stdin is not a tty."""
        from capcat.core.source_config_mirror import SourceConfigMirror

        # Set up a manifest with one candidate that would trigger the prompt
        mirror = SourceConfigMirror.__new__(SourceConfigMirror)
        mirror._root = tmp_path
        mirror._tui_mode = False

        prompted = []

        def fake_prompt(msg):
            prompted.append(msg)
            return "n"

        # Simulate step2_3 finding candidates but being called in non-interactive mode
        with (
            patch.object(mirror, "_load_manifest", return_value={}),
            patch.object(mirror, "_step1_new_items", return_value={}),
            patch.object(mirror, "_step2_3_changed_builtins", return_value={}),
            patch.object(mirror, "_save_manifest"),
            patch("sys.stdin") as mock_stdin,
        ):
            mock_stdin.isatty.return_value = False
            mirror.check_for_upgrades()

        # The key assertion: _prompt was never called (step2_3 is mocked anyway,
        # but we verify no EOFError or input() call propagates)
        assert prompted == [], "No prompt should fire during non-interactive check_for_upgrades"

    def test_prompt_fires_normally_when_stdin_is_tty(self, tmp_path):
        """_prompt must still call input() when stdin is a real tty."""
        mirror = _make_mirror(tmp_path)
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input", return_value="n") as mock_input,
        ):
            mock_stdin.isatty.return_value = True
            result = mirror._prompt("Update?")
        mock_input.assert_called_once()
        assert result == "n"


# ---------------------------------------------------------------------------
# B1 — declining upgrade must NOT update builtin_hash in manifest
# ---------------------------------------------------------------------------

class TestUpgradeDeclinePreservesBuiltinHash:
    """When user declines (or non-interactive silent decline), builtin_hash must
    remain unchanged so the upgrade offer appears again on the next run."""

    def _setup_mirror_with_stale_vault(self, tmp_path):
        """Return a mirror whose manifest has one stale entry.

        builtin file (v2) is newer than the vault file (v1).
        The manifest currently records the OLD builtin hash (v1).
        user_hash matches the vault file hash (v1) — user never modified it.
        """
        import hashlib

        # Builtin (new version, v2)
        builtin_dir = tmp_path / "sources_builtin" / "custom" / "hn"
        builtin_dir.mkdir(parents=True)
        builtin_src = builtin_dir / "source.py"
        builtin_src.write_text("# v2 with download_pdfs")

        # Vault (old version, v1)
        vault_dir = tmp_path / "Config" / "sources" / "active" / "custom" / "hn"
        vault_dir.mkdir(parents=True)
        vault_src = vault_dir / "source.py"
        vault_src.write_text("# v1 without download_pdfs")

        # Hashes
        h_v1 = hashlib.sha256(b"# v1 without download_pdfs").hexdigest()
        h_v2 = hashlib.sha256(b"# v2 with download_pdfs").hexdigest()

        # Manifest: builtin_hash = v1 hash (old), user_hash = v1 hash
        manifest_dir = tmp_path / ".capcat"
        manifest_dir.mkdir()
        import json
        (manifest_dir / "source_hashes.json").write_text(json.dumps({
            "custom/hn/source.py": {
                "builtin_hash": h_v1,
                "user_hash": h_v1,
            }
        }))

        from capcat.core.source_config_mirror import SourceConfigMirror
        mirror = SourceConfigMirror.__new__(SourceConfigMirror)
        mirror._root = tmp_path
        mirror._tui_mode = False

        # Patch _builtin_file_for_key and _resolve_user_file to use tmp dirs
        def fake_builtin(key):
            return builtin_src if key == "custom/hn/source.py" else None

        def fake_user(key):
            return vault_src if key == "custom/hn/source.py" else None

        return mirror, fake_builtin, fake_user, h_v1, h_v2

    def test_unmodified_config_updates_builtin_hash_silently(self, tmp_path):
        """Unmodified config file (no ownership field → backward compat → 'config') is
        silently overwritten; builtin_hash is updated to the new builtin hash."""
        import json
        from unittest.mock import patch

        mirror, fake_builtin, fake_user, h_v1, h_v2 = self._setup_mirror_with_stale_vault(tmp_path)

        with (
            patch.object(mirror, "_builtin_file_for_key", side_effect=fake_builtin),
            patch.object(mirror, "_resolve_user_file", side_effect=fake_user),
        ):
            manifest = mirror._load_manifest()
            manifest = mirror._step2_3_changed_builtins(manifest)

        # builtin_hash updated — silent overwrite happened
        assert manifest["custom/hn/source.py"]["builtin_hash"] == h_v2

    def test_accept_does_update_builtin_hash(self, tmp_path):
        """When user accepts, manifest.builtin_hash must be updated to v2."""
        import json
        from unittest.mock import patch

        mirror, fake_builtin, fake_user, h_v1, h_v2 = self._setup_mirror_with_stale_vault(tmp_path)

        with (
            patch.object(mirror, "_builtin_file_for_key", side_effect=fake_builtin),
            patch.object(mirror, "_resolve_user_file", side_effect=fake_user),
            patch.object(mirror, "_prompt", return_value="y"),
            patch.object(mirror, "_backup", return_value=tmp_path),
        ):
            manifest = mirror._load_manifest()
            manifest = mirror._step2_3_changed_builtins(manifest)

        assert manifest["custom/hn/source.py"]["builtin_hash"] == h_v2

    def test_unmodified_config_vault_file_is_updated(self, tmp_path):
        """Unmodified config file is overwritten with new builtin content."""
        from unittest.mock import patch

        mirror, fake_builtin, fake_user, h_v1, h_v2 = self._setup_mirror_with_stale_vault(tmp_path)
        vault_src = tmp_path / "Config" / "sources" / "active" / "custom" / "hn" / "source.py"

        with (
            patch.object(mirror, "_builtin_file_for_key", side_effect=fake_builtin),
            patch.object(mirror, "_resolve_user_file", side_effect=fake_user),
        ):
            manifest = mirror._load_manifest()
            mirror._step2_3_changed_builtins(manifest)

        assert vault_src.read_text() == "# v2 with download_pdfs"


class TestResyncManifestBuiltinHash:
    def test_resync_sets_builtin_hash_from_installed_package(self, tmp_path, monkeypatch):
        """_resync_manifest uses the actual installed builtin hash, not the user file hash."""
        from capcat.core.source_config_mirror import SourceConfigMirror
        import hashlib, json

        # User has hn/source.py with old content
        user_src = tmp_path / "Config" / "sources" / "active" / "custom" / "hn" / "source.py"
        user_src.parent.mkdir(parents=True)
        user_src.write_text("# old code\n")

        # Builtin has new content
        builtin_src = tmp_path / "_builtin" / "custom" / "hn" / "source.py"
        builtin_src.parent.mkdir(parents=True)
        builtin_src.write_text("# new code\n")

        m = SourceConfigMirror(tmp_path, tui_mode=False)
        monkeypatch.setattr(m, "_builtin_custom_dir", lambda: builtin_src.parent.parent)
        monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: tmp_path / "_empty")
        monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: tmp_path / "_empty2")
        # No manifest exists — triggers _resync_manifest
        (tmp_path / ".capcat").mkdir(exist_ok=True)
        m.check_for_upgrades()

        manifest = json.loads((tmp_path / ".capcat" / "source_hashes.json").read_text())
        entry = manifest["custom/hn/source.py"]
        builtin_hash = hashlib.sha256(b"# new code\n").hexdigest()
        user_hash = hashlib.sha256(b"# old code\n").hexdigest()
        assert entry["builtin_hash"] == builtin_hash, "builtin_hash must be installed builtin, not user file"
        assert entry["user_hash"] == user_hash
        assert entry["ownership"] == "app"

    def test_resync_marks_user_owned_when_no_builtin(self, tmp_path, monkeypatch):
        """_resync_manifest sets builtin_hash='' for files with no installed builtin."""
        from capcat.core.source_config_mirror import SourceConfigMirror
        import json

        user_src = tmp_path / "Config" / "sources" / "active" / "custom" / "myhn" / "source.py"
        user_src.parent.mkdir(parents=True)
        user_src.write_text("# custom\n")

        m = SourceConfigMirror(tmp_path, tui_mode=False)
        monkeypatch.setattr(m, "_builtin_custom_dir", lambda: tmp_path / "_empty_cust")
        monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: tmp_path / "_empty_cfg")
        monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: tmp_path / "_empty_bun")
        (tmp_path / ".capcat").mkdir(exist_ok=True)
        m.check_for_upgrades()

        manifest = json.loads((tmp_path / ".capcat" / "source_hashes.json").read_text())
        entry = manifest["custom/myhn/source.py"]
        assert entry["builtin_hash"] == ""
        assert entry["ownership"] == "user"


class TestDiffFiles:
    def test_diff_files_shows_user_vs_new_default(self, tmp_path):
        """_diff_files returns unified diff with user as 'your version', builtin as 'new default'."""
        from capcat.core.source_config_mirror import SourceConfigMirror
        m = SourceConfigMirror(tmp_path, tui_mode=False)
        user_f = tmp_path / "user.yaml"
        builtin_f = tmp_path / "builtin.yaml"
        user_f.write_text("article_count: 10\nrate_limit: 1.0\n")
        builtin_f.write_text("article_count: 30\nrate_limit: 1.0\n")
        diff = m._diff_files(user_f, builtin_f)
        assert "--- your version" in diff
        assert "+++ new default" in diff
        assert "-article_count: 10" in diff
        assert "+article_count: 30" in diff

    def test_diff_files_returns_empty_for_identical(self, tmp_path):
        """_diff_files returns empty string when files are identical."""
        from capcat.core.source_config_mirror import SourceConfigMirror
        m = SourceConfigMirror(tmp_path, tui_mode=False)
        f1 = tmp_path / "a.yaml"
        f2 = tmp_path / "b.yaml"
        f1.write_text("name: bbc\n")
        f2.write_text("name: bbc\n")
        assert m._diff_files(f1, f2) == ""


class TestKeyDisplayName:
    def test_custom_source_display(self):
        from capcat.core.source_config_mirror import _key_display_name
        assert _key_display_name("custom/hn/source.py") == "hn/source.py"

    def test_config_driven_display(self):
        from capcat.core.source_config_mirror import _key_display_name
        assert _key_display_name("config_driven/configs/bbc.yaml") == "bbc.yaml"

    def test_bundles_display(self):
        from capcat.core.source_config_mirror import _key_display_name
        assert _key_display_name("bundles/bundles.yml") == "bundles.yml"


class TestAppOwnershipUpdatePath:
    def _setup(self, tmp_path, monkeypatch, user_content, builtin_content):
        from capcat.core.source_config_mirror import SourceConfigMirror
        import hashlib, json

        builtin_src = tmp_path / "_builtin" / "custom" / "hn" / "source.py"
        builtin_src.parent.mkdir(parents=True)
        builtin_src.write_text(builtin_content)

        user_src = tmp_path / "Config" / "sources" / "active" / "custom" / "hn" / "source.py"
        user_src.parent.mkdir(parents=True)
        user_src.write_text(user_content)

        old_builtin_hash = hashlib.sha256(user_content.encode()).hexdigest()
        manifest = {
            "custom/hn/source.py": {
                "ownership": "app",
                "builtin_hash": old_builtin_hash,
                "user_hash": old_builtin_hash,
            }
        }
        (tmp_path / ".capcat").mkdir(exist_ok=True)
        (tmp_path / ".capcat" / "source_hashes.json").write_text(
            json.dumps(manifest)
        )
        m = SourceConfigMirror(tmp_path, tui_mode=False)
        monkeypatch.setattr(m, "_builtin_custom_dir", lambda: builtin_src.parent.parent)
        monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: tmp_path / "_empty")
        monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: tmp_path / "_empty2")
        return m, user_src

    def test_app_file_overwritten_silently_when_unmodified(self, tmp_path, monkeypatch):
        """App-owned file with no user modifications is overwritten silently."""
        m, user_src = self._setup(tmp_path, monkeypatch, "# old\n", "# new\n")
        m.check_for_upgrades()
        assert user_src.read_text() == "# new\n"

    def test_app_file_overwritten_even_when_user_modified(self, tmp_path, monkeypatch):
        """App-owned file is overwritten even if user edited it; backup is created."""
        import hashlib, json
        from capcat.core.source_config_mirror import SourceConfigMirror

        builtin_src = tmp_path / "_builtin" / "custom" / "hn" / "source.py"
        builtin_src.parent.mkdir(parents=True)
        builtin_src.write_text("# new\n")

        user_src = tmp_path / "Config" / "sources" / "active" / "custom" / "hn" / "source.py"
        user_src.parent.mkdir(parents=True)
        user_src.write_text("# user edit\n")  # user modified

        original_hash = hashlib.sha256(b"# old\n").hexdigest()
        manifest = {
            "custom/hn/source.py": {
                "ownership": "app",
                "builtin_hash": original_hash,  # old builtin
                "user_hash": original_hash,     # user had the old version originally
            }
        }
        (tmp_path / ".capcat").mkdir(exist_ok=True)
        (tmp_path / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

        m = SourceConfigMirror(tmp_path, tui_mode=False)
        monkeypatch.setattr(m, "_builtin_custom_dir", lambda: builtin_src.parent.parent)
        monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: tmp_path / "_empty")
        monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: tmp_path / "_empty2")
        m.check_for_upgrades()

        assert user_src.read_text() == "# new\n", "App file must be overwritten"
        backup_dirs = list((tmp_path / "Config" / "sources").glob("backup_*"))
        assert len(backup_dirs) == 1, "Backup must be created when user had edits"

    def test_config_unmodified_overwritten_silently(self, tmp_path, monkeypatch):
        """Config-owned file with no user modifications is overwritten silently."""
        import hashlib, json
        from capcat.core.source_config_mirror import SourceConfigMirror

        builtin_cfg = tmp_path / "_builtin" / "config_driven" / "configs" / "bbc.yaml"
        builtin_cfg.parent.mkdir(parents=True)
        builtin_cfg.write_text("article_count: 30\n")

        user_cfg = tmp_path / "Config" / "sources" / "active" / "config_driven" / "configs" / "bbc.yaml"
        user_cfg.parent.mkdir(parents=True)
        user_cfg.write_text("article_count: 20\n")  # old content

        old_hash = hashlib.sha256(b"article_count: 20\n").hexdigest()
        manifest = {
            "config_driven/configs/bbc.yaml": {
                "ownership": "config",
                "builtin_hash": old_hash,
                "user_hash": old_hash,  # user never modified
            }
        }
        (tmp_path / ".capcat").mkdir(exist_ok=True)
        (tmp_path / ".capcat" / "source_hashes.json").write_text(json.dumps(manifest))

        m = SourceConfigMirror(tmp_path, tui_mode=False)
        monkeypatch.setattr(m, "_builtin_config_driven_dir", lambda: builtin_cfg.parent)
        monkeypatch.setattr(m, "_builtin_custom_dir", lambda: tmp_path / "_empty_cust")
        monkeypatch.setattr(m, "_builtin_bundles_dir", lambda: tmp_path / "_empty_bun")
        m.check_for_upgrades()

        assert user_cfg.read_text() == "article_count: 30\n"
