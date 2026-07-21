"""Fetch data node for the e-commerce performance reporting agent."""

import asyncio
from typing import Any, Dict

import structlog

from agent.models.state import ReportingAgentState
from agent.tools.ga4_tools import get_ga4_sessions
from agent.tools.shopify_tools import get_shopify_orders


async def fetch_data_node(state: ReportingAgentState) -> Dict[str, Any]:
    """Fetch data concurrently from Shopify and Google Analytics 4 APIs.

    This node retrieves e-commerce order data from Shopify and web analytics
    session data from GA4 using concurrent API calls for optimal performance.
    The date_range from the report configuration is used to filter the data.

    Args:
        state: The current agent state containing the report configuration

    Returns:
        Dictionary containing raw_shopify_data and raw_ga4_data keys with
        the fetched data from both APIs

    Raises:
        Exception: If either API call fails or date_range is invalid
    """
    logger = structlog.get_logger()
    logger.info("Starting data fetching from Shopify and GA4")

    try:
        # Extract date range from report config
        date_range = state.report_config["date_range"]
        logger.info("Extracting date range from config", date_range=date_range)

        # Parse the date range string (format: "YYYY-MM-DD to YYYY-MM-DD")
        start_date, end_date = date_range.split(" to ")
        start_date = start_date.strip()
        end_date = end_date.strip()

        logger.info("Parsed date range", start_date=start_date, end_date=end_date)

        # Use asyncio.gather to call both tools concurrently
        logger.info("Initiating concurrent API calls to Shopify and GA4")

        shopify_data, ga4_data = await asyncio.gather(
            get_shopify_orders.ainvoke({"date_since": start_date}),
            get_ga4_sessions.ainvoke({"start_date": start_date, "end_date": end_date}),
        )

        logger.info(
            "Successfully fetched data from both APIs",
            shopify_count=len(shopify_data) if shopify_data else 0,
            ga4_count=len(ga4_data) if ga4_data else 0,
        )

        return {"raw_shopify_data": shopify_data, "raw_ga4_data": ga4_data}

    except Exception as e:
        logger.error(
            "Failed to fetch data",
            error=str(e),
            date_range=state.report_config.get("date_range"),
        )
        raise e
