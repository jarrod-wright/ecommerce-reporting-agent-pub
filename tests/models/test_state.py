def test_reporting_agent_state_instantiation():
    from agent.models.state import ReportingAgentState

    # Test data for report configuration
    report_config = {
        "output_format": "json",
        "include_metrics": True,
        "timestamp": "2025-08-23T10:00:00Z",
    }

    # This should create an instance with valid config
    state = ReportingAgentState(report_config=report_config)
    assert state.report_config == report_config
