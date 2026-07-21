"""Tests for fetch_data_node function."""

import pytest

from agent.graph.fetch_data_node import fetch_data_node
from agent.models.state import ReportingAgentState


@pytest.mark.asyncio
async def test_fetch_data_node_success(mocker):
    # Mock the LangChain tools
    mock_shopify_orders = [
        {"id": 1001, "total_price": "150.00", "created_at": "2024-01-15"},
        {"id": 1002, "total_price": "275.50", "created_at": "2024-01-20"},
    ]
    mock_ga4_sessions = [
        {"session_id": "s001", "page_views": 5, "duration": 300},
        {"session_id": "s002", "page_views": 8, "duration": 480},
    ]

    # Mock the ainvoke methods to return coroutines
    mock_shopify_tool = mocker.patch("agent.graph.fetch_data_node.get_shopify_orders")
    mock_shopify_tool.ainvoke = mocker.AsyncMock(return_value=mock_shopify_orders)

    mock_ga4_tool = mocker.patch("agent.graph.fetch_data_node.get_ga4_sessions")
    mock_ga4_tool.ainvoke = mocker.AsyncMock(return_value=mock_ga4_sessions)

    # Create initial state
    state = ReportingAgentState(
        report_config={
            "date_range": "2024-01-01 to 2024-01-31",
            "report_title": "Monthly Analytics Report",
        }
    )

    # Call the node function
    result = await fetch_data_node(state)

    # Assert the returned data matches our mocks
    assert "raw_shopify_data" in result
    assert "raw_ga4_data" in result
    assert result["raw_shopify_data"] == mock_shopify_orders
    assert result["raw_ga4_data"] == mock_ga4_sessions
