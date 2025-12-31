import pytest
import sys
from unittest.mock import patch, MagicMock, call

import cli
from core.exceptions import NetworkError

# --- Test Cases ---

@patch('cli.RssFeedIntrospector')
@patch('cli.SourceConfigGenerator')
@patch('cli.BundleManager')
@patch('cli.run_capcat_fetch')
@patch('questionary.text')
@patch('questionary.select')
@patch('questionary.confirm')
def test_add_source_happy_path(
    mock_confirm, mock_select, mock_text, mock_run_fetch,
    mock_bundle_manager, mock_config_generator, mock_introspector
):
    """
    Test 4.1 (Happy Path): Tests the entire add-source workflow with valid inputs.
    """
    # --- Mock Setup ---
    # 1. RssFeedIntrospector
    mock_feed = MagicMock()
    mock_feed.feed_title = "Ars Technica"
    mock_feed.base_url = "https://arstechnica.com/"
    mock_introspector.return_value = mock_feed

    # 2. BundleManager
    mock_bm_instance = MagicMock()
    mock_bm_instance.get_bundle_names.return_value = ["tech", "science"]
    mock_bundle_manager.return_value = mock_bm_instance

    # 3. SourceConfigGenerator
    mock_cg_instance = MagicMock()
    mock_config_generator.return_value = mock_cg_instance

    # 4. User Input (questionary)
    # Correctly mock the chained .ask() call
    mock_text.return_value.ask.side_effect = ["arstechnica"]
    mock_select.return_value.ask.side_effect = ["tech", "tech"]
    mock_confirm.return_value.ask.side_effect = [True, True]

    # 5. Final test command
    mock_run_fetch.return_value = True

    # --- Execution ---
    cli.add_source("https://arstechnica.com/feed/")

    # --- Assertions ---
    mock_introspector.assert_called_once_with("https://arstechnica.com/feed/")

    mock_config_generator.assert_called_once()
    generator_args = mock_config_generator.call_args[0][0]
    assert generator_args['source_id'] == 'arstechnica'
    assert generator_args['display_name'] == 'Ars Technica'
    assert generator_args['category'] == 'tech'

    mock_cg_instance.generate_and_save.assert_called_once()

    mock_bundle_manager.assert_called_once()
    mock_bm_instance.add_source_to_bundle.assert_called_once_with("arstechnica", "tech")

    mock_run_fetch.assert_called_once_with("arstechnica", 1)

@patch('cli.RssFeedIntrospector')
@patch('builtins.print')
def test_add_source_bad_url(mock_print, mock_introspector):
    """
    Test 4.2 (Failure Path - Bad URL): Tests that a network error is handled gracefully.
    """
    # --- Mock Setup ---
    url = "http://badurl.invalid"
    mock_introspector.side_effect = NetworkError(url, original_error=Exception("Test error"))

    # --- Execution ---
    with pytest.raises(SystemExit) as e:
        cli.add_source(url)

    # --- Assertions ---
    assert e.type == SystemExit
    assert e.value.code == 1

    # Check that a user-friendly error message was printed to stderr
    expected_error_msg = f"Error: Could not access {url}. The server may be temporarily unavailable or the link may be broken."
    mock_print.assert_any_call(expected_error_msg, file=sys.stderr)