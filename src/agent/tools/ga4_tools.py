"""Google Analytics 4 LangChain tools for fetching analytics data."""

import os
from typing import Any, Dict, List

from langchain_core.tools import tool

from agent.clients.ga4_client import GA4Client


@tool
def get_ga4_sessions(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Fetch session analytics data from Google Analytics 4 for performance reporting.

    This tool retrieves session metrics from a Google Analytics 4 property,
    including sessions, users, and device category breakdowns for the specified
    date range. It is designed to help analyze website performance, user engagement,
    and device usage patterns. The tool automatically uses configured GA4
    credentials from environment variables for security.

    Use this tool when you need to:
    - Analyze website traffic patterns and trends
    - Generate user engagement reports
    - Track session counts over time periods
    - Compare desktop vs mobile usage
    - Create performance dashboards for web analytics
    - Monitor user acquisition and retention metrics

    Args:
        start_date: Start date for data retrieval in YYYY-MM-DD format.
                   For example, '2024-01-15' will fetch data starting from
                   January 15th, 2024.
        end_date: End date for data retrieval in YYYY-MM-DD format.
                 For example, '2024-01-20' will fetch data up to and including
                 January 20th, 2024. Can be the same as start_date for single-day data.

    Returns:
        List of dictionaries containing session analytics data. Each dictionary includes:
        - date: Date of the data in YYYY-MM-DD format
        - device_category: Device type (desktop, mobile, tablet)
        - sessions: Number of sessions for that date/device combination
        - users: Number of unique users for that date/device combination

    Raises:
        ValueError: If GA4 environment variables are missing
        Exception: If GA4 API call fails or credentials are invalid

    Example:
        To get session data for a specific week:
        sessions_data = get_ga4_sessions("2024-01-15", "2024-01-21")

        To get data for a single day:
        daily_data = get_ga4_sessions("2024-01-15", "2024-01-15")
    """
    # Load GA4 configuration from environment variables for security
    property_id = os.environ.get("GA4_PROPERTY_ID")
    credentials_json_str = os.environ.get("GA4_CREDENTIALS_JSON")

    if not property_id or not credentials_json_str:
        raise ValueError(
            "Missing required environment variables: GA4_PROPERTY_ID and/or GA4_CREDENTIALS_JSON"
        )

    # Initialize GA4 client and fetch sessions data
    client = GA4Client(credentials_json_str=credentials_json_str)
    sessions_data = client.fetch_sessions_data(
        property_id=property_id, start_date=start_date, end_date=end_date
    )

    return sessions_data
