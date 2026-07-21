from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMClient(ABC):
    """Abstract base class for all LLM client implementations."""

    @abstractmethod
    def generate_structured_output(
        self, prompt: str, output_schema: type[BaseModel]
    ) -> BaseModel:
        """Generate structured output using the specified schema.

        Args:
            prompt: The prompt to send to the LLM
            output_schema: The Pydantic model class to structure the output

        Returns:
            An instance of the output_schema with the LLM's response
        """
        pass
