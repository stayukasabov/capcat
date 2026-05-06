"""
Regression tests: stale core/streamlined_comment_processor.py must not exist.

core/streamlined_comment_processor.py is a legacy duplicate of
capcat/core/streamlined_comment_processor.py. It has two problems:
1. Its process_comments_flattened() lacks comment_permalink_fn, so any
   caller using **_HN_SELECTORS raises TypeError at runtime.
2. It exposes GDPR-violating wrapper methods (process_hacker_news_comments_optimized
   etc.) that build profile URLs from usernames instead of using comment permalinks.

The fix is to delete the file. These tests enforce that it stays deleted.
"""
from __future__ import annotations

import importlib
import inspect
import sys


def test_core_streamlined_comment_processor_does_not_exist():
    """core.streamlined_comment_processor must not be importable (file deleted)."""
    for mod in list(sys.modules):
        if "core.streamlined_comment_processor" in mod:
            del sys.modules[mod]

    try:
        importlib.import_module("core.streamlined_comment_processor")
        assert False, (
            "core.streamlined_comment_processor is still importable - "
            "delete core/streamlined_comment_processor.py"
        )
    except (ImportError, ModuleNotFoundError):
        pass  # expected


def test_legacy_wrapper_methods_not_importable_from_core():
    """The GDPR-violating HN wrapper methods must not exist in the core module."""
    gdpr_violating_wrappers = [
        "process_hacker_news_comments_optimized",
        "process_hacker_news_comments_html_optimized",
        "process_lobsters_comments_optimized",
        "process_lobsters_comments_html_optimized",
    ]

    for mod in list(sys.modules):
        if "core.streamlined_comment_processor" in mod:
            del sys.modules[mod]

    try:
        mod = importlib.import_module("core.streamlined_comment_processor")
        cls = getattr(mod, "StreamlinedCommentProcessor", None)
        if cls is not None:
            for method in gdpr_violating_wrappers:
                assert not hasattr(cls, method), (
                    f"GDPR-violating method {method!r} exists on "
                    "core.streamlined_comment_processor.StreamlinedCommentProcessor - "
                    "delete core/streamlined_comment_processor.py"
                )
    except (ImportError, ModuleNotFoundError):
        pass  # module gone - that's the desired state
