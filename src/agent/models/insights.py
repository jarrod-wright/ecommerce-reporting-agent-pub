"""Pydantic models for structured insights generation from e-commerce performance data."""

import json
import re
from typing import Any, Dict, List

import bleach
from pydantic import BaseModel, Field, field_validator

_UNSAFE_TAGS = "script|iframe|img|object|embed|form"


def _sanitize_html(v: str) -> str:
    """Strip HTML/JS from an untrusted (LLM-produced) string.

    Single audited sanitisation path used by every free-text field. Opening/closing
    unsafe tags are replaced with [removed], inline event handlers / javascript: are
    stripped, and bleach performs a final tag-stripping pass.
    """
    if not isinstance(v, str):
        return v
    sanitized = re.sub(rf'<({_UNSAFE_TAGS})[^>]*/?>', '[removed]', v, flags=re.IGNORECASE)
    sanitized = re.sub(rf'</({_UNSAFE_TAGS})>', '[removed]', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'\s(on\w+\s*=|javascript:)[^>\s]*', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'\[removed\]\[removed\]', '[removed]', sanitized)
    return bleach.clean(sanitized, tags=[], attributes={}, strip=True)


class Recommendation(BaseModel):
    """A single strategic recommendation: a short action title plus its rationale."""

    title: str = Field(
        description="Short, action-oriented recommendation headline"
    )
    rationale: str = Field(
        default="",
        description="Why it matters and the expected impact, grounded in the data",
    )

    @field_validator("title", "rationale")
    @classmethod
    def _sanitize(cls, v: str) -> str:
        return _sanitize_html(v)


class ReportInsights(BaseModel):
    """
    Structured insights model for e-commerce performance analysis.

    This model captures the key components of business insights generated
    from processed Shopify and GA4 data, including summary analysis,
    calculated metrics, strategic recommendations, and data quality observations.
    """

    summary: str = Field(
        description="Concise summary of overall performance trends and key findings"
    )

    key_metrics: Dict[str, Any] = Field(
        description=(
            "A JSON object (dictionary) mapping metric names to their values, e.g. "
            '{"total_revenue": 12345.67, "average_order_value": 85.5, '
            '"conversion_rate": 0.031}. Return an object, not a string.'
        )
    )

    recommendations: List[Recommendation] = Field(
        description=(
            "A JSON array of recommendation objects, each with a short action-oriented "
            '"title" and a "rationale" grounded in the data, e.g. '
            '[{"title": "Increase spend on peak days", "rationale": "Jan 15 drove 40% of revenue."}].'
        )
    )

    data_quality_notes: str = Field(
        description="Observations about data quality, completeness, or anomalies"
    )

    @field_validator("key_metrics", mode="before")
    @classmethod
    def coerce_key_metrics(cls, v: Any) -> Any:
        """Tolerate models that return key_metrics as prose, JSON-string, or a list instead of a dict.

        Some providers (notably smaller models) format key_metrics as a string or
        list under structured output. A JSON *string* (observed with gemini-3.5-flash,
        which returns key_metrics as a serialised JSON object) is parsed back into a
        real dict/list so the report renders structured metric cards instead of one
        opaque {"details": "<raw json>"} blob. Genuine prose is preserved unchanged.
        """
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            stripped = v.strip()
            if stripped:
                try:
                    parsed = json.loads(stripped)
                except (ValueError, TypeError):
                    parsed = None
                if isinstance(parsed, dict):
                    return parsed
                if isinstance(parsed, list):
                    return {f"metric_{i + 1}": item for i, item in enumerate(parsed)}
            return {"details": v}
        if isinstance(v, list):
            return {f"metric_{i + 1}": item for i, item in enumerate(v)}
        if v is None:
            return {}
        return {"details": str(v)}

    @field_validator("recommendations", mode="before")
    @classmethod
    def coerce_recommendations(cls, v: Any) -> Any:
        """Coerce provider output into a list of {title, rationale} objects.

        Accepts the structured form (list of dicts) and stays backward-compatible with
        the older flat form (a list of strings, or a single string): a bare string
        becomes {"title": <str>, "rationale": ""}. Dicts using common alias keys
        (recommendation/action/headline/name; reason/why/impact/detail/description) are
        mapped, and any unrecognised dict shape is stringified so validation never
        crashes on provider drift.
        """
        if v is None:
            return []
        if isinstance(v, (str, dict)):
            v = [v]
        if not isinstance(v, list):
            v = [v]

        title_keys = ("title", "recommendation", "action", "headline", "name")
        rationale_keys = ("rationale", "reason", "why", "impact", "detail", "description")

        coerced: List[Any] = []
        for item in v:
            if isinstance(item, dict):
                title = next((item[k] for k in title_keys if item.get(k) not in (None, "")), None)
                rationale = next((item[k] for k in rationale_keys if item.get(k) not in (None, "")), "")
                if title is None:
                    title = "; ".join(f"{k}: {val}" for k, val in item.items()) if item else ""
                coerced.append({"title": str(title), "rationale": str(rationale)})
            elif isinstance(item, str):
                coerced.append({"title": item, "rationale": ""})
            else:
                coerced.append({"title": str(item), "rationale": ""})
        return coerced

    @field_validator("summary", "data_quality_notes")
    @classmethod
    def sanitize_html_string_fields(cls, v: str) -> str:
        """Sanitize HTML/JS from free-text string fields."""
        return _sanitize_html(v)
