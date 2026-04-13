"""Mirror builtin source configs to userspace Config/sources/active/."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
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
    _SKIP_DIRS = {"__pycache__"}

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
        manifest = self._load_manifest() or {}

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
        if manifest is None:
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

    def _load_manifest(self) -> Optional[dict]:
        p = self._root / ".capcat" / "source_hashes.json"
        if not p.exists():
            return None
        content = p.read_text(encoding="utf-8").strip()
        if not content:
            return {}
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            from capcat.core.logging_config import get_logger
            get_logger(__name__).warning(
                f"source_hashes.json is malformed — treating as empty: {exc}"
            )
            return {}

    def _save_manifest(self, manifest: dict) -> None:
        p = self._root / ".capcat" / "source_hashes.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def _prompt(self, message: str) -> str:
        """Display prompt; use questionary in TUI mode, print+input in CLI mode.

        Returns 'n' silently when stdin is not a tty (non-interactive/background run).
        """
        if self._tui_mode and questionary is not None:
            result = questionary.confirm(message, default=True, qmark="").ask()
            return "y" if result else "n"
        if not sys.stdin.isatty():
            return "n"
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
                if f.is_file() and not self._SKIP_DIRS.intersection(f.parts):
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
        """Detect and silently copy items present in builtins but absent from user mirror."""
        new_cfg: list = []
        new_custom: list = []
        new_bundles: list = []

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

        builtin_custom = self._builtin_custom_dir()
        user_custom = self._user_custom_dir()
        if builtin_custom.exists():
            for d in builtin_custom.iterdir():
                if d.is_dir() and not (user_custom / d.name).exists():
                    new_custom.append((d, user_custom / d.name))

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
                if f.is_file() and not self._SKIP_DIRS.intersection(f.parts):
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
        from capcat.core.logging_config import get_logger
        logger = get_logger(__name__)

        override_candidates: list = []  # (key, user_path, new_builtin_hash)
        keys_to_remove: list = []

        for key, entry in list(manifest.items()):
            stored_builtin_hash = entry.get("builtin_hash", "")
            stored_user_hash = entry.get("user_hash", "")

            if not stored_builtin_hash:
                continue  # user-added source

            builtin_file = self._builtin_file_for_key(key)
            if builtin_file is None:
                logger.debug(f"Builtin removed for {key} — leaving user file untouched")
                continue

            user_file = self._resolve_user_file(key)
            if user_file is None:
                logger.debug(f"User file absent for {key} — removing manifest entry")
                keys_to_remove.append(key)
                continue

            current_builtin_hash = self._compute_hash(builtin_file)

            if current_builtin_hash == stored_builtin_hash:
                continue  # builtin unchanged

            current_user_hash = self._compute_hash(user_file)

            if current_user_hash != stored_user_hash:
                continue  # user modified — skip silently

            override_candidates.append((key, user_file, current_builtin_hash))

        for key in keys_to_remove:
            del manifest[key]

        if not override_candidates:
            return manifest

        # Group by domain for prompt
        src_keys = [k for k, _, _ in override_candidates if k.startswith("config_driven/")]
        cust_keys = [k for k, _, _ in override_candidates if k.startswith("custom/")]
        bun_keys = [k for k, _, _ in override_candidates if k.startswith("bundles/")]

        src_names = [Path(k.removeprefix("config_driven/configs/")).stem for k in src_keys]
        # Strip second extension for .yaml.disabled stems
        src_names = [Path(n).stem if "." in n else n for n in src_names]
        cust_display = [k.removeprefix("custom/") for k in cust_keys]
        bun_display = [k.removeprefix("bundles/") for k in bun_keys]

        total = len(override_candidates)
        today_str = date.today().isoformat()
        msg = (
            f"Capcat: {total} item(s) have updates available:\n"
            f"  Sources: {', '.join(src_names) if src_names else '(none)'}\n"
            f"  Custom sources: {', '.join(cust_display) if cust_display else '(none)'}\n"
            f"  Bundles: {', '.join(bun_display) if bun_display else '(none)'}\n"
            f"Override with new defaults? Your files are unmodified.\n"
            f"Backup will be created at Config/sources/backup_{today_str}/. [Y/n]"
        )
        answer = self._prompt(msg)
        if answer.strip().lower() in ("", "y", "yes"):
            try:
                self._backup([(k, p) for k, p, _ in override_candidates])
            except OSError as exc:
                print(f"Capcat: backup failed ({exc}) — override aborted.")
                return manifest

            for key, user_file, new_builtin_hash in override_candidates:
                builtin_file = self._builtin_file_for_key(key)
                shutil.copy2(builtin_file, user_file)
                manifest[key]["builtin_hash"] = new_builtin_hash
                manifest[key]["user_hash"] = new_builtin_hash

        return manifest

    def _backup(self, resolved_user_files: list) -> Path:
        """Copy user files to timestamped backup dir. Raises OSError on failure."""
        today = date.today().isoformat()
        backup_base = self._root / "Config" / "sources"
        backup_dir = backup_base / f"backup_{today}"
        counter = 2
        while backup_dir.exists():
            backup_dir = backup_base / f"backup_{today}-{counter}"
            counter += 1

        backup_dir.mkdir(parents=True)
        for key, user_path in resolved_user_files:
            backup_name = key.replace("/", "-")
            shutil.copy2(user_path, backup_dir / backup_name)
        return backup_dir

    def _resolve_user_file(self, key: str) -> Optional[Path]:
        """Locate the actual user file for a manifest key. Returns None if absent."""
        if key.startswith("config_driven/configs/"):
            fname = key.removeprefix("config_driven/configs/")
            # Get stem (strip .disabled if present, then strip extension)
            p = Path(fname)
            stem = p.stem
            if stem.endswith(".yaml") or stem.endswith(".yml") or stem.endswith(".json"):
                stem = Path(stem).stem
            user_cfg = self._user_config_driven_dir()
            for ext in (".yaml", ".yaml.disabled", ".yml", ".json"):
                candidate = user_cfg / f"{stem}{ext}"
                if candidate.exists():
                    return candidate
            return None
        elif key.startswith("custom/"):
            rel = key.split("/", 1)[1]
            user_path = self._user_custom_dir() / rel
            return user_path if user_path.exists() else None
        elif key.startswith("bundles/"):
            fname = key.removeprefix("bundles/")
            user_path = self._user_bundles_dir() / fname
            return user_path if user_path.exists() else None
        return None

    def _builtin_file_for_key(self, key: str) -> Optional[Path]:
        """Return the builtin file Path for a manifest key, or None if not present."""
        if key.startswith("config_driven/configs/"):
            fname = key.removeprefix("config_driven/configs/")
            p = self._builtin_config_driven_dir() / fname
            return p if p.exists() else None
        elif key.startswith("custom/"):
            rel = key.removeprefix("custom/")
            p = self._builtin_custom_dir() / rel
            return p if p.exists() else None
        elif key.startswith("bundles/"):
            fname = key.removeprefix("bundles/")
            p = self._builtin_bundles_dir() / fname
            return p if p.exists() else None
        return None

    def _resync_manifest(self) -> None:
        """Rebuild manifest from current user files when source_hashes.json is missing.
        Never overwrites user files."""
        from capcat.core.logging_config import get_logger
        logger = get_logger(__name__)
        logger.debug("Capcat: source_hashes.json missing — rebuilt from current state.")

        manifest = {}

        # config_driven
        user_cfg = self._user_config_driven_dir()
        if user_cfg.exists():
            for f in user_cfg.iterdir():
                if f.is_file() and (
                    f.suffix in self._CONFIG_DRIVEN_EXTS
                    or f.name.endswith(".yaml.disabled")
                ):
                    h = self._compute_hash(f)
                    key = f"config_driven/configs/{f.name}"
                    manifest[key] = {"builtin_hash": h, "user_hash": h}

        # custom
        user_custom = self._user_custom_dir()
        if user_custom.exists():
            for source_dir in user_custom.iterdir():
                if source_dir.is_dir():
                    for f in source_dir.rglob("*"):
                        if f.is_file() and not self._SKIP_DIRS.intersection(f.parts):
                            rel = f.relative_to(source_dir)
                            h = self._compute_hash(f)
                            key = f"custom/{source_dir.name}/{rel}"
                            manifest[key] = {"builtin_hash": h, "user_hash": h}

        # bundles
        user_bundles = self._user_bundles_dir()
        if user_bundles.exists():
            for f in user_bundles.iterdir():
                if f.is_file() and f.suffix == ".yml":
                    h = self._compute_hash(f)
                    key = f"bundles/{f.name}"
                    manifest[key] = {"builtin_hash": h, "user_hash": h}

        self._save_manifest(manifest)
