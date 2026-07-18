"""Guards the --json hidden-flag constraint: never shown in help/usage text."""
import io
from contextlib import redirect_stdout

from capcat import cli


def _captured_output(*args):
    stream = io.StringIO()
    with redirect_stdout(stream):
        try:
            cli._dispatch(list(args))
        except SystemExit:
            pass
    return stream.getvalue()


def test_top_level_help_never_mentions_json():
    output = _captured_output("--help")
    assert "--json" not in output
    assert "json" not in output.lower()


def test_fetch_usage_never_mentions_json():
    output = _captured_output("fetch", "--help")
    assert "--json" not in output


def test_bundle_usage_never_mentions_json():
    output = _captured_output("bundle", "--help")
    assert "--json" not in output


def test_single_usage_never_mentions_json():
    output = _captured_output("single", "--help")
    assert "--json" not in output


def test_list_usage_never_mentions_json():
    output = _captured_output("list", "--help")
    assert "--json" not in output
