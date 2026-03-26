"""
Verify that config-driven sources (bbc, guardian, ieee) route through the new
source system, not the legacy _process_article_generic path.
"""
import importlib.util
import pathlib
import sys
import traceback

import pytest
from capcat.core.unified_source_processor import UnifiedSourceProcessor
from capcat.core.source_configs import is_source_configured


def test_bbc_in_new_system():
    """BBC must be routed through the new source system."""
    usp = UnifiedSourceProcessor()
    assert usp._is_source_in_new_system("bbc"), \
        "BBC must be in new system — ConfigDrivenSource auto-registration failed"


def test_guardian_in_new_system():
    """Guardian must be routed through the new source system."""
    usp = UnifiedSourceProcessor()
    assert usp._is_source_in_new_system("guardian"), \
        "Guardian must be in new system"


def test_ieee_in_new_system():
    """IEEE must be routed through the new source system."""
    usp = UnifiedSourceProcessor()
    assert usp._is_source_in_new_system("ieee"), \
        "IEEE must be in new system"


def test_hn_source_loads_directly():
    """Diagnostic: load hn/source.py exactly as _load_custom_source does — surfaces the real error."""
    import capcat
    capcat_root = pathlib.Path(capcat.__file__).parent
    source_file = capcat_root / "sources" / "builtin" / "custom" / "hn" / "source.py"
    module_name = "sources.custom.hn.source"
    spec = importlib.util.spec_from_file_location(module_name, source_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        pytest.fail(f"hn/source.py failed to import:\n{traceback.format_exc()}")


def test_hn_in_new_system():
    """HN must be routed through the new source system."""
    usp = UnifiedSourceProcessor()
    if not usp._is_source_in_new_system("hn"):
        available = sorted(usp.new_source_factory.get_available_sources()) if usp.new_source_factory else []
        pytest.fail(f"HN must be in new system. Sources actually loaded: {available}")



def test_lb_in_new_system():
    """Lobsters must be routed through the new source system."""
    usp = UnifiedSourceProcessor()
    assert usp._is_source_in_new_system("lb"), \
        "Lobsters must be in new system"


def test_all_configured_sources_in_new_system():
    """
    Every source returned by is_source_configured() must also be in the new registry.
    This is the invariant that gates legacy path deletion.
    """
    usp = UnifiedSourceProcessor()
    from capcat.core.source_configs import SOURCE_CONFIGURATIONS
    legacy_names = list(SOURCE_CONFIGURATIONS.keys())

    missing = [name for name in legacy_names if not usp._is_source_in_new_system(name)]
    assert missing == [], (
        f"Sources in legacy config but not in new registry: {missing}\n"
        "These must be migrated before the legacy adapter chain can be deleted."
    )


def test_news_source_article_fetcher_importable_from_article_fetcher():
    """NewsSourceArticleFetcher must be importable from article_fetcher after migration."""
    from capcat.core.article_fetcher import NewsSourceArticleFetcher
    assert NewsSourceArticleFetcher is not None
