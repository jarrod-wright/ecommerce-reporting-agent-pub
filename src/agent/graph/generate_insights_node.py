"""Generate insights node for the e-commerce performance reporting agent."""

from typing import Any, Dict

import structlog

from agent.clients.factory import get_llm_client_for_role
from agent.models.insights import ReportInsights
from agent.models.state import ReportingAgentState


def generate_insights_node(state: ReportingAgentState) -> Dict[str, Any]:
    """Generate business insights from processed e-commerce performance data using LLM.

    This node takes the processed and unified DataFrame containing Shopify revenue
    and GA4 analytics data, then uses a large language model with structured output
    to generate actionable business insights, key metrics calculations, and strategic
    recommendations
    for the e-commerce performance report.

    Args:
        state: The current agent state containing processed_dataframe_json with
               the unified DataFrame data ready for analysis

    Returns:
        Dictionary containing generated_insights key with the structured insights
        data as returned by the LLM analysis

    Raises:
        Exception: If LLM API call fails or data processing encounters errors
    """
    logger = structlog.get_logger()
    logger.info("Starting insights generation from processed data")

    try:
        # Extract processed DataFrame JSON from state
        processed_data = state.processed_dataframe_json

        logger.info(
            "Preparing data for LLM analysis",
            data_available=processed_data is not None,
            report_title=state.report_config.get("report_title"),
        )

        # Define prompt template for the expert e-commerce analyst
        prompt_template = """
        You are an expert e-commerce performance analyst. Analyze the following
        processed data from Shopify orders and Google Analytics 4 sessions to
        generate actionable business insights.

        Report Configuration:
        - Title: {report_title}
        - Date Range: {date_range}

        Processed Performance Data:
        {processed_data}

        Please provide a comprehensive analysis including:
        1. A concise summary of the overall performance trends
        2. Key metrics calculations (totals, averages, conversion rates)
        3. Specific recommendations for improving e-commerce performance
        4. Any data quality observations or anomalies you notice

        Focus on actionable insights that can drive business decisions.
        """

        # Format the prompt with actual data
        formatted_prompt = prompt_template.format(
            report_title=state.report_config.get("report_title", "Performance Report"),
            date_range=state.report_config.get("date_range", "Unknown"),
            processed_data=processed_data,
        )

        # Get the primary-role LLM client (provider + model resolved from settings)
        client = get_llm_client_for_role("primary")

        logger.info("Invoking LLM for insights generation")

        # Generate structured output using the LLM client
        insights = client.generate_structured_output(formatted_prompt, ReportInsights)

        logger.info(
            "Successfully generated insights",
            has_summary=bool(insights.summary),
            num_recommendations=len(insights.recommendations)
            if insights.recommendations
            else 0,
            num_key_metrics=len(insights.key_metrics) if insights.key_metrics else 0,
        )

        # Return the insights as model_dump()
        return {"generated_insights": insights.model_dump()}

    except Exception as e:
        logger.error(
            "Failed to generate insights",
            error=str(e),
            data_available=state.processed_dataframe_json is not None,
            report_config=state.report_config,
        )
        raise e
