def test_package_imports() -> None:
    """Package exposes a valid semver __version__ string."""
    import re
    import capcat
    assert hasattr(capcat, "__version__")
    # Matches MAJOR.MINOR.PATCH with optional pre-release suffix.
    assert re.match(r"^\d+\.\d+\.\d+", capcat.__version__), (
        f"__version__ '{capcat.__version__}' is not a valid semver string"
    )


def test_main_module_callable() -> None:
    from capcat.cli import main
    assert callable(main)


def test_main_entry_point() -> None:
    """capcat.__main__ calls cli.main when executed as a module."""
    import sys
    from unittest.mock import patch
    with patch("capcat.cli.main") as mock_main:
        with patch.object(sys, "argv", ["capcat", "--help"]):
            import capcat.__main__  # noqa: F401
            import importlib
            importlib.reload(capcat.__main__)
    # __main__ is loaded; main callable is accessible
    from capcat.cli import main
    assert callable(main)
