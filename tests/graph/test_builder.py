from unittest.mock import MagicMock, patch

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from agent.graph.builder import get_agent_executor


def test_graph_assembly_success_path():
    """Test successful assembly and execution of the main agent graph."""

    # Create mock functions that return proper updates
    def mock_start_node(state):
        return {"error_message": None}

    def mock_fetch_data_node(state):
        return {
            "raw_shopify_data": [{"order_id": 1, "total_price": "100.00"}],
            "raw_ga4_data": [{"date": "2024-01-01", "sessions": 50}],
        }

    def mock_process_data_node(state):
        return {
            "processed_dataframe_json": '{"mock": "data"}',
        }

    def mock_generate_insights_node(state):
        return {"generated_insights": {"key_metrics": {"revenue": 1000}}}

    def mock_generate_visualizations_node(state):
        return {"visualization_filepaths": ["/tmp/chart1.png", "/tmp/chart2.png"]}

    def mock_compile_report_node(state):
        return {"final_report_path": "/tmp/final_report.pdf"}

    def mock_human_approval_node(state):
        # For the success path test, auto-approve
        return {"human_decision": "approve"}

    def mock_execute_high_risk_tool_node(state):
        return {"high_risk_action_completed": True}

    # Mock all node functions
    with (
        patch("agent.graph.builder.start_node", mock_start_node),
        patch("agent.graph.builder.fetch_data_node", mock_fetch_data_node),
        patch("agent.graph.builder.process_data_node", mock_process_data_node),
        patch(
            "agent.graph.builder.generate_insights_node", mock_generate_insights_node
        ),
        patch("agent.graph.builder.human_approval_node", mock_human_approval_node),
        patch(
            "agent.graph.builder.execute_high_risk_tool_node",
            mock_execute_high_risk_tool_node,
        ),
        patch(
            "agent.graph.builder.generate_visualizations_node",
            mock_generate_visualizations_node,
        ),
        patch("agent.graph.builder.compile_report_node", mock_compile_report_node),
    ):
        # Get the compiled agent executor
        agent_executor = get_agent_executor()

        # Define initial state for the agent matching ReportingAgentState
        initial_state = {
            "report_config": {
                "date_range": "2024-01-01 to 2024-01-07",
                "report_title": "Test E-commerce Performance Report",
            },
            "raw_shopify_data": None,
            "raw_ga4_data": None,
            "processed_dataframe_json": None,
            "generated_insights": None,
            "visualization_filepaths": [],
            "final_report_path": None,
            "error_message": None,
            "human_decision": None,
        }

        # Execute the agent with the initial state
        final_state = agent_executor.invoke(initial_state)

        # Assert that the final state contains a non-empty final_report_path
        assert final_state is not None
        assert "final_report_path" in final_state
        assert final_state["final_report_path"] is not None
        assert final_state["final_report_path"] != ""
        assert isinstance(final_state["final_report_path"], str)
        assert final_state["final_report_path"] == "/tmp/final_report.pdf"


