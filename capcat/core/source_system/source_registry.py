"""Stub: replaced by Task 2.2 migration."""


class _StubRegistry:
    """Minimal stub so modules importing this don't crash at load time."""

    def discover_sources(self):
        return {}

    def reload_sources(self):
        pass

    def get_source(self, name):
        return None


def get_source_registry():
    return _StubRegistry()
