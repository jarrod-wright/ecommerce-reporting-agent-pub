from unittest.mock import patch


def test_main_function_exists():
    from streamlit_app.app import main
    assert callable(main)


def test_main_orchestrates_components():
    with patch('streamlit_app.app.configure_page') as mock_configure, \
         patch('streamlit_app.app.initialize_session_state') as mock_initialize, \
         patch('streamlit_app.app.render_header') as mock_header, \
         patch('streamlit_app.app.render_main_interface') as mock_interface:

        from streamlit_app.app import main

        main()

        # Assert that each component function was called exactly once
        mock_configure.assert_called_once()
        mock_initialize.assert_called_once()
        mock_header.assert_called_once()
        mock_interface.assert_called_once()
