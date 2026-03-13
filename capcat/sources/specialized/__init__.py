"""
Specialized source implementations for platforms like Medium and Substack.
These sources are automatically activated based on URL patterns and provide
optimized handling with platform-specific features.
"""

from .medium.source import MediumSource
from .substack.source import SubstackSource
from .twitter.source import TwitterSource
from .youtube.source import YouTubeSource
from .vimeo.source import VimeoSource

# Registry of specialized sources with their URL matching capabilities
# Order matters - more specific sources should be checked first
SPECIALIZED_SOURCES = {
    "twitter": TwitterSource,
    "youtube": YouTubeSource,
    "vimeo": VimeoSource,
    "substack": SubstackSource,
    "medium": MediumSource,
}


def get_specialized_source_for_url(url: str):
    """
    Determine which specialized source can handle the given URL.

    Args:
        url: The URL to check

    Returns:
        Tuple of (source_class, source_id) if a match is found, (None, None) otherwise
    """
    for source_id, source_class in SPECIALIZED_SOURCES.items():
        if hasattr(
            source_class, "can_handle_url"
        ) and source_class.can_handle_url(url):
            return source_class, source_id

    return None, None


def list_specialized_sources():
    """
    Get a list of all available specialized sources.

    Returns:
        Dict mapping source_id to source_class
    """
    return SPECIALIZED_SOURCES.copy()
