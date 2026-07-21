"""Tests for start_node function."""

from agent.graph.start_node import start_node
from agent.models.state import ReportingAgentState


def test_start_node_success():
    state = ReportingAgentState(
        report_config={
            "date_range": "2024-01-01 to 2024-01-31",
            "report_title": "Monthly Analytics Report",
        }
    )

    result = start_node(state)

    assert "error_message" not in result


def test_start_node_failure_missing_config():
    state = ReportingAgentState(report_config={})

    result = start_node(state)

    assert "error_message" in result
