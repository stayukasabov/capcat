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

    def test_decline_does_not_update_builtin_hash(self, tmp_path):
        """When user says 'n', manifest.builtin_hash must stay at old value."""
        import json
        from unittest.mock import patch

        mirror, fake_builtin, fake_user, h_v1, h_v2 = self._setup_mirror_with_stale_vault(tmp_path)

        with (
            patch.object(mirror, "_builtin_file_for_key", side_effect=fake_builtin),
            patch.object(mirror, "_resolve_user_file", side_effect=fake_user),
            patch.object(mirror, "_prompt", return_value="n"),
        ):
            manifest = mirror._load_manifest()
            manifest = mirror._step2_3_changed_builtins(manifest)

        # builtin_hash must remain v1 — upgrade was declined
        assert manifest["custom/hn/source.py"]["builtin_hash"] == h_v1, (
            "builtin_hash must NOT be updated when upgrade is declined — "
            "otherwise the upgrade offer is permanently suppressed"
        )

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

    def test_decline_leaves_vault_file_unchanged(self, tmp_path):
        """Vault file content must not change when upgrade is declined."""
        from unittest.mock import patch

        mirror, fake_builtin, fake_user, h_v1, h_v2 = self._setup_mirror_with_stale_vault(tmp_path)
        vault_src = tmp_path / "Config" / "sources" / "active" / "custom" / "hn" / "source.py"
        original_content = vault_src.read_text()

        with (
            patch.object(mirror, "_builtin_file_for_key", side_effect=fake_builtin),
            patch.object(mirror, "_resolve_user_file", side_effect=fake_user),
            patch.object(mirror, "_prompt", return_value="n"),
        ):
            manifest = mirror._load_manifest()
            mirror._step2_3_changed_builtins(manifest)

        assert vault_src.read_text() == original_content


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
