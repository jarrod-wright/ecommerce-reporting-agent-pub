from typing import Optional

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# The analyzer loads a heavy NLP model on first construction (~hundreds of MB);
# build it once per process and reuse it. The multi-scale performance suite
# measures process RSS, so repeated engine construction would break the memory
# budgets.
_engines: Optional[tuple] = None


def _get_engines() -> tuple:
    """Return the process-wide (analyzer, anonymizer) pair, building on first use."""
    global _engines
    if _engines is None:
        _engines = (AnalyzerEngine(), AnonymizerEngine())
    return _engines


def scrub_text_for_pii(text: str) -> str:
    """
    Scrub PII from text using Presidio analyzer and anonymizer.

    Args:
        text: Input text that may contain PII

    Returns:
        Text with PII replaced by entity type placeholders
    """
    analyzer, anonymizer = _get_engines()

    # Find PII entities in the text
    results = analyzer.analyze(text=text, language='en')

    # Configure anonymization to replace with entity type in square brackets
    operators = {}
    for entity_type in {result.entity_type for result in results}:
        operators[entity_type] = OperatorConfig(
            "replace", {"new_value": f"[{entity_type}]"}
        )

    # Anonymize the text
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=operators
    )

    return anonymized_result.text
