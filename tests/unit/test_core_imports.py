"""Verify all core modules import without errors."""
import importlib
import pkgutil
import pytest


def test_core_modules_importable():
    """All capcat.core modules must import cleanly after migration."""
    import capcat.core
    errors = []
    for _importer, modname, _ispkg in pkgutil.walk_packages(
        path=capcat.core.__path__,
        prefix="capcat.core.",
        onerror=lambda x: None,
    ):
        try:
            importlib.import_module(modname)
        except Exception as exc:
            errors.append(f"{modname}: {exc}")
    assert not errors, "Import failures:\n" + "\n".join(errors)
