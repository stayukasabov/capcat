"""Regression test — Accept-Encoding must not advertise brotli (dep removed)."""
from capcat.core.session_pool import SessionPool


def test_accept_encoding_excludes_brotli():
    """Session must not advertise br — brotli dep is removed."""
    pool = SessionPool()
    session = pool.get_session("test_source")
    enc = session.headers.get("Accept-Encoding", "")
    assert "br" not in enc, f"Session advertises brotli but dep is removed: {enc}"
    assert "gzip" in enc
