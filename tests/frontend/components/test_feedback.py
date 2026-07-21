from unittest.mock import patch


def test_display_success_message():
    from streamlit_app.components.feedback import display_success_message

    with patch('streamlit_app.components.feedback.st.success') as mock_success:
        display_success_message("Test message")
        mock_success.assert_called_once_with("✅ **Success:** Test message", icon="✅")


def test_display_error_message():
    from streamlit_app.components.feedback import display_error_message

    with patch('streamlit_app.components.feedback.st.error') as mock_error:
        display_error_message("Test error")
        mock_error.assert_called_once_with("❌ **Error:** Test error", icon="❌")
