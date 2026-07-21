from agent.tools.ga4_tools import get_ga4_sessions


def test_get_ga4_sessions_tool(mocker):
    """Test the get_ga4_sessions tool function."""
    # Mock environment variables for GA4 credentials
    credentials_json_str = '{"type": "service_account", "project_id": "test-project", "client_email": "test@test.iam.gserviceaccount.com", "token_uri": "https://oauth2.googleapis.com/token"}'
    property_id = "123456789"

    mocker.patch.dict(
        "os.environ",
        {"GA4_CREDENTIALS_JSON": credentials_json_str, "GA4_PROPERTY_ID": property_id},
    )

    # Mock the GA4Client class completely
    mock_ga4_client = mocker.patch("agent.tools.ga4_tools.GA4Client")

    # Configure mock client instance
    mock_client_instance = mock_ga4_client.return_value
    mock_sessions_data = [
        {
            "date": "2024-01-15",
            "device_category": "desktop",
            "sessions": 1250,
            "users": 980,
        },
        {
            "date": "2024-01-15",
            "device_category": "mobile",
            "sessions": 890,
            "users": 720,
        },
    ]
    mock_client_instance.fetch_sessions_data.return_value = mock_sessions_data

    # Test parameters
    start_date = "2024-01-15"
    end_date = "2024-01-15"

    # Call the tool function (using invoke for LangChain tools)
    result = get_ga4_sessions.invoke({"start_date": start_date, "end_date": end_date})

    # Assert GA4Client was instantiated with environment variables
    mock_ga4_client.assert_called_once_with(credentials_json_str=credentials_json_str)

    # Assert fetch_sessions_data method was called with correct arguments
    mock_client_instance.fetch_sessions_data.assert_called_once_with(
        property_id=property_id, start_date=start_date, end_date=end_date
    )

    # Assert the tool returns the expected data
    assert result == mock_sessions_data
