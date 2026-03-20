"""Mirror builtin source configs to userspace Config/sources/active/."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import date
from pathlib import Path
from typing import Optional

try:
    import questionary
except ImportError:
    questionary = None  # type: ignore[assignment]


class SourceConfigMirror:
    """Copy and track builtin source configs in userspace."""

    _CONFIG_DRIVEN_EXTS = {".yaml", ".yml", ".json"}

    def __init__(self, project_root: Path, tui_mode: bool) -> None:
        self._root = project_root
        self._tui_mode = tui_mode

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_mirrored(self) -> bool:
        """True if any domain dir exists under Config/sources/active/."""
        active = self._root / "Config" / "sources" / "active"
        return (
            (active / "config_driven" / "configs").exists()
            or (active / "custom").exists()
            or (active / "bundles").exists()
        )

    def run_first_mirror(self) -> None:
        """Copy all three domains, write manifest, print message."""
        manifest = self._load_manifest()

        self._mirror_config_driven(manifest)
        self._mirror_custom(manifest)
        self._mirror_bundles(manifest)

        self._save_manifest(manifest)
        print(
            "Capcat: source configs written to Config/sources/active/ "
            "— edit them to customise your sources."
        )

    def check_for_upgrades(self) -> None:
        """Diff all domains vs manifest. Prompt for new items and changed builtins."""
        manifest = self._load_manifest()
        if not manifest:
            self._resync_manifest()
            return

        manifest = self._step1_new_items(manifest)
        manifest = self._step2_3_changed_builtins(manifest)
        self._save_manifest(manifest)

    # ------------------------------------------------------------------
    # Hash / manifest helpers
    # ------------------------------------------------------------------

    def _compute_hash(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _load_manifest(self) -> dict:
        p = self._root / ".capcat" / "source_hashes.json"
        if not p.exists():
            return {}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_manifest(self, manifest: dict) -> None:
        p = self._root / ".capcat" / "source_hashes.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def _prompt(self, message: str) -> str:
        """Display prompt; use questionary in TUI mode, print+input in CLI mode."""
        if self._tui_mode:
            result = questionary.confirm(message, default=True).ask()
            return "y" if result else "n"
        print(message)
        return input("> ")

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _builtin_config_driven_dir(self) -> Path:
        return Path(__file__).parent.parent / "sources" / "builtin" / "config_driven" / "configs"

    def _user_config_driven_dir(self) -> Path:
        return self._root / "Config" / "sources" / "active" / "config_driven" / "configs"

    def _builtin_custom_dir(self) -> Path:
        return Path(__file__).parent.parent / "sources" / "builtin" / "custom"

    def _user_custom_dir(self) -> Path:
        return self._root / "Config" / "sources" / "active" / "custom"

    def _builtin_bundles_dir(self) -> Path:
        return Path(__file__).parent.parent / "sources" / "builtin"

    def _user_bundles_dir(self) -> Path:
        return self._root / "Config" / "sources" / "active" / "bundles"

    # ------------------------------------------------------------------
    # First-run domain mirrors
    # ------------------------------------------------------------------

    def _mirror_config_driven(self, manifest: dict) -> None:
        src = self._builtin_config_driven_dir()
        dst = self._user_config_driven_dir()
        dst.mkdir(parents=True, exist_ok=True)
        if not src.exists():
            return
        for f in src.iterdir():
            if f.suffix in self._CONFIG_DRIVEN_EXTS and ".disabled" not in f.suffixes:
                dest_file = dst / f.name
                shutil.copy2(f, dest_file)
                h = self._compute_hash(f)
                key = f"config_driven/configs/{f.name}"
                manifest[key] = {"builtin_hash": h, "user_hash": h}

    def _mirror_custom(self, manifest: dict) -> None:
        src = self._builtin_custom_dir()
        dst = self._user_custom_dir()
        dst.mkdir(parents=True, exist_ok=True)
        if not src.exists():
            return
        for source_dir in src.iterdir():
            if not source_dir.is_dir():
                continue
            dest_source = dst / source_dir.name
            if dest_source.exists():
                shutil.rmtree(dest_source)
            shutil.copytree(source_dir, dest_source)
            for f in dest_source.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(dest_source)
                    builtin_f = source_dir / rel
                    if builtin_f.exists():
                        h = self._compute_hash(builtin_f)
                        key = f"custom/{source_dir.name}/{rel}"
                        manifest[key] = {"builtin_hash": h, "user_hash": h}

    def _mirror_bundles(self, manifest: dict) -> None:
        src = self._builtin_bundles_dir()
        dst = self._user_bundles_dir()
        dst.mkdir(parents=True, exist_ok=True)
        if not src.exists():
            return
        for f in src.iterdir():
            if f.is_file() and f.suffix == ".yml":
                dest_file = dst / f.name
                shutil.copy2(f, dest_file)
                h = self._compute_hash(f)
                key = f"bundles/{f.name}"
                manifest[key] = {"builtin_hash": h, "user_hash": h}

    # ------------------------------------------------------------------
    # Upgrade diff placeholders (implemented in Tasks 3-5)
    # ------------------------------------------------------------------

    def _step1_new_items(self, manifest: dict) -> dict:
        return manifest  # placeholder

    def _step2_3_changed_builtins(self, manifest: dict) -> dict:
        return manifest  # placeholder

    def _resync_manifest(self) -> None:
        pass  # placeholder
