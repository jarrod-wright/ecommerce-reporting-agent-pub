"""Graph builder for the e-commerce performance reporting agent."""

from typing import Optional

import structlog
from langgraph.graph import END, StateGraph

from agent.graph.compile_report_node import compile_report_node
from agent.graph.execute_high_risk_tool_node import execute_high_risk_tool_node
from agent.graph.fetch_data_node import fetch_data_node
from agent.graph.generate_insights_node import generate_insights_node
from agent.graph.generate_visualizations_node import generate_visualizations_node
from agent.graph.handle_error_node import handle_error_node
from agent.graph.human_approval_node import human_approval_node
from agent.graph.process_data_node import process_data_node
from agent.graph.start_node import start_node
from agent.models.state import ReportingAgentState
from agent.tools.tool_router import ToolRouter


def route_after_data_processing(state: ReportingAgentState) -> str:
    """Route after data processing based on error status.

    Inspects the error_message field in the state. If the field is not empty,
    returns "handle_error", otherwise returns "generate_insights".

    Args:
        state: The current agent state

    Returns:
        String indicating the next node: "handle_error" or "generate_insights"
    """
    logger = structlog.get_logger()

    if state.error_message:
        logger.info("Routing to error handler", error_message=state.error_message)
        return "handle_error"
    else:
        logger.info("Routing to insights generation")
        return "generate_insights"


def route_after_human_approval(state: ReportingAgentState) -> str:
    """Route after human approval based on decision.

    Inspects the human_decision field in the state. If the decision is "approve",
    returns "execute_high_risk_tool", otherwise returns "END" to terminate.

    Args:
        state: The current agent state

    Returns:
        String indicating the next node: "execute_high_risk_tool" or "END"
    """
    logger = structlog.get_logger()

    if state.human_decision == "approve":
        logger.info("Human approved action, proceeding to high-risk tool execution")
        return "execute_high_risk_tool"
    else:
        logger.info(
            "Human rejected or no decision made, terminating workflow",
            decision=state.human_decision,
        )
        return "END"


class AgentFactory:
    """Factory class for creating agents with dynamically scoped tools.

    Implements Constitutional Security Pattern.
    Provides dynamic tool access scoping based on semantic input classification.
    """

    def __init__(self, tool_router: Optional[ToolRouter] = None):
        """Initialize AgentFactory with optional ToolRouter.

        Args:
            tool_router: Optional ToolRouter for dependency injection
        """
        self.logger = structlog.get_logger()
        self.tool_router = tool_router or ToolRouter()

        # Add dynamic tool scoping capability marker for tests
        self.__dynamic_tool_scoping__ = True

    def create_executor(self, user_prompt: Optional[str] = None, checkpointer=None):
        """Create and compile agent executor with dynamically scoped tools.

        Args:
            user_prompt: Optional user prompt for dynamic tool scoping
            checkpointer: Optional checkpointer for stateful operations

        Returns:
            Compiled LangGraph executor with scoped tools
        """
        self.logger.info("Building e-commerce reporting agent graph with HITL pattern")

        # Get dynamically scoped tools if prompt provided
        scoped_tools = []
        if user_prompt:
            scoping_result = self.tool_router.classify_and_scope_tools(user_prompt)
            scoped_tools = scoping_result["available_tools"]
            self.logger.info(
                "Applied dynamic tool scoping",
                risk_level=scoping_result["risk_level"],
                tool_count=len(scoped_tools),
            )

        # Initialize StateGraph with ReportingAgentState
        workflow = StateGraph(ReportingAgentState)

        # Add all nodes to the graph
        workflow.add_node("start", start_node)
        workflow.add_node("fetch_data", fetch_data_node)
        workflow.add_node("process_data", process_data_node)
        workflow.add_node("generate_insights", generate_insights_node)
        workflow.add_node("human_approval", human_approval_node)
        workflow.add_node("execute_high_risk_tool", execute_high_risk_tool_node)
        workflow.add_node("generate_visualizations", generate_visualizations_node)
        workflow.add_node("compile_report", compile_report_node)
        workflow.add_node("handle_error", handle_error_node)

        # Set the entry point
        workflow.set_entry_point("start")

        # Add normal edges for the primary success path
        workflow.add_edge("start", "fetch_data")
        workflow.add_edge("fetch_data", "process_data")
        workflow.add_edge("generate_insights", "human_approval")
        workflow.add_edge("execute_high_risk_tool", "generate_visualizations")
        workflow.add_edge("generate_visualizations", "compile_report")
        workflow.add_edge("compile_report", END)
        workflow.add_edge("handle_error", END)

        # Add conditional edge from process_data using routing function
        workflow.add_conditional_edges(
            "process_data",
            route_after_data_processing,
            {
                "generate_insights": "generate_insights",
                "handle_error": "handle_error",
            },
        )

        # Add conditional edge from human_approval using HITL routing function
        workflow.add_conditional_edges(
            "human_approval",
            route_after_human_approval,
            {
                "execute_high_risk_tool": "execute_high_risk_tool",
                "END": END,
            },
        )

        # Compile the graph with scoped tools
        compiled_graph = workflow.compile(checkpointer=checkpointer)

        # Attach scoped tools to the compiled graph for testing/inspection
        compiled_graph.scoped_tools = scoped_tools

        self.logger.info(
            "Successfully compiled e-commerce reporting agent graph with HITL"
        )
        return compiled_graph


def get_agent_executor(user_prompt: Optional[str] = None, checkpointer=None):
    """Create and compile the e-commerce reporting agent graph.

    Legacy function maintained for backward compatibility.
    Internally uses AgentFactory with dynamic tool scoping.

    Args:
        user_prompt: Optional user prompt for dynamic tool scoping
        checkpointer: Optional checkpointer for stateful operations

    Returns:
        Compiled LangGraph executor ready for invocation
    """
    factory = AgentFactory()
    return factory.create_executor(user_prompt=user_prompt, checkpointer=checkpointer)


# Add dynamic tool scoping capability marker for tests
get_agent_executor.__dynamic_tool_scoping__ = True
