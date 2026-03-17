"""Implementation of capcat init command."""
from __future__ import annotations
import shutil
from pathlib import Path


GITIGNORE_BLOCK = """\

# capcat — managed entries
.capcat/
News/
Capcats/
"""

DEFAULT_CONFIG = """\
# Capcat configuration
# See: https://github.com/<owner>/capcat/docs/quick-start.md

sources: []
bundles: {}
"""


class AlreadyInitializedError(Exception):
    """Raised when init is called on an existing project without --reinit."""


def _copy_themes_to(dest: Path) -> None:
    """Copy base.css, design-system.css, and Space-Grotesk/ from package themes to dest."""
    from capcat import __version__

    pkg_themes = Path(__file__).parent.parent / "themes"

    for filename in ("base.css", "design-system.css"):
        src = pkg_themes / filename
        if src.exists():
            shutil.copy2(src, dest / filename)

    font_src = pkg_themes / "Space-Grotesk"
    font_dst = dest / "Space-Grotesk"
    if font_src.is_dir():
        if font_dst.exists():
            shutil.rmtree(font_dst)
        shutil.copytree(font_src, font_dst)

    (dest / ".capcat-version").write_text(__version__ + "\n")


def init_project(root: Path, reinit: bool = False) -> None:
    """Initialize a capcat project in the given directory.

    Args:
        root: Directory to initialize as a capcat project.
        reinit: If True, reset .capcat/ internal state only.

    Raises:
        AlreadyInitializedError: If project exists and reinit is False.
    """
    capcat_dir = root / ".capcat"
    config_dir = root / "Config"

    if capcat_dir.exists() and not reinit:
        raise AlreadyInitializedError(
            f"Already a capcat project at {root}. "
            "Use 'capcat init --reinit' to reset internal state."
        )

    if capcat_dir.exists() and reinit:
        shutil.rmtree(capcat_dir)

    capcat_dir.mkdir(parents=True, exist_ok=True)
    (capcat_dir / "state.json").write_text("{}\n")
    (capcat_dir / "cache").mkdir(exist_ok=True)
    (capcat_dir / "registry").mkdir(exist_ok=True)

    if reinit:
        return  # Config is user-owned; never touch it on reinit

    config_dir.mkdir(exist_ok=True)
    sources_dir = config_dir / "sources" / "active"
    (sources_dir / "config_driven").mkdir(parents=True, exist_ok=True)
    (sources_dir / "custom").mkdir(parents=True, exist_ok=True)
    themes_dir = config_dir / "themes"
    themes_dir.mkdir(exist_ok=True)
    _copy_themes_to(themes_dir)

    config_file = config_dir / "capcat.yml"
    if not config_file.exists():
        config_file.write_text(DEFAULT_CONFIG)

    gitignore = root / ".gitignore"
    if gitignore.exists():
        existing = gitignore.read_text()
        if "# capcat — managed entries" not in existing:
            gitignore.write_text(existing + GITIGNORE_BLOCK)
    else:
        gitignore.write_text(GITIGNORE_BLOCK.lstrip())
