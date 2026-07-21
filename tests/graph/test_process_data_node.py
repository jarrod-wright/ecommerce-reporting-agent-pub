"""Tests for process_data_node function."""

import json

import polars as pl

from agent.graph.process_data_node import process_data_node
from agent.models.state import ReportingAgentState


def test_process_data_node_success():
    # Create sample raw data
    raw_shopify_data = [
        {
            "id": 1001,
            "total_price": "150.00",
            "created_at": "2024-01-15",
            "status": "fulfilled",
        },
        {
            "id": 1002,
            "total_price": "275.50",
            "created_at": "2024-01-20",
            "status": "pending",
        },
        {
            "id": 1003,
            "total_price": "99.99",
            "created_at": "2024-01-25",
            "status": "fulfilled",
        },
    ]

    raw_ga4_data = [
        {"session_id": "s001", "page_views": 5, "duration": 300, "date": "2024-01-15"},
        {"session_id": "s002", "page_views": 8, "duration": 480, "date": "2024-01-16"},
        {"session_id": "s003", "page_views": 3, "duration": 180, "date": "2024-01-20"},
    ]

    # Create state with raw data
    state = ReportingAgentState(
        report_config={
            "date_range": "2024-01-01 to 2024-01-31",
            "report_title": "Monthly Analytics Report",
        },
        raw_shopify_data=raw_shopify_data,
        raw_ga4_data=raw_ga4_data,
    )

    # Call the process_data_node function
    result = process_data_node(state)

    # Assert that the result contains processed_dataframe_json
    assert "processed_dataframe_json" in result

    # Assert that the value is a valid JSON string
    processed_json = result["processed_dataframe_json"]
    assert isinstance(processed_json, str)

    # Deserialize and validate as Polars DataFrame
    df_data = json.loads(processed_json)
    df = pl.DataFrame(df_data)

    # Assert expected columns exist (these would be the combined/processed columns)
    expected_columns = ["date", "shopify_revenue", "ga4_sessions", "page_views"]
    for col in expected_columns:
        assert col in df.columns

    # Assert data types are appropriate
    assert df["date"].dtype == pl.String or df["date"].dtype == pl.Date
    assert df["shopify_revenue"].dtype in [pl.Float64, pl.Float32]
    assert df["ga4_sessions"].dtype in [pl.Int64, pl.Int32]
    assert df["page_views"].dtype in [pl.Int64, pl.Int32]
