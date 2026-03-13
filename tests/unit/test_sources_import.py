def test_builtin_sources_package_importable():
    """capcat.sources.builtin must be importable after migration."""
    import capcat.sources.builtin
    assert capcat.sources.builtin is not None