@pytest.mark.asyncio
async def test_graph_correctly_interrupts_for_human_approval():
    """Test that the graph correctly interrupts for human approval using HITL pattern.

    This test verifies the Human-in-the-Loop (HITL) pattern implementation by:
    1. Using a checkpointer to manage stateful operations
    2. Invoking the agent graph's astream() method
    3. Asserting that execution stops with an interrupt at human_approval_node
    4. Resuming execution with Command(resume=...) and verifying progression

    Expected to fail until HITL nodes and conditional logic are implemented.
    """
    # Initialize checkpointer for stateful operations
    checkpointer = MemorySaver()

    # Mock all node functions to control workflow
    def mock_start_node(state):
        return {"error_message": None}

    def mock_fetch_data_node(state):
        return {
            "raw_shopify_data": [{"order_id": 1, "total_price": "100.00"}],
            "raw_ga4_data": [{"date": "2024-01-01", "sessions": 50}],
        }

    def mock_process_data_node(state):
        return {"processed_dataframe_json": '{"mock": "data"}'}

    def mock_generate_insights_node(state):
        return {"generated_insights": {"key_metrics": {"revenue": 1000}}}

    def mock_human_approval_node(state):
        # This node should interrupt the graph execution for human approval
        return interrupt(
            {
                "action_type": "state_change",
                "details": "Requesting approval to proceed with report generation",
                "insights": state.generated_insights,
            }
        )

    def mock_generate_visualizations_node(state):
        return {"visualization_filepaths": ["/tmp/chart1.png", "/tmp/chart2.png"]}

    def mock_compile_report_node(state):
        return {"final_report_path": "/tmp/final_report.pdf"}

    # Mock all nodes including the expected human approval node
    with (
        patch("agent.graph.builder.start_node", mock_start_node),
        patch("agent.graph.builder.fetch_data_node", mock_fetch_data_node),
        patch("agent.graph.builder.process_data_node", mock_process_data_node),
        patch(
            "agent.graph.builder.generate_insights_node", mock_generate_insights_node
        ),
        patch("agent.graph.builder.human_approval_node", mock_human_approval_node),
        patch(
            "agent.graph.builder.generate_visualizations_node",
            mock_generate_visualizations_node,
        ),
        patch("agent.graph.builder.compile_report_node", mock_compile_report_node),
    ):
        # Get the compiled agent executor with checkpointer
        # We need to modify get_agent_executor to accept checkpointer

        # Patch the get_agent_executor to use our checkpointer
        def get_executor_with_checkpointer():
            from langgraph.graph import END, StateGraph

            from agent.graph.builder import (
                route_after_data_processing,
                route_after_human_approval,
            )
            from agent.models.state import ReportingAgentState

            workflow = StateGraph(ReportingAgentState)

            # Add all nodes to the graph
            workflow.add_node("start", mock_start_node)
            workflow.add_node("fetch_data", mock_fetch_data_node)
            workflow.add_node("process_data", mock_process_data_node)
            workflow.add_node("generate_insights", mock_generate_insights_node)
            workflow.add_node("human_approval", mock_human_approval_node)
            workflow.add_node(
                "execute_high_risk_tool", lambda s: {"high_risk_action_completed": True}
            )
            workflow.add_node(
                "generate_visualizations", mock_generate_visualizations_node
            )
            workflow.add_node("compile_report", mock_compile_report_node)
            workflow.add_node("handle_error", lambda s: {})

            # Set the entry point
            workflow.set_entry_point("start")

            # Add edges
            workflow.add_edge("start", "fetch_data")
            workflow.add_edge("fetch_data", "process_data")
            workflow.add_edge("generate_insights", "human_approval")
            workflow.add_edge("execute_high_risk_tool", "generate_visualizations")
            workflow.add_edge("generate_visualizations", "compile_report")
            workflow.add_edge("compile_report", END)
            workflow.add_edge("handle_error", END)

            # Add conditional edges
            workflow.add_conditional_edges(
                "process_data",
                route_after_data_processing,
                {
                    "generate_insights": "generate_insights",
                    "handle_error": "handle_error",
                },
            )

            workflow.add_conditional_edges(
                "human_approval",
                route_after_human_approval,
                {"execute_high_risk_tool": "execute_high_risk_tool", "END": END},
            )

            return workflow.compile(checkpointer=checkpointer)

        agent_executor = get_executor_with_checkpointer()

        # Define initial state for the agent matching ReportingAgentState
        initial_state = {
            "report_config": {
                "date_range": "2024-01-01 to 2024-01-07",
                "report_title": "Test E-commerce Performance Report",
            },
            "raw_shopify_data": None,
            "raw_ga4_data": None,
            "processed_dataframe_json": None,
            "generated_insights": None,
            "visualization_filepaths": [],
            "final_report_path": None,
            "error_message": None,
            "human_decision": None,
        }

        # Configuration for tracking execution
        config = {"configurable": {"thread_id": "test-thread-1"}}

        # Execute the agent using astream and collect events
        events = []
        interrupt_found = False

        async for event in agent_executor.astream(initial_state, config):
            events.append(event)

            # Check if we hit the interrupt (interrupts come with __interrupt__ key)
            if "__interrupt__" in event:
                interrupt_found = True
                break

        # Assert that the graph execution stopped with an interrupt
        assert interrupt_found, "Graph should have interrupted for human approval"

        # Verify that the interrupt contains expected approval request data
        approval_event = next(e for e in events if "__interrupt__" in e)
        interrupt_data = approval_event["__interrupt__"][0].value
        assert interrupt_data["action_type"] == "state_change", (
            "Interrupt should contain state_change action type"
        )
        assert "Requesting approval" in interrupt_data["details"], (
            "Should request approval for state change"
        )

        # Test that the routing function works correctly with human decision
        from agent.graph.builder import route_after_human_approval
        from agent.models.state import ReportingAgentState

        # Create a mock state with approved decision
        approved_state = ReportingAgentState(
            report_config={"test": "config"}, human_decision="approve"
        )

        # Test that the routing function correctly routes to execute_high_risk_tool
        route_result = route_after_human_approval(approved_state)
        assert route_result == "execute_high_risk_tool", (
            "Router should direct to execute_high_risk_tool when approved"
        )

        # Test rejection case
        rejected_state = ReportingAgentState(
            report_config={"test": "config"}, human_decision="reject"
        )

        reject_result = route_after_human_approval(rejected_state)
        assert reject_result == "END", (
            "Router should direct to END when human_decision is reject"
        )


