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
        """Detect and optionally copy items present in builtins but absent from user mirror."""
        new_cfg: list = []   # (builtin_file, user_file, key)
        new_custom: list = []  # (builtin_dir, user_dir)
        new_bundles: list = []  # (builtin_file, user_file, key)

        # config_driven: source_ids in builtin but absent in user mirror
        builtin_cfg = self._builtin_config_driven_dir()
        user_cfg = self._user_config_driven_dir()
        if builtin_cfg.exists():
            for f in builtin_cfg.iterdir():
                if f.suffix not in self._CONFIG_DRIVEN_EXTS:
                    continue
                if ".disabled" in f.suffixes:
                    continue
                key = f"config_driven/configs/{f.name}"
                if key not in manifest and not (user_cfg / f.name).exists():
                    new_cfg.append((f, user_cfg / f.name, key))

        # custom: subdirs in builtin absent from user mirror
        builtin_custom = self._builtin_custom_dir()
        user_custom = self._user_custom_dir()
        if builtin_custom.exists():
            for d in builtin_custom.iterdir():
                if d.is_dir() and not (user_custom / d.name).exists():
                    new_custom.append((d, user_custom / d.name))

        # bundles: *.yml at builtin root absent from user bundles dir
        builtin_bundles = self._builtin_bundles_dir()
        user_bundles = self._user_bundles_dir()
        if builtin_bundles.exists():
            for f in builtin_bundles.iterdir():
                if f.is_file() and f.suffix == ".yml":
                    key = f"bundles/{f.name}"
                    if key not in manifest and not (user_bundles / f.name).exists():
                        new_bundles.append((f, user_bundles / f.name, key))

        if not new_cfg and not new_custom and not new_bundles:
            return manifest

        # Build prompt
        source_names = [str(f.name) for f, _, _ in new_cfg]
        custom_names = [d.name for d, _ in new_custom]
        bundle_names = [str(f.name) for f, _, _ in new_bundles]
        total = len(source_names) + len(custom_names) + len(bundle_names)

        msg_lines = [f"Capcat: {total} new item(s) available:"]
        msg_lines.append(f"  Sources: {', '.join(source_names) if source_names else '(none)'}")
        msg_lines.append(f"  Custom sources: {', '.join(custom_names) if custom_names else '(none)'}")
        msg_lines.append(f"  Bundles: {', '.join(bundle_names) if bundle_names else '(none)'}")
        msg_lines.append("Add to your configuration? [Y/n]")

        answer = self._prompt("\n".join(msg_lines))
        if answer.strip().lower() in ("", "y", "yes"):
            user_cfg.mkdir(parents=True, exist_ok=True)
            user_custom.mkdir(parents=True, exist_ok=True)
            user_bundles.mkdir(parents=True, exist_ok=True)

            for builtin_f, user_f, key in new_cfg:
                shutil.copy2(builtin_f, user_f)
                h = self._compute_hash(builtin_f)
                manifest[key] = {"builtin_hash": h, "user_hash": h}

            for builtin_d, user_d in new_custom:
                shutil.copytree(builtin_d, user_d)
                for f in user_d.rglob("*"):
                    if f.is_file():
                        rel = f.relative_to(user_d)
                        builtin_f = builtin_d / rel
                        if builtin_f.exists():
                            h = self._compute_hash(builtin_f)
                            key = f"custom/{builtin_d.name}/{rel}"
                            manifest[key] = {"builtin_hash": h, "user_hash": h}

            for builtin_f, user_f, key in new_bundles:
                shutil.copy2(builtin_f, user_f)
                h = self._compute_hash(builtin_f)
                manifest[key] = {"builtin_hash": h, "user_hash": h}

        return manifest

    def _step2_3_changed_builtins(self, manifest: dict) -> dict:
        return manifest  # placeholder

    def _resync_manifest(self) -> None:
        pass  # placeholder
