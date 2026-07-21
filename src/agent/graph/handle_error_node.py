"""Handle error node for the e-commerce performance reporting agent."""

from typing import Any, Dict

import structlog

from agent.models.state import ReportingAgentState


def handle_error_node(state: ReportingAgentState) -> Dict[str, Any]:
    """Handle and log errors that occurred during the reporting workflow.

    This node is responsible for logging error messages that were captured
    during the execution of the reporting workflow. It serves as the terminal
    node for error scenarios, providing structured logging of the failure
    and signaling the end of the workflow execution.

    Args:
        state: The current agent state containing the error_message to log

    Returns:
        Empty dictionary to signify the end of the workflow
    """
    logger = structlog.get_logger()

    # Log the error message from the state
    logger.error(
        "Reporting workflow encountered an error",
        error_message=state.error_message,
        report_config=state.report_config,
    )

    # Return empty dictionary to signify end of workflow
    return {}
