# streamlit_app/session_state.py

import streamlit as st


def initialize_session_state():
    """Initializes all required keys in the Streamlit session state."""

    if "report_bytes" not in st.session_state:
        st.session_state.report_bytes = None

    # Add other future state keys here
    # if "user_name" not in st.session_state:
    #     st.session_state.user_name = None
