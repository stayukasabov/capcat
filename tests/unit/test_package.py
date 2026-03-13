def test_package_imports():
    import capcat
    assert hasattr(capcat, "__version__")
    assert capcat.__version__ == "1.0.0"


def test_main_module_callable():
    from capcat.cli import main
    assert callable(main)
