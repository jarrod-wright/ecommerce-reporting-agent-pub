import os

import structlog
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

from agent.config import settings

from .llm_interface import LLMClient


class AnthropicClient(LLMClient):
    """Anthropic-specific implementation of the LLMClient interface."""

    def __init__(self, model: str | None = None) -> None:
        """Initialize the AnthropicClient with API key from settings.

        Args:
            model: Optional model ID override. Falls back to the primary model
                from settings when not provided.
        """
        if not settings.ANTHROPIC_API_KEY:
            try:
                api_key = os.environ["ANTHROPIC_API_KEY"]
            except KeyError as e:
                raise ValueError(
                    "ANTHROPIC_API_KEY environment variable not found"
                ) from e
        else:
            api_key = settings.ANTHROPIC_API_KEY

        self._client = ChatAnthropic(
            api_key=api_key, model=model or settings.PRIMARY_LLM_MODEL
        )

    def generate_structured_output(
        self, prompt: str, output_schema: type[BaseModel]
    ) -> BaseModel:
        """Generate structured output using the Anthropic API.

        Args:
            prompt: The prompt to send to the LLM
            output_schema: The Pydantic model class to structure the output

        Returns:
            An instance of the output_schema with the LLM's response

        Raises:
            Exception: If the API call fails
        """
        try:
            structured_client = self._client.with_structured_output(output_schema)
            result = structured_client.invoke(prompt)

            # Log token usage if available
            if hasattr(result, "usage_metadata") and result.usage_metadata:
                logger = structlog.get_logger()
                usage = result.usage_metadata
                logger.info(
                    "LLM token usage",
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                )

            return result
        except Exception as e:
            raise Exception(f"Failed to generate structured output: {e}") from e
