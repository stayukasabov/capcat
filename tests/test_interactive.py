import unittest
from unittest.mock import patch, call
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capcat import run_app
from core.interactive import (
    start_interactive_mode,
    _handle_bundle_flow,
    _handle_fetch_flow,
    _handle_single_source_flow,
    _handle_single_url_flow,
    _prompt_for_html,
    _confirm_and_execute,
)

class TestInteractiveMode(unittest.TestCase):

    @patch('core.interactive.start_interactive_mode')
    def test_catch_command_triggers_interactive_mode(self, mock_start_interactive_mode):
        with patch.object(sys, 'argv', ['capcat', 'catch']):
            try:
                run_app()
            except SystemExit:
                pass
        mock_start_interactive_mode.assert_called_once()

    @patch('questionary.select')
    def test_main_menu_exit(self, mock_select):
        mock_select.return_value.ask.return_value = 'exit'
        start_interactive_mode()
        mock_select.assert_called_once()

    @patch('core.interactive._handle_bundle_flow')
    @patch('questionary.select')
    def test_main_menu_bundle_flow(self, mock_select, mock_handle_bundle_flow):
        mock_select.return_value.ask.return_value = 'bundle'
        start_interactive_mode()
        mock_handle_bundle_flow.assert_called_once()

    @patch('cli.get_available_bundles')
    @patch('core.interactive._prompt_for_html')
    @patch('questionary.select')
    def test_handle_bundle_flow(self, mock_select, mock_prompt_html, mock_get_bundles):
        mock_get_bundles.return_value = {'tech': {'sources': ['hn', 'lb'], 'description': 'Tech news'}}
        mock_select.return_value.ask.return_value = 'tech'
        _handle_bundle_flow()
        mock_prompt_html.assert_called_once_with('bundle', 'tech')

    @patch('core.interactive._confirm_and_execute')
    @patch('questionary.confirm')
    def test_prompt_for_html(self, mock_confirm, mock_confirm_and_execute):
        mock_confirm.return_value.ask.return_value = True
        _prompt_for_html('bundle', 'tech')
        mock_confirm_and_execute.assert_called_once_with('bundle', 'tech', True)

    @patch('subprocess.run')
    @patch('questionary.confirm')
    def test_confirm_and_execute_bundle(self, mock_confirm, mock_subprocess):
        mock_confirm.return_value.ask.return_value = True
        _confirm_and_execute('bundle', 'tech', True)
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run_capcat.py'))
        mock_subprocess.assert_called_once_with(['python3', script_path, 'bundle', 'tech', '--html'])

if __name__ == '__main__':
    unittest.main()