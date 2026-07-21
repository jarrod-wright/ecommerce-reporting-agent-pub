"""Human approval node for the e-commerce performance reporting agent."""

import structlog
from langgraph.types import interrupt

from agent.models.state import ReportingAgentState


def human_approval_node(state: ReportingAgentState) -> dict:
    """Request human approval for high-risk actions.
    
    This node implements the Human-in-the-Loop (HITL) pattern by interrupting
    the graph execution and requesting human approval before proceeding with
    state-changing or high-risk operations.
    
    Args:
        state: The current agent state
        
    Returns:
        Dictionary from interrupt call (this function doesn't return normally)
    """
    logger = structlog.get_logger()

    logger.info(
        "Requesting human approval for high-risk action",
        insights_available=state.generated_insights is not None,
        report_config=state.report_config
    )

    # Interrupt the graph execution and request human approval
    return interrupt({
        "action_type": "state_change",
        "details": "Requesting approval to proceed with report generation",
        "insights": state.generated_insights,
        "report_title": state.report_config.get("report_title", "Unknown Report")
    })
