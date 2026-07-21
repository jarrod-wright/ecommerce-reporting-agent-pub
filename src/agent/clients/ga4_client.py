"""Google Analytics 4 client for interacting with GA4 API."""

import json
from typing import Any, Dict, List

import structlog
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account


class GA4Client:
    """
    Google Analytics 4 API client.

    This client handles authentication and communication with the Google Analytics 4
    Reporting API to fetch e-commerce and performance data.

    Attributes:
        credentials_json_str: JSON string containing service account credentials
    """

    def __init__(self, credentials_json_str: str) -> None:
        """
        Initialize the GA4Client with service account credentials.

        Args:
            credentials_json_str: JSON string containing Google service account
                                credentials with necessary GA4 API permissions

        Raises:
            ValueError: If credentials_json_str is empty or None
        """
        logger = structlog.get_logger()
        logger.info(
            "Initializing GA4Client", credentials_provided=bool(credentials_json_str)
        )

        if not credentials_json_str:
            logger.error(
                "GA4Client initialization failed: credentials_json_str is required"
            )
            raise ValueError("credentials_json_str cannot be empty or None")

        self.credentials_json_str = credentials_json_str

        logger.info("GA4Client initialized successfully")

    def fetch_sessions_data(
        self, property_id: str, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch sessions data from Google Analytics 4 API.

        This method retrieves session metrics including sessions, users, and device
        category for the specified date range and property.

        Args:
            property_id: GA4 property ID (e.g., '123456789')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of dictionaries containing session data with keys:
            - sessions: Number of sessions
            - users: Number of users
            - date: Date of the data
            - device_category: Device category (desktop, mobile, tablet)

        Raises:
            Exception: If the GA4 API call fails or credentials are invalid
        """
        logger = structlog.get_logger()
        logger.info(
            "Fetching sessions data from GA4 API",
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
        )

        try:
            # Parse credentials and create service account credentials
            credentials_info = json.loads(self.credentials_json_str)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            )

            # Initialize the GA4 client
            client = BetaAnalyticsDataClient(credentials=credentials)

            # Build the request
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[
                    Dimension(name="date"),
                    Dimension(name="deviceCategory"),
                ],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="totalUsers"),
                ],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            )

            # Make the API call
            response = client.run_report(request=request)

            # Format the response data
            formatted_data = []
            for row in response.rows:
                session_data = {
                    "date": row.dimension_values[0].value,
                    "device_category": row.dimension_values[1].value,
                    "sessions": int(row.metric_values[0].value),
                    "users": int(row.metric_values[1].value),
                }
                formatted_data.append(session_data)

            logger.info(
                "Successfully fetched sessions data",
                records_count=len(formatted_data),
                property_id=property_id,
            )

            return formatted_data

        except Exception as e:
            logger.error(
                "Failed to fetch sessions data from GA4 API",
                error=str(e),
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
            )
            raise e
