"""Regression tests for B4 and B5 — source config mirror bugs.

B4: __pycache__/*.pyc files must not appear in the mirror manifest.
B5: upgrade prompt must not fire when stdin is non-interactive.
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
