# streamlit_app/components/feedback.py

import streamlit as st


def display_success_message(message: str):
    """Displays a standardized success message."""
    st.success(f"✅ **Success:** {message}", icon="✅")


def display_error_message(message: str):
    """Displays a standardized error message."""
    st.error(f"❌ **Error:** {message}", icon="❌")
