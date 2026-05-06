"""bundle default_count must be removed - per-source article_count is the single truth."""


def test_bundle_config_has_no_default_count():
    from capcat.core.config.source_base import BundleConfig
    assert not hasattr(BundleConfig, "default_count"), (
        "BundleConfig still has default_count - remove it"
    )


def test_bundles_yml_has_no_default_count():
    import yaml
    from pathlib import Path
    bundles_path = Path("capcat/sources/builtin/bundles.yml")
    data = yaml.safe_load(bundles_path.read_text())
    for bundle_id, bundle_data in data.get("bundles", {}).items():
        assert "default_count" not in bundle_data, (
            f"bundles.yml bundle '{bundle_id}' still has default_count"
        )
