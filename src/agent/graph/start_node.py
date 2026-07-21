"""Start node for the e-commerce performance reporting agent."""

from typing import Any, Dict

import structlog

from agent.models.state import ReportingAgentState


def start_node(state: ReportingAgentState) -> Dict[str, Any]:
    """Start the performance reporting workflow by validating the report configuration.

    This node validates that the required configuration parameters are present
    in the agent state before proceeding with data collection and report generation.

    Args:
        state: The current agent state containing the report configuration

    Returns:
        Empty dictionary if validation succeeds, or dictionary with error_message
        key if validation fails
    """
    logger = structlog.get_logger()
    logger.info("Starting performance reporting workflow")

    # Validate that required keys exist in report_config
    required_keys = ["date_range", "report_title"]
    missing_keys = [key for key in required_keys if key not in state.report_config]

    if missing_keys:
        error_msg = f"Missing required configuration keys: {missing_keys}"
        logger.error("Validation failed", missing_keys=missing_keys)
        return {"error_message": error_msg}

    logger.info("Validation successful, proceeding with workflow")
    return {}
