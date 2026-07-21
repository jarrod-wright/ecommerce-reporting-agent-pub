"""Tests for handle_error_node function."""

from agent.graph.handle_error_node import handle_error_node
from agent.models.state import ReportingAgentState


def test_handle_error_node(mocker):
    # Mock the structlog logger
    mock_logger = mocker.MagicMock()
    mocker.patch(
        "agent.graph.handle_error_node.structlog.get_logger", return_value=mock_logger
    )

    # Create state with error message
    sample_error = "Failed to connect to Shopify API: Connection timeout"
    state = ReportingAgentState(
        report_config={
            "date_range": "2024-01-01 to 2024-01-31",
            "report_title": "Monthly Analytics Report",
        },
        error_message=sample_error,
    )

    # Call the handle_error_node function
    result = handle_error_node(state)

    # Assert that the logger's error method was called
    mock_logger.error.assert_called_once()

    # Assert that the logged message contains the sample error string
    call_args = mock_logger.error.call_args
    assert sample_error in str(call_args)

    # Assert that the function returns an empty dictionary
    assert result == {}
