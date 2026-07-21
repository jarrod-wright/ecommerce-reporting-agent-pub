"""Centralized configuration module for the E-commerce Performance Report Agent."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Substrings that mark a security secret as insecure/placeholder. Rejecting by
# marker (rather than exact match) is fail-closed by design: it catches the known
# legacy placeholders AND any variant that carries the same weak signal
# (e.g. a "…-change-in-production" or "test-secret…" derivative).
_INSECURE_SECRET_MARKERS = (
    "change-in-production",
    "test-secret",
)


class Settings(BaseSettings):
    """Centralized settings configuration using Pydantic BaseSettings.

    Configuration is loaded from environment variables and a local, gitignored
    ``.env`` file, falling back to the defaults defined here when neither is set.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM Role Configuration.
    # Each role resolves to an explicit (provider, model) pair, so the agent is
    # genuinely provider-agnostic: a graph node asks for a role and the concrete
    # provider/model is chosen here. Defaults run entirely on Google Gemini's
    # free tier for a zero-cost demo: `gemini-3.1-flash-lite` is the free-tier
    # cost-efficient staple. For higher-quality output, set PRIMARY_LLM_MODEL to
    # `gemini-3.5-flash` (a billed key), or CHALLENGER_PROVIDER=ANTHROPIC (plus an
    # ANTHROPIC_API_KEY) for true cross-provider adversarial critique.
    PRIMARY_PROVIDER: str = "GOOGLE"
    PRIMARY_LLM_MODEL: str = "gemini-3.1-flash-lite"
    CHALLENGER_PROVIDER: str = "GOOGLE"
    CHALLENGER_LLM_MODEL: str = "gemini-3.1-flash-lite"

    # API Keys (loaded from environment variables / .env)
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # Security Configuration.
    # These have NO default: they are required from the environment and are
    # rejected if empty or a known placeholder (fail-closed — see the validator).
    WEBHOOK_SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    @field_validator("WEBHOOK_SECRET_KEY", "JWT_SECRET_KEY")
    @classmethod
    def _reject_insecure_secret(cls, value: str, info) -> str:
        """Fail closed: reject an empty or placeholder-marked security secret."""
        stripped = value.strip()
        if not stripped or any(m in stripped for m in _INSECURE_SECRET_MARKERS):
            raise ValueError(
                f"{info.field_name} must be set to a secure, non-placeholder "
                "value via the environment (fail-closed config)."
            )
        return value

    # Observability Configuration
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "Ecomm-Report-Agent-Dev"


# Global settings instance
settings = Settings()
