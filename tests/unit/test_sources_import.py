from pathlib import Path


def test_builtin_sources_package_importable():
    """capcat.sources.builtin must be importable after migration."""
    import capcat.sources.builtin
    assert capcat.sources.builtin is not None


def test_url_routing_sources_discoverable():
    """Twitter and YouTube sources must be discoverable via the registry."""
    from capcat.core.source_system.source_registry import SourceRegistry
    reg = SourceRegistry()
    reg.discover_sources()
    sources = reg.get_available_sources()
    assert "twitter" in sources, f"twitter not in {sources}"
    assert "youtube" in sources, f"youtube not in {sources}"


def test_builtin_yaml_configs_present():
    """YAML source configs must ship inside the package."""
    import capcat.sources.builtin
    package_dir = Path(capcat.sources.builtin.__file__).parent
    configs_dir = package_dir / "config_driven" / "configs"
    assert configs_dir.exists(), f"configs dir not found at {configs_dir}"
    yaml_files = list(configs_dir.glob("*.yaml")) + list(configs_dir.glob("*.yml"))
    assert len(yaml_files) > 0, "No YAML configs found in builtin configs dir"