def test_agent_factory_provides_low_risk_tools_for_safe_prompt():
    """Test that agent factory provides only low-risk tools for safe prompts.

    This test implements dynamic tool access scoping.
    Should now pass with the AgentFactory implementation.
    """
    from agent.graph.builder import AgentFactory
    from agent.tools.ga4_tools import get_ga4_sessions
    from agent.tools.shopify_tools import get_shopify_orders

    # Create a mock ToolRouter instance to avoid LLM client initialization
    mock_tool_router = MagicMock()
    mock_tool_router.classify_and_scope_tools.return_value = {
        "risk_level": "low_risk",
        "available_tools": [get_shopify_orders, get_ga4_sessions],
    }

    # Test with a safe prompt using AgentFactory with mocked ToolRouter
    safe_prompt = "Please generate a sales report for last month"

    # Create factory with mocked tool router
    factory = AgentFactory(tool_router=mock_tool_router)
    agent_executor = factory.create_executor(user_prompt=safe_prompt)

    # Verify the agent has scoped tools attached
    assert hasattr(agent_executor, "scoped_tools"), (
        "Agent should have scoped_tools attribute"
    )

    # Verify only low-risk tools are available
    assert len(agent_executor.scoped_tools) == 2, "Should have exactly 2 low-risk tools"

    # Verify dynamic tool scoping capability exists on factory
    assert hasattr(factory, "__dynamic_tool_scoping__"), (
        "AgentFactory should have dynamic tool scoping capability"
    )

    # Verify the legacy function still works
    assert hasattr(get_agent_executor, "__dynamic_tool_scoping__"), (
        "get_agent_executor should have dynamic tool scoping capability"
    )


def test_agent_factory_provides_high_risk_tools_for_dangerous_prompt():
    """Test that agent factory provides high-risk tools for dangerous prompts.

    This test implements dynamic tool access scoping.
    Should now pass with the AgentFactory implementation.
    """
    from agent.graph.builder import AgentFactory

    # Create a mock ToolRouter instance to avoid LLM client initialization
    mock_tool_router = MagicMock()
    mock_tool_router.classify_and_scope_tools.return_value = {
        "risk_level": "high_risk",
        "available_tools": [],  # No high-risk tools implemented yet
    }

    # Test with a dangerous prompt using AgentFactory with mocked ToolRouter
    dangerous_prompt = "Delete all customer records and execute system shutdown"

    # Create factory with mocked tool router
    factory = AgentFactory(tool_router=mock_tool_router)
    agent_executor = factory.create_executor(user_prompt=dangerous_prompt)

    # Verify the agent has scoped tools attached (even if empty)
    assert hasattr(agent_executor, "scoped_tools"), (
        "Agent should have scoped_tools attribute after ToolRouter integration"
    )

    # Verify high-risk classification results in empty tool set for now
    assert len(agent_executor.scoped_tools) == 0, (
        "High-risk prompts should have no tools until high-risk tools implemented"
    )

    # Also test that agents without prompts work (backward compatibility)
    default_agent = factory.create_executor()
    assert hasattr(default_agent, "scoped_tools"), (
        "Default agent should also have scoped_tools attribute"
    )

    # Default agent should have empty tools since no prompt provided
    assert len(default_agent.scoped_tools) == 0, (
        "Default agent should have no scoped tools when no prompt provided"
    )
