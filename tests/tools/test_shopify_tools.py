from agent.tools.shopify_tools import get_shopify_orders


def test_get_shopify_orders_tool(mocker):
    """Test the get_shopify_orders tool function."""
    # Mock environment variables
    shop_url = "test-shop.myshopify.com"
    access_token = "test_access_token"
    mocker.patch.dict(
        "os.environ",
        {"SHOPIFY_SHOP_URL": shop_url, "SHOPIFY_ACCESS_TOKEN": access_token},
    )

    # Mock the ShopifyClient class completely
    mock_shopify_client = mocker.patch("agent.tools.shopify_tools.ShopifyClient")

    # Configure mock client instance
    mock_client_instance = mock_shopify_client.return_value
    mock_orders_data = [
        {
            "id": 123456,
            "order_number": "ORD001",
            "created_at": "2024-01-15T10:00:00Z",
            "total_price": "99.99",
        },
        {
            "id": 123457,
            "order_number": "ORD002",
            "created_at": "2024-01-15T11:00:00Z",
            "total_price": "149.99",
        },
    ]
    mock_client_instance.fetch_orders.return_value = mock_orders_data

    # Test date parameter
    date_since = "2024-01-15"

    # Call the tool function (using invoke for LangChain tools)
    result = get_shopify_orders.invoke({"date_since": date_since})

    # Assert ShopifyClient was instantiated with environment variables
    mock_shopify_client.assert_called_once_with(
        shop_url=shop_url, access_token=access_token
    )

    # Assert fetch_orders method was called with correct arguments
    mock_client_instance.fetch_orders.assert_called_once_with(date_since=date_since)

    # Assert the tool returns the expected data
    assert result == mock_orders_data
