"""Self-critique node for confidence scoring via challenger LLM."""

from typing import Any, Dict

import structlog
from pydantic import BaseModel

from agent.clients.factory import get_llm_client_for_role
from agent.models.state import ReportingAgentState

logger = structlog.get_logger()


class CritiqueReport(BaseModel):
    """Pydantic model for structured self-critique assessment output."""

    confidence_score: float
    critique: str


def self_critique_node(state: ReportingAgentState) -> Dict[str, Any]:
    """
    Assess confidence in generated insights using a challenger LLM.

    This node implements the Self-Critique component of the XAI Integration
    Playbook's "trust sandwich" architecture. It employs a challenger model
    (a distinct role, which may be a different provider) to critique the primary
    LLM's insights, following the "LLM-as-a-Judge" pattern for adversarial
    evaluation.

    Args:
        state: Current ReportingAgentState containing generated_insights

    Returns:
        Dictionary with confidence_score and critique keys

    Raises:
        Exception: If the challenger LLM client fails to generate critique
    """
    logger.info("Starting self-critique confidence assessment")

    try:
        # Validate input data exists
        if not state.generated_insights:
            logger.warning("No generated_insights found in state")
            return {
                "confidence_score": 0.0,
                "critique": "No insights found to critique.",
            }

        # Get the challenger-role LLM client (provider + model resolved from settings)
        client = get_llm_client_for_role("challenger")

        # Red Team CFO prompt template for skeptical evaluation
        summary = state.generated_insights.get("summary", "No summary provided")
        metrics = state.generated_insights.get("key_metrics", "No metrics provided")
        recommendations = state.generated_insights.get(
            "recommendations", "No recommendations provided"
        )
        quality_notes = state.generated_insights.get(
            "data_quality_notes", "No quality notes provided"
        )

        prompt = f"""
You are a skeptical CFO and financial risk analyst conducting a rigorous audit
of AI-generated business intelligence insights. Your role is to be the "Red Team"
challenger who identifies flaws, biases, and unsupported claims that could lead
to poor business decisions.

ORIGINAL BUSINESS QUESTION: Analyze e-commerce performance data

SOURCE DATA SUMMARY:
{state.processed_dataframe_json}

AI-GENERATED INSIGHTS TO CRITIQUE:
Summary: {summary}

Key Metrics: {metrics}

Recommendations: {recommendations}

Data Quality Notes: {quality_notes}

EVALUATION CRITERIA (Score each 0-1, then average):
1. **Factual Groundedness**: Are ALL claims fully supported by the source data?
   Look for extrapolations beyond what the data shows.

2. **Business Relevance**: Do insights directly answer strategic business questions?
   Are recommendations actionable and specific?

3. **Logical Consistency**: Are there internal contradictions?
   Do metrics align with stated conclusions?

4. **Risk Assessment**: What are the potential downsides if these recommendations
   are wrong? Are uncertainties acknowledged?

5. **Completeness**: Are there obvious blind spots or missing considerations
   that a business leader should know?

SCORING GUIDELINES:
- 0.9-1.0: Exceptional - Insights are rock-solid, well-supported, and ready for
  executive action
- 0.75-0.89: Strong - Generally reliable with minor gaps that don't affect core
  conclusions
- 0.6-0.74: Adequate - Useful insights but require additional validation before
  major decisions
- 0.4-0.59: Weak - Significant issues that undermine reliability; use for
  discussion only
- 0.0-0.39: Poor - Insights are misleading, unsupported, or could lead to
  harmful decisions

Provide your assessment as a skeptical CFO would: What would make you hesitate
to approve a budget or strategy based on these insights? What questions would
you ask the team before proceeding?

Be constructively critical - your role is to protect the business from poor
decisions while acknowledging what's done well.
"""

        logger.info("Generating structured self-critique assessment")

        # Generate structured output using challenger LLM client
        critique = client.generate_structured_output(prompt, CritiqueReport)

        logger.info(
            "Self-critique assessment completed",
            confidence_score=critique.confidence_score,
            critique_length=len(critique.critique),
        )

        # Return state update dictionary
        return {
            "confidence_score": critique.confidence_score,
            "critique": critique.critique,
        }

    except Exception as e:
        logger.error("Failed to assess insight confidence", error=str(e))
        return {
            "confidence_score": 0.0,
            "critique": (
                f"Self-critique assessment failed due to system error: {str(e)}"
            ),
        }
