from unittest.mock import patch

import pytest

from agent.clients.factory import get_llm_client


@patch("agent.clients.factory.AnthropicClient")
def test_get_llm_client_returns_anthropic_client(mock_anthropic_client):
    """Test that get_llm_client returns AnthropicClient for 'ANTHROPIC' provider."""
    client = get_llm_client("ANTHROPIC")
    mock_anthropic_client.assert_called_once()
    assert client is mock_anthropic_client.return_value


@patch("agent.clients.factory.GoogleAIClient")
def test_get_llm_client_returns_google_client(mock_google_client):
    """Test that get_llm_client returns GoogleAIClient for 'GOOGLE' provider."""
    client = get_llm_client("GOOGLE")
    mock_google_client.assert_called_once()
    assert client is mock_google_client.return_value


def test_get_llm_client_raises_error_for_unknown_provider():
    """Test that get_llm_client raises ValueError for unknown provider."""
    with pytest.raises(ValueError):
        get_llm_client("UNKNOWN_PROVIDER")
