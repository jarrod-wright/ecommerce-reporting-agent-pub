def test_theme_defines_required_constants():
    from streamlit_app.theme import COLORS, FONTS

    assert isinstance(COLORS, dict)
    assert "PRIMARY" in COLORS

    assert isinstance(FONTS, dict)
    assert "TITLE" in FONTS
