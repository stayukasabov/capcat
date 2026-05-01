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


def _key_display_name(key: str) -> str:
    """Convert a manifest key to a short human-readable name."""
    if key.startswith("custom/"):
        parts = key.split("/", 2)
        return f"{parts[1]}/{parts[2]}" if len(parts) == 3 else key
    if key.startswith("config_driven/configs/"):
        return key.removeprefix("config_driven/configs/")
    if key.startswith("bundles/"):
        return key.removeprefix("bundles/")
    return key


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
                manifest[key] = {"ownership": "config", "builtin_hash": h, "user_hash": h}

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
                        ownership = "app" if f.suffix == ".py" else "config"
                        manifest[key] = {"ownership": ownership, "builtin_hash": h, "user_hash": h}

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
                manifest[key] = {"ownership": "config", "builtin_hash": h, "user_hash": h}

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

        app_overwrite: list = []     # (key, user_file, builtin_file, new_hash, user_modified)
        config_silent: list = []     # (key, user_file, builtin_file, new_hash)
        config_modified: list = []   # (key, user_file, builtin_file, new_hash)
        keys_to_remove: list = []

        for key, entry in list(manifest.items()):
            stored_builtin_hash = entry.get("builtin_hash", "")
            stored_user_hash = entry.get("user_hash", "")
            # .py files are always app-owned — even in old manifests that predate the
            # ownership field. Without this, missing ownership defaults to "config",
            # causing changed .py files to hit the interactive prompt path and get
            # skipped silently in non-interactive (-q) mode.
            if key.endswith(".py"):
                ownership = "app"
            else:
                ownership = entry.get("ownership", "config")

            if not stored_builtin_hash:
                continue  # user-added source — never touch

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
            user_modified = current_user_hash != stored_user_hash

            if ownership == "app":
                app_overwrite.append((key, user_file, builtin_file, current_builtin_hash, user_modified))
            elif user_modified:
                config_modified.append((key, user_file, builtin_file, current_builtin_hash))
            else:
                config_silent.append((key, user_file, builtin_file, current_builtin_hash))

        for key in keys_to_remove:
            del manifest[key]

        # 1. App-owned: always overwrite; backup if user had edits
        for key, user_file, builtin_file, new_hash, user_modified in app_overwrite:
            if user_modified:
                try:
                    self._backup([(key, user_file)])
                except OSError as exc:
                    logger.warning(
                        f"Backup failed for {_key_display_name(key)} ({exc}) — skipping update"
                    )
                    continue
                logger.warning(
                    f"Updated {_key_display_name(key)} (had local edits — "
                    f"backup created at Config/sources/backup_*/)"
                )
            else:
                logger.info(f"Updated {_key_display_name(key)}")
            shutil.copy2(builtin_file, user_file)
            manifest[key]["builtin_hash"] = new_hash
            manifest[key]["user_hash"] = new_hash

        # 2. Config-owned, unmodified: silent overwrite
        for key, user_file, builtin_file, new_hash in config_silent:
            logger.info(f"Updated {_key_display_name(key)}")
            shutil.copy2(builtin_file, user_file)
            manifest[key]["builtin_hash"] = new_hash
            manifest[key]["user_hash"] = new_hash

        # 3. Config-owned, user-modified: interactive prompt
        if config_modified:
            manifest = self._prompt_config_updates(manifest, config_modified)

        return manifest

    def _prompt_config_updates(self, manifest: dict, candidates: list) -> dict:
        """Interactive prompt for config-owned files that the user has modified."""
        is_interactive = sys.stdin.isatty() and questionary is not None

        if not is_interactive:
            names = ", ".join(_key_display_name(k) for k, _, _, _ in candidates)
            print(
                f"WARNING: source updates available for modified files: {names}\n"
                f"Run capcat fetch interactively to review."
            )
            return manifest

        names_display = "\n".join(
            f"  - {_key_display_name(k)}" for k, _, _, _ in candidates
        )
        message = f"Capcat detected local modifications in:\n{names_display}\n"

        top_choice = questionary.select(
            message,
            choices=[
                "Overwrite all with new defaults",
                "Select individually",
                "No \u2014 keep my modifications",
            ],
        ).ask()

        if top_choice is None or top_choice.startswith("No"):
            return manifest

        if top_choice == "Overwrite all with new defaults":
            try:
                self._backup([(k, p) for k, p, _, _ in candidates])
            except OSError as exc:
                print(f"Capcat: backup failed ({exc}) \u2014 update aborted.")
                return manifest
            for key, user_file, builtin_file, new_hash in candidates:
                shutil.copy2(builtin_file, user_file)
                manifest[key]["builtin_hash"] = new_hash
                manifest[key]["user_hash"] = new_hash
            return manifest

        # Select individually
        for key, user_file, builtin_file, new_hash in candidates:
            diff = self._diff_files(user_file, builtin_file)
            if diff:
                print(f"\n{_key_display_name(key)}:\n{diff}")
            per_choice = questionary.select(
                f"Update {_key_display_name(key)}?",
                choices=["Update", "Skip"],
            ).ask()
            if per_choice == "Update":
                try:
                    self._backup([(key, user_file)])
                except OSError as exc:
                    print(
                        f"Capcat: backup failed for {_key_display_name(key)} ({exc}) \u2014 skipping."
                    )
                    continue
                shutil.copy2(builtin_file, user_file)
                manifest[key]["builtin_hash"] = new_hash
                manifest[key]["user_hash"] = new_hash

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

    def _diff_files(self, user_file: Path, builtin_file: Path) -> str:
        """Return a unified diff of user_file vs builtin_file.

        fromfile='your version', tofile='new default'.
        Returns empty string if files are identical.
        """
        import difflib
        user_lines = user_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        builtin_lines = builtin_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            user_lines,
            builtin_lines,
            fromfile="your version",
            tofile="new default",
            lineterm="",
        ))
        return "".join(diff)

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

        Uses the actual installed builtin hash as the baseline so future
        check_for_upgrades() diffs are accurate.
        """
        from capcat.core.logging_config import get_logger
        get_logger(__name__).debug(
            "Capcat: source_hashes.json missing — rebuilt from current state."
        )
        manifest = {}

        # config_driven
        user_cfg = self._user_config_driven_dir()
        if user_cfg.exists():
            for f in user_cfg.iterdir():
                if f.is_file() and (
                    f.suffix in self._CONFIG_DRIVEN_EXTS
                    or f.name.endswith(".yaml.disabled")
                ):
                    key = f"config_driven/configs/{f.name}"
                    user_h = self._compute_hash(f)
                    builtin_f = self._builtin_file_for_key(key)
                    builtin_h = self._compute_hash(builtin_f) if builtin_f else ""
                    manifest[key] = {
                        "ownership": "config",
                        "builtin_hash": builtin_h,
                        "user_hash": user_h,
                    }

        # custom
        user_custom = self._user_custom_dir()
        if user_custom.exists():
            for source_dir in user_custom.iterdir():
                if source_dir.is_dir():
                    for f in source_dir.rglob("*"):
                        if f.is_file() and not self._SKIP_DIRS.intersection(f.parts):
                            rel = f.relative_to(source_dir)
                            key = f"custom/{source_dir.name}/{rel}"
                            user_h = self._compute_hash(f)
                            builtin_f = self._builtin_file_for_key(key)
                            builtin_h = self._compute_hash(builtin_f) if builtin_f else ""
                            if not builtin_f:
                                ownership = "user"
                            else:
                                ownership = "app" if f.suffix == ".py" else "config"
                            manifest[key] = {
                                "ownership": ownership,
                                "builtin_hash": builtin_h,
                                "user_hash": user_h,
                            }

        # bundles
        user_bundles = self._user_bundles_dir()
        if user_bundles.exists():
            for f in user_bundles.iterdir():
                if f.is_file() and f.suffix == ".yml":
                    key = f"bundles/{f.name}"
                    user_h = self._compute_hash(f)
                    builtin_f = self._builtin_file_for_key(key)
                    builtin_h = self._compute_hash(builtin_f) if builtin_f else ""
                    manifest[key] = {
                        "ownership": "config",
                        "builtin_hash": builtin_h,
                        "user_hash": user_h,
                    }

        self._save_manifest(manifest)
