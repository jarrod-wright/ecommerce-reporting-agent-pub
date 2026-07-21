from unittest.mock import Mock, patch

from langchain_core.messages import AIMessage

from agent.clients.anthropic_client import AnthropicClient
from agent.clients.llm_interface import LLMClient


def test_anthropic_client_adheres_to_interface():
    """Test that AnthropicClient is a subclass of LLMClient."""
    assert issubclass(AnthropicClient, LLMClient)


@patch("agent.clients.anthropic_client.settings")
@patch("structlog.get_logger")
@patch("agent.clients.anthropic_client.ChatAnthropic")
def test_anthropic_client_captures_token_usage(
    mock_chat_anthropic, mock_get_logger, mock_settings
):
    """Test that AnthropicClient captures and logs token usage from responses."""
    # Arrange
    mock_settings.ANTHROPIC_API_KEY = "test-key"
    mock_settings.PRIMARY_LLM_MODEL = "claude-3-sonnet"

    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger

    mock_ai_message = AIMessage(
        content="test response",
        usage_metadata={"input_tokens": 100, "output_tokens": 200, "total_tokens": 300},
    )

    mock_structured_client = Mock()
    mock_structured_client.invoke.return_value = mock_ai_message

    mock_llm_instance = Mock()
    mock_llm_instance.with_structured_output.return_value = mock_structured_client
    mock_chat_anthropic.return_value = mock_llm_instance

    client = AnthropicClient()

    # Act
    client.generate_structured_output("test prompt", str)

    # Assert
    mock_logger.info.assert_called_with(
        "LLM token usage", input_tokens=100, output_tokens=200
    )
