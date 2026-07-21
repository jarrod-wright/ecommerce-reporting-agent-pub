"""Tests for the centralized settings configuration module."""

from agent.config import Settings


def test_settings_load_from_env(monkeypatch):
    """Test that Settings class loads configuration from environment variables."""
    monkeypatch.setenv("PRIMARY_LLM_MODEL", "mock_model_name")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
    monkeypatch.setenv("LANGCHAIN_API_KEY", "mock_ls_api_key")
    monkeypatch.setenv("LANGCHAIN_PROJECT", "Test Project")

    settings = Settings()

    assert settings.PRIMARY_LLM_MODEL == "mock_model_name"
    assert settings.LANGCHAIN_TRACING_V2 is True
    assert settings.LANGCHAIN_API_KEY == "mock_ls_api_key"
    assert settings.LANGCHAIN_PROJECT == "Test Project"
