# streamlit_app/components/header.py

import streamlit as st


def render_header():
    """Renders the main application header and title."""

    st.title("E-commerce Performance Report Agent")
    st.subheader("Your AI-powered business intelligence partner for Shopify & GA4.")
    st.divider()
