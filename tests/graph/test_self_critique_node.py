"""Tests for self_critique_node function."""

from unittest.mock import Mock, patch

from agent.graph.self_critique_node import CritiqueReport, self_critique_node
from agent.models.state import ReportingAgentState


def test_self_critique_node_success():
    """Test self_critique_node processes insights and returns confidence scores."""

    # Create a sample state with processed data and generated insights
    state = ReportingAgentState(
        report_config={"date_range": "2024-01-01 to 2024-01-31"},
        processed_dataframe_json='[{"product": "Widget A", "revenue": 1000}]',
        generated_insights={
            "summary": "Revenue peaked on January 15th with $1000 from Widget A sales.",
            "key_metrics": {"total_revenue": 1000, "product_count": 1},
            "recommendations": ["Focus on Widget A marketing expansion"],
            "data_quality_notes": "Complete data with no anomalies detected",
        },
    )

    # Create mock critique output as CritiqueReport
    mock_critique = CritiqueReport(
        confidence_score=0.88,
        critique=(
            "The insights are well-grounded in the data and clearly presented. "
            "Recommendations are actionable though could benefit from specificity."
        ),
    )

    # Mock the LLM client and factory using Agnostic Factory Testing Protocol
    mock_client = Mock()
    mock_client.generate_structured_output.return_value = mock_critique

    with patch(
        "agent.graph.self_critique_node.get_llm_client_for_role"
    ) as mock_factory:
        mock_factory.return_value = mock_client

        result = self_critique_node(state)

        # Assert factory was called with the correct challenger role
        mock_factory.assert_called_once_with("challenger")

        # Assert returned dictionary contains expected keys and values
        assert "confidence_score" in result
        assert "critique" in result
        assert result["confidence_score"] == 0.88
        assert result["critique"] == (
            "The insights are well-grounded in the data and clearly presented. "
            "Recommendations are actionable though could benefit from specificity."
        )
