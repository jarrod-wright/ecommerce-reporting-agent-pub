"""Dynamic tool access scoping for AI agent security.

Implements semantic input classification to scope tool access based on prompt risk.
Part of the Constitutional Security Pattern.
"""

from enum import Enum
from typing import Any, Dict, List

import structlog

from agent.clients.factory import get_llm_client
from agent.tools.ga4_tools import get_ga4_sessions
from agent.tools.shopify_tools import get_shopify_orders


class RiskLevel(Enum):
    """Risk classification levels for dynamic tool scoping."""

    LOW_RISK = "low_risk"
    HIGH_RISK = "high_risk"


class ToolRouter:
    """Routes and scopes tools based on semantic input classification."""

    def __init__(self, llm_provider: str = "GOOGLE"):
        """Initialize ToolRouter with LLM client for classification.

        Args:
            llm_provider: Provider for classification LLM ("GOOGLE" for Gemini Flash)
        """
        self.logger = structlog.get_logger()

        # Try to initialize LLM client, fallback to None if credentials missing
        try:
            self.llm_client = get_llm_client(llm_provider)
        except ValueError as e:
            self.logger.warning(
                "Failed to initialize LLM client, will use simple keyword fallback",
                error=str(e),
            )
            self.llm_client = None

        # Low-risk tools: read-only analytics and reporting
        self.low_risk_tools = [get_shopify_orders, get_ga4_sessions]

        # High-risk tools: system modification capabilities (placeholder tools)
        self.high_risk_tools = []

        self.classification_prompt = """Analyze the following user prompt and classify its risk level.

LOW_RISK prompts are for:
- Reading data (analytics, reports, viewing information)
- Generating insights or visualizations
- Creating reports or summaries
- Non-destructive analysis tasks

HIGH_RISK prompts involve:
- Modifying, deleting, or updating data
- System commands or administrative tasks
- External API calls that change state
- Any destructive or side-effect operations

User prompt: "{prompt}"

Respond with only "low_risk" or "high_risk" (no explanation needed)."""

    def classify_and_scope_tools(self, user_prompt: str) -> Dict[str, Any]:
        """Classify input prompt using LLM and return appropriate tool scope.

        Args:
            user_prompt: User input to classify for risk level

        Returns:
            Dictionary containing risk_level and available_tools
        """
        try:
            # Use LLM for classification if available
            if self.llm_client:
                classification_request = self.classification_prompt.format(
                    prompt=user_prompt
                )
                response = self.llm_client.generate(
                    prompt=classification_request,
                    max_tokens=10,
                    temperature=0.0,  # Deterministic classification
                )

                risk_level = response.strip().lower()
                self.logger.info(
                    "Classified user prompt using LLM",
                    risk_level=risk_level,
                    prompt_length=len(user_prompt),
                )

                if risk_level == "high_risk":
                    return {
                        "risk_level": RiskLevel.HIGH_RISK.value,
                        "available_tools": self.high_risk_tools,
                    }
                else:
                    # Default to low_risk for safety
                    return {
                        "risk_level": RiskLevel.LOW_RISK.value,
                        "available_tools": self.low_risk_tools,
                    }
            else:
                # Fallback to keyword-based classification
                self.logger.info(
                    "Using keyword-based classification fallback",
                    prompt_length=len(user_prompt),
                )
                if any(
                    keyword in user_prompt.lower()
                    for keyword in [
                        "delete",
                        "modify",
                        "execute",
                        "command",
                        "system",
                        "remove",
                        "drop",
                    ]
                ):
                    return {
                        "risk_level": RiskLevel.HIGH_RISK.value,
                        "available_tools": self.high_risk_tools,
                    }
                else:
                    return {
                        "risk_level": RiskLevel.LOW_RISK.value,
                        "available_tools": self.low_risk_tools,
                    }

        except Exception as e:
            # Fallback to safe default on any error
            self.logger.warning(
                "Classification failed, defaulting to low_risk",
                error=str(e),
                prompt_length=len(user_prompt),
            )
            return {
                "risk_level": RiskLevel.LOW_RISK.value,
                "available_tools": self.low_risk_tools,
            }

    def get_tool_names(self, tools: List) -> List[str]:
        """Extract tool names from tool objects for compatibility."""
        return [tool.name if hasattr(tool, "name") else str(tool) for tool in tools]


def create_agent_with_scoped_tools(user_prompt: str, tool_router: ToolRouter = None):
    """Factory function to create agent with dynamically scoped tools.

    Args:
        user_prompt: User input to analyze for tool scoping
        tool_router: Optional ToolRouter instance for dependency injection

    Returns:
        Mock agent object with scoped tools (placeholder implementation)
    """
    if tool_router is None:
        tool_router = ToolRouter()

    scoping_result = tool_router.classify_and_scope_tools(user_prompt)

    # Placeholder agent creation - this would be replaced with actual agent factory
    return {
        "risk_level": scoping_result["risk_level"],
        "available_tools": scoping_result["available_tools"],
        "prompt": user_prompt,
    }
