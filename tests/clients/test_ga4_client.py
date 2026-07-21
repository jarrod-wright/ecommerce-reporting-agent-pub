from agent.clients.ga4_client import GA4Client


def test_ga4_client_initialization():
    mock_credentials_json_str = (
        '{"type": "service_account", "project_id": "test-project"}'
    )

    client = GA4Client(credentials_json_str=mock_credentials_json_str)

    assert client is not None


def test_fetch_sessions_data_success(mocker):
    """Test successful fetching of sessions data from GA4 API."""
    mock_credentials_json_str = (
        '{"type": "service_account", "project_id": "test-project"}'
    )

    # Mock the service account credentials
    mock_service_account = mocker.patch("agent.clients.ga4_client.service_account")
    mock_credentials = mocker.MagicMock()
    mock_service_account.Credentials.from_service_account_info.return_value = (
        mock_credentials
    )

    # Mock the Google Analytics Data Client
    mock_analytics_client = mocker.patch(
        "agent.clients.ga4_client.BetaAnalyticsDataClient"
    )

    # Create mock GA4 API response structure
    mock_row1 = mocker.MagicMock()
    mock_row1.dimension_values = [
        mocker.MagicMock(value="2024-01-15"),
        mocker.MagicMock(value="desktop"),
    ]
    mock_row1.metric_values = [
        mocker.MagicMock(value="1250"),
        mocker.MagicMock(value="980"),
    ]

    mock_row2 = mocker.MagicMock()
    mock_row2.dimension_values = [
        mocker.MagicMock(value="2024-01-15"),
        mocker.MagicMock(value="mobile"),
    ]
    mock_row2.metric_values = [
        mocker.MagicMock(value="890"),
        mocker.MagicMock(value="720"),
    ]

    mock_response = mocker.MagicMock()
    mock_response.rows = [mock_row1, mock_row2]

    # Configure the mock client instance to return our test data
    mock_client_instance = mock_analytics_client.return_value
    mock_client_instance.run_report.return_value = mock_response

    # Create GA4Client and call fetch_sessions_data
    client = GA4Client(credentials_json_str=mock_credentials_json_str)
    result = client.fetch_sessions_data(
        property_id="123456789", start_date="2024-01-15", end_date="2024-01-15"
    )

    # Assert that the returned data matches expected format
    expected_data = [
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
    assert result == expected_data

    # Verify that the Google Analytics client was instantiated and called correctly
    mock_analytics_client.assert_called_once()
    mock_client_instance.run_report.assert_called_once()
