from unittest.mock import patch


class MockSessionState:
    def __init__(self):
        self._data = {}

    def __contains__(self, key):
        return key in self._data

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value


def test_initialize_session_state_creates_keys():
    from streamlit_app.session_state import initialize_session_state

    mock_session_state = MockSessionState()

    with patch('streamlit_app.session_state.st.session_state', mock_session_state):
        initialize_session_state()

        # Assert that the report_bytes key now exists
        assert "report_bytes" in mock_session_state
