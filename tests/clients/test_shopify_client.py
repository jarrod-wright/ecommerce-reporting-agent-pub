# This test will fail because the import fails. This is the correct TDD start.
from agent.clients.shopify_client import ShopifyClient


def test_shopify_client_initialization():
    """Test that ShopifyClient can be initialized."""
    # We don't need mock credentials for this simple test,
    # as we only care if the class can be instantiated.
    shop_url = "test.myshopify.com"
    access_token = "mock_token"

    client = ShopifyClient(shop_url=shop_url, access_token=access_token)

    assert client is not None


def test_fetch_orders_success(mocker):
    """Test that fetch_orders returns order data successfully."""
    # Create client instance
    shop_url = "test.myshopify.com"
    access_token = "mock_token"
    client = ShopifyClient(shop_url=shop_url, access_token=access_token)

    # Mock sample order data
    sample_orders = [
        {"id": 1001, "order_number": "1001", "total_price": "29.99"},
        {"id": 1002, "order_number": "1002", "total_price": "49.99"},
    ]

    # Mock the shopify.Order.find method to prevent real network calls
    mock_find = mocker.patch("shopify.Order.find", return_value=sample_orders)

    # Call the method that doesn't exist yet
    result = client.fetch_orders()

    # Assert the returned data matches the mocked data
    assert result == sample_orders
    mock_find.assert_called_once()
