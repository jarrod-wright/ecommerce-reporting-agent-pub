from typing import Optional

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# en_core_web_sm (not presidio's en_core_web_lg default): the lg model loads
# ~560MB RSS and breaks the multi-scale performance suite's memory budgets;
# sm loads ~40MB and detects the same common entities. Built once per process.
_NLP_CONF = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}

_engines: Optional[tuple] = None


def _get_engines() -> tuple:
    """Return the process-wide (analyzer, anonymizer) pair, building on first use."""
    global _engines
    if _engines is None:
        nlp_engine = NlpEngineProvider(nlp_engine_configuration=_NLP_CONF).create_engine()
        _engines = (
            AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"]),
            AnonymizerEngine(),
        )
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
