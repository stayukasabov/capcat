from pathlib import Path
import capcat


def test_themes_directory_ships_with_package():
    """themes/ must exist inside the installed package."""
    package_dir = Path(capcat.__file__).parent
    themes_dir = package_dir / "themes"
    assert themes_dir.exists(), f"themes/ not found at {themes_dir}"
    assert any(themes_dir.iterdir()), "themes/ is empty"
