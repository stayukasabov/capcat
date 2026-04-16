"""Test that the PDF informational message is printed before the prompt."""
from unittest.mock import patch, MagicMock


def test_pdf_info_message_printed_before_prompt(capsys):
    """
    An informational message about per-source PDF config must be
    printed before the questionary.select prompt is shown.
    """
    with patch("capcat.core.interactive.questionary") as mock_q, \
         patch("capcat.core.interactive.suppress_logging"), \
         patch("capcat.cli._dispatch"):
        mock_select = MagicMock()
        mock_select.ask.return_value = "no"
        mock_q.select.return_value = mock_select
        mock_q.Choice = MagicMock(side_effect=lambda label, value: value)

        from capcat.core.interactive import _confirm_and_execute
        try:
            _confirm_and_execute(action="fetch", selection=["hn"], generate_html=False)
        except Exception:
            pass

    captured = capsys.readouterr()
    assert "download_pdfs" in captured.out, (
        "Info block must mention download_pdfs so users know the YAML key"
    )
    assert "Config/sources/" in captured.out, (
        "Info block must reference Config/sources/ so users know where to configure"
    )
