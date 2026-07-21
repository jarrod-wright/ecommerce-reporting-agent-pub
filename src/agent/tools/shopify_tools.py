"""Shopify LangChain tools for fetching e-commerce data."""

import os
from typing import Any, Dict, List

from langchain_core.tools import tool

from agent.clients.shopify_client import ShopifyClient


@tool
def get_shopify_orders(date_since: str) -> List[Dict[str, Any]]:
    """
    Fetch orders from Shopify store for performance reporting and analysis.

    This tool retrieves order data from a Shopify store using the Shopify API.
    It is designed to help analyze e-commerce performance by fetching order
    information from a specified date onwards. The tool automatically uses
    configured Shopify credentials from environment variables for security.

    Use this tool when you need to:
    - Analyze recent sales performance
    - Generate revenue reports
    - Track order trends over time
    - Examine customer purchase patterns
    - Create performance dashboards

    Args:
        date_since: ISO date string (YYYY-MM-DD format) to filter orders
                   created since this date. For example, '2024-01-15' will
                   fetch all orders created from January 15th onwards.

    Returns:
        List of dictionaries containing order data. Each dictionary includes:
        - id: Unique order identifier
        - order_number: Human-readable order number
        - created_at: ISO timestamp when order was created
        - total_price: Total order value as string
        - customer: Customer information (if available)
        - line_items: List of products in the order
        - financial_status: Payment status (paid, pending, etc.)
        - fulfillment_status: Shipping status (fulfilled, unfulfilled, etc.)

    Raises:
        Exception: If Shopify API credentials are missing or API call fails

    Example:
        To get orders from the last week:
        orders = get_shopify_orders("2024-01-15")
    """
    # Load Shopify credentials from environment variables for security
    shop_url = os.environ.get("SHOPIFY_SHOP_URL")
    access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN")

    if not shop_url or not access_token:
        raise ValueError(
            "Missing required environment variables: SHOPIFY_SHOP_URL and/or SHOPIFY_ACCESS_TOKEN"
        )

    # Initialize Shopify client and fetch orders
    client = ShopifyClient(shop_url=shop_url, access_token=access_token)
    orders = client.fetch_orders(date_since=date_since)

    return orders
