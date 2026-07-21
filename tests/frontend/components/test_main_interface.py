from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from agent.models.insights import ReportInsights


def test_render_main_interface_calls_api_on_click():

    with patch(
        'streamlit_app.components.main_interface.trigger_report_generation'
    ) as mock_trigger:
        # Use AppTest pattern to simulate component interaction
        at = AppTest.from_string("""
import streamlit as st
from streamlit_app.components.main_interface import render_main_interface

render_main_interface()
""")

        at.run()

        # Simulate clicking the primary button
        at.button[0].click().run()

        # Assert that the API function was called exactly once
        mock_trigger.assert_called_once()


def test_render_main_interface_calls_render_results_dashboard_on_success():
    """Test that render_main_interface calls render_results_dashboard when report is successfully generated."""

    with patch('streamlit_app.components.main_interface.trigger_report_generation') as mock_trigger, \
         patch('streamlit_app.components.main_interface.render_results_dashboard') as mock_render_dashboard:

        # Configure mock to return successful report bytes
        mock_trigger.return_value = b"fake_pdf_bytes"

        # Use AppTest pattern to simulate component interaction
        at = AppTest.from_string("""
import streamlit as st
from streamlit_app.components.main_interface import render_main_interface

render_main_interface()
""")

        at.run()

        # Simulate clicking the primary button
        at.button[0].click().run()

        # Assert that render_results_dashboard was called at least once after successful API call
        # The function should be called with the ReportInsights object created in main_interface
        assert mock_render_dashboard.call_count >= 1

        # Verify the call was made with a ReportInsights object
        call_args = mock_render_dashboard.call_args[0][0]
        assert isinstance(call_args, ReportInsights)
        assert call_args.summary == "Strong quarterly performance with significant growth in key metrics"
