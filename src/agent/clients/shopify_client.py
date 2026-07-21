"""Shopify API client for e-commerce data retrieval."""

from typing import Any, Dict, List

import shopify
import structlog


class ShopifyClient:
    """Client for interacting with the Shopify API.

    This class provides a foundation for making requests to the Shopify API
    to retrieve e-commerce data for performance reporting.
    """

    def __init__(self, shop_url: str, access_token: str) -> None:
        """Initialize the Shopify client.

        Args:
            shop_url: The Shopify shop URL (e.g., 'test.myshopify.com')
            access_token: The access token for API authentication
        """
        self.logger = structlog.get_logger()
        self.logger.info("Initializing ShopifyClient", shop_url=shop_url)

        self.shop_url = shop_url
        self.access_token = access_token

        self.logger.info("ShopifyClient initialized successfully")

    def fetch_orders(self, date_since: str = None) -> List[Dict[str, Any]]:
        """Fetch orders from the Shopify API.

        This method activates a Shopify session and retrieves orders from the store.
        All API calls are wrapped in error handling to manage potential failures.

        Args:
            date_since: Optional ISO date string to filter orders created since this date

        Returns:
            List of order dictionaries containing order data

        Raises:
            Exception: If the Shopify API call fails or returns an error
        """
        self.logger.info("Fetching orders from Shopify", date_since=date_since)

        try:
            # Activate Shopify session
            session = shopify.Session(self.shop_url, "2023-10", self.access_token)
            shopify.ShopifyResource.activate_session(session)

            # Fetch orders using the Shopify library
            orders = shopify.Order.find()

            self.logger.info("Successfully fetched orders", count=len(orders))
            return orders

        except Exception as e:
            self.logger.error(
                "Failed to fetch orders", error=str(e), shop_url=self.shop_url
            )
            raise e
        finally:
            # Clean up session
            shopify.ShopifyResource.clear_session()
