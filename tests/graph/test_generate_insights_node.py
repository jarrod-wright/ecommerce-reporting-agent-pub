"""Tests for generate_insights_node function."""

import json
from unittest.mock import Mock, patch

from agent.graph.generate_insights_node import generate_insights_node
from agent.models.insights import ReportInsights
from agent.models.state import ReportingAgentState


def test_generate_insights_node_success():
    # Create sample processed DataFrame JSON
    sample_df_data = [
        {
            "date": "2024-01-15",
            "shopify_revenue": 425.50,
            "ga4_sessions": 2,
            "page_views": 13,
        },
        {
            "date": "2024-01-16",
            "shopify_revenue": 0.0,
            "ga4_sessions": 1,
            "page_views": 8,
        },
        {
            "date": "2024-01-20",
            "shopify_revenue": 275.50,
            "ga4_sessions": 1,
            "page_views": 3,
        },
        {
            "date": "2024-01-25",
            "shopify_revenue": 99.99,
            "ga4_sessions": 0,
            "page_views": 0,
        },
    ]
    processed_dataframe_json = json.dumps(sample_df_data)

    # Create mock ReportInsights object
    mock_insights = ReportInsights(
        summary="Revenue peaked on January 15th with $425.50 from 2 sessions.",
        key_metrics={
            "total_revenue": 800.99,
            "total_sessions": 4,
            "total_page_views": 24,
            "conversion_rate": 0.167,
        },
        recommendations=[
            "Focus marketing efforts on high-performing days like January 15th",
            "Investigate why January 25th had revenue but no sessions",
        ],
        data_quality_notes="All data appears complete with no missing values",
    )

    # Create mock LLM client that follows the LLMClient interface
    mock_client = Mock()
    mock_client.generate_structured_output.return_value = mock_insights

    # Create state with processed DataFrame JSON
    state = ReportingAgentState(
        report_config={
            "date_range": "2024-01-01 to 2024-01-31",
            "report_title": "Monthly Analytics Report",
        },
        processed_dataframe_json=processed_dataframe_json,
    )

    # Patch the role-based factory function at its point of use
    with patch(
        "agent.graph.generate_insights_node.get_llm_client_for_role"
    ) as mock_factory:
        mock_factory.return_value = mock_client

        # Call the generate_insights_node function
        result = generate_insights_node(state)

        # Assert that the factory was called with the correct role
        mock_factory.assert_called_once_with("primary")

        # Assert that the client's generate_structured_output method was called
        mock_client.generate_structured_output.assert_called_once()

        # Assert that the result contains generated_insights
        assert "generated_insights" in result

        # Assert that the value matches the mocked insights
        assert result["generated_insights"] == mock_insights.model_dump()
