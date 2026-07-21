from agent.config import settings

from .anthropic_client import AnthropicClient
from .google_client import GoogleAIClient
from .llm_interface import LLMClient

# Maps a logical role to the (provider, model) settings attributes that define it.
_ROLE_MAP = {
    "primary": ("PRIMARY_PROVIDER", "PRIMARY_LLM_MODEL"),
    "challenger": ("CHALLENGER_PROVIDER", "CHALLENGER_LLM_MODEL"),
}


def get_llm_client(provider: str, model: str | None = None) -> LLMClient:
    """Create an LLM client for an explicit provider.

    Args:
        provider: The provider string ("ANTHROPIC" or "GOOGLE").
        model: Optional model ID. When omitted, the client falls back to its
            own configured default model.

    Returns:
        An instantiated LLM client that implements the LLMClient interface.

    Raises:
        ValueError: If the provider string is not recognized.
    """
    if provider == "ANTHROPIC":
        return AnthropicClient(model=model)
    elif provider == "GOOGLE":
        return GoogleAIClient(model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def get_llm_client_for_role(role: str) -> LLMClient:
    """Create an LLM client for a named role, resolving provider + model from settings.

    This keeps graph nodes provider-agnostic: a node asks for the "primary" or
    "challenger" role and the concrete provider/model is chosen by configuration,
    so a provider can be swapped without touching graph code.

    Args:
        role: The role name ("primary" or "challenger").

    Returns:
        An instantiated LLM client that implements the LLMClient interface.

    Raises:
        ValueError: If the role is not recognized.
    """
    try:
        provider_attr, model_attr = _ROLE_MAP[role]
    except KeyError as e:
        raise ValueError(f"Unknown role: {role}") from e

    provider = getattr(settings, provider_attr)
    model = getattr(settings, model_attr)
    return get_llm_client(provider, model)
