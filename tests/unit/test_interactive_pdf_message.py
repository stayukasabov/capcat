"""Test that the PDF informational message is printed before the prompt."""
from unittest.mock import patch, MagicMock


def test_pdf_info_message_printed_before_prompt(capsys):
    """
    An informational message about PDF download speed and config must be
    printed before the questionary.confirm prompt is shown.
    """
    with patch("capcat.core.interactive.questionary") as mock_q, \
         patch("capcat.core.interactive.suppress_logging"), \
         patch("capcat.cli._dispatch"):
        mock_confirm = MagicMock()
        mock_confirm.ask.return_value = False
        mock_q.confirm.return_value = mock_confirm

        from capcat.core.interactive import _confirm_and_execute
        try:
            _confirm_and_execute(action="fetch", selection=["hn"], generate_html=False)
        except Exception:
            pass

    captured = capsys.readouterr()
    assert "significant" in captured.out.lower(), (
        "Message about PDF download speed must be printed before the prompt"
    )
    assert "Global-settings.yaml" in captured.out, (
        "Message must reference Global-settings.yaml so users know where to configure"
    )
