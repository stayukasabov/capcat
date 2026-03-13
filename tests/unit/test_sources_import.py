from pathlib import Path


def test_builtin_sources_package_importable():
    """capcat.sources.builtin must be importable after migration."""
    import capcat.sources.builtin
    assert capcat.sources.builtin is not None


def test_specialized_sources_dict_populated():
    """SPECIALIZED_SOURCES must be populated with real source entries."""
    from capcat.sources.specialized import SPECIALIZED_SOURCES
    assert len(SPECIALIZED_SOURCES) > 0, "SPECIALIZED_SOURCES is empty"
    # Twitter/X and YouTube must be present
    source_ids = list(SPECIALIZED_SOURCES.keys())
    assert any("twitter" in sid or "x.com" in sid for sid in source_ids), \
        f"No Twitter source found in {source_ids}"


def test_builtin_yaml_configs_present():
    """YAML source configs must ship inside the package."""
    import capcat.sources.builtin
    package_dir = Path(capcat.sources.builtin.__file__).parent
    configs_dir = package_dir / "config_driven" / "configs"
    assert configs_dir.exists(), f"configs dir not found at {configs_dir}"
    yaml_files = list(configs_dir.glob("*.yaml")) + list(configs_dir.glob("*.yml"))
    assert len(yaml_files) > 0, "No YAML configs found in builtin configs dir"
