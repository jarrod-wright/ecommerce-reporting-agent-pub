# streamlit_app/streamlit_config.py

import streamlit as st


def configure_page():
    """Sets the page configuration and injects custom CSS for the app."""

    # --- Page Config ---
    st.set_page_config(
        page_title="AI Software Factory | E-commerce BI Agent",
        layout="wide",
        csp={
            "default-src": "'self'",
            "img-src": "'self' data:",
            "script-src": "'self' 'unsafe-inline'",
            "style-src": "'self' 'unsafe-inline'",
            "frame-ancestors": "'none'",
        },
    )

    # --- Custom CSS Injection ---
    # This injects our custom font and other styles.
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600&display=swap');
            
            /* General Body Font */
            html, body, [class*="st-"] {
                font-family: 'Inter', sans-serif;
            }

            /* Title Font */
            h1 {
                font-family: 'Poppins', sans-serif;
                font-weight: 600;
                letter-spacing: -0.5px;
            }

            /* Header Font */
            h2 {
                font-family: 'Poppins', sans-serif;
                font-weight: 500;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
