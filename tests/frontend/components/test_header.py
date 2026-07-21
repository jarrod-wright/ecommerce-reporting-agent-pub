def test_render_header_exists_and_is_callable():
    from streamlit_app.components.header import render_header

    assert callable(render_header)
