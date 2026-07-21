from unittest.mock import patch


def test_configure_page_exists_and_is_callable():
    from streamlit_app.streamlit_config import configure_page

    assert callable(configure_page)


def test_configure_page_sets_strict_content_security_policy():
    """Test that configure_page sets a strict Content Security Policy.

    This test enforces CISO Blue Team Recommendation #2: Establish Frontend
    Security Boundaries by requiring CSP headers to prevent XSS attacks.
    """
    from streamlit_app.streamlit_config import configure_page

    # Patch streamlit.set_page_config at its point of use in the module
    with patch(
        "streamlit_app.streamlit_config.st.set_page_config"
    ) as mock_set_page_config:
        # Call the configure_page function
        configure_page()

        # Assert that set_page_config was called exactly once
        mock_set_page_config.assert_called_once()

        # Get the kwargs from the call
        call_kwargs = mock_set_page_config.call_args.kwargs

        # Assert that csp argument was present
        assert "csp" in call_kwargs, (
            "CSP argument must be present in set_page_config call"
        )

        # Get the CSP value
        csp_value = call_kwargs["csp"]

        # Assert required CSP directives are present
        assert isinstance(csp_value, dict), "CSP value must be a dictionary"
        assert "default-src" in csp_value, "CSP must include default-src directive"
        assert csp_value["default-src"] == "'self'", "CSP default-src must be 'self'"
        assert "script-src" in csp_value, "CSP must include script-src directive"
        assert "'self'" in csp_value["script-src"], "CSP script-src must include 'self'"
