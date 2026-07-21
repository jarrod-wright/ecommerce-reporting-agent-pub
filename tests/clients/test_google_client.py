from agent.clients.google_client import GoogleAIClient
from agent.clients.llm_interface import LLMClient


def test_google_client_adheres_to_interface():
    """Test that GoogleAIClient is a subclass of LLMClient."""
    assert issubclass(GoogleAIClient, LLMClient)
