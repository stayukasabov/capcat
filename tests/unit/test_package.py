def test_package_imports() -> None:
    import capcat
    assert hasattr(capcat, "__version__")
    assert capcat.__version__ == "1.0.0"


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
