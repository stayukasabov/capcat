"""Regression test - ConfigManager must find Config/capcat.yml in vault layout.

The vault stores capcat.yml at Config/capcat.yml (not at the project root).
_load_default_config_files must check Config/capcat.yml before falling back
to the CWD root, so source_overrides from the sources list are populated.
"""
import os
import yaml


class TestConfigManagerFindsVaultCapcatYml:
    def test_source_overrides_loaded_from_config_subdir(self, tmp_path):
        """Config/capcat.yml sources list must populate source_overrides."""
        cfg_dir = tmp_path / "Config"
        cfg_dir.mkdir()
        (cfg_dir / "capcat.yml").write_text(yaml.dump({
            "sources": [{"name": "hn", "article_count": 5}],
            "bundles": {},
        }))

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            from capcat.core.config import ConfigManager
            mgr = ConfigManager()
            cfg = mgr.load_config()
        finally:
            os.chdir(old_cwd)

        assert cfg.source_overrides.get("hn", {}).get("article_count") == 5, (
            f"Expected source_overrides['hn']['article_count'] == 5, got: {cfg.source_overrides}"
        )

    def test_root_capcat_yml_still_works(self, tmp_path):
        """capcat.yml at project root must still be found as fallback."""
        (tmp_path / "capcat.yml").write_text(yaml.dump({
            "sources": [{"name": "lb", "article_count": 7}],
            "bundles": {},
        }))

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            from capcat.core.config import ConfigManager
            mgr = ConfigManager()
            cfg = mgr.load_config()
        finally:
            os.chdir(old_cwd)

        assert cfg.source_overrides.get("lb", {}).get("article_count") == 7

    def test_config_subdir_takes_precedence_over_root(self, tmp_path):
        """Config/capcat.yml must be preferred over capcat.yml at root."""
        cfg_dir = tmp_path / "Config"
        cfg_dir.mkdir()
        (cfg_dir / "capcat.yml").write_text(yaml.dump({
            "sources": [{"name": "hn", "article_count": 3}],
        }))
        (tmp_path / "capcat.yml").write_text(yaml.dump({
            "sources": [{"name": "hn", "article_count": 99}],
        }))

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            from capcat.core.config import ConfigManager
            mgr = ConfigManager()
            cfg = mgr.load_config()
        finally:
            os.chdir(old_cwd)

        assert cfg.source_overrides.get("hn", {}).get("article_count") == 3, (
            "Config/capcat.yml (3) must win over root capcat.yml (99)"
        )
