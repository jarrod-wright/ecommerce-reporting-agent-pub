"""Pre-flight check node for data quality assessment."""

from typing import Any, Dict

import structlog
from pydantic import BaseModel

from agent.clients.factory import get_llm_client
from agent.models.state import ReportingAgentState

logger = structlog.get_logger()


class DataQualityReport(BaseModel):
    """Pydantic model for structured data quality assessment output."""

    data_quality_score: float
    justification: str


def pre_flight_check_node(state: ReportingAgentState) -> Dict[str, Any]:
    """
    Assess data quality before proceeding with analysis.

    This node implements the Pre-Flight Check as specified in the XAI Integration
    Playbook. It evaluates the processed_dataframe_json for structural integrity,
    missing values, inconsistencies, and logical outliers.

    Args:
        state: Current ReportingAgentState containing processed_dataframe_json

    Returns:
        Dictionary with data_quality_score and data_quality_justification keys

    Raises:
        Exception: If the LLM client fails to generate structured output
    """
    logger.info("Starting pre-flight data quality check")

    try:
        # Validate input data exists
        if not state.processed_dataframe_json:
            logger.warning("No processed_dataframe_json found in state")
            return {
                "data_quality_score": 0.0,
                "data_quality_justification": (
                    "No processed data found to assess quality."
                ),
            }

        # Get LLM client for data quality assessment
        client = get_llm_client("ANTHROPIC")

        # Sophisticated prompt template for data quality analysis
        prompt = f"""
You are an expert data quality analyst specializing in e-commerce analytics data.
Your task is to assess the structural integrity and quality of the provided dataset.

DATASET TO ANALYZE:
{state.processed_dataframe_json}

ASSESSMENT CRITERIA:
1. Data Completeness: Check for missing values, null entries, or empty fields
2. Data Consistency: Verify consistent formatting for dates, numbers, and text
3. Logical Outliers: Identify values that seem unreasonable or impossible
4. Structural Anomalies: Check for malformed JSON, unexpected data types
5. Business Logic Validation: Ensure values make business sense (e.g., positive revenue)

SCORING GUIDELINES:
- 0.9-1.0: Excellent - Clean, complete, consistent data ready for analysis
- 0.75-0.89: Good - Minor issues that won't significantly impact analysis
- 0.5-0.74: Fair - Moderate issues requiring attention but analysis can proceed
- 0.25-0.49: Poor - Significant data quality issues affecting reliability
- 0.0-0.24: Critical - Data quality too poor for reliable analysis

Provide a numeric score between 0.0 and 1.0, and a clear justification explaining:
- What issues (if any) were found
- How these issues might impact the analysis
- Your confidence in the data's reliability for business intelligence purposes

Be thorough but concise in your assessment.
"""

        logger.info("Generating structured data quality assessment")

        # Generate structured output using the LLM client
        assessment = client.generate_structured_output(prompt, DataQualityReport)

        logger.info(
            "Data quality assessment completed",
            data_quality_score=assessment.data_quality_score,
            justification_length=len(assessment.justification),
        )

        # Return state update dictionary
        return {
            "data_quality_score": assessment.data_quality_score,
            "data_quality_justification": assessment.justification,
        }

    except Exception as e:
        logger.error("Failed to assess data quality", error=str(e))
        return {
            "data_quality_score": 0.0,
            "data_quality_justification": (
                f"Data quality assessment failed due to system error: {str(e)}"
            ),
        }
