import os

import structlog
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from agent.config import settings

from .llm_interface import LLMClient


class GoogleAIClient(LLMClient):
    """Google AI-specific implementation of the LLMClient interface."""

    def __init__(self, model: str | None = None) -> None:
        """Initialize the GoogleAIClient with API key from settings.

        Args:
            model: Optional model ID override. Falls back to the challenger
                model from settings when not provided.
        """
        if not settings.GOOGLE_API_KEY:
            try:
                api_key = os.environ["GOOGLE_API_KEY"]
            except KeyError as e:
                raise ValueError("GOOGLE_API_KEY environment variable not found") from e
        else:
            api_key = settings.GOOGLE_API_KEY

        self._client = ChatGoogleGenerativeAI(
            api_key=api_key,
            model=model or settings.CHALLENGER_LLM_MODEL,
            temperature=0,
            convert_system_message_to_human=True,
        )

    def generate_structured_output(
        self, prompt: str, output_schema: type[BaseModel]
    ) -> BaseModel:
        """Generate structured output using the Google AI API.

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
