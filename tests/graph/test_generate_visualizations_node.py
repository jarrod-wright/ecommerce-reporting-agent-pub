"""Tests for generate_visualizations_node function."""

import json

from agent.graph.generate_visualizations_node import generate_visualizations_node
from agent.models.state import ReportingAgentState


def test_generate_visualizations_node_success(mocker):
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

    # Mock plotly.graph_objects.Figure.to_image to return mock bytes
    mock_to_image = mocker.patch("plotly.graph_objects.Figure.to_image")
    mock_to_image.return_value = b"mock_image_bytes"

    # Create state with processed DataFrame JSON
    state = ReportingAgentState(
        report_config={
            "date_range": "2024-01-01 to 2024-01-31",
            "report_title": "Monthly Analytics Report",
        },
        processed_dataframe_json=processed_dataframe_json,
    )

    # Call the generate_visualizations_node function
    result = generate_visualizations_node(state)

    # Assert that the result contains visualization_filepaths
    assert "visualization_filepaths" in result

    # Assert that visualization_filepaths is a list containing at least one string
    assert isinstance(result["visualization_filepaths"], list)
    assert len(result["visualization_filepaths"]) >= 1
    assert all(isinstance(path, str) for path in result["visualization_filepaths"])

    # Assert that the plotly Figure.to_image mock was called
    mock_to_image.assert_called()
