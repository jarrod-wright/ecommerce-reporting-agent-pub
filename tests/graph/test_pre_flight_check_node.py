"""Tests for pre_flight_check_node function."""

from unittest.mock import Mock, patch

from agent.graph.pre_flight_check_node import DataQualityReport, pre_flight_check_node
from agent.models.state import ReportingAgentState


def test_pre_flight_check_node_success():
    """Test pre_flight_check_node processes valid data and returns scores."""

    # Create a sample state with valid processed_dataframe_json
    state = ReportingAgentState(
        report_config={"date_range": "2024-01-01 to 2024-01-31"},
        processed_dataframe_json='[{"product": "Widget A", "revenue": 1000}]',
    )

    # Create mock structured output as DataQualityReport
    mock_assessment = DataQualityReport(
        data_quality_score=0.95,
        justification="Data is clean, complete, and well-structured.",
    )

    # Mock the LLM client and factory
    mock_client = Mock()
    mock_client.generate_structured_output.return_value = mock_assessment

    with patch("agent.graph.pre_flight_check_node.get_llm_client") as mock_factory:
        mock_factory.return_value = mock_client

        result = pre_flight_check_node(state)

        # Assert returned dictionary contains expected keys and values
        assert "data_quality_score" in result
        assert "data_quality_justification" in result
        assert result["data_quality_score"] == 0.95
        assert result["data_quality_justification"] == (
            "Data is clean, complete, and well-structured."
        )
