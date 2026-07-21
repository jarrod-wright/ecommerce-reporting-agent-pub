# streamlit_app/app.py

from .components.header import render_header
from .components.main_interface import render_main_interface
from .session_state import initialize_session_state
from .streamlit_config import configure_page


def main():
    """
    Main function to orchestrate the Streamlit application.
    """
    # 1. Set page config and styles (must be the first Streamlit command)
    configure_page()

    # 2. Initialize all session state keys
    initialize_session_state()

    # 3. Render the header component
    render_header()

    # 4. Render the main interactive component
    render_main_interface()


if __name__ == "__main__":
    main()
